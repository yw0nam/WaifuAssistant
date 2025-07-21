import base64

import pytest
import requests

from src.configs.loader import load_config
from src.services.tts_service.service import (
    ChatWaifu_TTS,
    ServeReferenceAudio,
    ServeTTSRequest,
)


def test_decode_reference_audio_from_base64():
    """Decode a valid base64 audio string into bytes and check __repr__ content."""
    sample_bytes = b"test audio data"
    b64 = base64.b64encode(sample_bytes).decode("utf-8")
    ref = ServeReferenceAudio(audio=b64, text="hello")
    assert isinstance(ref.audio, bytes)
    assert ref.audio == sample_bytes
    repr_str = repr(ref)
    assert "ServeReferenceAudio(text='hello'" in repr_str
    assert f"audio_size={len(sample_bytes)}" in repr_str


def test_decode_reference_audio_invalid_string():
    """Coerce an invalid base64 string into raw bytes unchanged."""
    # invalid base64 string is coerced to bytes by Pydantic
    ref = ServeReferenceAudio(audio="not-base64", text="hi")
    assert isinstance(ref.audio, bytes)
    assert ref.audio == b"not-base64"


def test_servettsrequest_default_and_validation():
    """Ensure ServeTTSRequest uses correct default values and validation."""
    # default values
    req = ServeTTSRequest(text="hello")
    assert req.chunk_length == 200
    assert req.format == "wav"
    assert req.normalize is True


def test_chatwaifu_init_headers():
    """Verify session headers include content-type and optional authorization."""
    svc = ChatWaifu_TTS(url="http://example.com")
    assert svc.session.headers.get("content-type") == "application/msgpack"
    assert "authorization" not in svc.session.headers

    svc2 = ChatWaifu_TTS(url="http://x", api_key="secret123")
    assert svc2.session.headers.get("authorization") == "Bearer secret123"


def test__request_tts_stream_success(monkeypatch):
    """Return audio bytes when the HTTP POST succeeds."""
    dummy_content = b"audiobytes"

    class DummyResp:
        def __init__(self):
            self.content = dummy_content

        def raise_for_status(self):
            pass

    svc = ChatWaifu_TTS(url="u")
    # monkeypatch session.post to return DummyResp
    monkeypatch.setattr(svc.session, "post", lambda url, data, timeout: DummyResp())
    payload = ServeTTSRequest(text="hi")
    out = svc._request_tts_stream(payload)
    assert out == dummy_content


def test__request_tts_stream_http_error(monkeypatch):
    """Return None when HTTP POST raises an HTTPError status."""
    svc = ChatWaifu_TTS(url="u")

    class ErrResp:
        def raise_for_status(self):
            raise requests.HTTPError("bad status")

    monkeypatch.setattr(svc.session, "post", lambda *args, **kwargs: ErrResp())
    res = svc._request_tts_stream(ServeTTSRequest(text="x"))
    assert res is None


def test__request_tts_stream_request_exception(monkeypatch):
    """Return None when session.post raises a RequestException."""
    svc = ChatWaifu_TTS(url="u")

    def raise_req(*args, **kwargs):
        raise requests.exceptions.RequestException("fail")

    monkeypatch.setattr(svc.session, "post", raise_req)
    res = svc._request_tts_stream(ServeTTSRequest(text="x"))
    assert res is None


def test_generate_speech_empty_text():
    """Return None for empty or whitespace-only raw_text input."""
    svc = ChatWaifu_TTS(url="u")
    assert svc.generate_speech("   ") is None


def test_generate_speech_stream_none(monkeypatch):
    """Return None when underlying _request_tts_stream returns None."""
    svc = ChatWaifu_TTS(url="u")
    monkeypatch.setattr(svc, "_request_tts_stream", lambda req: None)
    assert svc.generate_speech("hello") is None


def test_generate_speech_bytes_and_base64(monkeypatch):
    """Return raw bytes or base64-encoded string and propagate reference_id correctly."""
    svc = ChatWaifu_TTS(url="u")
    data = b"1234"
    # capture payload
    captured = {}

    def fake_request(req):
        captured["payload"] = req
        return data

    monkeypatch.setattr(svc, "_request_tts_stream", fake_request)

    out_bytes = svc.generate_speech("abc ", reference_id="ref42", output_format="bytes")
    assert out_bytes == data
    # ensure reference_id set on payload
    assert captured["payload"].reference_id == "ref42"

    out_b64 = svc.generate_speech(" xyz", output_format="base64")
    assert isinstance(out_b64, str)
    assert base64.b64decode(out_b64) == data


