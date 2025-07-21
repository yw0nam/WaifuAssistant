"""
WebSocket connection management module.

This module handles the main WebSocket connection lifecycle, message routing,
and resource cleanup.
"""

import asyncio
from typing import Dict

from fastapi import WebSocket, WebSocketDisconnect
from langchain_core.messages import SystemMessage

from src.core.logging import setup_logging

from ..models import ASRTranscribeRequest, ChatRequest, PingRequest, TTSInterruptRequest
from .asr_handler import ASRHandler
from .chat_handler import ChatHandler
from .error_handler import send_error_response
from .message_parser import parse_websocket_message
from .ping_handler import handle_ping_request
from .tts_handler import TTSHandler

logger = setup_logging("websocket_connection_manager")

# 클라이언트별 AI 응답 상태 추적
client_ai_responding: Dict[str, bool] = {}


async def handle_websocket(
    websocket: WebSocket,
    client_id: str,
    chat_handler: ChatHandler,
    tts_handler: TTSHandler,
    asr_handler: ASRHandler,
    persona: str,
    mcp_config: dict,
) -> None:
    """
    WebSocket connection handler with robust error handling

    Args:
        websocket: WebSocket connection
        client_id: Client identifier
        chat_waifu_llm: LLM service instance
        chat_waifu_tts: TTS service instance
        persona: AI persona/system message
        mcp_config: MCP configuration
    """
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
                tts_handler.worker_manager.tts_worker(
                    str(client_id), websocket, tts_handler.worker_manager.service
                )
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
                            await tts_handler.tts_interrupt_request(
                                websocket,
                                client_id,
                                TTSInterruptRequest(reason="New chat message received"),
                            )
                            logger.info(
                                f"🚫 Client #{client_id} TTS interrupted - AI was responding when user sent new message"
                            )
                        else:
                            logger.info(
                                f"✅ Client #{client_id} new chat message - no TTS to interrupt (AI not responding)"
                            )

                        # AIDEV-NOTE: Process chat request and handle TTS for each sentence chunk
                        async for sentence_data in chat_handler.chat_request(
                            websocket,
                            client_id,
                            request,
                            message_history,
                            mcp_config,
                            client_ai_responding,
                        ):
                            if sentence_data and sentence_data.get("sentence"):
                                await tts_handler.send_to_tts(
                                    client_id=client_id,
                                    sentence=sentence_data["sentence"],
                                    reference_id=sentence_data.get("reference_id"),
                                )

                    elif isinstance(request, PingRequest):
                        await handle_ping_request(websocket, request)
                    elif isinstance(request, TTSInterruptRequest):
                        await tts_handler.tts_interrupt_request(
                            websocket, client_id, request
                        )
                    elif isinstance(request, ASRTranscribeRequest):
                        # AIDEV-NOTE: Handle ASR transcription requests
                        async for asr_response in asr_handler.transcribe_request(
                            request
                        ):
                            await websocket.send_json(asr_response)
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
        await tts_handler.clean_tts_queue(client_id)

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
