import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import WebSocket
from langchain_openai import ChatOpenAI
from src.core.app import create_app
from src.core.logging import setup_logging
from src.services.llm_service.service import ChatWaifu_LLM, load_persona
from src.services.tts_service.service import ChatWaifu_TTS
from src.websocket.handlers import handle_websocket
from src.configs import settings

# 로깅 설정
logger = setup_logging()

# FastAPI 앱 생성
app = create_app()

# 전역 변수들 (초기화는 나중에)
chat_waifu_llm = None
chat_waifu_tts = None
PERSONA = None
MCP_CONFIG = None


def initialize_services():
    """서비스들을 초기화합니다."""
    global chat_waifu_llm, chat_waifu_tts, PERSONA, MCP_CONFIG

    if chat_waifu_llm is not None:  # 이미 초기화되었으면 스킵
        return

    # 서비스 인스턴스 초기화
    chat_openai_model = ChatOpenAI(
        **settings.llm_configs.model_dump(), extra_body={"min_p": 0, "top_k": 20}
    )
    chat_waifu_llm = ChatWaifu_LLM(llm=chat_openai_model)
    chat_waifu_tts = ChatWaifu_TTS(
        url=settings.tts_configs.url, api_key=settings.tts_configs.api_key
    )
    PERSONA = load_persona()
    MCP_CONFIG = settings.mcp_configs.mcp_servers

    # 시작 로그 (한 번만 출력)
    logger.info(f"🚀 서버 시작! http://localhost:8800 에서 접속 대기 중...")
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
            chat_waifu_llm=chat_waifu_llm,
            chat_waifu_tts=chat_waifu_tts,
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
