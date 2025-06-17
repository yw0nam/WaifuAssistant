# 인터랙티브 AI 데스크탑 어시스턴트

LLM(대규모 언어 모델), STT(음성-텍스트 변환), TTS(텍스트-음성 변환) 기술을 통합한 실시간 AI 데스크탑 어시스턴트

## 🎯 프로젝트 목적

본 프로젝트는 사용자와 실시간으로 소통하는 인터랙티브 AI 데스크탑 어시스턴트를 개발하는 것을 목표로 합니다. 사용자는 단순한 텍스트 기반의 챗봇을 넘어, 설정 가능한 **페르소나(Persona)**를 가진 AI와 직접 음성으로 대화하며, 시각적으로 생동감 넘치는 경험(향후 Live2D 연동)을 할 수 있습니다.

## ✨ 주요 기능

- **실시간 음성 대화**: 사용자의 음성을 인식하고, AI가 생성한 음성으로 즉각적인 응답 제공
- **고성능 언어 모델 (LLM)**: Langchain과 Langgraph를 활용한 맥락 기억 및 외부 도구 연동
- **커스텀 페르소나**: `persona.yaml` 파일을 통한 AI 성격, 말투, 배경 이야기 자유 설정
- **모듈화된 서비스 구조**: STT, LLM, TTS 등 독립적 서비스 설계로 확장성 확보
- **외부 도구 연동 (MCP)**: Multi-Server MCP Client를 통한 무한 기능 확장

## 🏗️ 시스템 아키텍처

본 프로젝트는 클라이언트-서버 모델을 따르며, 모든 핵심 로직은 Backend API 서버에서 처리됩니다.

### 백엔드 폴더 구조

```
BACKEND-API/
├── configs/              # ⚙️ 설정 파일 관리
│   ├── app_config.yaml   #    - 서비스 설정 (LLM, TTS 등)
│   ├── mcp_config.json   #    - MCP 도구 설정
│   └── persona.yaml      #    - AI 페르소나 설정
├── src/                  # 🐍 파이썬 소스 코드
│   ├── services/         #    - 핵심 비즈니스 로직
│   │   ├── llm_service.py
│   │   └── tts_service.py
│   ├── config.py         #    - 설정 로딩 및 검증
│   └── main.py           #    - FastAPI 엔트리포인트
├── .venv/                #    - 가상 환경
├── pyproject.toml        #    - 프로젝트 의존성
└── requirements.txt      #    - 패키지 목록
```

### 데이터 흐름

1. **입력 (Input)**: 
   - (향후) 클라이언트가 사용자 음성을 STT로 텍스트 변환
   - (현재) 텍스트 직접 입력

2. **처리 (Processing)**:
   - WebSocket 핸들러가 텍스트 수신
   - LLM 서비스가 페르소나와 MCP 도구를 활용하여 응답 생성
   - 실시간 스트리밍으로 응답 전송

3. **출력 (Output)**:
   - TTS 서비스가 텍스트를 음성으로 변환
   - Base64 인코딩된 음성 데이터를 WebSocket으로 전송
   - (향후) Live2D 캐릭터 애니메이션 연동

## 🚀 설치 및 실행

### 사전 준비

- Python 3.12+
- uv
- 필요한 API 키 (예: OpenAI)

### 환경 설정

1. **환경 변수 설정**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **설정 파일 편집**:
   - [`configs/app_config.yaml`](configs/app_config.yaml): LLM, TTS 서비스 설정
   - [`configs/persona.yaml`](configs/persona.yaml): AI 페르소나 정의
   - [`configs/mcp_config.json`](configs/mcp_config.json): 외부 도구 설정

### 실행 방법

1. **의존성 설치**:
   ```bash
   # 프로젝트 루트 디렉토리에서 실행
   uv pip install -r requirements.txt
   ```

2. **백엔드 서버 실행**:
   ```bash
   # 프로젝트 루트 디렉토리에서 실행
   uvicorn src.main:app --reload
   ```

3. **서버 접속**:
   - HTTP: `http://localhost:8000`
   - WebSocket: `ws://localhost:8000/ws/{client_id}`

## 📁 주요 파일 설명

- [`src/main.py`](src/main.py): FastAPI 애플리케이션 및 WebSocket 핸들러
- [`src/config.py`](src/config.py): Pydantic 모델을 사용한 설정 관리
- [`src/services/llm_service.py`](src/services/llm_service.py): LLM 서비스 로직
- [`src/services/tts_service.py`](src/services/tts_service.py): TTS 서비스 로직

## 🔧 개발 상태

- ✅ 기본 WebSocket 통신
- ✅ LLM 서비스 연동
- ✅ TTS 서비스 연동
- ✅ 페르소나 시스템
- ✅ MCP 도구 연동
- 🚧 STT 서비스 (개발 중)
- 🚧 Live2D 연동 (계획 중)
- 🚧 Frontend 클라이언트 (계획 중)

## 🤝 기여하기

이슈나 풀 리퀘스트를 통해 프로젝트에 기여해 주세요!

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.