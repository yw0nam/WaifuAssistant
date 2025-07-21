import base64
import json
import tempfile
import wave
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest

from src.websocket.handlers.asr_handler import ASRHandler
from src.websocket.models import ASRTranscribeRequest, ResponseType


def create_test_audio_data():
    """Create test audio data in base64 format."""
    # Create a temporary WAV file
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

    # Generate a simple sine wave (0.5 second, 16kHz)
    sample_rate = 16000
    duration = 0.5
    frequency = 440  # A note

    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

    # Write to WAV file
    with wave.open(temp_file.name, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

    # Read and encode as base64
    with open(temp_file.name, "rb") as f:
        audio_bytes = f.read()

    # Cleanup temp file
    import os

    os.unlink(temp_file.name)

    return base64.b64encode(audio_bytes).decode("utf-8")


class TestASRIntegration:
    """Test ASR WebSocket integration."""

    @pytest.fixture
    def asr_request(self):
        """Create ASR transcription request."""
        return ASRTranscribeRequest(
            audio_data=create_test_audio_data(),
            format="wav",
            language="ko",
            streaming=False,
        )

    @pytest.fixture
    def streaming_asr_request(self):
        """Create streaming ASR transcription request."""
        return ASRTranscribeRequest(
            audio_data=create_test_audio_data(),
            format="wav",
            language="en",
            streaming=True,
        )

    @patch("src.websocket.handlers.asr_handler.ASRService")
    @pytest.mark.asyncio
    async def test_asr_handler_regular_transcription(
        self, mock_asr_service, asr_request
    ):
        """Test regular ASR transcription through handler."""
        # Setup mock
        mock_service_instance = AsyncMock()
        mock_asr_service.return_value = mock_service_instance
        mock_service_instance.transcribe_async.return_value = (
            "안녕하세요, 테스트 전사 결과입니다."
        )

        # Create handler
        handler = ASRHandler()
        handler.asr_service = mock_service_instance

        # Process request
        responses = []
        async for response in handler.handle_transcribe_request(asr_request):
            responses.append(response)

        # Verify responses
        assert len(responses) == 1
        response_data = responses[0]

        # Parse JSON response
        if isinstance(response_data, dict):
            parsed_response = response_data
        else:
            parsed_response = json.loads(response_data)

        assert parsed_response["type"] == ResponseType.ASR_RESULT
        assert parsed_response["text"] == "안녕하세요, 테스트 전사 결과입니다."
        assert parsed_response["language"] == "ko"
        assert "processing_time" in parsed_response

        # Verify service was called correctly
        mock_service_instance.transcribe_async.assert_called_once()
        call_args = mock_service_instance.transcribe_async.call_args
        assert call_args[1]["language"] == "ko"

    @patch("src.websocket.handlers.asr_handler.ASRService")
    @pytest.mark.asyncio
    async def test_asr_handler_streaming_transcription(
        self, mock_asr_service, streaming_asr_request
    ):
        """Test streaming ASR transcription through handler."""

        # Setup mock service instance
        mock_service_instance = AsyncMock()
        mock_asr_service.return_value = mock_service_instance

        # AIDEV-NOTE: Create proper async generator mock for streaming
        async def mock_transcribe_stream(*args, **kwargs):
            chunks = ["Hello, ", "this is ", "a streaming ", "test."]
            for chunk in chunks:
                yield chunk

        mock_service_instance.transcribe_stream = mock_transcribe_stream

        # Create handler
        handler = ASRHandler()
        handler.asr_service = mock_service_instance

        # Process request
        responses = []
        async for response in handler.handle_transcribe_request(streaming_asr_request):
            responses.append(response)

        # Verify responses (4 streaming chunks + 1 final)
        assert len(responses) == 5

        # Check streaming responses
        for i in range(4):
            response_data = responses[i]
            if isinstance(response_data, dict):
                parsed_response = response_data
            else:
                parsed_response = json.loads(response_data)

            assert parsed_response["type"] == ResponseType.ASR_STREAMING
            assert parsed_response["is_final"] is False

        # Check final response
        final_response_data = responses[4]
        if isinstance(final_response_data, dict):
            final_parsed = final_response_data
        else:
            final_parsed = json.loads(final_response_data)

        assert final_parsed["type"] == ResponseType.ASR_STREAMING
        assert final_parsed["is_final"] is True
        assert final_parsed["text"] == ""

    @patch("src.websocket.handlers.asr_handler.ASRService")
    @pytest.mark.asyncio
    async def test_asr_handler_invalid_audio_data(self, mock_asr_service):
        """Test ASR handler with invalid base64 audio data."""
        # Create request with invalid base64 data
        invalid_request = ASRTranscribeRequest(
            audio_data="invalid_base64_data!!!",
            format="wav",
            language="ko",
            streaming=False,
        )

        mock_service_instance = AsyncMock()
        mock_asr_service.return_value = mock_service_instance

        # Create handler
        handler = ASRHandler()
        handler.asr_service = mock_service_instance

        # Process request
        responses = []
        async for response in handler.handle_transcribe_request(invalid_request):
            responses.append(response)

        # Verify error response
        assert len(responses) == 1
        response_data = responses[0]

        if isinstance(response_data, dict):
            parsed_response = response_data
        else:
            parsed_response = json.loads(response_data)

        assert parsed_response["type"] == ResponseType.ERROR
        assert parsed_response["error_code"] == "INVALID_AUDIO_DATA"
        assert "Invalid base64 audio data" in parsed_response["message"]

        # Verify service was not called
        mock_service_instance.transcribe_async.assert_not_called()

    def test_asr_request_model_validation(self):
        """Test ASR request model validation."""
        # Valid request
        valid_request = ASRTranscribeRequest(
            audio_data=create_test_audio_data(),
            format="wav",
            language="ko",
        )
        assert valid_request.type == "asr_transcribe"
        assert valid_request.streaming is False
        assert valid_request.language == "ko"

        # Test with optional parameters
        full_request = ASRTranscribeRequest(
            audio_data=create_test_audio_data(),
            format="mp3",
            language="en",
            temperature=0.5,
            response_format="text",
            streaming=True,
        )
        assert full_request.format == "mp3"
        assert full_request.temperature == 0.5
        assert full_request.response_format == "text"
        assert full_request.streaming is True

    @pytest.mark.asyncio
    async def test_asr_handler_cleanup(self):
        """Test ASR handler cleanup."""
        # Create handler with mock service
        handler = ASRHandler()
        mock_service = AsyncMock()
        handler.asr_service = mock_service

        # Test cleanup
        await handler.close()

        # Verify service cleanup was called
        mock_service.aclose.assert_called_once()

    @patch("src.websocket.handlers.asr_handler.ASRService")
    @pytest.mark.asyncio
    async def test_asr_handler_service_error(self, mock_asr_service, asr_request):
        """Test ASR handler when service raises error."""
        # Setup mock to raise error
        mock_service_instance = AsyncMock()
        mock_asr_service.return_value = mock_service_instance
        mock_service_instance.transcribe_async.side_effect = Exception("Service error")

        # Create handler
        handler = ASRHandler()
        handler.asr_service = mock_service_instance

        # Process request
        responses = []
        async for response in handler.handle_transcribe_request(asr_request):
            responses.append(response)

        # Verify error response
        assert len(responses) == 1
        response_data = responses[0]

        if isinstance(response_data, dict):
            parsed_response = response_data
        else:
            parsed_response = json.loads(response_data)

        assert parsed_response["type"] == ResponseType.ERROR
        assert parsed_response["error_code"] == "REGULAR_TRANSCRIPTION_ERROR"
        assert "Regular transcription failed" in parsed_response["message"]
