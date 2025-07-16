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
    - ✅ Add ASR service
    - [ ] Speech Detection, If user keep telling something, AI should keep listening until the speech end. And, user speech detection, when AI speech, AI should be stop talking. 
    - [ ] Active speech(Not only waiting user input, saying something them selves)
    - [ ] Add Memory system. Short-term, Long-term, Working-Memory.
    - [ ] Add Agent2Agent feature.
    - [ ] Get mcp config from frontend, not static config.