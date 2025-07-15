from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessageChunk

from src.services.llm_service.service import ChatWaifu_LLM

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
    llm = ChatWaifu_LLM(llm=SimpleNamespace(model_name="test-model"))
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
    llm = ChatWaifu_LLM(llm=SimpleNamespace(model_name="m"))
    results = []
    async for item in llm.process_message(messages=[], agent=agent, config="c"):
        results.append(item)
    # No immediate flush for msg1, final flush yields combined text
    assert len(results) == 1
    assert results[0]["text"] == "Partial text more text"


async def test_process_message_tool_call():
    """Yield a tool_call dict when AIMessageChunk contains tool_call_chunks."""
    # simulate two chunks to assemble a complete tool call
    tool_chunk1 = DummyToolChunk(chunks=["a"], name="mytool", args="{arg:1}")
    tool_chunk2 = DummyToolChunk(chunks=["b"], name="mytool", args="{arg:1}")
    # first yield not complete, second yields and triggers
    agent = DummyAgent(
        [
            (tool_chunk1, {"langgraph_node": "n3"}),
            (tool_chunk2, {"langgraph_node": "n3"}),
        ]
    )
    llm = ChatWaifu_LLM(llm=SimpleNamespace(model_name="m"))
    results = []
    async for item in llm.process_message(messages=[], agent=agent, config="c"):
        results.append(item)
    assert len(results) == 1
    assert results[0]["type"] == "tool_call"
    assert results[0]["tool_name"] == "mytool"
    assert "args" in results[0]


async def test_process_message_error_handling():
    """Yield error dict when agent.astream raises an exception, and flush buffer."""
    msg = SimpleNamespace(content="Error part", additional_kwargs={})
    # error occurs immediately
    agent = DummyAgent(outputs=[(msg, {})], error=True)
    llm = ChatWaifu_LLM(llm=SimpleNamespace(model_name="x"))
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

    monkeypatch.setattr(
        "src.services.llm_service.service.MultiServerMCPClient", StubClient
    )

    # stub agent with process_message stub
    class StubAgent:
        def __init__(self):
            pass

        async def astream(self, *args, **kwargs):
            return

        def get_state(self, config):
            return SimpleNamespace(values={"messages": ["m1", "m2"]})

    monkeypatch.setattr(
        "src.services.llm_service.service.create_react_agent",
        lambda llm, tools, checkpointer: StubAgent(),
    )
    # stub process_message to yield one content
    monkeypatch.setattr(
        ChatWaifu_LLM,
        "process_message",
        lambda self, messages, agent, config: iter(
            [{"type": "content", "text": "hi", "node": None}]
        ),
    )
    llm = ChatWaifu_LLM(llm=SimpleNamespace(model_name="m"))
    results = []
    async for item in llm.stream(
        message=["msg"], mcp_config={"mcp_servers": []}, client_id="cid"
    ):
        results.append(item)
    # last item should be end type
    assert results[-1]["type"] == "end"
    assert "message_history" in results[-1]
