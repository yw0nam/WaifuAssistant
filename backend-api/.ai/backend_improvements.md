### Backend Improvement Plan

This document tracks the step-by-step improvements for the backend API.

- [ ] **1. Introduce a Dedicated Testing Suite**
    - [ ] Create `tests/` directory.
    - [ ] Add basic unit tests for a service (e.g., `tts_service`).
    - [ ] Add a basic integration test for a WebSocket handler (e.g., `chat_handler`).

- [] **2. Enhance Configuration Management with Pydantic**
    - [ ] Add `pydantic` and `pydantic-settings` to dependencies.
    - [ ] Refactor `src/configs/models.py` to use Pydantic `BaseSettings`.
    - [ ] Update `src/configs/loader.py` to use the new Pydantic models.

- [ ] **3. Implement Dependency Injection**
    - [ ] Choose a dependency injection approach (e.g., FastAPI's built-in system or a library).
    - [ ] Refactor WebSocket handlers to receive services via dependency injection.

- [ ] **4. Add Code Formatting and Linting**
    - ✅ Add `black`, `isort`and `ruff` to `pyproject.toml`.
    - ✅ Add lint.sh for auto lint.
    - [ ] Add github/workflow for automatic check when commit.

- [ ] **5. Document Your WebSocket API**
    - [ ] Create an `API.md` file.
    - [ ] Document the WebSocket endpoint and message schemas.

- [ ] **6. Add New feature**
    - Core Interaction & Memory
        - [ ] ASR Service Integration: Add an Automatic Speech Recognition service to process user voice input.
        - [ ] Advanced Speech Detection: VAD (Voice Activity Detection): AI keeps listening until the user finishes speaking.Barge-in: AI stops talking immediately when the user starts speaking.
        - [ ] Proactive Interaction: The AI initiates conversation or makes comments without waiting for user input (e.g., based on time of day).
        - [ ] Comprehensive Memory System: Implement Short-term, Long-term, and Working-Memory for context-aware and personalized conversations.
        - [ ] Agent-to-Agent Communication: Enable the main agent to consult with other specialized agents for complex tasks.
        - [ ] Dynamic Configuration: Allow the frontend to send and update MCP (Multi-Server MCP Client) configurations dynamically.  
    - New Expressiveness & Utility Features
        - [ ] Emotion-Driven Animation: Connect extracted emotion tags (e.g., (curious), (shy)) directly to Live2D animations for a more expressive and lively character.
        - [ ] Screen Awareness (Vision): Allow the agent to perceive the user's screen content and react to it, such as commenting on a browsed website or an active game.
        - [ ] Dynamic Personality & Mood System: Implement a system where the agent's mood and tone shift based on the flow of the conversation, making it feel more alive and less robotic.
        - [ ] Desktop Automation Assistant: Use tool integration (LangGraph) to perform simple desktop tasks via voice commands like "Play music," "Set an alarm," or "Find the latest news."