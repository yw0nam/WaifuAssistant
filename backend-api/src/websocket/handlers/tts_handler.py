"""
TTS interrupt handling module.

This module handles TTS interruption requests and manages TTS queue operations.
"""

from fastapi import WebSocket

from src.configs import TTSSettings
from src.core.logging import setup_logging
from src.services.tts.service import ChatWaifu_TTS
from src.services.tts.tts_worker import TTSWorkerManager

from ..models import TTSInterruptedResponse, TTSInterruptRequest
from .error_handler import send_error_response

logger = setup_logging("websocket_tts_handler")


class TTSHandler:
    """TTS WebSocket 메시지 처리기"""

    def __init__(self, settings: TTSSettings):
        """TTS 핸들러 초기화"""
        logger.info("TTSHandler initialized")
        self.service = ChatWaifu_TTS(url=settings.url, api_key=settings.api_key)
        self.worker_manager = TTSWorkerManager(self.service)

    async def tts_interrupt_request(
        self, websocket: WebSocket, client_id: str, request: TTSInterruptRequest
    ) -> None:
        """
        TTS 중단 요청 처리

        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            request: TTS interrupt request object
        """
        logger.info(f"Client #{client_id} TTS interrupt requested: {request.reason}")

        try:
            interrupted_count = await self.worker_manager.interrupt_tts(str(client_id))

            interrupt_response = TTSInterruptedResponse(
                message=f"TTS interrupted: {request.reason}",
                interrupted_count=interrupted_count,
            )
            await websocket.send_json(interrupt_response.model_dump())

            logger.info(
                f"Client #{client_id} TTS interrupted successfully, cleared {interrupted_count} items"
            )

        except Exception as e:
            logger.error(f"Client #{client_id} TTS interrupt failed: {e}")
            await send_error_response(
                websocket,
                f"TTS interrupt failed: {str(e)}",
                error_code="TTS_INTERRUPT_FAILED",
            )

    async def clean_tts_queue(self, client_id: str) -> None:
        """
        TTS 큐 정리

        Args:
            client_id: Client identifier
        """
        logger.info(f"Client #{client_id} cleaning up TTS queue...")
        try:
            await self.worker_manager.cleanup_tts_queue(str(client_id))
            logger.info(f"Client #{client_id} TTS queue cleaned up successfully")
        except Exception as e:
            logger.error(f"Client #{client_id} TTS queue cleanup failed: {e}")

    async def send_to_tts(
        self,
        client_id: str,
        sentence: str,
        reference_id: str = None,
    ) -> None:
        """
        TTS 요청을 TTS 워커에 전달

        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            sentence: TTS로 변환할 문장
            reference_id: Optional reference ID for TTS voice identification
        """
        await self.worker_manager.add_tts_to_queue(
            client_id=client_id, sentence=sentence, reference_id=reference_id
        )
        logger.info(
            f"Client #{client_id} TTS request added: '{sentence[:50]}...', reference_id={reference_id}"
        )
