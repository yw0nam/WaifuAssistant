from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from src.services.llm_service import ChatWaifu_LLM
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from src.config import settings
import yaml, logging

logger = logging.getLogger("waifu_backend")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
# FastAPI 애플리케이션 인스턴스를 생성해요. 우리 앱의 이름도 지어줄 수 있지!
app = FastAPI(title="나만의 인터랙티브 데스크탑 모델 Backend ✨")

# CORS (Cross-Origin Resource Sharing) 미들웨어 설정
# 개발 중에는 모든 출처를 허용하도록 '*'로 설정할 수 있지만,
# 실제 배포 시에는 보안을 위해 프론트엔드 주소만 명시하는 게 좋아요! (예: ["http://localhost:3000"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (개발용)
    allow_credentials=True,  # 쿠키를 포함한 요청 허용
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

# 웹소켓 연결을 관리하는 매니저 (여러 클라이언트 동시 관리에 유용)
# manager = ConnectionManager()

chat_openai_model = ChatOpenAI(
    **settings.llm_configs.model_dump(), extra_body={"min_p": 0, "top_k": 20}
)
chat_waifu_llm = ChatWaifu_LLM(llm=chat_openai_model)
MCP_CONFIG = settings.mcp_configs.mcp_servers

with open("./configs/persona.yaml", "r", encoding="utf-8") as f:
    persona_data = yaml.safe_load(f)
PERSONA = yaml.dump(persona_data, allow_unicode=True, sort_keys=False, indent=2)


logger.info(f"🚀 서버 시작! http://localhost:8000 에서 접속 대기 중...")
logger.info(
    f"▶️ LLM 설정: 모델='{settings.llm_configs.model}', API Base='{settings.llm_configs.openai_api_base}'"
)
logger.info(f"▶️ MCP 설정: {MCP_CONFIG} 클라이언트 사용 예정")


# API: 루트 경로 (기본 테스트용)
@app.get("/")
async def read_root():
    return {
        "message": f"백엔드 (v2 - 설정 적용!), 정상 작동 중! LLM 모델: {settings.llm_configs.model}"
    }


# --- 💬 WebSocket 엔드포인트 ---
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    logger.info(f"Client #{client_id} 가 연결되었어요! 반가워요! 👋")

    message_history = [{"role": "system", "content": PERSONA}]

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Client #{client_id} 로부터 온 메시지: '{data}'")
            message_history.append(HumanMessage(content=data))

            logger.info(
                f"Client #{client_id} 에게 LLM 스트리밍 시작 (모델: {settings.llm_configs.model})..."
            )

            ai_response_text_chunks = []
            async for result in chat_waifu_llm.stream(
                message=message_history,
                mcp_config=MCP_CONFIG,  # ✨ MCP 설정을 여기서 사용!
            ):
                await websocket.send_json(result)
                if result.get("type") == "content" and result.get("text"):
                    ai_response_text_chunks.append(result.get("text"))

            if ai_response_text_chunks:
                full_ai_response = "".join(ai_response_text_chunks)
                message_history.append(AIMessage(content=full_ai_response))
                logger.info(f"LLM 응답 (Client #{client_id}): '{full_ai_response}'")

    except WebSocketDisconnect:
        logger.info(f"Client #{client_id} 와의 연결이 끊어졌어요. 다음에 또 만나요! 😢")
    except Exception as e:
        logger.error(f"Client #{client_id} 와의 통신 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        await websocket.close(code=1011)


# 개발 환경에서 Uvicorn을 사용해 FastAPI 앱을 실행해요.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
