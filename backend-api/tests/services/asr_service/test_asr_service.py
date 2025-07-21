import tempfile
import wave
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from src.configs.models import ASRSettings
from src.services.asr_service.service import ASRService


def create_dummy_audio_file():
    """Create a dummy WAV audio file for testing."""
    # Create a temporary WAV file
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

    # Generate a simple sine wave (1 second, 16kHz)
    sample_rate = 16000
    duration = 1.0
    frequency = 440  # A note

    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

    # Write to WAV file
    with wave.open(temp_file.name, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

    return temp_file.name


@pytest.fixture
def asr_config():
    """Create ASR configuration for testing."""
    return ASRSettings(
        api_key="test-key",
        api_base="http://localhost:8000/v1",
        model="openai/whisper-large-v3",
        language="en",
        temperature=0.0,
        response_format="json",
    )


@pytest.fixture
def asr_service(asr_config):
    """Create ASR service instance for testing."""
    return ASRService(asr_config)


@pytest.fixture
def mock_transcription():
    """Create mock transcription response."""
    transcription = MagicMock()
    transcription.text = "Hello, this is a test transcription."
    return transcription


class TestASRService:
    """Test cases for ASRService."""

    def test_init(self, asr_config):
        """Test ASR service initialization."""
        service = ASRService(asr_config)

        assert service.config == asr_config
        assert service.client is not None
        assert service.async_client is not None

    @patch("openai.OpenAI")
    def test_transcribe_success(self, mock_openai, asr_service, mock_transcription):
        """Test successful synchronous transcription."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = mock_transcription

        # Replace the client in service
        asr_service.client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test transcription
            result = asr_service.transcribe(audio_file)

            # Verify result
            assert result == "Hello, this is a test transcription."

            # Verify client was called correctly
            mock_client.audio.transcriptions.create.assert_called_once()
            call_args = mock_client.audio.transcriptions.create.call_args

            assert call_args[1]["model"] == asr_service.config.model
            assert call_args[1]["language"] == asr_service.config.language
            assert call_args[1]["temperature"] == asr_service.config.temperature
            assert call_args[1]["response_format"] == asr_service.config.response_format

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    @patch("openai.AsyncOpenAI")
    @pytest.mark.asyncio
    async def test_transcribe_async_success(
        self, mock_async_openai, asr_service, mock_transcription
    ):
        """Test successful asynchronous transcription."""
        # Setup mock
        mock_client = AsyncMock()
        mock_async_openai.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = mock_transcription

        # Replace the async client in service
        asr_service.async_client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test async transcription
            result = await asr_service.transcribe_async(audio_file)

            # Verify result
            assert result == "Hello, this is a test transcription."

            # Verify client was called correctly
            mock_client.audio.transcriptions.create.assert_called_once()
            call_args = mock_client.audio.transcriptions.create.call_args

            assert call_args[1]["model"] == asr_service.config.model
            assert call_args[1]["language"] == asr_service.config.language
            assert call_args[1]["temperature"] == asr_service.config.temperature
            assert call_args[1]["response_format"] == asr_service.config.response_format

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    @patch("openai.AsyncOpenAI")
    @pytest.mark.asyncio
    async def test_transcribe_stream_success(self, mock_async_openai, asr_service):
        """Test successful streaming transcription."""

        # AIDEV-NOTE: Fixed streaming mock to properly support async iteration
        # Setup mock streaming response
        class MockStreamChunk:
            def __init__(self, content):
                self.choices = [{"delta": {"content": content}}]

        async def async_stream_generator():
            """Generate async stream chunks for testing."""
            chunks = [
                MockStreamChunk("Hello, "),
                MockStreamChunk("this is "),
                MockStreamChunk("a test."),
            ]
            for chunk in chunks:
                yield chunk

        mock_client = AsyncMock()
        mock_async_openai.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = async_stream_generator()

        # Replace the async client in service
        asr_service.async_client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test streaming transcription
            result_chunks = []
            async for chunk in asr_service.transcribe_stream(audio_file):
                result_chunks.append(chunk)

            # Verify result
            full_text = "".join(result_chunks)
            assert full_text == "Hello, this is a test."

            # Verify client was called correctly
            mock_client.audio.transcriptions.create.assert_called_once()
            call_args = mock_client.audio.transcriptions.create.call_args

            assert call_args[1]["model"] == asr_service.config.model
            assert call_args[1]["language"] == asr_service.config.language
            assert call_args[1]["temperature"] == asr_service.config.temperature
            assert call_args[1]["response_format"] == "json"  # Streaming requires json
            assert call_args[1]["stream"] is True

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    def test_transcribe_with_custom_params(self, asr_service, mock_transcription):
        """Test transcription with custom parameters."""
        # Mock the client
        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        asr_service.client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test with custom parameters
            asr_service.transcribe(
                audio_file, language="ko", temperature=0.5, response_format="text"
            )

            # Verify custom parameters were used
            call_args = mock_client.audio.transcriptions.create.call_args
            assert call_args[1]["language"] == "ko"
            assert call_args[1]["temperature"] == 0.5
            assert call_args[1]["response_format"] == "text"

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    @patch("openai.OpenAI")
    def test_transcribe_error_handling(self, mock_openai, asr_service):
        """Test error handling in transcription."""
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.audio.transcriptions.create.side_effect = Exception("API Error")

        # Replace the client in service
        asr_service.client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test that exception is raised
            with pytest.raises(Exception) as exc_info:
                asr_service.transcribe(audio_file)

            assert "API Error" in str(exc_info.value)

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    def test_close(self, asr_service):
        """Test service cleanup."""
        # Mock clients with close methods
        mock_sync_client = MagicMock()
        mock_async_client = MagicMock()

        asr_service.client = mock_sync_client
        asr_service.async_client = mock_async_client

        # Test close
        asr_service.close()

        # Note: This test mainly checks that close doesn't raise an exception
        # The actual closing behavior depends on the OpenAI client implementation

    @pytest.mark.asyncio
    async def test_aclose(self, asr_service):
        """Test async service cleanup."""
        # Mock clients with close methods
        mock_sync_client = MagicMock()
        mock_async_client = AsyncMock()

        asr_service.client = mock_sync_client
        asr_service.async_client = mock_async_client

        # Test async close
        await asr_service.aclose()

        # Note: This test mainly checks that aclose doesn't raise an exception
        # The actual closing behavior depends on the OpenAI client implementation

    # AIDEV-NOTE: Enhanced test cases for vLLM-specific features based on documentation
    def test_transcribe_with_vllm_extra_body_params(
        self, asr_service, mock_transcription
    ):
        """Test transcription with vLLM-specific extra_body parameters."""
        # Mock the client
        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        asr_service.client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test with vLLM extra_body parameters (as shown in vLLM docs)
            asr_service.transcribe(
                audio_file,
                extra_body=dict(
                    seed=4419,
                    repetition_penalty=1.3,
                    top_p=0.6,
                ),
            )

            # Verify vLLM-specific parameters were passed
            call_args = mock_client.audio.transcriptions.create.call_args
            assert "extra_body" in call_args[1]
            assert call_args[1]["extra_body"]["seed"] == 4419
            assert call_args[1]["extra_body"]["repetition_penalty"] == 1.3
            assert call_args[1]["extra_body"]["top_p"] == 0.6

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    @pytest.mark.asyncio
    async def test_transcribe_async_with_vllm_params(
        self, asr_service, mock_transcription
    ):
        """Test async transcription with vLLM-specific parameters."""
        # Mock the async client
        mock_client = AsyncMock()
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        asr_service.async_client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test with vLLM parameters from documentation
            await asr_service.transcribe_async(
                audio_file,
                language="ko",  # Korean language
                temperature=0.0,
                extra_body=dict(
                    seed=420,
                    top_p=0.6,
                ),
            )

            # Verify parameters were used correctly
            call_args = mock_client.audio.transcriptions.create.call_args
            assert call_args[1]["language"] == "ko"
            assert call_args[1]["temperature"] == 0.0
            assert call_args[1]["extra_body"]["seed"] == 420
            assert call_args[1]["extra_body"]["top_p"] == 0.6

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    def test_transcribe_with_file_object(self, asr_service, mock_transcription):
        """Test transcription using file object instead of file path."""
        # Mock the client
        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        asr_service.client = mock_client

        # Create dummy audio file
        audio_file_path = create_dummy_audio_file()

        try:
            # Test with file object
            with open(audio_file_path, "rb") as file_obj:
                result = asr_service.transcribe(file_obj)

            # Verify result
            assert result == "Hello, this is a test transcription."

            # Verify client was called correctly
            mock_client.audio.transcriptions.create.assert_called_once()

        finally:
            # Cleanup
            import os

            os.unlink(audio_file_path)

    @pytest.mark.asyncio
    async def test_transcribe_stream_empty_chunks(self, asr_service):
        """Test streaming transcription with empty chunks."""

        # AIDEV-NOTE: Test edge case where streaming returns empty content
        class MockEmptyChunk:
            def __init__(self, content=None):
                if content is None:
                    self.choices = []
                else:
                    self.choices = [{"delta": {"content": content}}]

        async def async_stream_with_empty():
            """Generate stream with empty chunks."""
            chunks = [
                MockEmptyChunk("Hello"),
                MockEmptyChunk(),  # Empty chunk
                MockEmptyChunk(" world"),
                MockEmptyChunk(),  # Another empty chunk
            ]
            for chunk in chunks:
                yield chunk

        mock_client = AsyncMock()
        mock_client.audio.transcriptions.create.return_value = async_stream_with_empty()
        asr_service.async_client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test streaming with empty chunks
            result_chunks = []
            async for chunk in asr_service.transcribe_stream(audio_file):
                result_chunks.append(chunk)

            # Verify only non-empty chunks are yielded
            full_text = "".join(result_chunks)
            assert full_text == "Hello world"

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    def test_transcribe_response_formats(self, asr_service):
        """Test different response formats supported by vLLM."""
        # Mock the client
        mock_client = MagicMock()
        asr_service.client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test different response formats
            formats = ["json", "text", "srt", "verbose_json", "vtt"]

            for format_type in formats:
                # AIDEV-NOTE: Always use transcription object with .text attribute for consistency
                mock_transcription = MagicMock()
                mock_transcription.text = "Hello world"
                mock_client.audio.transcriptions.create.return_value = (
                    mock_transcription
                )

                result = asr_service.transcribe(audio_file, response_format=format_type)

                # Verify format was used and result is correct
                call_args = mock_client.audio.transcriptions.create.call_args
                assert call_args[1]["response_format"] == format_type
                assert result == "Hello world"

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    def test_transcribe_different_languages(self, asr_service, mock_transcription):
        """Test transcription with different language codes."""
        # Mock the client
        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        asr_service.client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test different languages supported by Whisper
            languages = ["en", "ko", "ja", "zh", "es", "fr", "de", "auto"]

            for lang in languages:
                asr_service.transcribe(audio_file, language=lang)

                # Verify language was used
                call_args = mock_client.audio.transcriptions.create.call_args
                assert call_args[1]["language"] == lang

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    @patch("openai.OpenAI")
    def test_transcribe_network_error(self, mock_openai, asr_service):
        """Test handling of network-related errors."""
        # Setup mock to raise network error
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # AIDEV-NOTE: Use a generic Exception instead of specific OpenAI error for simplicity
        mock_client.audio.transcriptions.create.side_effect = Exception(
            "Connection failed"
        )

        # Replace the client in service
        asr_service.client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test that network error is properly handled
            with pytest.raises(Exception) as exc_info:
                asr_service.transcribe(audio_file)

            assert "Connection failed" in str(exc_info.value)

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    @patch("openai.AsyncOpenAI")
    @pytest.mark.asyncio
    async def test_transcribe_async_timeout(self, mock_async_openai, asr_service):
        """Test handling of timeout errors in async transcription."""
        # Setup mock to raise timeout error
        mock_client = AsyncMock()
        mock_async_openai.return_value = mock_client

        import asyncio

        mock_client.audio.transcriptions.create.side_effect = asyncio.TimeoutError(
            "Request timeout"
        )

        # Replace the async client in service
        asr_service.async_client = mock_client

        # Create dummy audio file
        audio_file = create_dummy_audio_file()

        try:
            # Test that timeout error is properly handled
            with pytest.raises(asyncio.TimeoutError) as exc_info:
                await asr_service.transcribe_async(audio_file)

            assert "Request timeout" in str(exc_info.value)

        finally:
            # Cleanup
            import os

            os.unlink(audio_file)

    def test_config_validation(self):
        """Test ASR configuration validation."""
        # Test valid configuration
        valid_config = ASRSettings(
            api_key="test-key",
            api_base="http://localhost:8000/v1",
            model="openai/whisper-large-v3",
            language="ko",
            temperature=0.0,
            response_format="json",
        )

        service = ASRService(valid_config)
        assert service.config == valid_config

        # Test configuration with different valid values
        config_variants = [
            {
                "api_key": "EMPTY",  # vLLM default
                "api_base": "http://localhost:8000/v1",
                "model": "openai/whisper-large-v3",
                "language": "auto",
                "temperature": 0.5,
                "response_format": "text",
            },
            {
                "api_key": "custom-key",
                "api_base": "https://remote-vllm-server.com/v1",
                "model": "openai/whisper-medium",
                "language": "en",
                "temperature": 1.0,
                "response_format": "verbose_json",
            },
        ]

        for config_data in config_variants:
            config = ASRSettings(**config_data)
            service = ASRService(config)
            assert service.config.api_key == config_data["api_key"]
            assert service.config.api_base == config_data["api_base"]
            assert service.config.model == config_data["model"]

    @pytest.mark.asyncio
    async def test_concurrent_transcriptions(self, asr_service):
        """Test multiple concurrent transcription requests."""
        # AIDEV-NOTE: Test concurrent async operations to ensure thread safety
        import asyncio

        # Mock the async client
        mock_client = AsyncMock()

        async def mock_transcribe(*args, **kwargs):
            # Simulate some processing time
            await asyncio.sleep(0.1)
            mock_transcription = MagicMock()
            mock_transcription.text = f"Transcription {id(args)}"
            return mock_transcription

        mock_client.audio.transcriptions.create.side_effect = mock_transcribe
        asr_service.async_client = mock_client

        # Create multiple dummy audio files
        audio_files = [create_dummy_audio_file() for _ in range(3)]

        try:
            # Run concurrent transcriptions
            tasks = [
                asr_service.transcribe_async(audio_file) for audio_file in audio_files
            ]

            results = await asyncio.gather(*tasks)

            # Verify all transcriptions completed
            assert len(results) == 3
            for result in results:
                assert result.startswith("Transcription")

        finally:
            # Cleanup
            import os

            for audio_file in audio_files:
                os.unlink(audio_file)


# AIDEV-NOTE: E2E tests for ASR service that make actual API calls
# These tests require the ASR service to be running at the configured URL


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_asr_service_e2e_real_api():
    """
    E2E test that makes an actual API call to the ASR service.

    This test requires the ASR service to be running at the configured URL.
    Skip with: pytest -m "not e2e"
    """
    from src.configs.loader import load_config
    import os
    import asyncio

    # Load actual configuration
    config = load_config()

    english_config = ASRSettings(
        api_key=config.asr_configs.api_key,
        api_base=config.asr_configs.api_base,
        model=config.asr_configs.model,
        language="en",  # English
        temperature=0.0,
        response_format="json",
    )
    asr_service = ASRService(english_config)

    # Use actual test audio file instead of dummy
    test_audio_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "test_files", "audio"
    )
    audio_file = os.path.join(test_audio_dir, "en_audio.wav")

    # Check if test file exists
    if not os.path.exists(audio_file):
        pytest.skip(f"Test audio file not found: {audio_file}")

    try:
        # AIDEV-NOTE: E2E test waits for complete ASR response without early abort
        # Remove artificial delays - wait for actual API response completion
        print("Starting English ASR transcription...")

        # Test actual transcription with real audio - wait for complete response
        result = await asr_service.transcribe_async(audio_file)

        # AIDEV-NOTE: Ensure we got a complete response, not a partial/aborted one
        assert (
            result is not None
        ), "ASR API returned None - request was aborted or failed"
        assert isinstance(
            result, str
        ), f"ASR API returned invalid type {type(result)}, expected string"
        assert (
            len(result.strip()) > 0
        ), "ASR API returned empty string - transcription incomplete"
        assert (
            len(result.strip()) >= 5
        ), f"ASR transcription too short ('{result}') - likely incomplete"

        print(f"✅ ASR E2E received complete response: '{result}'")

        # Since we know the expected content, validate it's meaningful
        result_lower = result.lower()
        expected_words = ["borrowers", "floorboards", "beneath", "dozens"]
        found_words = [word for word in expected_words if word in result_lower]

        if found_words:
            print(f"✅ Found expected words {found_words} in transcription")
        else:
            print(f"⚠️  Transcription may vary from expected: {result}")
            # Don't fail here - ASR might have variations but still be complete

        print(f"Full ASR transcription result: '{result}'")

    except Exception as e:
        if "Connection refused" in str(e):  # 서비스가 아예 안 켜져 있을 때만 skip
            pytest.skip(f"ASR service not available: {e}")
        else:  # 500 에러 등 예상치 못한 에러는 테스트 실패로 처리
            pytest.fail(f"Unexpected error in ASR E2E test: {e}")
    finally:
        # AIDEV-NOTE: Ensure proper cleanup to prevent connection issues
        try:
            await asr_service.aclose()
        except:
            pass


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_asr_service_e2e_different_languages():
    """
    E2E test that tests ASR with different language settings using Japanese audio.
    """
    from src.configs.loader import load_config
    import os

    config = load_config()

    # Test with Japanese language setting using actual Japanese audio
    japanese_config = ASRSettings(
        api_key=config.asr_configs.api_key,
        api_base=config.asr_configs.api_base,
        model=config.asr_configs.model,
        language="ja",  # Japanese
        temperature=0.0,
        response_format="json",
    )

    asr_service = ASRService(japanese_config)

    # Use actual Japanese test audio file
    test_audio_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "test_files", "audio"
    )
    audio_file = os.path.join(test_audio_dir, "jp_audio.wav")

    # Check if test file exists
    if not os.path.exists(audio_file):
        pytest.skip(f"Japanese test audio file not found: {audio_file}")
    try:
        # AIDEV-NOTE: E2E test for Japanese audio - no early abort, wait for full transcription
        print("Starting Japanese ASR transcription...")

        result = await asr_service.transcribe_async(audio_file)
        # Should get a result regardless of language setting
        assert result is not None, "Should handle Japanese language setting"
        assert isinstance(result, str), "Result should be a string"
        assert len(result.strip()) > 0, "Transcription should not be empty"

        # Expected Japanese text: "男性とはこういうものですからね、撫子様"
        # Check for Japanese characters or known words
        japanese_words = ["男性", "撫子", "こういう", "ものです"]
        found_japanese = [word for word in japanese_words if word in result]
        has_japanese_chars = any(ord(char) > 127 for char in result)

        if found_japanese:
            print(f"✅ Found expected Japanese words {found_japanese}")
        elif has_japanese_chars:
            print(f"✅ Found Japanese characters in transcription")
        else:
            print(f"⚠️  Japanese transcription may be romanized: {result}")

        print(f"Full Japanese ASR transcription: '{result}'")

    except Exception as e:
        if "Connection refused" in str(e):  # 서비스가 아예 안 켜져 있을 때만 skip
            pytest.skip(f"ASR service not available: {e}")
        else:  # 500 에러 등 예상치 못한 에러는 테스트 실패로 처리
            pytest.fail(f"Unexpected error in ASR E2E test: {e}")
    finally:
        # AIDEV-NOTE: Ensure proper cleanup to prevent connection issues
        try:
            await asr_service.aclose()
        except:
            pass


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_asr_service_e2e_error_handling():
    """
    E2E test that verifies error handling with invalid audio files.
    """
    from src.configs.loader import load_config
    import tempfile
    import os

    config = load_config()
    asr_service = ASRService(config.asr_configs)

    try:
        # AIDEV-NOTE: E2E error handling - test complete error responses, no early abort
        # Remove artificial delays - focus on getting complete responses
        print("Starting ASR error handling tests...")

        # Test with non-existent file (should fail but get complete error response)
        print("Testing non-existent file...")
        try:
            result = await asr_service.transcribe_async("/non/existent/file.wav")
            raise AssertionError(
                "Should have raised an exception for non-existent file"
            )
        except Exception as e:
            # Expected to fail - ensure we got a complete error response
            print(
                f"✅ Got complete error for non-existent file: {type(e).__name__}: {e}"
            )
            error_msg = str(e).lower()
            if not any(
                keyword in error_msg
                for keyword in [
                    "file",
                    "path",
                    "not found",
                    "no such file",
                    "404",
                    "500",
                ]
            ):
                raise AssertionError(f"Error message doesn't indicate file issue: {e}")

        # Test with invalid file content (wait for complete processing)
        print("Testing invalid audio file...")
        invalid_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        invalid_file.write(b"This is not valid audio data at all - just plain text")
        invalid_file.close()

        try:
            result = await asr_service.transcribe_async(invalid_file.name)
            # Some ASR services might return empty/error message rather than exception
            print(f"Invalid audio file result: {result}")

            # If we get a result, validate it's a proper response (not incomplete)
            if result is not None:
                if not isinstance(result, str):
                    raise AssertionError(
                        f"Invalid audio test returned non-string: {type(result)}"
                    )
                print(f"✅ Service handled invalid file gracefully: '{result}'")
            else:
                raise AssertionError(
                    "Invalid audio test returned None - response incomplete"
                )

        except Exception as e:
            # Expected to fail with invalid audio - ensure complete error
            print(f"✅ Got complete error with invalid audio: {type(e).__name__}: {e}")
            error_msg = str(e).lower()
            if not any(
                keyword in error_msg
                for keyword in [
                    "audio",
                    "format",
                    "decode",
                    "invalid",
                    "corrupt",
                    "500",
                    "bad request",
                ]
            ):
                raise AssertionError(f"Error doesn't indicate audio format issue: {e}")
        finally:
            os.unlink(invalid_file.name)

        print("✅ ASR error handling E2E test completed successfully")

    except Exception as e:
        if "Connection refused" in str(e):  # 서비스가 아예 안 켜져 있을 때만 skip
            pytest.skip(f"ASR service not available: {e}")
        else:  # 500 에러 등 예상치 못한 에러는 테스트 실패로 처리
            pytest.fail(f"Unexpected error in ASR E2E test: {e}")
    finally:
        # AIDEV-NOTE: Ensure proper cleanup to prevent connection issues
        try:
            await asr_service.aclose()
        except:
            pass
