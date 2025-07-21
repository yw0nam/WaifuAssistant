import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import WebSocket

from src.configs import settings
from src.configs.prompts import NANAMI
from src.core.app import create_app
from src.core.logging import setup_logging
from src.websocket.handlers import (
    ASRHandler,
    ChatHandler,
    TTSHandler,
    handle_websocket,
)

# 로깅 설정
logger = setup_logging()

# FastAPI 앱 생성
app = create_app()

# 전역 변수들 (초기화는 나중에)
USER_NAME = "エクリア"
PERSONA = NANAMI.format(your_name=USER_NAME)
MCP_CONFIG = None

# AIDEV-NOTE: Global handler instances - refactored from individual service instances
CHAT_HANDLER = None
TTS_HANDLER = None
ASR_HANDLER = None


def initialize_services():
    """서비스들을 초기화합니다."""
    global CHAT_HANDLER, TTS_HANDLER, ASR_HANDLER, PERSONA, MCP_CONFIG

    if CHAT_HANDLER is not None:  # 이미 초기화되었으면 스킵
        return

    # 서비스 핸들러 인스턴스 초기화
    CHAT_HANDLER = ChatHandler(settings.llm_configs)
    TTS_HANDLER = TTSHandler(settings.tts_configs)
    ASR_HANDLER = ASRHandler(settings.asr_configs)
    MCP_CONFIG = settings.mcp_configs.mcp_servers

    # 시작 로그 (한 번만 출력)
    logger.info("🚀 서버 시작! http://localhost:8800 에서 접속 대기 중...")
    logger.info(
        f"▶️ LLM 설정: 모델='{settings.llm_configs.model}', API Base='{settings.llm_configs.openai_api_base}'"
    )
    logger.info(f"▶️ TTS 설정: URL='{settings.tts_configs.url}'")
    logger.info(f"▶️ MCP 설정: {len(MCP_CONFIG)}개 서버 설정됨")


# WebSocket endpoint with error handling
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint with robust error handling"""
    try:
        # Initialize services (only on first connection)
        initialize_services()
        logger.info(f"🔗 Client #{client_id} attempting to connect...")

        await handle_websocket(
            websocket=websocket,
            client_id=client_id,
            chat_handler=CHAT_HANDLER,
            tts_handler=TTS_HANDLER,
            asr_handler=ASR_HANDLER,
            persona=PERSONA,
            mcp_config=MCP_CONFIG,
        )
    except Exception as e:
        logger.error(f"❌ WebSocket endpoint error for client #{client_id}: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        # Don't re-raise to avoid server crash


# 개발 환경에서 Uvicorn을 사용해 FastAPI 앱을 실행
if __name__ == "__main__":
    import uvicorn

    # 직접 앱 객체를 전달하여 중복 import 방지
    uvicorn.run(app, host="0.0.0.0", port=8800, reload=True)
