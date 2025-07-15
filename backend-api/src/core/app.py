from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.configs import settings


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성 및 설정"""
    app = FastAPI(title="나만의 인터랙티브 데스크탑 모델 Backend ✨")

    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 모든 출처 허용 (개발용)
        allow_credentials=True,  # 쿠키를 포함한 요청 허용
        allow_methods=["*"],  # 모든 HTTP 메소드 허용
        allow_headers=["*"],  # 모든 HTTP 헤더 허용
    )

    # 루트 경로
    @app.get("/")
    async def read_root():
        return {
            "message": f"백엔드 (v2 - 설정 적용!), 정상 작동 중! LLM 모델: {settings.llm_configs.model}"
        }

    return app
