import json
import asyncio
import time
from typing import Union
from fastapi import WebSocket, WebSocketDisconnect
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import ValidationError
from src.services.llm_service import ChatWaifu_LLM
from src.services.tts_service import ChatWaifu_TTS
from src.configs import settings
from src.core.logging import setup_logging
from .tts_worker import tts_worker, add_tts_to_queue, cleanup_tts_queue
from .models import (
    ChatRequest,
    PingRequest,
    ContentResponse,
    AudioResponse,
    LLMCompleteResponse,
    ErrorResponse,
    PongResponse,
    MessageType,
    ResponseType,
)

logger = setup_logging("websocket_handler")


async def parse_websocket_message(raw_data: str) -> Union[ChatRequest, PingRequest]:
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
        return ChatRequest(text=raw_data, enable_tts=True)


async def send_error_response(
    websocket: WebSocket, message: str, error_code: str = None
):
    """에러 응답 전송"""
    error_response = ErrorResponse(message=message, error_code=error_code)
    await websocket.send_json(error_response.model_dump())


async def handle_chat_request(
    websocket: WebSocket,
    client_id: int,
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

    logger.info(f"Client #{client_id} 에게 LLM 스트리밍 시작...")

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
            chunk_id += 1
        else:
            # 다른 타입의 메시지는 그대로 전송
            await websocket.send_json(result)

    # LLM 응답 완료 처리
    if ai_response_text_chunks:
        full_ai_response = "".join(ai_response_text_chunks)
        message_history.append(AIMessage(content=full_ai_response))
        logger.info(f"LLM 응답 (Client #{client_id}): '{full_ai_response}'")

        # 완료 응답 전송
        complete_response = LLMCompleteResponse(
            text=full_ai_response,
            tts_enabled=request.enable_tts,
            token_count=len(full_ai_response.split()),  # 대략적인 토큰 수
        )
        await websocket.send_json(complete_response.model_dump())

        # 조건부 TTS 처리
        if request.enable_tts:
            await add_tts_to_queue(str(client_id), full_ai_response)
            logger.info(f"Client #{client_id} TTS 큐에 추가됨")


async def handle_ping_request(websocket: WebSocket, request: PingRequest):
    """Ping 요청 처리"""
    pong_response = PongResponse(
        timestamp=time.time(), client_timestamp=request.timestamp
    )
    await websocket.send_json(pong_response.model_dump())


async def handle_websocket(
    websocket: WebSocket,
    client_id: int,
    chat_waifu_llm: ChatWaifu_LLM,
    chat_waifu_tts: ChatWaifu_TTS,
    persona: str,
    mcp_config: dict,
):
    """WebSocket 연결 핸들러"""
    await websocket.accept()
    logger.info(f"Client #{client_id} 가 연결되었어요! 반가워요! 👋")

    message_history = [{"role": "system", "content": persona}]

    # TTS 워커 태스크 시작
    tts_task = asyncio.create_task(
        tts_worker(str(client_id), websocket, chat_waifu_tts)
    )

    try:
        while True:
            raw_data = await websocket.receive_text()

            try:
                # 메시지 파싱 및 검증
                request = await parse_websocket_message(raw_data)

                # 메시지 타입별 처리
                if isinstance(request, ChatRequest):
                    await handle_chat_request(
                        websocket,
                        client_id,
                        request,
                        chat_waifu_llm,
                        message_history,
                        mcp_config["mcp_servers"],
                    )
                elif isinstance(request, PingRequest):
                    await handle_ping_request(websocket, request)
                else:
                    # 지원하지 않는 요청 타입
                    await send_error_response(
                        websocket,
                        "지원하지 않는 요청 타입입니다.",
                        error_code="UNSUPPORTED_REQUEST_TYPE",
                    )

            except ValueError as e:
                logger.warning(f"Client #{client_id} 잘못된 요청: {e}")
                await send_error_response(
                    websocket, str(e), error_code="INVALID_REQUEST"
                )
            except Exception as e:
                logger.error(f"Client #{client_id} 요청 처리 중 오류: {e}")
                await send_error_response(
                    websocket,
                    "요청 처리 중 오류가 발생했습니다.",
                    error_code="PROCESSING_ERROR",
                )

    except WebSocketDisconnect:
        logger.info(f"Client #{client_id} 와의 연결이 끊어졌어요. 다음에 또 만나요! 😢")
    except Exception as e:
        logger.error(f"Client #{client_id} 와의 통신 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # TTS 워커 정리
        cleanup_tts_queue(str(client_id))
        tts_task.cancel()

        try:
            await websocket.close(code=1000)
        except:
            pass
