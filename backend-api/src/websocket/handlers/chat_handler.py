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
from langchain_core.messages import HumanMessage

from src.configs import LLMSettings
from src.core.logging import setup_logging
from src.services.llm.service import ChatWaifu_LLM
from src.utils.text_chunker import TextChunkProcessor, TTSTextProcessor
from src.websocket.models import ChatRequest, ContentResponse

logger = setup_logging("websocket_chat_handler")


class ChatHandler:
    """Chat WebSocket 메시지 처리기"""

    def __init__(self, settings: LLMSettings):
        """Chat 핸들러 초기화"""

        self.service = ChatWaifu_LLM(**settings.model_dump())
        logger.info("ChatHandler initialized")

    from typing import AsyncGenerator

    async def process_chat_request(
        self,
        streaming_processor: TextChunkProcessor,
        text_processor: TTSTextProcessor,
        websocket: WebSocket,
        client_id: str,
        request: ChatRequest,
        result: dict,
    ) -> AsyncGenerator[dict, None]:
        chunk_text = result.get("text")
        complete_sentences = streaming_processor.add_chunk(chunk_text)
        if not complete_sentences:
            yield {}
        else:
            for sentence in complete_sentences:
                processed_data = text_processor.process_text(sentence)
                if processed_data and processed_data.filtered_text:
                    content_response = ContentResponse(
                        text=processed_data.filtered_text,
                        node=result.get("node"),
                        emotion_tag=processed_data.emotion_tag,
                    )
                    await websocket.send_json(content_response.model_dump())
                yield {
                    "client_id": client_id,
                    "sentence": sentence,
                    "reference_id": request.reference_id,
                }
                # await self.tts_worker_manager.add_tts_to_queue(
                #     client_id=str(client_id),
                #     sentence=sentence,
                #     reference_id=request.reference_id,
                # )
                # logger.info(f"Client #{client_id} '{sentence[:50]}...'")
                # if request.enable_tts:
                #     streaming_tts_response = StreamingTTSResponse(
                #         sentence=sentence,
                #     )
                #     await websocket.send_json(streaming_tts_response.model_dump())

    async def chat_request(
        self,
        websocket: WebSocket,
        client_id: str,
        request: ChatRequest,
        message_history: List,
        mcp_config: dict,
        client_ai_responding: Dict[str, bool],
    ) -> AsyncGenerator[dict, None]:
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
        logger.info(f"Client #{client_id} LLM streaming started...")

        try:
            # Initialize streaming TTS processor if TTS is enabled
            streaming_processor = TextChunkProcessor(
                reasoning_start_tag=request.reasoning_start_tag,
                reasoning_end_tag=request.reasoning_end_tag,
            )
            text_processor = TTSTextProcessor()

            logger.info(f"Client #{client_id} streaming processor initialized")

            async for result in self.service.stream(
                message=message_history, mcp_config=mcp_config, client_id=client_id
            ):
                if result.get("node") == "agent" and result.get("type") == "content":
                    yield await self.process_chat_request(
                        streaming_processor,
                        text_processor,
                        websocket,
                        client_id,
                        request,
                        result,
                    )

        finally:
            client_ai_responding[client_id] = False
            logger.info(f"Client #{client_id} AI response completed")
