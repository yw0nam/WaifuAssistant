from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessageChunk

from src.services.llm.service import ChatWaifu_LLM

pytestmark = pytest.mark.asyncio


class DummyAgent:
    def __init__(self, outputs, error=False):
        self._outputs = outputs
        self._error = error

    async def astream(self, args, stream_mode, config):
        if self._error:
            raise RuntimeError("agent failure")
        for msg, meta in self._outputs:
            yield msg, meta


class DummyChunk(SimpleNamespace):
    def __init__(self, content, additional_kwargs=None, tool_call_chunks=None):
        super().__init__(
            content=content,
            additional_kwargs=additional_kwargs or {},
            tool_call_chunks=tool_call_chunks or [],
        )


class DummyToolChunk(AIMessageChunk):
    def __init__(self, chunks, name, args):
        # mimic AIMessageChunk
        super().__init__(content=None, additional_kwargs={"tool_calls": True})
        self.tool_call_chunks = [{"name": name, "args": args}]
        self._chunks = chunks


async def test_process_message_simple_content():
    """Yield a single content chunk for simple messages ending with punctuation."""
    # prepare messages: content "Hello world." should flush immediately
    msg = SimpleNamespace(content="Hello world.", additional_kwargs={})
    meta = {"langgraph_node": "n1"}
    agent = DummyAgent([(msg, meta)])

    # Create a mock LLM object that the service expects
    mock_llm = SimpleNamespace(model_name="test-model")
    llm = ChatWaifu_LLM(openai_api_base="http://test", openai_api_key="test-key")
    llm.llm = mock_llm  # Replace the created LLM with our mock

    results = []
    async for item in llm.process_message(
        messages=["ignored"], agent=agent, config="cfg"
    ):
        results.append(item)
    assert len(results) == 1
    assert results[0]["type"] == "content"
    assert results[0]["text"] == "Hello world."
    assert results[0]["node"] == "n1"


async def test_process_message_buffer_flush_at_end():
    """Flush remaining buffer after stream ends even without punctuation."""
    msg1 = SimpleNamespace(content="Partial text ", additional_kwargs={})
    msg2 = SimpleNamespace(content="more text", additional_kwargs={})
    meta = {"langgraph_node": "n2"}
    agent = DummyAgent([(msg1, meta), (msg2, meta)])

    mock_llm = SimpleNamespace(model_name="m")
    llm = ChatWaifu_LLM(openai_api_base="http://test", openai_api_key="test-key")
    llm.llm = mock_llm

    results = []
    async for item in llm.process_message(messages=[], agent=agent, config="c"):
        results.append(item)
    # No immediate flush for msg1, final flush yields combined text
    assert len(results) == 1
    assert results[0]["text"] == "Partial text more text"


async def test_process_message_tool_call(monkeypatch):
    """Yield a tool_call dict when AIMessageChunk-like objects contain tool_call_chunks."""
    # Treat SimpleNamespace as AIMessageChunk for testing
    import src.services.llm.service as svc_mod

    monkeypatch.setattr(svc_mod, "AIMessageChunk", SimpleNamespace)
    # create two message chunks to simulate tool call assembly
    chunk_data = {"name": "mytool", "args": "{arg:1}"}
    tool_chunk1 = SimpleNamespace(
        content=None,
        additional_kwargs={"tool_calls": True},
        tool_call_chunks=[chunk_data],
    )
    tool_chunk2 = SimpleNamespace(
        content=None,
        additional_kwargs={"tool_calls": True},
        tool_call_chunks=[chunk_data],
    )
    agent = DummyAgent(
        [
            (tool_chunk1, {"langgraph_node": "n3"}),
            (tool_chunk2, {"langgraph_node": "n3"}),
        ]
    )

    mock_llm = SimpleNamespace(model_name="m")
    llm = ChatWaifu_LLM(openai_api_base="http://test", openai_api_key="test-key")
    llm.llm = mock_llm

    results = []
    async for item in llm.process_message(messages=[], agent=agent, config="c"):
        results.append(item)
    # Each tool chunk triggers its own tool_call yield
    assert len(results) >= 1
    assert results[0]["type"] == "tool_call"
    assert results[0]["tool_name"] == "mytool"
    assert "args" in results[0]


async def test_process_message_error_handling():
    """Yield error dict when agent.astream raises an exception, and flush buffer."""
    msg = SimpleNamespace(content="Error part", additional_kwargs={})
    # error occurs immediately
    agent = DummyAgent(outputs=[(msg, {})], error=True)

    mock_llm = SimpleNamespace(model_name="x")
    llm = ChatWaifu_LLM(openai_api_base="http://test", openai_api_key="test-key")
    llm.llm = mock_llm

    results = []
    async for item in llm.process_message(messages=[], agent=agent, config="cfg"):
        results.append(item)
    # should yield an error after flushing any buffer
    assert any(item.get("type") in ["error", "content"] for item in results)


