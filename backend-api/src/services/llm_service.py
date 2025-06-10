import logging
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessageChunk

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

    async def process_message(self, messages, agent):
        logger.debug(f"Processing message with agent for messages: {messages}")
        node = None
        tool_called = False
        gathered = ""
        async for msg, metadata in agent.astream(
            {"messages": messages},
            stream_mode="messages",
        ):
            if node != metadata["langgraph_node"]:
                logger.debug(f"Langgraph node changed to: {metadata['langgraph_node']}")
                yield {"type": "node_change", "node_name": metadata["langgraph_node"]}
                node = metadata["langgraph_node"]

            # For regular message content, print it directly.
            if isinstance(msg.content, str) and msg.additional_kwargs == {}:
                logger.debug(f"Yielding content: {msg.content}")
                yield {"type": "content", "text": msg.content}
            # Process AI message chunks and handle tool call chunks.
            elif (
                isinstance(msg, AIMessageChunk)
                and "tool_calls" in msg.additional_kwargs
            ):
                if not tool_called:
                    gathered = msg
                    tool_called = True
                else:
                    gathered = gathered + msg
                if msg.tool_call_chunks:
                    tool_info = gathered.tool_call_chunks[0]
                    args_str = tool_info.get("args", "")
                    if args_str and args_str.strip().endswith("}"):
                        tool_name = tool_info.get("name", "")
                        logger.info(
                            f"Tool call detected: '{tool_name}' with args: {args_str}"
                        )
                        yield {
                            "type": "tool_call",
                            "tool_name": tool_name,
                            "args": args_str,
                        }

            else:
                logger.debug(f"Received unhandled message type or content: {msg}")

    async def stream(self, message: list, mcp_config: dict):
        logger.info(f"Starting LLM stream for messages: {message}")
        logger.info(f"MCP Config: {mcp_config}")

        logger.debug("Initializing MultiServerMCPClient.")
        client = MultiServerMCPClient(mcp_config)

        tools = await client.get_tools()
        logger.info(
            f"Fetched {len(tools)} tools from MCP client: {[tool.name for tool in tools]}"
        )

        logger.debug("Creating react agent.")
        agent = create_react_agent(
            self.llm,
            tools=tools,
        )
        # stream 메서드는 process_message 라는 비동기 제너레이터를 반환합니다.
        async for item in self.process_message(messages=message, agent=agent):
            yield item
