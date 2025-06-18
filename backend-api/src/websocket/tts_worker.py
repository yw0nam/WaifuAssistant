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
    """TTS processing background worker with robust error handling"""
    queue = None
    try:
        logger.info(f"🎵 Client #{client_id} TTS worker starting...")

        # Initialize TTS queue safely
        if client_id not in tts_queues:
            tts_queues[client_id] = asyncio.Queue()
            logger.info(f"📝 Client #{client_id} TTS queue created")

        queue = tts_queues[client_id]
        logger.info(f"✅ Client #{client_id} TTS worker initialized successfully")

        while True:
            try:
                # Wait for TTS requests from queue with timeout
                logger.debug(f"⏳ Client #{client_id} waiting for TTS request...")
                tts_text = await asyncio.wait_for(queue.get(), timeout=1.0)
                logger.info(
                    f"📨 Client #{client_id} received TTS request: {tts_text[:50]}..."
                )

                if tts_text is None:  # Shutdown signal
                    logger.info(
                        f"🛑 Client #{client_id} TTS worker shutdown signal received"
                    )
                    break

                try:
                    logger.info(f"🔊 Client #{client_id} starting TTS generation...")

                    # Validate TTS service is available
                    if not chat_waifu_tts:
                        logger.error(
                            f"❌ Client #{client_id} TTS service not available"
                        )
                        raise Exception("TTS service not initialized")

                    tts_request = ServeTTSRequest(
                        text=tts_text,
                        format="wav",
                        reference_id=getattr(
                            settings.tts_configs, "reference_id", None
                        ),
                        chunk_length=200,
                        normalize=True,
                        temperature=0.8,
                    )

                    # Generate TTS with timeout
                    audio_base64 = await asyncio.wait_for(
                        asyncio.to_thread(
                            chat_waifu_tts.request_tts_base64, tts_request
                        ),
                        timeout=30.0,
                    )

                    if audio_base64:
                        # Send audio data via WebSocket
                        audio_response = AudioResponse(
                            data=audio_base64,
                            format="wav",
                            text=tts_text,
                            duration=None,
                        )
                        await websocket.send_json(audio_response.model_dump())
                        logger.info(
                            f"✅ Client #{client_id} TTS audio data sent successfully"
                        )
                    else:
                        logger.warning(
                            f"⚠️ Client #{client_id} TTS generation failed - no audio data"
                        )
                        error_response = ErrorResponse(
                            message="TTS audio generation failed.",
                            error_code="TTS_GENERATION_FAILED",
                        )
                        try:
                            await websocket.send_json(error_response.model_dump())
                        except Exception as send_error:
                            logger.error(f"Failed to send error response: {send_error}")

                except asyncio.TimeoutError:
                    logger.error(f"❌ Client #{client_id} TTS generation timeout")
                    error_response = ErrorResponse(
                        message="TTS generation timeout.", error_code="TTS_TIMEOUT"
                    )
                    try:
                        await websocket.send_json(error_response.model_dump())
                    except Exception as send_error:
                        logger.error(f"Failed to send timeout error: {send_error}")
                except Exception as tts_error:
                    logger.error(
                        f"❌ Client #{client_id} TTS processing error: {tts_error}"
                    )
                    error_response = ErrorResponse(
                        message=f"TTS processing error: {str(tts_error)}",
                        error_code="TTS_PROCESSING_ERROR",
                    )
                    try:
                        await websocket.send_json(error_response.model_dump())
                    except Exception as send_error:
                        logger.error(f"Failed to send processing error: {send_error}")
                finally:
                    if queue:
                        queue.task_done()

            except asyncio.TimeoutError:
                # Normal timeout, continue waiting
                continue
            except asyncio.CancelledError:
                logger.info(f"🛑 Client #{client_id} TTS worker cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Client #{client_id} TTS queue processing error: {e}")
                # Don't break the loop for non-critical errors
                await asyncio.sleep(0.1)  # Brief pause before retrying

    except Exception as e:
        logger.error(f"❌ Client #{client_id} TTS worker critical error: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        # Don't re-raise the exception to avoid crashing the WebSocket connection
    finally:
        logger.info(f"🧹 Client #{client_id} TTS worker cleanup completed")
        # Ensure queue is cleaned up even if there was an error
        if client_id in tts_queues:
            try:
                # Clear any remaining items in the queue
                while not tts_queues[client_id].empty():
                    try:
                        tts_queues[client_id].get_nowait()
                        tts_queues[client_id].task_done()
                    except:
                        break
            except Exception as cleanup_error:
                logger.error(f"Error during queue cleanup: {cleanup_error}")


async def add_tts_to_queue(client_id: str, text: str):
    """Add text to TTS queue with error handling"""
    try:
        if client_id in tts_queues:
            await tts_queues[client_id].put(text)
            logger.debug(f"Added TTS request to queue for client #{client_id}")
        else:
            logger.warning(f"TTS queue not found for client #{client_id}")
    except Exception as e:
        logger.error(f"Failed to add TTS to queue for client #{client_id}: {e}")


def cleanup_tts_queue(client_id: str):
    """Cleanup TTS queue with error handling"""
    try:
        if client_id in tts_queues:
            # Send shutdown signal
            try:
                tts_queues[client_id].put_nowait(None)
            except Exception as e:
                logger.error(f"Failed to send shutdown signal: {e}")

            # Remove from queues
            del tts_queues[client_id]
            logger.info(f"TTS queue cleaned up for client #{client_id}")
    except Exception as e:
        logger.error(f"Error during TTS queue cleanup for client #{client_id}: {e}")
