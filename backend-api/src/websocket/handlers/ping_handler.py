"""
Ping/Pong WebSocket handler.

This module handles ping/pong messages for WebSocket connection health checks.
"""

import time

from fastapi import WebSocket

from src.core.logging import setup_logging

from ..models import PingRequest, PongResponse

logger = setup_logging("websocket_ping_handler")


async def handle_ping_request(websocket: WebSocket, request: PingRequest) -> None:
    """
    Ping 요청 처리

    Args:
        websocket: WebSocket connection
        request: Ping request object containing timestamp
    """
    try:
        pong_response = PongResponse(
            timestamp=time.time(), client_timestamp=request.timestamp
        )
        await websocket.send_json(pong_response.model_dump())
        logger.debug(f"Pong response sent (client_timestamp: {request.timestamp})")
    except Exception as e:
        logger.error(f"Failed to send pong response: {e}")
        raise
