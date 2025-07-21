import asyncio
import logging
from typing import BinaryIO, Optional, Union

from openai import AsyncOpenAI, OpenAI

from ...configs.models import ASRSettings

# AIDEV-NOTE: ASR service implementation follows vLLM OpenAI-compatible API patterns
# Compatible with remote vLLM servers running Whisper models for speech recognition
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

__doc__ = """
This module contains the implementation of the ASRService class, which provides functionality for automatic speech recognition using vLLM with OpenAI-compatible API.

Classes:
- ASRService: A class that encapsulates the logic for audio transcription using remote vLLM server.

Functions:
- transcribe: Performs synchronous audio transcription
- transcribe_async: Performs asynchronous audio transcription
- transcribe_stream: Performs streaming audio transcription

Example usage:
    asr_config = ASRSettings(...)
    asr_service = ASRService(asr_config)
    
    # Sync transcription
    result = asr_service.transcribe(audio_file_path)
    
    # Async transcription
    result = await asr_service.transcribe_async(audio_file_path)
    
    # Streaming transcription
    async for chunk in asr_service.transcribe_stream(audio_file_path):
        print(chunk, end="", flush=True)
"""


class ASRService:
    """ASR service using vLLM with OpenAI-compatible API for speech recognition."""

    def __init__(self, config: ASRSettings):
        """
        Initialize ASR service with configuration.

        Args:
            config: ASRSettings configuration object
        """
        self.config = config

        # Initialize sync OpenAI client
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_base,
        )

        # Initialize async OpenAI client
        self.async_client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_base,
        )

        # AIDEV-NOTE: vLLM server should be running with: vllm serve openai/whisper-large-v3
        logger.info(f"ASRService initialized with model: {self.config.model}")
        logger.info(f"ASR API base: {self.config.api_base}")

    def transcribe(
        self,
        audio_file: Union[str, BinaryIO],
        language: Optional[str] = None,
        temperature: Optional[float] = None,
        response_format: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Perform synchronous audio transcription.

        Args:
            audio_file: Path to audio file or file-like object
            language: Language code (optional, uses config default)
            temperature: Sampling temperature (optional, uses config default)
            response_format: Response format (optional, uses config default)
            **kwargs: Additional parameters for the transcription API

        Returns:
            Transcribed text
        """
        try:
            # Use provided parameters or fall back to config defaults
            lang = language or self.config.language
            temp = temperature if temperature is not None else self.config.temperature
            resp_format = response_format or self.config.response_format

            logger.debug(
                f"Starting transcription with language: {lang}, temperature: {temp}"
            )

            # Handle file path vs file object
            if isinstance(audio_file, str):
                with open(audio_file, "rb") as f:
                    transcription = self.client.audio.transcriptions.create(
                        file=f,
                        model=self.config.model,
                        language=lang,
                        response_format=resp_format,
                        temperature=temp,
                        **kwargs,
                    )
            else:
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.config.model,
                    language=lang,
                    response_format=resp_format,
                    temperature=temp,
                    **kwargs,
                )

            result = transcription.text
            logger.info(
                f"Transcription completed successfully. Length: {len(result)} characters"
            )
            return result

        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise

    async def transcribe_async(
        self,
        audio_file: Union[str, BinaryIO],
        language: Optional[str] = None,
        temperature: Optional[float] = None,
        response_format: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Perform asynchronous audio transcription.

        Args:
            audio_file: Path to audio file or file-like object
            language: Language code (optional, uses config default)
            temperature: Sampling temperature (optional, uses config default)
            response_format: Response format (optional, uses config default)
            **kwargs: Additional parameters for the transcription API

        Returns:
            Transcribed text
        """
        try:
            # Use provided parameters or fall back to config defaults
            lang = language or self.config.language
            temp = temperature if temperature is not None else self.config.temperature
            resp_format = response_format or self.config.response_format

            logger.debug(
                f"Starting async transcription with language: {lang}, temperature: {temp}"
            )

            # Handle file path vs file object
            if isinstance(audio_file, str):
                with open(audio_file, "rb") as f:
                    transcription = await self.async_client.audio.transcriptions.create(
                        file=f,
                        model=self.config.model,
                        language=lang,
                        response_format=resp_format,
                        temperature=temp,
                        **kwargs,
                    )
            else:
                transcription = await self.async_client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.config.model,
                    language=lang,
                    response_format=resp_format,
                    temperature=temp,
                    **kwargs,
                )

            result = transcription.text
            logger.info(
                f"Async transcription completed successfully. Length: {len(result)} characters"
            )
            return result

        except Exception as e:
            logger.error(f"Error during async transcription: {str(e)}")
            raise

    async def transcribe_stream(
        self,
        audio_file: Union[str, BinaryIO],
        language: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ):
        """
        Perform streaming audio transcription.

        Args:
            audio_file: Path to audio file or file-like object
            language: Language code (optional, uses config default)
            temperature: Sampling temperature (optional, uses config default)
            **kwargs: Additional parameters for the transcription API

        Yields:
            Transcription chunks as they become available
        """
        try:
            # Use provided parameters or fall back to config defaults
            lang = language or self.config.language
            temp = temperature if temperature is not None else self.config.temperature

            logger.debug(
                f"Starting streaming transcription with language: {lang}, temperature: {temp}"
            )

            # Handle file path vs file object
            if isinstance(audio_file, str):
                with open(audio_file, "rb") as f:
                    transcription = await self.async_client.audio.transcriptions.create(
                        file=f,
                        model=self.config.model,
                        language=lang,
                        response_format="json",  # Streaming requires json format
                        temperature=temp,
                        stream=True,
                        **kwargs,
                    )
            else:
                transcription = await self.async_client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.config.model,
                    language=lang,
                    response_format="json",  # Streaming requires json format
                    temperature=temp,
                    stream=True,
                    **kwargs,
                )

            async for chunk in transcription:
                if chunk.choices:
                    content = chunk.choices[0].get("delta", {}).get("content")
                    if content:
                        yield content

            logger.info("Streaming transcription completed successfully")

        except Exception as e:
            logger.error(f"Error during streaming transcription: {str(e)}")
            raise

    def close(self):
        """Close the ASR service clients."""
        try:
            if hasattr(self.client, "close"):
                self.client.close()
            if hasattr(self.async_client, "close"):
                asyncio.create_task(self.async_client.close())
            logger.info("ASR service clients closed")
        except Exception as e:
            logger.warning(f"Error closing ASR service clients: {str(e)}")

    async def aclose(self):
        """Asynchronously close the ASR service clients."""
        try:
            if hasattr(self.client, "close"):
                self.client.close()
            if hasattr(self.async_client, "close"):
                await self.async_client.close()
            logger.info("ASR service clients closed asynchronously")
        except Exception as e:
            logger.warning(f"Error closing ASR service clients: {str(e)}")
