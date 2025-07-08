"""
WebSocket handlers module - Main entry point.

This module provides a clean public API for WebSocket request handling.
The actual implementation has been modularized into focused handler modules
for better maintainability and testability.

This file serves as a backward-compatible entry point for existing imports.
"""

from src.core.logging import setup_logging

# Import all handler functions from modular implementation
from .handlers import (
    parse_websocket_message,
    send_error_response,
    handle_ping_request,
    handle_tts_interrupt_request,
    handle_chat_request,
    handle_websocket,
)

# Re-export all functions for backward compatibility
__all__ = [
    "parse_websocket_message",
    "send_error_response",
    "handle_ping_request",
    "handle_tts_interrupt_request",
    "handle_chat_request",
    "handle_websocket",
]

logger = setup_logging("websocket_handler")
