"""
Chat request handling module.

This module handles chat requests, including LLM streaming, TTS processing,
and message history management.

TODO: This module could be further modularized into:
- llm_streaming_handler.py - LLM response streaming logic
- tts_streaming_handler.py - TTS streaming coordination
- message_history_manager.py - Conversation history management
"""

from typing import Dict, List
from fastapi import WebSocket
from langchain_core.messages import HumanMessage, AIMessage
from src.services.llm_service.service import ChatWaifu_LLM
from src.utils.text_chunker import TextChunkProcessor
from src.core.logging import setup_logging
from ..models import (
    ChatRequest,
    ContentResponse,
    StreamingTTSResponse,
    LLMCompleteResponse,
)
from ..tts_worker import add_tts_to_queue

logger = setup_logging("websocket_chat_handler")


async def handle_chat_request(
    websocket: WebSocket,
    client_id: str,
    request: ChatRequest,
    chat_waifu_llm: ChatWaifu_LLM,
    message_history: List,
    mcp_config: dict,
    client_ai_responding: Dict[str, bool],
) -> None:
    """
    채팅 요청 처리

    Args:
        websocket: WebSocket connection
        client_id: Client identifier
        request: Chat request object
        chat_waifu_llm: LLM service instance
        message_history: Conversation history
        mcp_config: MCP configuration
        client_ai_responding: Client AI response state tracker
    """
    logger.info(
        f"Client #{client_id} 메시지: '{request.text}' (TTS: {request.enable_tts})"
    )
    message_history.append(HumanMessage(content=request.text))

    # AI 응답 시작 - 상태 설정
    client_ai_responding[client_id] = True
    logger.info(f"Client #{client_id} 에게 LLM 스트리밍 시작...")

    try:
        # Initialize streaming TTS processor if TTS is enabled
        streaming_processor = None
        sentence_id = 0

        if request.enable_tts:
            streaming_processor = TextChunkProcessor(
                reasoning_start_tag=request.reasoning_start_tag,
                reasoning_end_tag=request.reasoning_end_tag,
            )
            logger.info(
                f"Client #{client_id} 스트리밍 TTS 프로세서 초기화 (reasoning_tags: '{request.reasoning_start_tag}' -> '{request.reasoning_end_tag}')"
            )

        chunk_id = 0
        async for result in chat_waifu_llm.stream(
            message=message_history, mcp_config=mcp_config, client_id=client_id
        ):
            # 텍스트 콘텐츠가 있고, 노드가 'agent'인 경우에만 TTS 처리
            if result.get("node") == "agent" and result.get("type") == "content":
                chunk_text = result.get("text")
                complete_sentences = streaming_processor.add_chunk(chunk_text)

                for sentence in complete_sentences:
                    content_response = ContentResponse(
                        text=sentence,
                        chunk_id=chunk_id,
                        node=result.get("node"),
                    )
                    await websocket.send_json(content_response.model_dump())

                    await add_tts_to_queue(
                        client_id=str(client_id),
                        sentence=sentence,
                        reference_id=request.reference_id,
                    )

                    streaming_tts_response = StreamingTTSResponse(
                        sentence=sentence,
                        sentence_id=sentence_id,
                        is_final=False,
                    )

                    await websocket.send_json(streaming_tts_response.model_dump())

                    # Add to TTS queue immediately with reference_id
                    logger.info(
                        f"Client #{client_id} 스트리밍 TTS 문장 #{sentence_id} (from agent): '{sentence[:50]}...'"
                    )
                    sentence_id += 1
                chunk_id += 1

            elif result.get("type") == "tool_call":
                logger.info(
                    f"Client #{client_id} 도구 호출: {result.get('tool_name')} (args: {result.get('args')})"
                )
            elif result.get("node") == "tools":
                logger.info(
                    f"Client #{client_id} 도구 응답: {result.get('tool_name')} (args: {result.get('args')})"
                )
            elif result.get("type") == "end":
                logger.info(
                    f"Client #{client_id} 상태 업데이트: {result.get('message_history')}, message: {result.get('message')}"
                )
                message_history = result.get("message_history", message_history)
    finally:
        # AI 응답 완료 - 상태 해제
        client_ai_responding[client_id] = False
        logger.info(f"Client #{client_id} AI 응답 완료, 상태 해제")