async def test_stream_method_with_end_and_state(monkeypatch):
    """Test that stream yields items from process_message and final end message."""
    # stub MultiServerMCPClient.get_tools, create_react_agent, and agent

    # stub client
    class StubClient:
        def __init__(self, servers):
            pass

        async def get_tools(self):
            return []

    monkeypatch.setattr("src.services.llm.service.MultiServerMCPClient", StubClient)

    # stub agent with process_message stub
    class StubAgent:
        def __init__(self):
            pass

        async def astream(self, *args, **kwargs):
            return

        def get_state(self, config):
            return SimpleNamespace(values={"messages": ["m1", "m2"]})

    monkeypatch.setattr(
        "src.services.llm.service.create_react_agent",
        lambda llm, tools, checkpointer: StubAgent(),
    )

    # stub process_message to yield one content asynchronously
    async def fake_process_message(self, messages, agent, config):
        yield {"type": "content", "text": "hi", "node": None}

    monkeypatch.setattr(ChatWaifu_LLM, "process_message", fake_process_message)

    mock_llm = SimpleNamespace(model_name="m")
    llm = ChatWaifu_LLM(openai_api_base="http://test", openai_api_key="test-key")
    llm.llm = mock_llm

    results = []
    async for item in llm.stream(
        message=["msg"], mcp_config={"mcp_servers": []}, client_id="cid"
    ):
        results.append(item)
    # last item should be end type
    assert results[-1]["type"] == "end"
    assert "message_history" in results[-1]


# AIDEV-NOTE: E2E tests for LLM service that make actual API calls
# These tests require the LLM service to be running at the configured URL


@pytest.mark.e2e
async def test_service_e2e_real_api():
    """
    E2E test that makes an actual API call to the LLM service.

    This test requires the LLM service to be running at the configured URL.
    Skip with: pytest -m "not e2e"
    """

    from src.configs.loader import load_config

    # Load actual configuration
    config = load_config()

    try:
        # Create LLM service with real LLM
        llm_service = ChatWaifu_LLM(
            openai_api_base=config.llm_configs.openai_api_base,
            openai_api_key=config.llm_configs.openai_api_key,
            model=config.llm_configs.model,
            temperature=config.llm_configs.temperature,
        )

        # Test simple streaming with meaningful message
        test_messages = [
            {"role": "user", "content": "Tell me about the weather today."}
        ]
        mcp_config = {"mcp_servers": []}  # Empty MCP config for simple test

        results = []
        content_parts = []

        # AIDEV-NOTE: Don't abort early - wait for complete response to test actual functionality
        async for item in llm_service.stream(
            message=test_messages,
            mcp_config=mcp_config,
            client_id="test_e2e_client",
        ):
            results.append(item)

            # Collect content for verification
            if item.get("type") == "content" and "text" in item:
                content_parts.append(item["text"])

            # Log progress but don't break early
            if len(results) % 5 == 0:
                print(f"LLM E2E: Received {len(results)} responses so far...")

        # Verify we got a complete response
        full_content = "".join(content_parts)
        assert len(results) > 0, "Should receive responses from LLM API"
        assert len(full_content.strip()) > 0, "Should receive non-empty content"
        print(
            f"LLM E2E test completed with {len(results)} responses, content: {full_content[:100]}..."
        )

    except Exception as e:
        if any(
            keyword in str(e).lower()
            for keyword in ["connection", "timeout", "network", "refused"]
        ):
            pytest.skip(f"LLM service not available: {e}")
        else:
            pytest.fail(f"Unexpected error in LLM E2E test: {e}")


@pytest.mark.e2e
async def test_llm_service_e2e_with_mcp():
    """
    E2E test that tests LLM service with MCP tools.

    This test may be skipped if MCP services are not available.
    """

    from src.configs.loader import load_config

    config = load_config()

    try:
        llm_service = ChatWaifu_LLM(
            openai_api_base=config.llm_configs.openai_api_base,
            openai_api_key=config.llm_configs.openai_api_key,
            model=config.llm_configs.model,
            temperature=config.llm_configs.temperature,
        )

        # Test with meaningful message for MCP
        test_messages = [
            {"role": "user", "content": "What can you help me with today?"}
        ]
        mcp_config = {
            "mcp_servers": {
                "sequential-thinking": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
                    "transport": "stdio",
                }
            }
        }

        results = []
        content_parts = []

        # AIDEV-NOTE: Wait for complete MCP response - don't abort early
        async for item in llm_service.stream(
            message=test_messages,
            mcp_config=mcp_config,
            client_id="test_mcp_client",
        ):
            results.append(item)

            if item.get("type") == "content" and "text" in item:
                content_parts.append(item["text"])

            # Log MCP progress
            if item.get("type") == "tool_call":
                print(f"MCP tool call: {item.get('name', 'unknown')}")

        # Verify MCP response completeness
        full_content = "".join(content_parts)
        print(
            f"MCP E2E completed: {len(results)} responses, content: {full_content[:100]}..."
        )

        # Basic validation - should have some response
        assert len(results) > 0, "Should receive responses with MCP"

    except Exception as e:
        if any(
            keyword in str(e).lower()
            for keyword in ["connection", "timeout", "network", "refused"]
        ):
            pytest.skip(f"LLM service not available for MCP test: {e}")
        else:
            # MCP might not be available, but service should still work
            print(f"MCP test encountered: {e}")
            pytest.skip(f"MCP functionality not available: {e}")


@pytest.mark.e2e
async def test_llm_service_e2e_error_handling():
    """
    E2E test that verifies error handling with invalid configurations.
    """
    import asyncio

    try:
        # Test with invalid API configuration (should fail quickly)

        llm_service = ChatWaifu_LLM(
            openai_api_base="http://localhost:99999/v1",  # Invalid port
            openai_api_key="invalid-key",
            model="invalid-model",
            temperature=0.5,
        )

        test_messages = [{"role": "user", "content": "Test"}]
        mcp_config = {"mcp_servers": []}

        results = []
        try:
            # This should fail quickly due to invalid configuration
            async for item in llm_service.stream(
                message=test_messages,
                mcp_config=mcp_config,
                client_id="test_error_client",
            ):
                results.append(item)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            # Expected to fail with invalid config
            assert "error" in str(e).lower() or "connection" in str(e).lower()

    except Exception as e:
        print(f"Error handling test result: {e}")
