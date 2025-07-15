from .loader import get_settings, load_config
from .models import AppConfig, LLMSettings, MCPSettings, TTSSettings

# 전역 설정 객체
settings = get_settings()

__all__ = [
    "AppConfig",
    "LLMSettings",
    "TTSSettings",
    "MCPSettings",
    "load_config",
    "get_settings",
    "settings",
]
