# tts_worker.py
import asyncio
from typing import Dict, NamedTuple, Optional

from fastapi import WebSocket

from src.core.logging import setup_logging
from src.services.tts.service import ChatWaifu_TTS
from src.websocket.models import AudioResponse

logger = setup_logging("tts_worker")


class TTSRequest(NamedTuple):
    """TTS 큐에 저장될 요청 데이터 (텍스트와 레퍼런스 ID 포함)"""

    text: str
    reference_id: Optional[str] = None


class TTSWorkerManager:
    def __init__(self, service: ChatWaifu_TTS):
        self.tts_queues: Dict[str, asyncio.Queue[Optional[TTSRequest]]] = {}
        self.tts_interrupt_flags: Dict[str, bool] = {}
        self.service = service
        logger.info("TTSWorkerManager initialized with ChatWaifu_TTS service")

    async def tts_worker(self, client_id: str, websocket: WebSocket) -> None:
        """
        단순화된 TTS 백그라운드 워커.
        큐에서 완성된 문장을 받아 TTS 서비스로 전달하는 역할만 수행합니다.
        """
        logger.info(f"🎵 Client #{client_id} TTS worker starting...")
        queue = self.tts_queues.setdefault(client_id, asyncio.Queue())
        self.tts_interrupt_flags.setdefault(client_id, False)

        while True:
            try:
                # 큐에서 TTS 요청을 기다림
                tts_request = await queue.get()

                if tts_request is None:  # 종료 신호
                    logger.info(
                        f"🛑 Client #{client_id} TTS worker shutdown signal received"
                    )
                    break

                # 핸들러에서 이미 TTS 대상을 선별했으므로, 바로 처리 시작
                sentence = tts_request.text
                reference_id = tts_request.reference_id
                logger.info(
                    f"📨 Client #{client_id} TTS 작업 시작: '{sentence[:50]}...'"
                )

                # 매 작업 전 중단 플래그 확인
                if self.tts_interrupt_flags.get(client_id, False):
                    logger.info(
                        f"🚫 Client #{client_id} TTS 작업 중단됨 (플래그 활성화)"
                    )
                    self.tts_interrupt_flags[client_id] = False  # 플래그 리셋
                    queue.task_done()
                    continue

                # ChatWaifu_TTS 서비스의 메인 메서드를 호출하여 오디오 생성
                # generate_speech는 내부적으로 텍스트 처리 및 API 호출을 모두 수행함
                audio_base64 = await asyncio.to_thread(
                    self.service.generate_speech,
                    raw_text=sentence,
                    reference_id=reference_id,
                    output_format="base64",
                )

                # 오디오 생성 후에도 중단 플래그를 다시 확인 (생성 도중 인터럽트가 걸렸을 수 있음)
                if self.tts_interrupt_flags.get(client_id, False):
                    logger.info(
                        f"🚫 Client #{client_id} TTS 작업 중단됨 (오디오 생성 후)"
                    )
                    self.tts_interrupt_flags[client_id] = False  # 플래그 리셋
                    queue.task_done()
                    continue

                if audio_base64 and isinstance(audio_base64, str):
                    audio_response = AudioResponse(data=audio_base64, text=sentence)
                    await websocket.send_json(audio_response.model_dump())
                    logger.info(f"✅ Client #{client_id} TTS 오디오 전송 완료")
                else:
                    logger.warning(
                        f"⚠️ Client #{client_id} TTS 오디오 생성 실패: '{sentence[:50]}...'"
                    )

            except asyncio.CancelledError:
                logger.info(f"🛑 Client #{client_id} TTS worker cancelled")
                break
            except Exception as e:
                logger.error(
                    f"❌ Client #{client_id} TTS worker에서 에러 발생: {e}",
                    exc_info=True,
                )
                # 특정 작업 실패 시에도 워커가 중단되지 않도록 잠시 대기 후 계속
                await asyncio.sleep(0.1)
            finally:
                if "queue" in locals() and queue:
                    # 현 작업이 끝났음을 큐에 알림
                    if not queue.empty():
                        queue.task_done()

        logger.info(f"🧹 Client #{client_id} TTS worker cleanup completed")

    async def add_tts_to_queue(
        self, client_id: str, sentence: str, reference_id: Optional[str] = None
    ):
        """TTS 큐에 요청을 추가합니다."""
        if client_id in self.tts_queues:
            tts_request = TTSRequest(text=sentence, reference_id=reference_id)
            await self.tts_queues[client_id].put(tts_request)
        else:
            logger.warning(f"TTS 큐를 찾을 수 없음: client #{client_id}")

    async def interrupt_tts(self, client_id: str) -> int:
        """TTS 작업을 중단하고 큐를 비웁니다."""
        interrupted_count = 0
        self.tts_interrupt_flags[client_id] = True
        if client_id in self.tts_queues:
            queue = self.tts_queues[client_id]
            while not queue.empty():
                try:
                    queue.get_nowait()
                    queue.task_done()
                    interrupted_count += 1
                except asyncio.QueueEmpty:
                    break
            logger.info(
                f"🧹 Client #{client_id} TTS 큐에서 {interrupted_count}개 항목 제거됨"
            )
        return interrupted_count

    def cleanup_tts_queue(self, client_id: str):
        """TTS 워커 종료 시 관련 리소스를 정리합니다."""
        if client_id in self.tts_queues:
            try:
                self.tts_queues[client_id].put_nowait(None)  # 종료 신호
            except asyncio.QueueFull:
                pass  # 큐가 꽉 찼으면 어차피 종료 중이므로 무시
            del self.tts_queues[client_id]
        if client_id in self.tts_interrupt_flags:
            del self.tts_interrupt_flags[client_id]
        logger.info(f"TTS 리소스 정리 완료: client #{client_id}")
