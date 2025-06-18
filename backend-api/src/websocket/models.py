from pydantic import BaseModel, Field
from typing import Optional, Union
from enum import Enum


class MessageType(str, Enum):
    """메시지 타입 열거형"""

    CHAT = "chat"
    PING = "ping"


class ChatRequest(BaseModel):
    """채팅 요청 모델"""

    type: MessageType = Field(default=MessageType.CHAT, description="메시지 타입")
    text: str = Field(
        ..., min_length=1, max_length=4000, description="사용자 입력 텍스트"
    )
    enable_tts: bool = Field(default=True, description="TTS 음성 생성 여부")
    reference_id: Optional[str] = Field(default=None, description="사용할 음성 ID")

    class Config:
        json_schema_extra = {
            "examples": [
                {"type": "chat", "text": "안녕하세요!", "enable_tts": True},
                {"type": "chat", "text": "빠른 질문입니다", "enable_tts": False},
            ]
        }


class PingRequest(BaseModel):
    """연결 상태 확인 요청"""

    type: MessageType = Field(default=MessageType.PING, description="메시지 타입")
    timestamp: Optional[float] = Field(
        default=None, description="클라이언트 타임스탬프"
    )


class ResponseType(str, Enum):
    """응답 타입 열거형"""

    CONTENT = "content"
    AUDIO = "audio"
    LLM_COMPLETE = "llm_complete"
    ERROR = "error"
    PONG = "pong"


class ContentResponse(BaseModel):
    """LLM 콘텐츠 스트리밍 응답"""

    type: ResponseType = Field(default=ResponseType.CONTENT)
    text: str = Field(..., description="스트리밍 텍스트 청크")
    chunk_id: Optional[int] = Field(default=None, description="청크 순서")


class AudioResponse(BaseModel):
    """TTS 음성 응답"""

    type: ResponseType = Field(default=ResponseType.AUDIO)
    data: str = Field(..., description="Base64 인코딩된 음성 데이터")
    format: str = Field(default="wav", description="오디오 포맷")
    text: str = Field(..., description="음성으로 변환된 텍스트")
    duration: Optional[float] = Field(default=None, description="음성 길이(초)")


class LLMCompleteResponse(BaseModel):
    """LLM 응답 완료 신호"""

    type: ResponseType = Field(default=ResponseType.LLM_COMPLETE)
    text: str = Field(..., description="완성된 전체 응답 텍스트")
    tts_enabled: bool = Field(..., description="TTS 처리 여부")
    token_count: Optional[int] = Field(default=None, description="사용된 토큰 수")


class ErrorResponse(BaseModel):
    """에러 응답"""

    type: ResponseType = Field(default=ResponseType.ERROR)
    message: str = Field(..., description="에러 메시지")
    error_code: Optional[str] = Field(default=None, description="에러 코드")
    details: Optional[dict] = Field(default=None, description="추가 에러 정보")


class PongResponse(BaseModel):
    """Ping 응답"""

    type: ResponseType = Field(default=ResponseType.PONG)
    timestamp: float = Field(..., description="서버 타임스탬프")
    client_timestamp: Optional[float] = Field(
        default=None, description="클라이언트 타임스탬프 에코"
    )


# Union 타입들
WebSocketRequest = Union[ChatRequest, PingRequest]
WebSocketResponse = Union[
    ContentResponse,
    AudioResponse,
    LLMCompleteResponse,
    ErrorResponse,
    PongResponse,
]
