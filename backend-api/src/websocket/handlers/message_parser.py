"""
WebSocket message parsing and validation module.

This module handles parsing and validation of incoming WebSocket messages,
converting them to appropriate request objects.
"""

import json
from typing import Union

from pydantic import ValidationError

from ..models import ChatRequest, MessageType, PingRequest, TTSInterruptRequest


async def parse_websocket_message(
    raw_data: str,
) -> Union[ChatRequest, PingRequest, TTSInterruptRequest]:
    """
    WebSocket 메시지 파싱 및 검증

    Args:
        raw_data: Raw WebSocket message data

    Returns:
        Parsed and validated request object

    Raises:
        ValueError: If message format is invalid
    """
    try:
        # JSON 파싱 시도
        if raw_data.startswith("{"):
            data = json.loads(raw_data)
            message_type = data.get("type", "chat")

            if message_type == MessageType.CHAT:
                return ChatRequest(**data)
            elif message_type == MessageType.PING:
                return PingRequest(**data)
            elif message_type == MessageType.TTS_INTERRUPT:
                return TTSInterruptRequest(**data)
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