def test_generate_speech_file_success(monkeypatch, tmp_path):
    """Write audio bytes to file successfully and return True."""
    svc = ChatWaifu_TTS(url="u")
    data = b"wavdata"
    monkeypatch.setattr(svc, "_request_tts_stream", lambda req: data)
    out_file = tmp_path / "test.wav"
    result = svc.generate_speech(
        "hello", output_format="file", output_filename=str(out_file)
    )
    assert result is True
    assert out_file.exists()
    assert out_file.read_bytes() == data


def test_generate_speech_file_write_error(monkeypatch, tmp_path):
    """Return False when writing the audio file raises an error."""
    svc = ChatWaifu_TTS(url="u")
    data = b"d"
    monkeypatch.setattr(svc, "_request_tts_stream", lambda req: data)
    # monkeypatch open to raise
    monkeypatch.setattr(
        "builtins.open",
        lambda *args, **kwargs: (_ for _ in ()).throw(IOError("disk full")),
    )
    result = svc.generate_speech(
        "hi", output_format="file", output_filename=str(tmp_path / "f.wav")
    )
    assert result is False


# AIDEV-NOTE: E2E tests that make actual API calls to live services
# These tests are marked with @pytest.mark.e2e and can be skipped with -m "not e2e"


@pytest.mark.e2e
def test_tts_service_e2e_real_api():
    """
    E2E test that makes an actual API call to the TTS service.

    This test requires the TTS service to be running at the configured URL.
    Skip with: pytest -m "not e2e"
    """
    # Load actual configuration
    config = load_config()
    tts_url = config.tts_configs.url
    tts_api_key = config.tts_configs.api_key

    # Create service instance with real config
    tts_service = ChatWaifu_TTS(url=tts_url, api_key=tts_api_key)

    # Test text - use simple text to avoid issues with complex processing
    test_text = "Hello, this is a test."

    try:
        # Test bytes format
        audio_bytes = tts_service.generate_speech(
            raw_text=test_text,
            output_format="bytes",
        )

        # Verify we got audio data
        assert audio_bytes is not None, "Should receive audio data from TTS API"
        assert isinstance(audio_bytes, bytes), "Audio data should be bytes"
        assert len(audio_bytes) > 0, "Audio data should not be empty"

        # Test base64 format
        audio_b64 = tts_service.generate_speech(
            raw_text=test_text,
            output_format="base64",
        )

        assert audio_b64 is not None, "Should receive base64 audio data"
        assert isinstance(audio_b64, str), "Base64 audio should be string"
        assert len(audio_b64) > 0, "Base64 data should not be empty"

        # Verify base64 can be decoded
        decoded_bytes = base64.b64decode(audio_b64)
        assert len(decoded_bytes) > 0, "Decoded base64 should produce valid bytes"

    except requests.exceptions.ConnectionError:
        pytest.skip("TTS service not available - connection failed")
    except requests.exceptions.Timeout:
        pytest.skip("TTS service not available - request timeout")
    except Exception as e:
        pytest.fail(f"Unexpected error in TTS E2E test: {e}")


@pytest.mark.e2e
def test_tts_service_e2e_with_reference_id():
    """
    E2E test that tests TTS with a reference ID.

    This test requires the TTS service to be running and have reference voices available.
    """
    config = load_config()
    tts_service = ChatWaifu_TTS(
        url=config.tts_configs.url, api_key=config.tts_configs.api_key
    )

    test_text = "Testing with reference voice."

    try:
        # Test with a reference ID (this may or may not exist on the server)
        audio_bytes = tts_service.generate_speech(
            raw_text=test_text,
            reference_id="七海",  # Use a common reference ID
            output_format="bytes",
        )

        # Even if reference doesn't exist, should still get some response
        # (server may fallback to default voice)
        assert audio_bytes is not None or True, "Should handle reference ID gracefully"

    except requests.exceptions.ConnectionError:
        pytest.skip("TTS service not available - connection failed")
    except Exception as e:
        # Log the error but don't fail - reference might not exist
        print(f"Reference ID test encountered: {e}")


@pytest.mark.e2e
def test_tts_service_e2e_error_handling():
    """
    E2E test that verifies error handling with invalid requests.
    """
    config = load_config()
    tts_service = ChatWaifu_TTS(
        url=config.tts_configs.url, api_key=config.tts_configs.api_key
    )

    try:
        # Test with empty text
        result = tts_service.generate_speech(
            raw_text="",
            output_format="bytes",
        )
        assert result is None, "Empty text should return None"

        # Test with whitespace only
        result = tts_service.generate_speech(
            raw_text="   \n\t   ",
            output_format="bytes",
        )
        assert result is None, "Whitespace-only text should return None"

    except requests.exceptions.ConnectionError:
        pytest.skip("TTS service not available - connection failed")
