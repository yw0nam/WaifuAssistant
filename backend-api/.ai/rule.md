# 📖 PROJECT_BIBLE.md: Waifu Assistant Backend API
*Last updated 2025-07-16*

> **Purpose** – This document is the onboarding manual for every AI pair programmer and human developer who contributes to this repository. It defines the coding standards, architecture, and core principles to ensure consistent and high-quality development.

---

## 1. Project Overview

The Waifu Assistant Backend API is the server-side foundation for the Waifu Assistant application. Its primary goal is to leverage LLMs to provide users with an intelligent and interactive assistant experience.

- **Project Name**: `waifu-assistant-backend-api`
- **Repository**: [https://github.com/yw0nam/WaifuAssistant](https://github.com/yw0nam/WaifuAssistant)

---

## 2. Core Rules & Prohibitions

| #: | AI *may* do                                                            | AI *must NOT* do                                                                    |
|---|------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| G-0 | Whenever unsure about something that's related to the project, ask the developer for clarification before making changes.    |  ❌ Write changes or use tools when you are not sure about something project specific, or if you don't have context for a particular feature/decision. |
| G-1 | Generate code **only inside** relevant source directories (e.g., `src/services/llm/` for the service, `src/utils/` for the utilities) or explicitly pointed files.    | ❌ Touch `tests/`  files without permission. |
| G-2 | Add/update **`AIDEV-NOTE:` anchor comments** near non-trivial edited code. | ❌ Delete or mangle existing `AIDEV-` comments.                                     |
| G-3 | Follow lint/style configs (`pyproject.toml`) Use the project's configured linter, if available, instead of manually re-formatting code. | ❌ Re-format code to any other style.                                               |
| G-4 | For changes >300 LOC or >3 files, **ask for confirmation**.            | ❌ Refactor large modules without human guidance.                                     |
| G-5 | Stay within the current task context. Inform the dev if it'd be better to start afresh.                                  | ❌ Continue work from a prior prompt after "new task" – start a fresh session.      |

---

## 3. Coding Standards & Conventions

**Golden Rule**: All code must pass the `lint.sh` script checks before being committed. AI assistants must adhere to these rules when generating code.

- **Formatter**: `black` with a line-length of 88.
- **Import Sorter**: `isort` using the `black` profile.
- **Linter**: `ruff` for linting and formatting checks.
- **Naming**:
    - `snake_case` for functions and variables.
    - `PascalCase` for classes.
    - `SCREAMING_SNAKE_CASE` for constants.
- **Error Handling**: Use typed, hierarchical exceptions and context managers for resource management.
- **Documentation**: Use Google-style docstrings for all public functions and classes.
- **Testing**: Test files should be located in the `tests/` directory and match the source file patterns.

### Test code:

- Start with the Core: Write tests for the most critical parts of your application first.
- Expand Incrementally: Once the core is stable, gradually extend your test suite to cover surrounding modules and features.
- Use Coverage as a Guide: Use test coverage metrics not as a strict rule to follow, but as a tool to identify untested parts of your code.

- 1. Core Business Logic
    - What it is: The code that handles the primary functions of your application. For example, payment processing, order creation, or user authentication in an e-commerce platform.
    - Why it's first: A bug in the core logic can be catastrophic to your entire service. These tests ensure your application works as intended for its main purpose.
- 2. Integration Points
    - What it is: Any part of your code that interacts with external systems, such as a database, an external API, or the file system.
    - Why it's important: These are common points of failure, as they depend on external factors. It's good practice to use mocking tools like pytest's monkeypatch or Python's unittest.mock to isolate your application logic from the external system during tests.

- 3. Complex Logic & Algorithms
    - What it is: Code with many conditional branches (if/else), loops, or complex calculations.
    - Why it's important: The more complex the logic, the higher the chance of hidden bugs and unhandled edge cases. These areas require thorough testing with a wide variety of inputs.

### Linting & Formatting Script
The following script (`lint.sh`) is used to enforce code quality. It formats, sorts imports, and lints the codebase automatically.

```bash
#!/bin/bash
# lint.sh

# 1. Black: Check and apply code formatting
echo "Running black..."
uv run black src tests
uv run black --check src tests

# 2. isort: Check and apply import sorting
echo "Running isort..."
uv run isort src tests
uv run isort --check src tests

# 3. Ruff: Lint, format, and apply automatic fixes
echo "Running ruff..."
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests
```

### Error Handling Pattern
Catch specific, typed exceptions instead of generic `Exception`. Use `try/finally` for cleanup in async code.

```python
from common.exceptions import ValidationError # Hypothetical path

async def process_data(data: dict) -> Result:
    try:
        # Process data
        return result
    except KeyError as e:
        # Re-raise with a typed, project-specific exception
        raise ValidationError(f"Missing required field: {e}") from e
```

---


## 4. Technology Stack

| Category      | Technology                 | Description                                                                                                                              |
| :------------ | :------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| **Language** | Python 3.12+               | The core programming language.                                                                                                           |
| **Frameworks**| FastAPI                    | The primary asynchronous web framework.                                                                                                  |
|               | LangChain & LangGraph      | For composing LLM chains and agents.                                                                                                     |
|               | Pydantic                   | For data validation and settings management.                                                                                             |
| **Tooling** | `uv`                       | The package manager and runner.                                                                                                          |
| **Dependencies**| `pyproject.toml`           | See `[project.dependencies]` for main dependencies and `[project.optional-dependencies].dev` for development tools like `ruff`, `black`, and `isort`. |

---

## 5. Architecture & Directory Structure

| Directory         | Description                                                                          |
| :---------------- | :----------------------------------------------------------------------------------- |
| `src/`            | The root for all core application source code.                                       |
| `src/main.py`     | The application entrypoint. It imports and uses the FastAPI app object from `src/core/app.py`. |
| `src/core/`       | Contains core application components like the FastAPI instance and logging configuration. |
| `src/configs/`    | Manages sensitive configurations (e.g., API keys, database URLs) using Pydantic-settings. |
| `src/services/`   | Implements business logic and integration with external services (ASR, LLM, TTS). Each service controller file must be named `service.py`. |
| `src/utils/`      | Contains reusable utility functions used across the project.                         |
| `src/websocket/`  | Handles all WebSocket connection and communication logic.                            |
| `tests/`          | Contains all pytest test code.                                                       |

---
## 6. Setup & Execution

Use `uv` for all environment management and script execution to ensure consistency.

```bash
# Create a virtual environment and install all dependencies
uv sync

# Run the development server
uv run uvicorn src.main:app --port 8000 --reload

# Run tests
uv run pytest -q
```

---

## 7. Anchor Comments

Add specially formatted comments throughout the codebase where appropriate. This creates a trail of inline knowledge that can be easily searched for by both humans and AI.

**Guidelines**:
- Use `AIDEV-NOTE:`, `AIDEV-TODO:`, or `AIDEV-QUESTION:` (all-caps prefix) for comments aimed at AI and developers.
- Keep them concise (≤ 120 chars).
- **Important:** Before scanning files, always first try to **locate existing anchors** `AIDEV-*` in relevant subdirectories.
- **Update relevant anchors** when modifying associated code.
- **Do not remove `AIDEV-NOTE`s** without explicit human instruction.
- Make sure to add relevant anchor comments, whenever a file or piece of code is:
  * too long, or
  * too complex, or
  * very important, or
  * confusing, or
  * could have a bug unrelated to the task you are currently working on.
**Example**:
```python
# AIDEV-NOTE: This is a performance-critical path; avoid extra allocations.
async def handle_websocket_stream(...):
    ...
```

---

## 8. Commit Discipline

-  **Granular commits**: One logical change per commit.
- **Clear Commit Messages**: Explain the *why* behind the change, not just the *what*.
- **Tag AI-generated commits**: e.g., `feat: optimise feed query [AI]`.
- **Use `git worktree`** for parallel/long-running AI branches (e.g., `git worktree add ../wip-foo -b wip-foo`).
- **Review AI-generated code**: Never merge code you don't understand.
- **Follow the commit convention**: Check the commit_convention.md which follows the [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)

---

## 9. Versioning Conventions

This project follows Semantic Versioning (SemVer: `MAJOR.MINOR.PATCH`), as specified in the `pyproject.toml` file.

- **MAJOR** version update: For incompatible API changes.
- **MINOR** version update: For adding functionality in a backward-compatible manner.
- **PATCH** version update: For backward-compatible bug fixes.

---

## 10. AI Assistant Workflow: Step-by-Step Methodology

When responding to user instructions, the AI assistant should follow this process to ensure clarity, correctness, and maintainability:

1.  **Consult This Document**: When given an instruction, first consult this `PROJECT_BIBLE.md` to understand the project's rules and context.
2.  **Clarify Ambiguities**: If any part of the request is unclear, ask targeted questions to clarify the requirements before proceeding.
3.  **Break Down & Plan**: For non-trivial tasks, break down the request into smaller steps and present the plan to the developer for review.
4.  **Execute & Implement**: Once the plan is approved, implement the changes, adhering strictly to the project's coding standards.
5.  **Track Progress**: Use an internal checklist to track progress on complex, multi-step tasks.
6.  **Update Documentation**: After the task is complete, update any relevant anchor comments (`AIDEV-NOTE`, etc.) in the code you touched.
7.  **Request Review**: Ask the developer to review the completed work and be ready to iterate based on feedback.
8.  **Respect Session Boundaries**: If a new request is unrelated to the current context, suggest starting a fresh session to avoid confusion.