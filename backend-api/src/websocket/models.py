from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class MessageType(str, Enum):
    """메시지 타입 열거형"""

    CHAT = "chat"
    PING = "ping"
    TTS_INTERRUPT = "tts_interrupt"
    ASR_TRANSCRIBE = "asr_transcribe"  # AIDEV-NOTE: Audio transcription request


class ChatRequest(BaseModel):
    """채팅 요청 모델"""

    type: MessageType = Field(default=MessageType.CHAT, description="메시지 타입")
    text: str = Field(
        ..., min_length=1, max_length=4000, description="사용자 입력 텍스트"
    )
    enable_tts: bool = Field(default=True, description="TTS 음성 생성 여부")
    skip_internal_reasoning: bool = Field(
        default=True, description="내부 추론 과정 TTS 제외 여부"
    )
    reference_id: Optional[str] = Field(default=None, description="사용할 음성 ID")
    reasoning_start_tag: str = Field(default="<think>", description="추론 시작 태그")
    reasoning_end_tag: str = Field(default="</think>", description="추론 종료 태그")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "chat",
                    "text": "안녕하세요!",
                    "enable_tts": True,
                    "reasoning_start_tag": "<think>",
                    "reasoning_end_tag": "</think>",
                },
                {
                    "type": "chat",
                    "text": "빠른 질문입니다",
                    "enable_tts": False,
                    "reasoning_start_tag": "<thinking>",
                    "reasoning_end_tag": "</thinking>",
                },
            ]
        }
    )


class PingRequest(BaseModel):
    """연결 상태 확인 요청"""

    type: MessageType = Field(default=MessageType.PING, description="메시지 타입")
    timestamp: Optional[float] = Field(
        default=None, description="클라이언트 타임스탬프"
    )


class TTSInterruptRequest(BaseModel):
    """TTS 중단 요청"""

    type: MessageType = Field(
        default=MessageType.TTS_INTERRUPT, description="메시지 타입"
    )
    reason: Optional[str] = Field(default="user_interrupt", description="중단 이유")


class ASRTranscribeRequest(BaseModel):
    """ASR 음성 인식 요청"""

    type: MessageType = Field(
        default=MessageType.ASR_TRANSCRIBE, description="메시지 타입"
    )
    audio_data: str = Field(..., description="Base64 인코딩된 오디오 데이터")
    format: str = Field(default="wav", description="오디오 포맷 (wav, mp3, m4a 등)")
    language: Optional[str] = Field(
        default=None, description="음성 언어 코드 (ko, en, auto 등)"
    )
    temperature: Optional[float] = Field(default=None, description="샘플링 온도")
    response_format: Optional[str] = Field(
        default=None, description="응답 포맷 (json, text 등)"
    )
    streaming: bool = Field(default=False, description="스트리밍 전사 여부")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "asr_transcribe",
                    "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",
                    "format": "wav",
                    "language": "ko",
                    "streaming": False,
                },
                {
                    "type": "asr_transcribe",
                    "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",
                    "format": "mp3",
                    "language": "auto",
                    "streaming": True,
                },
            ]
        }
    )


class ResponseType(str, Enum):
    """응답 타입 열거형"""

    CONTENT = "content"
    LLM_COMPLETE = "llm_complete"
    ERROR = "error"
    PONG = "pong"
    AUDIO = "audio"
    TTS_INTERRUPTED = "tts_interrupted"
    STREAMING_TTS = "streaming_tts"  # New: For real-time TTS sentences
    ASR_RESULT = "asr_result"  # AIDEV-NOTE: ASR transcription result
    ASR_STREAMING = "asr_streaming"  # AIDEV-NOTE: ASR streaming chunk


class ContentResponse(BaseModel):
    """LLM 콘텐츠 스트리밍 응답"""

    type: ResponseType = Field(default=ResponseType.CONTENT)
    text: str = Field(..., description="스트리밍 텍스트 청크")
    emotion_tag: Optional[str] = Field(
        default=None, description="감정 태그 (예: happy, sad 등)"
    )


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


class TTSInterruptedResponse(BaseModel):
    """TTS 중단 응답"""

    type: ResponseType = Field(default=ResponseType.TTS_INTERRUPTED)
    message: str = Field(..., description="중단 메시지")
    interrupted_count: Optional[int] = Field(default=None, description="중단된 항목 수")


class StreamingTTSResponse(BaseModel):
    """실시간 TTS 문장 응답"""

    type: ResponseType = Field(default=ResponseType.STREAMING_TTS)
    sentence: str = Field(..., description="TTS로 변환될 완성된 문장")


class ASRResultResponse(BaseModel):
    """ASR 음성 인식 결과 응답"""

    type: ResponseType = Field(default=ResponseType.ASR_RESULT)
    text: str = Field(..., description="전사된 텍스트")
    language: Optional[str] = Field(default=None, description="감지된 언어")
    confidence: Optional[float] = Field(default=None, description="신뢰도 점수")
    processing_time: Optional[float] = Field(default=None, description="처리 시간(초)")


class ASRStreamingResponse(BaseModel):
    """ASR 스트리밍 전사 응답"""

    type: ResponseType = Field(default=ResponseType.ASR_STREAMING)
    text: str = Field(..., description="실시간 전사 텍스트 청크")
    is_final: bool = Field(default=False, description="최종 결과 여부")


# Union 타입들
WebSocketRequest = Union[
    ChatRequest, PingRequest, TTSInterruptRequest, ASRTranscribeRequest
]
WebSocketResponse = Union[
    ContentResponse,
    AudioResponse,
    LLMCompleteResponse,
    ErrorResponse,
    PongResponse,
    TTSInterruptedResponse,
    StreamingTTSResponse,
    ASRResultResponse,
    ASRStreamingResponse,
]
