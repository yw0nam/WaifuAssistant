"""
WebSocket error handling utilities.

This module provides centralized error handling for WebSocket connections,
including error response formatting and sending.
"""

from fastapi import WebSocket
from src.core.logging import setup_logging
from ..models import ErrorResponse

logger = setup_logging("websocket_error_handler")


async def send_error_response(
    websocket: WebSocket, message: str, error_code: str = None
) -> None:
    """
    에러 응답 전송

    Args:
        websocket: WebSocket connection
        message: Error message to send
        error_code: Optional error code for categorization
    """
    try:
        error_response = ErrorResponse(message=message, error_code=error_code)
        await websocket.send_json(error_response.model_dump())
        logger.debug(f"Error response sent: {message} (code: {error_code})")
    except Exception as e:
        logger.error(f"Failed to send error response: {e}")
        # Don't raise here to avoid cascading errors
