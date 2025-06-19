import asyncio
from typing import Dict, List, Optional, NamedTuple
from fastapi import WebSocket
from src.services.tts_service.service import ChatWaifu_TTS, ServeTTSRequest
from src.configs import settings
from src.core.logging import setup_logging
from .models import AudioResponse, ErrorResponse, TTSInterruptedResponse

logger = setup_logging("tts_worker")


class TTSRequest(NamedTuple):
    """TTS request containing text and optional reference_id"""

    text: str
    reference_id: Optional[str] = None


# 클라이언트별 TTS 처리 큐
tts_queues: Dict[str, asyncio.Queue] = {}
# 클라이언트별 중단 플래그
tts_interrupt_flags: Dict[str, bool] = {}


async def tts_worker(
    client_id: str, websocket: WebSocket, chat_waifu_tts: ChatWaifu_TTS
):
    """TTS processing background worker with robust error handling and sentence processing"""
    queue = None
    try:
        logger.info(f"🎵 Client #{client_id} TTS worker starting...")

        # Initialize TTS queue and interrupt flag safely
        if client_id not in tts_queues:
            tts_queues[client_id] = asyncio.Queue()
            logger.info(f"📝 Client #{client_id} TTS queue created")

        if client_id not in tts_interrupt_flags:
            tts_interrupt_flags[client_id] = False

        queue = tts_queues[client_id]
        logger.info(f"✅ Client #{client_id} TTS worker initialized successfully")

        while True:
            try:
                # Wait for TTS requests from queue with timeout
                logger.debug(f"⏳ Client #{client_id} waiting for TTS request...")
                tts_request_item = await asyncio.wait_for(queue.get(), timeout=1.0)

                if tts_request_item is None:  # Shutdown signal
                    logger.info(
                        f"🛑 Client #{client_id} TTS worker shutdown signal received"
                    )
                    break

                # Extract text and reference_id from request
                if isinstance(tts_request_item, TTSRequest):
                    tts_text = tts_request_item.text
                    reference_id = tts_request_item.reference_id
                else:
                    # Backward compatibility for plain text
                    tts_text = tts_request_item
                    reference_id = None

                logger.info(
                    f"📨 Client #{client_id} received TTS request: {tts_text[:50]}... (reference_id: {reference_id})"
                )

                # Check if TTS should be interrupted before processing (not after receiving)
                # This allows new TTS requests but interrupts ongoing processing
                if tts_interrupt_flags.get(client_id, False):
                    logger.info(
                        f"🚫 Client #{client_id} TTS interrupted before processing"
                    )
                    tts_interrupt_flags[client_id] = False  # Reset flag after handling
                    continue

                try:
                    logger.info(f"🔊 Client #{client_id} starting TTS processing...")

                    # Validate TTS service is available
                    if not chat_waifu_tts:
                        logger.error(
                            f"❌ Client #{client_id} TTS service not available"
                        )
                        raise Exception("TTS service not initialized")

                    # Process text for TTS (clean and split into sentences)
                    if not chat_waifu_tts.should_process_for_tts(tts_text):
                        logger.info(
                            f"⚠️ Client #{client_id} text not suitable for TTS, skipping"
                        )
                        continue

                    sentences = chat_waifu_tts.process_text_for_tts(tts_text)
                    if not sentences:
                        logger.info(
                            f"⚠️ Client #{client_id} no sentences to process for TTS"
                        )
                        continue

                    logger.info(
                        f"📝 Client #{client_id} processing {len(sentences)} sentences for TTS"
                    )

                    # Process each sentence separately
                    for i, sentence in enumerate(sentences):
                        # Check for interruption before processing each sentence
                        if tts_interrupt_flags.get(client_id, False):
                            logger.info(
                                f"🚫 Client #{client_id} TTS interrupted during sentence {i+1}/{len(sentences)}"
                            )
                            tts_interrupt_flags[client_id] = False
                            break

                        logger.debug(
                            f"🎤 Client #{client_id} processing sentence {i+1}/{len(sentences)}: {sentence}"
                        )

                        tts_request = ServeTTSRequest(
                            text=sentence,
                            format="wav",
                            reference_id=reference_id,  # Use user-provided reference_id
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

                        # Check for interruption after TTS generation
                        if tts_interrupt_flags.get(client_id, False):
                            logger.info(
                                f"🚫 Client #{client_id} TTS interrupted after generating sentence {i+1}"
                            )
                            tts_interrupt_flags[client_id] = False
                            break

                        if audio_base64:
                            # Send audio data via WebSocket
                            audio_response = AudioResponse(
                                data=audio_base64,
                                format="wav",
                                text=sentence,
                                duration=None,
                            )
                            await websocket.send_json(audio_response.model_dump())
                            logger.info(
                                f"✅ Client #{client_id} TTS audio sent for sentence {i+1}/{len(sentences)}"
                            )
                        else:
                            logger.warning(
                                f"⚠️ Client #{client_id} TTS generation failed for sentence {i+1} - no audio data"
                            )

                    logger.info(
                        f"✅ Client #{client_id} completed TTS processing for all sentences"
                    )

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


async def add_tts_to_queue(
    client_id: str, text: str, reference_id: Optional[str] = None
):
    """Add text and reference_id to TTS queue with error handling"""
    try:
        if client_id in tts_queues:
            tts_request = TTSRequest(text=text, reference_id=reference_id)
            await tts_queues[client_id].put(tts_request)
            logger.debug(
                f"Added TTS request to queue for client #{client_id} (reference_id: {reference_id})"
            )
        else:
            logger.warning(f"TTS queue not found for client #{client_id}")
    except Exception as e:
        logger.error(f"Failed to add TTS to queue for client #{client_id}: {e}")


async def interrupt_tts(client_id: str) -> int:
    """
    Interrupt ongoing TTS processing and clear queue

    Returns:
        Number of items cleared from queue
    """
    try:
        interrupted_count = 0

        # Set interrupt flag
        tts_interrupt_flags[client_id] = True
        logger.info(f"🚫 Client #{client_id} TTS interrupt flag set")

        # Clear TTS queue
        if client_id in tts_queues:
            queue = tts_queues[client_id]
            while not queue.empty():
                try:
                    queue.get_nowait()
                    queue.task_done()
                    interrupted_count += 1
                except asyncio.QueueEmpty:
                    break
            logger.info(
                f"🧹 Client #{client_id} cleared {interrupted_count} items from TTS queue"
            )

        return interrupted_count
    except Exception as e:
        logger.error(f"Error during TTS interrupt for client #{client_id}: {e}")
        return 0


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

        # Clean up interrupt flag
        if client_id in tts_interrupt_flags:
            del tts_interrupt_flags[client_id]
            logger.info(f"TTS interrupt flag cleaned up for client #{client_id}")

    except Exception as e:
        logger.error(f"Error during TTS queue cleanup for client #{client_id}: {e}")
