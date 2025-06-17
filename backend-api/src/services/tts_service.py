import requests
import ormsgpack
from typing import Literal
from pydantic import BaseModel, Field, conint, model_validator
from typing_extensions import Annotated
import base64


class ServeReferenceAudio(BaseModel):
    audio: bytes
    text: str

    @model_validator(mode="before")
    def decode_audio(cls, values):
        audio = values.get("audio")
        if (
            isinstance(audio, str) and len(audio) > 255
        ):  # Check if audio is a string (Base64)
            try:
                values["audio"] = base64.b64decode(audio)
            except Exception as e:
                # If the audio is not a valid base64 string, we will just ignore it and let the server handle it
                pass
        return values

    def __repr__(self) -> str:
        return f"ServeReferenceAudio(text={self.text!r}, audio_size={len(self.audio)})"


class ServeTTSRequest(BaseModel):
    text: str
    chunk_length: Annotated[int, conint(ge=100, le=300, strict=True)] = 200
    # Audio format
    format: Literal["wav", "pcm", "mp3"] = "wav"
    # References audios for in-context learning
    references: list[ServeReferenceAudio] = []
    # Reference id
    reference_id: str | None = None
    seed: int | None = None
    use_memory_cache: Literal["on", "off"] = "off"
    # Normalize text for en & zh, this increase stability for numbers
    normalize: bool = True
    # not usually used below
    streaming: bool = False
    max_new_tokens: int = 1024
    top_p: Annotated[float, Field(ge=0.1, le=1.0, strict=True)] = 0.8
    repetition_penalty: Annotated[float, Field(ge=0.9, le=2.0, strict=True)] = 1.1
    temperature: Annotated[float, Field(ge=0.1, le=1.0, strict=True)] = 0.8

    class Config:
        # Allow arbitrary types for pytorch related types
        arbitrary_types_allowed = True


class ChatWaifu_TTS(object):
    def __init__(self):
        pass

    def request_tts_stream(
        self, url: str, api_key: str, request: ServeTTSRequest
    ) -> bytes | None:
        """
        TTS 요청을 보내고 오디오 데이터를 바이트로 반환 (파일 저장 없음)

        Returns:
            bytes: 성공 시 오디오 바이트 데이터
            None: 실패 시
        """
        headers = {
            "content-type": "application/msgpack",
        }

        # API 키가 있는 경우 Authorization 헤더 추가
        if api_key:
            headers["authorization"] = f"Bearer {api_key}"

        try:
            # POST 요청 전송
            response = requests.post(
                url,
                data=ormsgpack.packb(request, option=ormsgpack.OPT_SERIALIZE_PYDANTIC),
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()

            if response.status_code == 200:
                print(f"✅ 음성 데이터 생성 성공 ({len(response.content)} bytes)")
                return response.content
            else:
                print(f"❌ 요청 실패: HTTP {response.status_code}")
                return None

        except requests.exceptions.ConnectionError:
            print("❌ 서버에 연결할 수 없습니다.")
            return None
        except requests.exceptions.Timeout:
            print("❌ 요청 시간 초과")
            return None
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return None

    def request_tts_base64(
        self, url: str, api_key: str, request: ServeTTSRequest
    ) -> str | None:
        """
        TTS 요청을 보내고 Base64 인코딩된 오디오 데이터 반환
        WebSocket 전송에 최적화

        Returns:
            str: 성공 시 Base64 인코딩된 오디오 데이터
            None: 실패 시
        """
        audio_bytes = self.request_tts_stream(url, api_key, request)
        if audio_bytes:
            return base64.b64encode(audio_bytes).decode("utf-8")
        return None

    # 기존 파일 저장 메서드는 호환성을 위해 유지
    def request_tts(
        self, url: str, api_key: str, output_filename: str, request: ServeTTSRequest
    ) -> bool:
        """기존 파일 저장 방식 (호환성을 위해 유지)"""
        audio_bytes = self.request_tts_stream(url, api_key, request)
        if audio_bytes:
            try:
                with open(output_filename, "wb") as f:
                    f.write(audio_bytes)
                print(f"✅ 음성 파일이 성공적으로 생성되었습니다: {output_filename}")
                return True
            except Exception as e:
                print(f"❌ 파일 저장 오류: {e}")
                return False
        return False
