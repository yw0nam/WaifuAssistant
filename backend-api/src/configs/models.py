from pydantic import BaseModel, ConfigDict, Field

# AIDEV-NOTE: Updated to use ConfigDict for Pydantic v2 compatibility
# https://docs.pydantic.dev/latest/usage/configuration/#configdict


class LLMSettings(BaseModel):
    """LLM 관련 설정"""

    model_config = ConfigDict(env_prefix="LLM_")

    openai_api_key: str
    model: str
    openai_api_base: str
    temperature: float
    top_p: float
    max_tokens: int


class MCPSettings(BaseModel):
    """MCP 관련 설정"""

    model_config = ConfigDict(env_prefix="MCP_")

    mcp_servers: dict = Field(default_factory=dict)


class TTSSettings(BaseModel):
    """TTS 관련 설정"""

    model_config = ConfigDict(env_prefix="TTS_")

    api_key: str = Field(default="")
    url: str = Field(default="http://localhost:8080/v1/tts")


class ASRSettings(BaseModel):
    """ASR 관련 설정"""

    model_config = ConfigDict(env_prefix="ASR_")

    api_key: str = Field(default="EMPTY")
    api_base: str = Field(default="http://localhost:8000/v1")
    model: str = Field(default="openai/whisper-large-v3")
    language: str = Field(default="ko")
    temperature: float = Field(default=0.0)
    response_format: str = Field(default="json")


class AppConfig(BaseModel):
    """전체 애플리케이션 설정"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm_configs: LLMSettings
    tts_configs: TTSSettings
    asr_configs: ASRSettings
    mcp_configs: MCPSettings
