from pydantic import BaseModel, Field
from typing import Optional


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
    reference_id: Optional[str] = Field(default=None)
    format: str = Field(default="wav")
    chunk_length: int = Field(default=200, ge=100, le=300)
    normalize: bool = Field(default=True)
    temperature: float = Field(default=0.8, ge=0.1, le=1.0)

    class Config:
        env_prefix = "TTS_"


class AppConfig(BaseModel):
    """전체 애플리케이션 설정"""

    llm_configs: LLMSettings
    tts_configs: TTSSettings
    mcp_configs: MCPSettings

    class Config:
        arbitrary_types_allowed = True
