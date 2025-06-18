# 🎭 WaifuAssistant - 프로젝트 현황 및 로드맵

## 📊 현재 상태 (2025년 6월 17일)

### ✅ 완료된 기능
- **백엔드 API 서버**: FastAPI + WebSocket 기반 실시간 통신
- **LLM 서비스**: OpenAI/Langchain 기반 대화형 AI
- **TTS 서비스**: 텍스트→음성 변환 및 Base64 스트리밍
- **설정 시스템**: YAML/JSON 기반 구성 관리
- **페르소나 시스템**: AI 캐릭터 성격 커스터마이징
- **MCP 도구 연동**: 외부 도구 확장 가능 (filesystem, tavily, memory, fetch, notion)

### 🏗️ 기술 스택
**백엔드**: Python 3.12+, FastAPI, WebSocket, Langchain, Langgraph, OpenAI API
**프론트엔드**: React 18, TypeScript, CSS3
**통신**: WebSocket 실시간 양방향 통신
**배포**: Docker Compose

### 📁 프로젝트 구조
```
WaifuAssistant/
├── backend-api/              # 백엔드 API 서버
│   ├── src/
│   │   ├── main.py          # FastAPI 애플리케이션
│   │   ├── config.py        # 설정 관리
│   │   └── services/        # 비즈니스 로직
│   └── configs/             # 설정 파일들
├── frontend-app/            # 프론트엔드 (현재 템플릿 상태)
└── docker-compose.yml       # 컨테이너 오케스트레이션
```

## 🎯 향후 개발 로드맵

### Phase 1: Frontend 핵심 기능 (1-2주)
**우선순위: 긴급**
- [ ] **채팅 UI 구현**
  - ChatContainer.tsx - 메인 채팅 화면
  - MessageBubble.tsx - 대화 말풍선 컴포넌트
  - InputArea.tsx - 텍스트 입력 인터페이스
- [ ] **WebSocket 연결**
  - useWebSocket.ts - 백엔드 실시간 연결
  - 메시지 송수신 로직
- [ ] **기본 채팅 기능**
  - 실시간 텍스트 대화
  - 채팅 히스토리 관리

### Phase 2: 오디오 통합 (1주)
**우선순위: 높음**
- [ ] **TTS 음성 재생**
  - AudioPlayer.tsx - 음성 재생 컴포넌트
  - Base64 → Audio 변환 로직
  - 음성 재생 상태 표시
- [ ] **오디오 UI/UX**
  - 음성 재생 중 시각적 피드백
  - 음성 On/Off 토글

### Phase 3: STT 서비스 (2주)
**우선순위: 중간**
- [ ] **음성 인식 구현**
  - Whisper API 또는 다른 STT 서비스 연동
  - 실시간 음성 입력 처리
- [ ] **음성 입력 UI**
  - VoiceRecorder.tsx - 음성 녹음 컴포넌트
  - 마이크 권한 관리
  - 음성 입력 시각적 피드백

### Phase 4: 캐릭터 시스템 (2-3주)
**우선순위: 중간**
- [ ] **Live2D 연동 준비**
  - Live2DViewer.tsx - 캐릭터 표시 컴포넌트
  - 감정/상태별 애니메이션
- [ ] **페르소나 UI**
  - PersonaSelector.tsx - 캐릭터 선택
  - ConfigPanel.tsx - 설정 패널

### Phase 5: 데스크탑 앱화 (3-4주)
**우선순위: 낮음**
- [ ] **네이티브 앱 변환**
  - Electron 또는 Tauri 적용
  - 시스템 트레이 상주
  - 단축키 지원

## 🛠️ 즉시 시작할 작업

### 1. Frontend 재구조화
현재 일반적인 React 템플릿을 AI 어시스턴트용으로 변경:

```
src/
├── components/
│   ├── chat/                 # 💬 채팅 관련
│   │   ├── ChatContainer.tsx
│   │   ├── MessageBubble.tsx
│   │   └── InputArea.tsx
│   ├── audio/                # 🔊 오디오 처리
│   │   └── AudioPlayer.tsx
│   └── character/            # 🎭 캐릭터 관련
│       └── CharacterStatus.tsx
├── hooks/                    # 🪝 커스텀 훅
│   ├── useWebSocket.ts
│   ├── useAudioPlayer.ts
│   └── useChat.ts
├── services/                 # 🔌 서비스
│   ├── websocket.ts
│   └── audioUtils.ts
└── types/                    # 📝 타입 정의
    ├── chat.ts
    ├── websocket.ts
    └── audio.ts
```

### 2. 핵심 타입 정의
```typescript
interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  audioData?: string; // Base64 encoded
}

interface WebSocketMessage {
  type: 'message' | 'audio' | 'status';
  data: any;
}
```

### 3. WebSocket 연결 구현
백엔드 엔드포인트: `ws://localhost:8000/ws/{client_id}`

## 🎨 UI/UX 설계

### 메인 화면 레이아웃
```
┌─────────────────────────────────────────────┐
│  🎭 WaifuAssistant                     ⚙️   │
├─────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐   │
│  │   Live2D        │  │   Chat Messages │   │
│  │   Character     │  │                 │   │
│  │   (향후 구현)    │  │   User: Hello   │   │
│  │                 │  │   AI: Hi there! │   │
│  │   [🔊 Speaking] │  │   [스크롤 가능]  │   │
│  └─────────────────┘  └─────────────────┘   │
├─────────────────────────────────────────────┤
│  💬 [     텍스트 입력창     ] [전송]        │
│     🎤 [음성입력] 🔊 [음성출력]             │
└─────────────────────────────────────────────┘
```

## 📈 성공 지표

### Phase 1 완료 기준
- [ ] 백엔드와 WebSocket 연결 성공
- [ ] 실시간 텍스트 채팅 가능
- [ ] TTS 음성 재생 작동

### 최종 목표
- [ ] 완전한 음성 대화 가능 (STT + LLM + TTS)
- [ ] Live2D 캐릭터 애니메이션
- [ ] 데스크탑 네이티브 앱으로 동작

## 🔧 개발 환경 설정

### 백엔드 실행
```bash
cd backend-api
uvicorn src.main:app --reload
```

### 프론트엔드 실행 (향후)
```bash
cd frontend-app
npm install
npm start
```

### Docker 실행 (향후)
```bash
docker-compose up --build
```

## 📝 참고사항

- **MCP 도구**: filesystem, tavily-search, memory, fetch, notion API 연동 완료
- **설정 파일**: `configs/` 디렉토리에서 페르소나, API 키 등 관리
- **확장성**: 모듈화된 구조로 새로운 기능 추가 용이
- **실시간성**: WebSocket 기반 즉시 응답 시스템

---
**마지막 업데이트**: 2025년 6월 17일
**다음 액션**: Frontend ChatContainer 구현 시작
