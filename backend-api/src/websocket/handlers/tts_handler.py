"""
TTS interrupt handling module.

This module handles TTS interruption requests and manages TTS queue operations.
"""

from fastapi import WebSocket

from src.core.logging import setup_logging
from src.services.tts_service.tts_worker import interrupt_tts

from ..models import TTSInterruptedResponse, TTSInterruptRequest
from .error_handler import send_error_response

logger = setup_logging("websocket_tts_handler")


async def handle_tts_interrupt_request(
    websocket: WebSocket, client_id: str, request: TTSInterruptRequest
) -> None:
    """
    TTS 중단 요청 처리

    Args:
        websocket: WebSocket connection
        client_id: Client identifier
        request: TTS interrupt request object
    """
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
