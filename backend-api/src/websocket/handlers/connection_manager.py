"""
WebSocket connection management module.

This module handles the main WebSocket connection lifecycle, message routing,
and resource cleanup.
"""

import asyncio
from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect
from langchain_core.messages import SystemMessage
from src.services.llm_service.service import ChatWaifu_LLM
from src.services.tts_service.service import ChatWaifu_TTS
from src.core.logging import setup_logging
from ..models import ChatRequest, PingRequest, TTSInterruptRequest
from ..tts_worker import tts_worker, cleanup_tts_queue, interrupt_tts
from .message_parser import parse_websocket_message
from .error_handler import send_error_response
from .chat_handler import handle_chat_request
from .ping_handler import handle_ping_request
from .tts_handler import handle_tts_interrupt_request

logger = setup_logging("websocket_connection_manager")

# 클라이언트별 AI 응답 상태 추적
client_ai_responding: Dict[str, bool] = {}


async def handle_websocket(
    websocket: WebSocket,
    client_id: str,
    chat_waifu_llm: ChatWaifu_LLM,
    chat_waifu_tts: ChatWaifu_TTS,
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
                            client_ai_responding,
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
