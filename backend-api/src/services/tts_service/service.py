import requests
import ormsgpack
from typing import Literal, Optional
from pydantic import BaseModel, Field, conint, model_validator
from typing_extensions import Annotated
import base64
from src.utils.text_processor import TTSTextProcessor, ProcessedText
from src.core.logging import setup_logging

logger = setup_logging("tts_service")


class ServeReferenceAudio(BaseModel):
    audio: bytes
    text: str

    @model_validator(mode="before")
    def decode_audio(cls, values):
        audio = values.get("audio")
        if isinstance(audio, str):
            try:
                values["audio"] = base64.b64decode(audio)
            except Exception:
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
    seed: int | None = 1004
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


class ChatWaifu_TTS:
    """
    외부 TTS API와 통신하여 텍스트로부터 음성을 생성하는 서비스입니다.
    텍스트 처리부터 API 요청까지 모든 과정을 캡슐화합니다.
    """

    def __init__(self, url: str, api_key: Optional[str] = None):
        self.url = url
        self.api_key = api_key
        # TTSTextProcessor 인스턴스를 내부적으로 소유합니다.
        self.text_processor = TTSTextProcessor()
        self.session = requests.Session()
        headers = {"content-type": "application/msgpack"}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        self.session.headers.update(headers)

    def _request_tts_stream(self, request_payload: ServeTTSRequest) -> Optional[bytes]:
        """
        [내부 메서드] TTS 요청을 보내고 오디오 데이터를 바이트로 반환합니다.

        Args:
            request_payload: API에 전송할 Pydantic 요청 모델

        Returns:
            성공 시 오디오 바이트 데이터, 실패 시 None
        """
        try:
            response = self.session.post(
                self.url,
                data=ormsgpack.packb(
                    request_payload, option=ormsgpack.OPT_SERIALIZE_PYDANTIC
                ),
                timeout=30,
            )
            response.raise_for_status()
            logger.info(f"음성 데이터 생성 성공 ({len(response.content)} bytes)")
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS API 요청 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"TTS 처리 중 예상치 못한 오류: {e}")
            return None

    def generate_speech(
        self,
        raw_text: str,
        reference_id: Optional[str] = None,
        output_format: Literal["bytes", "base64", "file"] = "bytes",
        output_filename: Optional[str] = "output.wav",
    ) -> Optional[bytes | str | bool]:
        """
        [메인 메서드] 원본 텍스트를 받아 음성을 생성하고 지정된 포맷으로 반환합니다.

        Args:
            raw_text: LLM으로부터 받은 원본 텍스트
            reference_id: 사용할 음성 레퍼런스 ID
            output_format: 반환할 오디오 데이터 형식 ('bytes', 'base64', 'file')
            output_filename: 'file' 포맷일 경우 저장할 파일명

        Returns:
            - "bytes": 오디오 데이터 (bytes)
            - "base64": Base64 인코딩된 문자열 (str)
            - "file": 저장 성공 여부 (bool)
            - 처리할 텍스트가 없거나 실패 시 None
        """
        # 1. TTSTextProcessor를 사용해 텍스트 처리 및 정보 추출
        processed_data: ProcessedText = self.text_processor.process_text(raw_text)

        # 2. TTS로 처리할 텍스트가 있는지 확인
        tts_text = processed_data.filtered_text
        if not tts_text:
            logger.info("TTS로 처리할 내용이 없어 스킵합니다.")
            return None

        # 3. API 요청 페이로드 생성
        request_payload = ServeTTSRequest(text=tts_text, reference_id=reference_id)

        # 4. API 호출하여 오디오 데이터 획득
        audio_bytes = self._request_tts_stream(request_payload)

        if not audio_bytes:
            return None

        # 5. 요청된 포맷에 맞춰 결과 반환
        if output_format == "base64":
            return base64.b64encode(audio_bytes).decode("utf-8")
        elif output_format == "file":
            try:
                with open(output_filename, "wb") as f:
                    f.write(audio_bytes)
                logger.info(f"음성 파일이 성공적으로 생성되었습니다: {output_filename}")
                return True
            except Exception as e:
                logger.error(f"파일 저장 오류: {e}")
                return False
        else:  # "bytes"가 기본값
            return audio_bytes


# --- 사용 예제 ---
if __name__ == "__main__":
    # TTS 서비스 URL (실제 URL로 변경 필요)
    TTS_API_URL = "http://localhost:8080/v1/tts"

    # 1. 서비스 인스턴스 생성
    tts_service = ChatWaifu_TTS(url=TTS_API_URL)

    # 2. LLM에서 받은 것과 유사한 원본 텍스트
    llm_output_text = "<think>User seems happy. I should respond cheerfully.</think> (delighted) That's wonderful news! I'm so happy for you!"

    # 3. 서비스의 메인 메서드 하나만 호출하여 오디오 데이터 받기
    print("--- 'bytes' 포맷으로 오디오 생성 시도 ---")
    audio_data = tts_service.generate_speech(
        raw_text=llm_output_text,
        reference_id="ナツメ",
        output_format="bytes",
    )

    if audio_data:
        print(f"성공! 오디오 데이터 수신 (크기: {len(audio_data)} bytes)")
    else:
        print("실패.")

    print("\n--- 'file' 포맷으로 오디오 생성 시도 ---")
    file_audio = tts_service.generate_speech(
        raw_text=llm_output_text,
        output_format="file",
        output_filename="output.wav",
        reference_id="ナツメ",
    )

    if file_audio:
        print(f"성공! 파일로 저장되었습니다: output.wav")
    else:
        print("실패.")
