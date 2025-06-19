import json
import asyncio
import time
from typing import Union, Dict
from fastapi import WebSocket, WebSocketDisconnect
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import ValidationError
from src.services.llm_service.service import ChatWaifu_LLM
from src.services.tts_service.service import ChatWaifu_TTS
from src.configs import settings
from src.core.logging import setup_logging
from .tts_worker import tts_worker, add_tts_to_queue, cleanup_tts_queue, interrupt_tts
from .models import (
    ChatRequest,
    PingRequest,
    TTSInterruptRequest,
    ContentResponse,
    StreamingTTSResponse,
    AudioResponse,
    LLMCompleteResponse,
    ErrorResponse,
    PongResponse,
    TTSInterruptedResponse,
    MessageType,
    ResponseType,
)

logger = setup_logging("websocket_handler")

# 클라이언트별 AI 응답 상태 추적
client_ai_responding: Dict[str, bool] = {}


async def parse_websocket_message(
    raw_data: str,
) -> Union[ChatRequest, PingRequest, TTSInterruptRequest]:
    """WebSocket 메시지 파싱 및 검증"""
    try:
        # JSON 파싱 시도
        if raw_data.startswith("{"):
            data = json.loads(raw_data)
            message_type = data.get("type", "chat")

            if message_type == MessageType.CHAT:
                return ChatRequest(**data)
            elif message_type == MessageType.PING:
                return PingRequest(**data)
            elif message_type == MessageType.TTS_INTERRUPT:
                return TTSInterruptRequest(**data)
            else:
                # 기본값으로 ChatRequest 처리
                return ChatRequest(text=data.get("text", ""), **data)
        else:
            # 일반 텍스트인 경우 ChatRequest로 처리
            return ChatRequest(text=raw_data, enable_tts=True)

    except ValidationError as e:
        raise ValueError(f"잘못된 요청 형식: {e}")
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 일반 텍스트로 처리
        return ChatRequest(text=raw_data, enable_tts=True)


async def send_error_response(
    websocket: WebSocket, message: str, error_code: str = None
):
    """에러 응답 전송"""
    error_response = ErrorResponse(message=message, error_code=error_code)
    await websocket.send_json(error_response.model_dump())


