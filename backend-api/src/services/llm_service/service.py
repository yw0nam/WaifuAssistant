import logging
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessageChunk
import yaml
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

__doc__ = """
This module contains the implementation of the ChatWaifu_LLM class, which provides functionality for processing chat messages using a language model and tools from a Multi-Server MCP client.

Classes:
- ChatWaifu_LLM: A class that encapsulates the logic for message processing and tool interaction.

Functions:
- process_message: Processes incoming messages asynchronously through an agent and yields responses or tool calls.
- stream: Initializes the agent with the provided language model and configuration, then streams message processing results.

Example usage:
    llm = ChatOpenAI(...)
    chat_waifu = ChatWaifu_LLM(llm)
    async for result in chat_waifu.stream(messages=[...], mcp_config={...}):
        print(result)
"""


class ChatWaifu_LLM(object):

    def __init__(
        self,
        llm: ChatOpenAI,
    ):
        self.llm = llm
        logger.info(f"ChatWaifu_LLM initialized with model: {self.llm.model_name}")

    async def process_message(self, messages, agent, config: str):
        """메시지를 처리하고 스트리밍 응답을 생성합니다."""
        logger.debug(f"Processing message with agent for {len(messages)} messages")

        node = None
        tool_called = False
        gathered = ""
        content_buffer = ""

        # 개선된 버퍼링 설정
        MIN_BUFFER_SIZE = 20  # 최소 버퍼 크기 (더 큰 청크로 전송)
        MAX_BUFFER_SIZE = 100  # 최대 버퍼 크기 (메모리 보호)

        # 문장 종료 문자 (더 자연스러운 분할점)
        SENTENCE_ENDINGS = (".", "!", "?", "\n")
        WORD_ENDINGS = (" ", ",", ";", ":")

        chunk_count = 0

        try:
            async for msg, metadata in agent.astream(
                {"messages": messages}, stream_mode="messages", config=config
            ):
                # 노드 변경 처리 (로깅만, 클라이언트 전송 없음)
                if node != metadata.get("langgraph_node"):
                    node = metadata.get("langgraph_node", "unknown")

                # 일반 메시지 콘텐츠 처리
                if isinstance(msg.content, str) and not msg.additional_kwargs:
                    content = msg.content

                    # 빈 콘텐츠 및 공백만 있는 콘텐츠 스킵
                    if not content or content.isspace():
                        continue

                    # 버퍼에 콘텐츠 추가
                    content_buffer += content

                    # 메모리 보호: 최대 크기 초과 시 강제 전송
                    if len(content_buffer) > MAX_BUFFER_SIZE:
                        if content_buffer.strip():
                            yield {
                                "type": "content",
                                "text": content_buffer.strip(),
                                "node": node,
                            }
                            chunk_count += 1
                        content_buffer = ""
                        continue

                    # 자연스러운 분할점에서 전송
                    should_send = False

                    # 1. 문장 종료 시 전송
                    if (
                        content.endswith(SENTENCE_ENDINGS)
                        and len(content_buffer) >= MIN_BUFFER_SIZE
                    ):
                        should_send = True
                    # 2. 단어 종료 시 최소 크기 확인 후 전송
                    elif (
                        content.endswith(WORD_ENDINGS)
                        and len(content_buffer) >= MIN_BUFFER_SIZE * 2
                    ):
                        should_send = True

                    if should_send and content_buffer.strip():
                        yield {
                            "type": "content",
                            "text": content_buffer.strip(),
                            "node": node,
                        }
                        chunk_count += 1
                        content_buffer = ""

                # AI 메시지 청크 및 툴 콜 처리 (향후 MCP 재활성화 대비)
                elif isinstance(msg, AIMessageChunk) and msg.additional_kwargs.get(
                    "tool_calls"
                ):
                    if not tool_called:
                        gathered = msg
                        tool_called = True
                    else:
                        gathered = gathered + msg

                    # 툴 콜 완성 확인
                    if hasattr(msg, "tool_call_chunks") and msg.tool_call_chunks:
                        tool_info = gathered.tool_call_chunks[0]
                        args_str = tool_info.get("args", "")
                        if args_str and args_str.strip().endswith("}"):
                            tool_name = tool_info.get("name", "unknown")
                            logger.info(f"Tool call detected: '{tool_name}'")
                            yield {
                                "type": "tool_call",
                                "tool_name": tool_name,
                                "args": args_str,
                                "node": node,
                            }
                            # 상태 리셋
                            tool_called = False
                            gathered = ""

            # 마지막 버퍼 처리
            if content_buffer.strip():
                yield {
                    "type": "content",
                    "text": content_buffer.strip(),
                    "node": node,
                }
                chunk_count += 1

            logger.info(f"Message processing completed. Total chunks: {chunk_count}")

        except Exception as e:
            logger.error(f"Error in process_message: {e}")
            # 버퍼에 남은 내용이 있으면 먼저 전송
            if content_buffer.strip():
                yield {"type": "content", "text": content_buffer.strip(), "node": node}
            yield {"type": "error", "message": "메시지 처리 중 오류가 발생했습니다."}

    async def stream(self, message: list, mcp_config: dict, client_id: str):
        logger.info(f"Starting LLM stream for messages: {message}")
        logger.info(f"MCP Config: {mcp_config}")
        memory = MemorySaver()
        try:
            # MCP 기능을 일시적으로 비활성화하고 기본 LLM만 사용
            # logger.info("MCP 기능을 비활성화하고 기본 LLM만 사용합니다.")

            # # 빈 도구 목록으로 에이전트 생성
            # logger.debug("Creating react agent with no tools.")
            # agent = create_react_agent(
            #     self.llm,
            #     tools=[],  # 빈 도구 목록
            # )
            client = MultiServerMCPClient(mcp_config["mcp_servers"])

            tools = await client.get_tools()
            logger.info(
                f"Fetched {len(tools)} tools from MCP client: {[tool.name for tool in tools]}"
            )

            logger.debug("Creating react agent.")
            agent = create_react_agent(
                self.llm,
                tools=tools,
                checkpointer=memory,
            )
            config = {"configurable": {"thread_id": client_id}}
            # stream 메서드는 process_message 라는 비동기 제너레이터를 반환합니다.
            async for item in self.process_message(
                messages=message, agent=agent, config=config
            ):
                yield item

            yield {
                "type": "end",
                "message": "LLM stream completed successfully.",
                "message_history": agent.get_state(config=config).values["messages"],
            }
        except Exception as e:
            logger.error(f"Error in stream method: {e}")
            import traceback

            traceback.print_exc()
            raise


def load_persona(persona_file: str = "./configs/persona.yaml") -> str:
    """페르소나 설정 로드"""
    with open(persona_file, "r", encoding="utf-8") as f:
        persona_data = yaml.safe_load(f)
    return yaml.dump(persona_data, allow_unicode=True, sort_keys=False, indent=2)
