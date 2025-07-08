# WebSocket Handlers Module

This module provides a modular WebSocket request handling system for the Waifu Assistant backend.

## Architecture

The WebSocket handlers have been modularized to improve maintainability, testability, and follow the Single Responsibility Principle. Each handler module focuses on a specific aspect of WebSocket communication.

## Module Structure

```
websocket/handlers/
├── __init__.py                 # Module exports and public API
├── message_parser.py           # WebSocket message parsing and validation
├── error_handler.py           # Centralized error handling utilities
├── ping_handler.py            # Ping/Pong health check handling
├── tts_handler.py             # TTS interrupt and management
├── chat_handler.py            # Chat request and LLM streaming
└── connection_manager.py      # Main WebSocket connection lifecycle
```

## Handler Responsibilities

### `message_parser.py`
- Parses incoming WebSocket messages
- Validates message format and structure
- Converts raw data to typed request objects
- Handles both JSON and plain text inputs

### `error_handler.py`
- Provides centralized error response formatting
- Handles error message sending to clients
- Includes proper error logging and categorization

### `ping_handler.py`
- Handles ping/pong messages for connection health checks
- Manages client timestamp tracking
- Provides connection latency monitoring

### `tts_handler.py`
- Handles TTS interruption requests
- Manages TTS queue operations
- Provides TTS status feedback to clients

### `chat_handler.py`
- Processes chat requests and responses
- Manages LLM streaming and text processing
- Handles streaming TTS integration
- Maintains conversation history
- Filters content by node type (agent vs other)

### `connection_manager.py`
- Manages main WebSocket connection lifecycle
- Handles connection acceptance and cleanup
- Routes messages to appropriate handlers
- Manages client state tracking
- Provides resource cleanup and error recovery

## Usage

The main entry point remains unchanged for backward compatibility:

```python
from src.websocket.handlers import handle_websocket

# All other functions are also available:
from src.websocket.handlers import (
    parse_websocket_message,
    send_error_response,
    handle_ping_request,
    handle_tts_interrupt_request,
    handle_chat_request,
)
```

## Benefits

1. **Maintainability**: Each module has a single, clear responsibility
2. **Testability**: Individual handlers can be tested in isolation
3. **Readability**: Shorter, focused files are easier to understand
4. **Modularity**: Changes to one handler don't affect others
5. **Reusability**: Individual handlers can be reused in different contexts
6. **Debugging**: Issues can be isolated to specific handler modules

## Client State Management

The connection manager maintains client-specific state including:
- AI response status (`client_ai_responding`)
- Message history per client
- TTS worker tasks
- Connection cleanup tracking

## Error Handling

Each handler module includes robust error handling:
- Graceful failure modes
- Detailed error logging
- Client error notifications
- Resource cleanup on failures

## Future Enhancements

This modular structure makes it easy to:
- Add new message types and handlers
- Implement handler-specific middleware
- Add handler-level metrics and monitoring
- Create handler-specific tests
- Implement handler hot-reloading for development