async def handle_chat_request(
    websocket: WebSocket,
    client_id: str,
    request: ChatRequest,
    chat_waifu_llm: ChatWaifu_LLM,
    message_history: list,
    mcp_config: dict,
):
    """채팅 요청 처리"""
    logger.info(
        f"Client #{client_id} 메시지: '{request.text}' (TTS: {request.enable_tts})"
    )
    message_history.append(HumanMessage(content=request.text))

    # AI 응답 시작 - 상태 설정
    client_ai_responding[client_id] = True
    logger.info(f"Client #{client_id} 에게 LLM 스트리밍 시작...")

    try:
        # Initialize streaming TTS processor if TTS is enabled
        streaming_processor = None
        sentence_id = 0

        if request.enable_tts:
            from src.services.tts_service.streaming_processor import (
                StreamingTTSProcessor,
            )

            streaming_processor = StreamingTTSProcessor(
                skip_internal_reasoning=request.skip_internal_reasoning,
                reasoning_start_tag=request.reasoning_start_tag,
                reasoning_end_tag=request.reasoning_end_tag,
            )
            logger.info(
                f"Client #{client_id} 스트리밍 TTS 프로세서 초기화 (skip_internal_reasoning: {request.skip_internal_reasoning}, "
                f"reasoning_tags: '{request.reasoning_start_tag}' -> '{request.reasoning_end_tag}')"
            )

        ai_response_text_chunks = []
        chunk_id = 0

        async for result in chat_waifu_llm.stream(
            message=message_history, mcp_config=mcp_config
        ):
            # 기존 스트리밍 결과를 새로운 형식으로 변환
            if result.get("type") == "content" and result.get("text"):
                content_response = ContentResponse(
                    text=result.get("text"), chunk_id=chunk_id
                )
                await websocket.send_json(content_response.model_dump())
                ai_response_text_chunks.append(result.get("text"))

                # Streaming TTS processing
                if streaming_processor and request.enable_tts:
                    chunk_text = result.get("text")
                    if streaming_processor.should_process_chunk_for_tts(chunk_text):
                        complete_sentences = streaming_processor.add_chunk(chunk_text)

                        # Send complete sentences immediately for TTS
                        for sentence in complete_sentences:
                            streaming_tts_response = StreamingTTSResponse(
                                sentence=sentence,
                                sentence_id=sentence_id,
                                is_final=False,
                            )
                            await websocket.send_json(
                                streaming_tts_response.model_dump()
                            )

                            # Add to TTS queue immediately with reference_id
                            await add_tts_to_queue(
                                str(client_id), sentence, request.reference_id
                            )
                            logger.info(
                                f"Client #{client_id} 스트리밍 TTS 문장 #{sentence_id}: '{sentence[:50]}...'"
                            )
                            sentence_id += 1

                chunk_id += 1
            else:
                # 다른 타입의 메시지는 그대로 전송
                await websocket.send_json(result)

        # LLM 응답 완료 처리
        if ai_response_text_chunks:
            full_ai_response = "".join(ai_response_text_chunks)
            message_history.append(AIMessage(content=full_ai_response))
            logger.info(f"LLM 응답 (Client #{client_id}): '{full_ai_response}'")

            # Process any remaining text for streaming TTS
            if streaming_processor and request.enable_tts:
                final_sentences = streaming_processor.finalize()
                for sentence in final_sentences:
                    streaming_tts_response = StreamingTTSResponse(
                        sentence=sentence, sentence_id=sentence_id, is_final=True
                    )
                    await websocket.send_json(streaming_tts_response.model_dump())

                    # Add to TTS queue with reference_id
                    await add_tts_to_queue(
                        str(client_id), sentence, request.reference_id
                    )
                    logger.info(
                        f"Client #{client_id} 최종 TTS 문장 #{sentence_id}: '{sentence[:50]}...'"
                    )
                    sentence_id += 1

            # 완료 응답 전송
            complete_response = LLMCompleteResponse(
                text=full_ai_response,
                tts_enabled=request.enable_tts,
                token_count=len(full_ai_response.split()),  # 대략적인 토큰 수
            )
            await websocket.send_json(complete_response.model_dump())

            # Legacy TTS processing (fallback if streaming TTS is disabled)
            if request.enable_tts and not streaming_processor:
                await add_tts_to_queue(
                    str(client_id), full_ai_response, request.reference_id
                )
                logger.info(f"Client #{client_id} 레거시 TTS 큐에 추가됨")

    finally:
        # AI 응답 완료 - 상태 해제
        client_ai_responding[client_id] = False
        logger.info(f"Client #{client_id} AI 응답 완료, 상태 해제")


async def handle_ping_request(websocket: WebSocket, request: PingRequest):
    """Ping 요청 처리"""
    pong_response = PongResponse(
        timestamp=time.time(), client_timestamp=request.timestamp
    )
    await websocket.send_json(pong_response.model_dump())


async def handle_tts_interrupt_request(
    websocket: WebSocket, client_id: str, request: TTSInterruptRequest
):
    """TTS 중단 요청 처리"""
    logger.info(f"🚫 Client #{client_id} TTS interrupt requested: {request.reason}")

    try:
        interrupted_count = await interrupt_tts(str(client_id))

        interrupt_response = TTSInterruptedResponse(
            message=f"TTS interrupted: {request.reason}",
            interrupted_count=interrupted_count,
        )
        await websocket.send_json(interrupt_response.model_dump())

        logger.info(
            f"✅ Client #{client_id} TTS interrupted successfully, cleared {interrupted_count} items"
        )

    except Exception as e:
        logger.error(f"❌ Client #{client_id} TTS interrupt failed: {e}")
        await send_error_response(
            websocket,
            f"TTS interrupt failed: {str(e)}",
            error_code="TTS_INTERRUPT_FAILED",
        )


