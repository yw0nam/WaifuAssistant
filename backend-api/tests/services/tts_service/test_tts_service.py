import base64

import requests

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
