import yaml, json
from pathlib import Path
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal, Optional

CONFIG_DIR = Path(__file__).parent.parent / "configs"
DEFAULT_CONFIG_FILE = CONFIG_DIR / "app_config.yaml"
DEFAULT_MCP_FILE = CONFIG_DIR / "mcp_config.json"


class LLMSettings(BaseModel):
    openai_api_key: str
    model: str
    openai_api_base: str
    temperature: float
    top_p: float
    max_tokens: int


class MCPSettings(BaseModel):
    mcp_servers: dict = Field(default_factory=dict)


class AppConfig(BaseModel):
    llm_configs: LLMSettings
    # tts: TTSSettings
    mcp_configs: MCPSettings


def load_config(config_file: Path = DEFAULT_CONFIG_FILE) -> AppConfig:
    """YAML 설정 파일을 읽어서 AppConfig 객체로 변환해요."""

    with open(config_file, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    with open(DEFAULT_MCP_FILE, "r", encoding="utf-8") as f:
        mcp_data = json.load(f)
    # YAML 데이터를 Pydantic 모델로 파싱해요.
    # 이때 환경 변수가 YAML 파일의 값보다 우선적으로 적용될 수 있도록 Pydantic 모델 설정을 활용할 수 있어요.
    # (Pydantic은 모델 초기화 시 환경 변수를 자동으로 고려함, Field(env=...) 설정 덕분)
    # 여기서는 YAML 데이터를 기본으로 하되, 환경 변수가 정의된 필드는 그 값을 우선 사용할 거예요.
    return AppConfig(**config_data, mcp_configs=MCPSettings(**mcp_data))


settings: AppConfig = load_config()
