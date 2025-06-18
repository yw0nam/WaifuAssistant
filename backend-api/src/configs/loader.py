import yaml
import json
import os
from pathlib import Path
from typing import Optional
from .models import AppConfig, LLMSettings, TTSSettings, MCPSettings

# 설정 파일 경로 정의
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "configs"
DEFAULT_CONFIG_FILE = CONFIG_DIR / "app_config.yaml"
DEFAULT_MCP_FILE = CONFIG_DIR / "mcp_config.json"


def load_yaml_config(config_file: Path = DEFAULT_CONFIG_FILE) -> dict:
    """YAML 설정 파일을 읽어서 딕셔너리로 반환"""
    if not config_file.exists():
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_mcp_config(mcp_file: Path = DEFAULT_MCP_FILE) -> dict:
    """MCP 설정 파일을 읽어서 딕셔너리로 반환"""
    if not mcp_file.exists():
        return {}  # MCP 설정이 없어도 기본값으로 처리

    with open(mcp_file, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_env_variables(config_data: dict) -> dict:
    """환경 변수로 설정값 오버라이드"""
    # OpenAI API Key 환경변수 처리
    if openai_key := os.getenv("OPENAI_API_KEY"):
        config_data.setdefault("llm_configs", {})["openai_api_key"] = openai_key

    # TTS API Key 환경변수 처리
    if tts_key := os.getenv("TTS_API_KEY"):
        config_data.setdefault("tts_configs", {})["api_key"] = tts_key

    return config_data


def load_config(
    config_file: Optional[Path] = None, mcp_file: Optional[Path] = None
) -> AppConfig:
    """
    설정 파일들을 로드하여 AppConfig 객체 생성

    Args:
        config_file: YAML 설정 파일 경로 (기본: app_config.yaml)
        mcp_file: MCP 설정 파일 경로 (기본: mcp_config.json)

    Returns:
        AppConfig: 완전한 설정 객체

    Raises:
        FileNotFoundError: 필수 설정 파일이 없는 경우
        ValueError: 설정 파일 형식이 잘못된 경우
    """
    try:
        # 설정 파일들 로드
        config_data = load_yaml_config(config_file or DEFAULT_CONFIG_FILE)
        mcp_data = load_mcp_config(mcp_file or DEFAULT_MCP_FILE)

        # 환경 변수로 오버라이드
        config_data = merge_env_variables(config_data)

        # Pydantic 모델로 변환
        return AppConfig(
            llm_configs=LLMSettings(**config_data["llm_configs"]),
            tts_configs=TTSSettings(**config_data["tts_configs"]),
            mcp_configs=MCPSettings(mcp_servers=mcp_data),
        )

    except Exception as e:
        raise ValueError(f"설정 로드 중 오류 발생: {e}") from e


def validate_config(config: AppConfig) -> None:
    """설정 유효성 검증"""
    # OpenAI API Key 검증
    if not config.llm_configs.openai_api_key:
        raise ValueError(
            "OpenAI API Key가 설정되지 않았습니다. OPENAI_API_KEY 환경변수를 설정하세요."
        )

    # TTS URL 검증
    if not config.tts_configs.url:
        raise ValueError("TTS URL이 설정되지 않았습니다.")

    print("✅ 설정 검증 완료")


# 설정 객체 생성 및 검증
def get_settings() -> AppConfig:
    """검증된 설정 객체 반환"""
    config = load_config()
    validate_config(config)
    return config
