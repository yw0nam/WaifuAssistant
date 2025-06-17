from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from src.services.llm_service import ChatWaifu_LLM
from src.services.tts_service import ChatWaifu_TTS, ServeTTSRequest
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from src.config import settings
import yaml, logging
import asyncio
from typing import Dict
import json

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
chat_waifu_tts = ChatWaifu_TTS()  # TTS 서비스 인스턴스 생성
MCP_CONFIG = settings.mcp_configs.mcp_servers

with open("./configs/persona.yaml", "r", encoding="utf-8") as f:
    persona_data = yaml.safe_load(f)
PERSONA = yaml.dump(persona_data, allow_unicode=True, sort_keys=False, indent=2)

logger.info(f"🚀 서버 시작! http://localhost:8000 에서 접속 대기 중...")
logger.info(
    f"▶️ LLM 설정: 모델='{settings.llm_configs.model}', API Base='{settings.llm_configs.openai_api_base}'"
)
logger.info(f"▶️ TTS 설정: URL='{settings.tts_configs.url}'")
logger.info(f"▶️ MCP 설정: {MCP_CONFIG} 클라이언트 사용 예정")


# API: 루트 경로 (기본 테스트용)
@app.get("/")
async def read_root():
    return {
        "message": f"백엔드 (v2 - 설정 적용!), 정상 작동 중! LLM 모델: {settings.llm_configs.model}"
    }


# 클라이언트별 TTS 처리 큐
tts_queues: Dict[str, asyncio.Queue] = {}


async def tts_worker(client_id: str, websocket: WebSocket):
    """TTS 처리를 위한 백그라운드 워커"""
    if client_id not in tts_queues:
        tts_queues[client_id] = asyncio.Queue()

    queue = tts_queues[client_id]

    try:
        while True:
            # 큐에서 TTS 요청 대기
            tts_text = await queue.get()

            if tts_text is None:  # 종료 신호
                break

            try:
                logger.info(f"Client #{client_id} TTS 생성 시작...")

                tts_request = ServeTTSRequest(
                    text=tts_text,
                    format="wav",
                    reference_id=getattr(settings.tts_configs, "reference_id", None),
                    chunk_length=200,
                    normalize=True,
                    temperature=0.8,
                )

                # Base64로 인코딩된 음성 데이터 받기
                audio_base64 = chat_waifu_tts.request_tts_base64(
                    url=settings.tts_configs.url,
                    api_key=getattr(settings.tts_configs, "api_key", None),
                    request=tts_request,
                )

                if audio_base64:
                    # 음성 데이터를 WebSocket으로 전송
                    await websocket.send_json(
                        {
                            "type": "audio",
                            "data": audio_base64,
                            "format": "wav",
                            "text": tts_text,
                        }
                    )
                    logger.info(f"✅ Client #{client_id} TTS 음성 데이터 전송 완료")
                else:
                    logger.warning(f"⚠️ Client #{client_id} TTS 생성 실패")
                    await websocket.send_json(
                        {"type": "error", "message": "TTS 음성 생성에 실패했습니다."}
                    )

            except Exception as tts_error:
                logger.error(f"❌ Client #{client_id} TTS 처리 중 오류: {tts_error}")
                await websocket.send_json(
                    {"type": "error", "message": f"TTS 처리 오류: {str(tts_error)}"}
                )
            finally:
                queue.task_done()

    except Exception as e:
        logger.error(f"❌ Client #{client_id} TTS 워커 오류: {e}")


# --- 💬 WebSocket 엔드포인트 ---
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    logger.info(f"Client #{client_id} 가 연결되었어요! 반가워요! 👋")

    message_history = [{"role": "system", "content": PERSONA}]

    # TTS 워커 태스크 시작
    tts_task = asyncio.create_task(tts_worker(str(client_id), websocket))

    try:
        while True:
            # JSON 형태로 메시지 받기
            raw_data = await websocket.receive_text()

            try:
                # JSON 파싱 시도
                data = (
                    json.loads(raw_data)
                    if raw_data.startswith("{")
                    else {"text": raw_data, "enable_tts": True}
                )
            except:
                # 일반 텍스트인 경우 기본값 사용
                data = {"text": raw_data, "enable_tts": True}

            user_message = data.get("text", "")
            enable_tts = data.get("enable_tts", True)

            logger.info(
                f"Client #{client_id} 메시지: '{user_message}' (TTS: {enable_tts})"
            )
            message_history.append(HumanMessage(content=user_message))

            logger.info(
                f"Client #{client_id} 에게 LLM 스트리밍 시작 (모델: {settings.llm_configs.model})..."
            )

            ai_response_text_chunks = []
            async for result in chat_waifu_llm.stream(
                message=message_history,
                mcp_config=MCP_CONFIG,
            ):
                await websocket.send_json(result)
                if result.get("type") == "content" and result.get("text"):
                    ai_response_text_chunks.append(result.get("text"))

            # LLM 응답 완료 처리
            if ai_response_text_chunks:
                full_ai_response = "".join(ai_response_text_chunks)
                message_history.append(AIMessage(content=full_ai_response))
                logger.info(f"LLM 응답 (Client #{client_id}): '{full_ai_response}'")

                # 응답 완료 신호 전송
                await websocket.send_json(
                    {
                        "type": "llm_complete",
                        "text": full_ai_response,
                        "tts_enabled": enable_tts,
                    }
                )

                # 조건부 TTS 처리
                if enable_tts and str(client_id) in tts_queues:
                    await tts_queues[str(client_id)].put(full_ai_response)
                    logger.info(f"Client #{client_id} TTS 큐에 추가됨")

    except WebSocketDisconnect:
        logger.info(f"Client #{client_id} 와의 연결이 끊어졌어요. 다음에 또 만나요! 😢")
    except Exception as e:
        logger.error(f"Client #{client_id} 와의 통신 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # TTS 워커 정리
        if str(client_id) in tts_queues:
            await tts_queues[str(client_id)].put(None)  # 종료 신호
            tts_task.cancel()
            del tts_queues[str(client_id)]

        try:
            await websocket.close(code=1000)
        except:
            pass


# 개발 환경에서 Uvicorn을 사용해 FastAPI 앱을 실행해요.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
