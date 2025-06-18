import asyncio
from typing import Dict
from fastapi import WebSocket
from src.services.tts_service import ChatWaifu_TTS, ServeTTSRequest
from src.configs import settings
from src.core.logging import setup_logging
from .models import AudioResponse, ErrorResponse

logger = setup_logging("tts_worker")

# 클라이언트별 TTS 처리 큐
tts_queues: Dict[str, asyncio.Queue] = {}


async def tts_worker(
    client_id: str, websocket: WebSocket, chat_waifu_tts: ChatWaifu_TTS
):
    """TTS 처리를 위한 백그라운드 워커"""
    if client_id not in tts_queues:
        tts_queues[client_id] = asyncio.Queue()

    queue = tts_queues[client_id]

    try:
        while True:
            # 큐에서 TTS 요청 대기
            tts_text = await queue.get()

            if tts_text is None:  # 종료 신호
                break

            try:
                logger.info(f"Client #{client_id} TTS 생성 시작...")

                tts_request = ServeTTSRequest(
                    text=tts_text,
                    format="wav",
                    reference_id=getattr(settings.tts_configs, "reference_id", None),
                    chunk_length=200,
                    normalize=True,
                    temperature=0.8,
                )

                # Base64로 인코딩된 음성 데이터 받기
                audio_base64 = chat_waifu_tts.request_tts_base64(request=tts_request)

                if audio_base64:
                    # 음성 데이터를 WebSocket으로 전송
                    audio_response = AudioResponse(
                        data=audio_base64,
                        format="wav",
                        text=tts_text,
                        duration=None  # 향후 실제 음성 길이 계산 추가
                    )
                    await websocket.send_json(audio_response.model_dump())
                    logger.info(f"✅ Client #{client_id} TTS 음성 데이터 전송 완료")
                else:
                    logger.warning(f"⚠️ Client #{client_id} TTS 생성 실패")
                    error_response = ErrorResponse(
                        message="TTS 음성 생성에 실패했습니다.",
                        error_code="TTS_GENERATION_FAILED"
                    )
                    await websocket.send_json(error_response.model_dump())

            except Exception as tts_error:
                logger.error(f"❌ Client #{client_id} TTS 처리 중 오류: {tts_error}")
                error_response = ErrorResponse(
                    message=f"TTS 처리 오류: {str(tts_error)}",
                    error_code="TTS_PROCESSING_ERROR"
                )
                await websocket.send_json(error_response.model_dump())
            finally:
                queue.task_done()

    except Exception as e:
        logger.error(f"❌ Client #{client_id} TTS 워커 오류: {e}")


async def add_tts_to_queue(client_id: str, text: str):
    """TTS 큐에 텍스트 추가"""
    if client_id in tts_queues:
        await tts_queues[client_id].put(text)


def cleanup_tts_queue(client_id: str):
    """TTS 큐 정리"""
    if client_id in tts_queues:
        tts_queues[client_id].put_nowait(None)  # 종료 신호
        del tts_queues[client_id]
