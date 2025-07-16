from pydantic import BaseModel, Field

# TODO: pydantic v2로 변경 시 ConfigDict로 변경 필요
# https://docs.pydantic.dev/latest/usage/configuration/#configdict


class LLMSettings(BaseModel):
    """LLM 관련 설정"""

    openai_api_key: str
    model: str
    openai_api_base: str
    temperature: float
    top_p: float
    max_tokens: int

    class Config:
        env_prefix = "LLM_"  # 환경변수 prefix


class MCPSettings(BaseModel):
    """MCP 관련 설정"""

    mcp_servers: dict = Field(default_factory=dict)

    class Config:
        env_prefix = "MCP_"


class TTSSettings(BaseModel):
    """TTS 관련 설정"""

    api_key: str = Field(default="")
    url: str = Field(default="http://localhost:8080/v1/tts")

    class Config:
        env_prefix = "TTS_"


class ASRSettings(BaseModel):
    """ASR 관련 설정"""

    api_key: str = Field(default="EMPTY")
    api_base: str = Field(default="http://localhost:8000/v1")
    model: str = Field(default="openai/whisper-large-v3")
    language: str = Field(default="ko")
    temperature: float = Field(default=0.0)
    response_format: str = Field(default="json")

    class Config:
        env_prefix = "ASR_"


class AppConfig(BaseModel):
    """전체 애플리케이션 설정"""

    llm_configs: LLMSettings
    tts_configs: TTSSettings
    asr_configs: ASRSettings
    mcp_configs: MCPSettings

    class Config:
        arbitrary_types_allowed = True
