"""
WebSocket handlers module.

This package provides modular WebSocket request handlers for the Waifu Assistant.
Each handler is responsible for a specific type of WebSocket message or functionality.
"""

from .chat_handler import handle_chat_request
from .connection_manager import handle_websocket
from .error_handler import send_error_response
from .message_parser import parse_websocket_message
from .ping_handler import handle_ping_request
from .tts_handler import handle_tts_interrupt_request

__all__ = [
    "parse_websocket_message",
    "send_error_response",
    "handle_ping_request",
    "handle_tts_interrupt_request",
    "handle_chat_request",
    "handle_websocket",
]
