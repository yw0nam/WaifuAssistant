# 🚀 2025년 6월 TTS/일본어/실시간 Reasoning 필터 대규모 업데이트

- **실시간 TTS 스트리밍**: LLM 응답을 문장 단위로 실시간 추출하여 TTS로 전송, 자연스러운 대화 흐름 구현
- **일본어 텍스트 완벽 지원**: 일본어 문장 경계(。！？), 특수문자(♪♫♬♡♥★☆ 등) 보존, 이모지/음표 등도 자연스럽게 처리
- **Reasoning/내적 추론 태그 실시간 필터**: `<think>...</think>` 등 reasoning 태그가 청크로 분할되어도 정확히 필터링
- **프론트엔드 TTS 설정 UI**: TTS on/off, reasoning 태그, reference_id 등 실시간 설정 및 localStorage 저장
- **Reference ID**: 사용자 지정 voice reference_id로 TTS 음성 선택 가능
- **중요 버그 픽스**: 첫 문장 스킵, 청크 필터링, 일본어 문장 경계, reasoning 태그 분할 등
- **아키텍처 개선**: 서비스 모듈화, WebSocket 프로토콜 개선, 클라이언트별 AI 응답 상태 추적

# Interactive AI Desktop Assistant

A real-time AI desktop assistant integrating LLM (Large Language Models), STT (Speech-to-Text), and TTS (Text-to-Speech) technologies with a modern React frontend.

## 🎯 Project Overview

This project aims to develop an interactive AI desktop assistant that communicates with users in real-time. Beyond simple text-based chatbots, users can engage in voice conversations with an AI that has configurable **Personas**, providing a lively and engaging experience with future Live2D integration planned.

## ✨ Key Features

- **Real-time Voice Conversation**: Voice recognition and immediate AI-generated audio responses
- **High-Performance Language Model (LLM)**: Context memory and external tool integration using Langchain and Langgraph
- **Custom Personas**: Freely configurable AI personality, speech patterns, and background stories via `persona.yaml`
- **Modular Service Architecture**: Independent service design (STT, LLM, TTS) ensuring scalability
- **External Tool Integration (MCP)**: Infinite functionality expansion through Multi-Server MCP Client
- **Modern React Frontend**: TypeScript-based web interface with real-time WebSocket communication
- **Audio Streaming**: Real-time audio playback with base64-encoded audio streaming

## 🏗️ System Architecture

This project follows a client-server model with a **FastAPI backend** and **React TypeScript frontend**. All core logic is processed on the backend API server, while the frontend provides a modern web interface for user interaction.

### Project Structure

```
WaifuAssistant/
├── backend-api/              # 🐍 Python FastAPI Backend
│   ├── configs/              # ⚙️ Configuration Files
│   │   ├── app_config.yaml   #    - Service Configuration (LLM, TTS, etc.)
│   │   ├── mcp_config.json   #    - MCP Tool Configuration
│   │   └── persona.yaml      #    - AI Persona Configuration
│   ├── src/                  # 📦 Python Source Code
│   │   ├── main.py           #    - FastAPI Entry Point
│   │   ├── core/             #    - Core Application Logic
│   │   ├── services/         #    - Business Logic Services
│   │   │   ├── llm_service/  #      - LLM Service Implementation
│   │   │   └── tts_service/  #      - TTS Service Implementation
│   │   ├── websocket/        #    - WebSocket Handlers
│   │   └── configs/          #    - Configuration Management
│   ├── pyproject.toml        #    - Project Dependencies (UV)
│   └── uv.lock              #    - Dependency Lock File
└── frontend-app/             # ⚛️ React TypeScript Frontend
    ├── public/               # 🌐 Static Assets
    ├── src/                  # 📱 React Source Code
    │   ├── components/       #    - React Components
    │   │   └── Chat.tsx      #      - Main Chat Interface
    │   ├── hooks/            #    - Custom React Hooks
    │   │   ├── useWebSocket.ts #    - WebSocket Hook
    │   │   └── useAudio.ts   #      - Audio Playback Hook
    │   ├── services/         #    - Frontend Services
    │   └── types/            #    - TypeScript Type Definitions
    ├── package.json          #    - Node.js Dependencies
    └── build/                #    - Production Build Output
```

### Data Flow

1. **Input**: 
   - Frontend React app captures user text input
   - (Future) STT integration for voice input

2. **Processing**:
   - WebSocket connection between frontend and backend
   - Backend WebSocket handlers receive messages
   - LLM service generates responses using persona and MCP tools
   - Real-time streaming response delivery

3. **Output**:
   - TTS service converts text to speech
   - Base64-encoded audio data streamed via WebSocket
   - Frontend plays audio in real-time
   - (Future) Live2D character animation integration

## 🚀 Installation and Setup

### Prerequisites

- **Backend**: Python 3.12+, UV package manager
- **Frontend**: Node.js 16+, npm or yarn
- **API Keys**: Required API keys (e.g., OpenAI)

### Environment Setup

