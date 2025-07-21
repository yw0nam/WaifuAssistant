"""
WebSocket handlers module.

This package provides modular WebSocket request handlers for the Waifu Assistant.
Each handler is responsible for a specific type of WebSocket message or functionality.
"""

from .asr_handler import ASRHandler
from .chat_handler import ChatHandler
from .connection_manager import handle_websocket
from .error_handler import send_error_response
from .message_parser import parse_websocket_message
from .ping_handler import handle_ping_request
from .tts_handler import TTSHandler

__all__ = [
    "parse_websocket_message",
    "send_error_response",
    "handle_ping_request",
    "handle_websocket",
    "ASRHandler",
    "ChatHandler",
    "TTSHandler",
]