async def handle_websocket(
    websocket: WebSocket,
    client_id: str,
    chat_waifu_llm: ChatWaifu_LLM,
    chat_waifu_tts: ChatWaifu_TTS,
    persona: str,
    mcp_config: dict,
):
    """WebSocket connection handler with robust error handling"""
    tts_task = None
    try:
        await websocket.accept()
        logger.info(f"✅ Client #{client_id} connection accepted successfully!")

        # Initialize Langchain message format
        message_history = [SystemMessage(content=persona)]
        logger.info(f"📝 Client #{client_id} message history initialized")

        # Start TTS worker task with error isolation
        logger.info(f"🔊 Client #{client_id} starting TTS worker...")
        try:
            tts_task = asyncio.create_task(
                tts_worker(str(client_id), websocket, chat_waifu_tts)
            )
            logger.info(f"✅ Client #{client_id} TTS worker started successfully")
        except Exception as tts_init_error:
            logger.error(
                f"⚠️ Client #{client_id} TTS worker initialization failed: {tts_init_error}"
            )
            # Continue without TTS functionality

        logger.info(
            f"✅ Client #{client_id} initialization complete! Waiting for messages..."
        )

        while True:
            try:
                logger.debug(f"⏳ Client #{client_id} waiting for message...")
                raw_data = await websocket.receive_text()
                logger.info(
                    f"📨 Client #{client_id} message received: {raw_data[:100]}..."
                )

                try:
                    # Parse and validate message
                    request = await parse_websocket_message(raw_data)
                    logger.info(
                        f"✅ Client #{client_id} message parsed successfully: {type(request).__name__}"
                    )

                    # Handle message by type
                    if isinstance(request, ChatRequest):
                        # Only interrupt TTS if AI is currently responding
                        if client_ai_responding.get(client_id, False):
                            await interrupt_tts(str(client_id))
                            logger.info(
                                f"🚫 Client #{client_id} TTS interrupted - AI was responding when user sent new message"
                            )
                        else:
                            logger.info(
                                f"✅ Client #{client_id} new chat message - no TTS to interrupt (AI not responding)"
                            )

                        await handle_chat_request(
                            websocket,
                            client_id,
                            request,
                            chat_waifu_llm,
                            message_history,
                            mcp_config,
                        )
                    elif isinstance(request, PingRequest):
                        await handle_ping_request(websocket, request)
                    elif isinstance(request, TTSInterruptRequest):
                        await handle_tts_interrupt_request(
                            websocket, client_id, request
                        )
                    else:
                        # Unsupported request type
                        await send_error_response(
                            websocket,
                            "Unsupported request type.",
                            error_code="UNSUPPORTED_REQUEST_TYPE",
                        )

                except ValueError as e:
                    logger.warning(f"Client #{client_id} invalid request: {e}")
                    await send_error_response(
                        websocket, str(e), error_code="INVALID_REQUEST"
                    )
                except Exception as e:
                    logger.error(f"Client #{client_id} request processing error: {e}")
                    await send_error_response(
                        websocket,
                        "Error occurred while processing request.",
                        error_code="PROCESSING_ERROR",
                    )

            except WebSocketDisconnect:
                logger.info(
                    f"Client #{client_id} disconnected normally. See you next time! 😊"
                )
                break
            except Exception as message_error:
                logger.error(
                    f"Client #{client_id} message handling error: {message_error}"
                )
                # Try to send error response, but don't crash if it fails
                try:
                    await send_error_response(
                        websocket,
                        "Connection error occurred.",
                        error_code="CONNECTION_ERROR",
                    )
                except:
                    logger.error(
                        f"Failed to send error response to client #{client_id}"
                    )
                break

    except WebSocketDisconnect:
        logger.info(f"Client #{client_id} disconnected during connection. Goodbye! 😢")
    except Exception as e:
        logger.error(f"Client #{client_id} critical connection error: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        # Resource cleanup
        logger.info(f"🧹 Client #{client_id} cleaning up resources...")

        # Cleanup TTS queue
        try:
            cleanup_tts_queue(str(client_id))
        except Exception as cleanup_error:
            logger.error(f"TTS cleanup error: {cleanup_error}")

        # Cancel TTS task
        if tts_task and not tts_task.done():
            try:
                tts_task.cancel()
                try:
                    await asyncio.wait_for(tts_task, timeout=2.0)
                except asyncio.TimeoutError:
                    logger.warning(
                        f"TTS task cancellation timeout for client #{client_id}"
                    )
            except Exception as cancel_error:
                logger.error(f"TTS task cancellation error: {cancel_error}")

        logger.info(f"✅ Client #{client_id} cleanup completed")