1. **Environment Variables**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **Configuration Files**:
   - [`backend-api/configs/app_config.yaml`](backend-api/configs/app_config.yaml): LLM, TTS service settings
   - [`backend-api/configs/persona.yaml`](backend-api/configs/persona.yaml): AI persona definition
   - [`backend-api/configs/mcp_config.json`](backend-api/configs/mcp_config.json): External tool settings

### Running the Application

#### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend-api
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Start the backend server**:
   ```bash
   uv run uvicorn src.main:app --reload
   ```

4. **Backend endpoints**:
   - HTTP API: `http://localhost:8000`
   - WebSocket: `ws://localhost:8000/ws/{client_id}`
   - API Documentation: `http://localhost:8000/docs`

#### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend-app
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

4. **Access the application**:
   - Frontend: `http://localhost:3000`

#### Production Build

1. **Build frontend for production**:
   ```bash
   cd frontend-app
   npm run build
   ```

2. **Serve the built frontend** (the backend can serve static files):
   - Built files are in `frontend-app/build/`

## 📁 Key Files Description

### Backend Files
- [`backend-api/src/main.py`](backend-api/src/main.py): FastAPI application and WebSocket handlers
- [`backend-api/src/core/app.py`](backend-api/src/core/app.py): Core application setup and configuration
- [`backend-api/src/configs/`](backend-api/src/configs/): Configuration management with Pydantic models
- [`backend-api/src/services/llm_service/`](backend-api/src/services/llm_service/): LLM service logic with Langchain/Langgraph
- [`backend-api/src/services/tts_service/`](backend-api/src/services/tts_service/): TTS service implementation
- [`backend-api/src/websocket/`](backend-api/src/websocket/): WebSocket handlers and models

### Frontend Files
- [`frontend-app/src/components/Chat.tsx`](frontend-app/src/components/Chat.tsx): Main chat interface component
- [`frontend-app/src/hooks/useWebSocket.ts`](frontend-app/src/hooks/useWebSocket.ts): WebSocket connection management
- [`frontend-app/src/hooks/useAudio.ts`](frontend-app/src/hooks/useAudio.ts): Audio playback and streaming
- [`frontend-app/src/types/`](frontend-app/src/types/): TypeScript type definitions
- [`frontend-app/src/services/`](frontend-app/src/services/): Frontend service utilities

## 🔧 Development Status

### ✅ Completed Features
- **WebSocket Communication**: Real-time bidirectional communication
- **LLM Service Integration**: Langchain/Langgraph with OpenAI models
- **TTS Service Integration**: Text-to-speech with audio streaming
- **Persona System**: Configurable AI personality and behavior
- **MCP Tool Integration**: External tool connectivity
- **React Frontend**: Modern TypeScript-based web interface
- **Audio Streaming**: Real-time audio playback with queue management
- **Configuration Management**: YAML/JSON-based configuration system

### 🚧 In Development
- **STT Service**: Speech-to-text integration (planned)
- **Live2D Integration**: Character animation system (planned)
- **Enhanced UI**: Improved frontend design and UX
- **Voice Input**: Browser-based speech recognition

### 📋 Planned Features
- **Desktop Application**: Electron wrapper for desktop deployment
- **Plugin System**: Extensible plugin architecture
- **Multi-language Support**: Internationalization (i18n)
- **Voice Cloning**: Custom voice generation
- **Memory System**: Long-term conversation memory

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **Package Manager**: UV
- **LLM Integration**: Langchain, Langgraph, Langchain-OpenAI
- **MCP Integration**: Langchain-MCP-Adapters
- **Audio Processing**: Librosa
- **WebSocket**: FastAPI WebSockets
- **Configuration**: Pydantic, YAML/JSON

### Frontend
- **Framework**: React 19+ with TypeScript
- **Build Tool**: Create React App
- **State Management**: React Hooks
- **Real-time Communication**: WebSocket API
- **Audio Handling**: Web Audio API
- **Styling**: CSS Modules

### Development Tools
- **Backend Testing**: Python unittest framework
- **Frontend Testing**: Jest, React Testing Library
- **Type Checking**: TypeScript, Pydantic
- **Code Quality**: ESLint (frontend)

## 🔄 API Reference

### WebSocket Events

#### Client → Server
```typescript
// Send user message
{
  "type": "message",
  "content": "Hello, AI assistant!"
}
```

#### Server → Client
```typescript
// Streaming LLM response
{
  "type": "content",
  "content": "Hello! How can I help you today?",
  "is_complete": false
}

// Audio response
{
  "type": "audio",
  "audio_data": "base64-encoded-audio",
  "text": "Hello! How can I help you today?"
}

// Completion notification
{
  "type": "llm_complete"
}

// Error message
{
  "type": "error",
  "error": "Error description"
}
```

## 🤝 Contributing

We welcome contributions to this project! Please feel free to submit issues or pull requests.

### Development Guidelines
1. **Backend**: Follow Python PEP 8 standards
2. **Frontend**: Use TypeScript and follow React best practices
3. **Testing**: Write tests for new features
4. **Documentation**: Update README and code comments

### Getting Started with Development
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is distributed under the MIT License.

## 📞 Support

For questions or support, please open an issue on the GitHub repository.