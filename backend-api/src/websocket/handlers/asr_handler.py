import base64
import logging
import tempfile
import time
from typing import AsyncGenerator

from src.services.asr.service import ASRService
from src.websocket.models import (
    ASRResultResponse,
    ASRStreamingResponse,
    ASRTranscribeRequest,
    ErrorResponse,
)

# AIDEV-NOTE: ASR WebSocket handler for real-time audio transcription
# Handles both one-shot and streaming transcription requests
logger = logging.getLogger(__name__)


class ASRHandler:
    """ASR WebSocket 메시지 처리기"""

    def __init__(self, asr_settings):
        """ASR 핸들러 초기화"""
        self.service = ASRService(asr_settings)
        logger.info("ASRHandler initialized with vLLM ASR service")

    async def transcribe_request(
        self, request: ASRTranscribeRequest
    ) -> AsyncGenerator[dict, None]:
        """
        ASR 전사 요청 처리

        Args:
            request: ASR 전사 요청

        Yields:
            ASR 응답 메시지들
        """
        start_time = time.time()

        try:
            # Base64 오디오 데이터를 바이너리로 디코딩
            try:
                audio_data = base64.b64decode(request.audio_data)
            except Exception as e:
                logger.error(f"Failed to decode base64 audio data: {e}")
                yield ErrorResponse(
                    message="Invalid base64 audio data",
                    error_code="INVALID_AUDIO_DATA",
                    details={"error": str(e)},
                ).model_dump()
                return

            # 임시 파일에 오디오 데이터 저장
            # AIDEV-NOTE: vLLM ASR service requires file input, so we use temporary files
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(
                    suffix=f".{request.format}", delete=False
                ) as temp_file:
                    temp_file.write(audio_data)
                    temp_file_path = temp_file.name

                logger.debug(
                    f"Created temporary audio file: {temp_file_path} "
                    f"({len(audio_data)} bytes, format: {request.format})"
                )

                if request.streaming:
                    # 스트리밍 전사 처리
                    async for chunk in self._handle_streaming_transcription(
                        temp_file_path, request
                    ):
                        yield chunk
                else:
                    # 일반 전사 처리
                    async for response in self._handle_regular_transcription(
                        temp_file_path, request, start_time
                    ):
                        yield response

            finally:
                # 임시 파일 정리
                if temp_file and hasattr(temp_file, "name"):
                    try:
                        import os

                        os.unlink(temp_file.name)
                        logger.debug(f"Cleaned up temporary file: {temp_file.name}")
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to cleanup temp file: {cleanup_error}")

        except Exception as e:
            logger.error(f"Error in ASR transcription: {e}")
            yield ErrorResponse(
                message="ASR transcription failed",
                error_code="TRANSCRIPTION_ERROR",
                details={"error": str(e)},
            ).model_dump()

    async def _regular_transcription(
        self, audio_file_path: str, request: ASRTranscribeRequest, start_time: float
    ) -> AsyncGenerator[dict, None]:
        """일반 (비스트리밍) 전사 처리"""
        try:
            # ASR 서비스를 사용하여 전사 수행
            result = await self.service.transcribe_async(
                audio_file_path,
                language=request.language,
                temperature=request.temperature,
                response_format=request.response_format or "json",
            )

            processing_time = time.time() - start_time

            logger.info(
                f"ASR transcription completed in {processing_time:.2f}s. "
                f"Result length: {len(result)} characters"
            )

            # 결과 응답 생성
            yield ASRResultResponse(
                text=result,
                language=request.language,
                processing_time=processing_time,
            ).model_dump()

        except Exception as e:
            logger.error(f"Error in regular transcription: {e}")
            yield ErrorResponse(
                message="Regular transcription failed",
                error_code="REGULAR_TRANSCRIPTION_ERROR",
                details={"error": str(e)},
            ).model_dump()

    async def _streaming_transcription(
        self, audio_file_path: str, request: ASRTranscribeRequest
    ) -> AsyncGenerator[dict, None]:
        """스트리밍 전사 처리"""
        try:
            logger.debug("Starting streaming ASR transcription")

            # 스트리밍 전사 수행
            async for chunk in self.service.transcribe_stream(
                audio_file_path,
                language=request.language,
                temperature=request.temperature,
            ):
                # 스트리밍 응답 생성
                yield ASRStreamingResponse(
                    text=chunk,
                    is_final=False,
                ).model_dump()

            # 최종 완료 신호
            yield ASRStreamingResponse(
                text="",
                is_final=True,
            ).model_dump()

            logger.info("Streaming ASR transcription completed")

        except Exception as e:
            logger.error(f"Error in streaming transcription: {e}")
            yield ErrorResponse(
                message="Streaming transcription failed",
                error_code="STREAMING_TRANSCRIPTION_ERROR",
                details={"error": str(e)},
            ).model_dump()

    async def close(self):
        """ASR 핸들러 정리"""
        try:
            await self.service.aclose()
            logger.info("ASRHandler closed successfully")
        except Exception as e:
            logger.warning(f"Error closing ASRHandler: {e}")
