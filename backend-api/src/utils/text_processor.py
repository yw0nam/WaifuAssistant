import re
from typing import List, NamedTuple, Optional, Tuple

# from src.core.logging import setup_logging

# logger = setup_logging("text_processor")


class ProcessedText(NamedTuple):
    """
    처리된 텍스트의 구조화된 결과를 담는 데이터 클래스입니다.
    """

    filtered_text: str
    emotion_tag: Optional[str]
    reasoning_text: Optional[str]


class TTSTextProcessor:
    """
    TTS 변환 전 텍스트를 최적화하기 위한 텍스트 처리기입니다.
    내적 추론, 감정 태그를 분리하고 불필요한 요소를 제거합니다.
    """

    def __init__(self):
        # 1. 내적 추론(Reasoning) 추출 패턴
        # <think>...</think> 태그 안의 텍스트를 캡처합니다.
        self.reasoning_pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL)

        # 2. 감정/톤/특수 마커 추출 패턴
        # 사용자가 제공한 모든 태그 목록을 기반으로 생성합니다.
        emotion_keywords = [
            "angry",
            "sad",
            "disdainful",
            "excited",
            "surprised",
            "satisfied",
            "unhappy",
            "anxious",
            "hysterical",
            "delighted",
            "scared",
            "worried",
            "indifferent",
            "upset",
            "impatient",
            "nervous",
            "guilty",
            "scornful",
            "frustrated",
            "depressed",
            "panicked",
            "furious",
            "empathetic",
            "embarrassed",
            "reluctant",
            "disgusted",
            "keen",
            "moved",
            "proud",
            "relaxed",
            "grateful",
            "confident",
            "interested",
            "curious",
            "confused",
            "joyful",
            "disapproving",
            "negative",
            "denying",
            "astonished",
            "serious",
            "sarcastic",
            "conciliative",
            "comforting",
            "sincere",
            "sneering",
            "hesitating",
            "yielding",
            "painful",
            "awkward",
            "amused",
            # Tone markers
            "in a hurry tone",
            "shouting",
            "screaming",
            "whispering",
            "soft tone",
            # Special markers
            "laughing",
            "chuckling",
            "sobbing",
            "crying loudly",
            "sighing",
            "panting",
            "groaning",
            "crowd laughing",
            "background laughter",
            "audience laughing",
        ]
        # | 문자로 키워드를 연결하여 정규표현식 패턴을 만듭니다.
        emotion_pattern_str = (
            r"\(((" + "|".join(re.escape(k) for k in emotion_keywords) + r"))\)"
        )
        self.emotion_pattern = re.compile(emotion_pattern_str, re.IGNORECASE)

        # 3. 제거할 기타 패턴
        # TTS에 불필요한 나머지 요소들을 제거합니다.
        self.cleanup_patterns = [
            re.compile(r"\*[^*]*\*"),  # *...* (행동 지시)
            re.compile(r"\[[^\]]*\]"),  # [...] (무대 지시)
            re.compile(r"<[^>]+>"),  # 남은 HTML 태그
        ]

        # 일본어 감지용 패턴 (기존 코드 활용)
        self.japanese_chars = re.compile(r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]")

    # TODO: Maybe this function can be removed, since it is handled in the streaming processor.
    #       But it is kept for now to avoid breaking changes.
    def _extract_reasoning(self, text: str) -> Tuple[str, Optional[str]]:
        """
        텍스트에서 <think> 태그와 그 내용을 추출합니다.

        Args:
            text: 원본 텍스트

        Returns:
            (태그가 제거된 텍스트, 추출된 내적 추론 텍스트)
        """
        match = self.reasoning_pattern.search(text)
        if match:
            reasoning_text = match.group(1).strip()
            # 원본 텍스트에서 해당 태그 부분을 제거합니다.
            cleaned_text = self.reasoning_pattern.sub("", text, count=1).strip()
            return cleaned_text, reasoning_text
        return text, None

    def _extract_emotion_tag(self, text: str) -> str | None:
        """
        텍스트에서 첫 번째로 발견되는 감정 태그를 추출합니다.

        Args:
            text: 내적 추론 태그가 제거된 텍스트

        Returns:
            (태그가 제거된 텍스트, 추출된 감정 태그)
        """
        match = self.emotion_pattern.search(text)
        if match:
            # 캡처된 그룹 (태그 전체 괄호 포함)을 반환합니다.
            emotion_tag = match.group(0)
            # 원본 텍스트에서 해당 태그 부분을 제거합니다.
            return emotion_tag
        return None

    def _clean_remaining_text(self, text: str) -> str:
        """
        남아있는 불필요한 패턴들을 제거하고 공백을 정리합니다.

        Args:
            text: 내적 추론 및 감정 태그가 제거된 텍스트

        Returns:
            최종적으로 정리된 TTS용 텍스트
        """
        cleaned_text = text
        for pattern in self.cleanup_patterns:
            cleaned_text = pattern.sub("", cleaned_text)

        # 여러 공백을 하나의 공백으로 변경하고, 앞뒤 공백을 제거합니다.
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        return cleaned_text

    def process_text(self, text: str) -> ProcessedText:
        """
        전체 텍스트 처리 파이프라인을 실행합니다.

        Args:
            text: LLM에서 받은 원본 텍스트

        Returns:
            ProcessedText 객체 (filtered_text, emotion_tag, reasoning_text)
        """
        if not text or not text.strip():
            return ProcessedText("", None, None)

        # 1단계: 내적 추론(Reasoning) 텍스트 추출
        text_after_reasoning, reasoning_text = self._extract_reasoning(text)

        # 2단계: 감정(Emotion) 태그 추출
        emotion_tag = self._extract_emotion_tag(text_after_reasoning)

        # 3단계: 나머지 불필요한 텍스트 정리
        filtered_text = self._clean_remaining_text(text_after_reasoning)

        # logger.debug(
        #     f"텍스트 처리 완료: 원본='{text[:50]}...' -> 필터링된 텍스트='{filtered_text[:50]}...', 감정='{emotion_tag}', 추론='{reasoning_text is not None}'"
        # )

        return ProcessedText(
            filtered_text=filtered_text,
            emotion_tag=emotion_tag,
            reasoning_text=reasoning_text,
        )

    # --- 보조 기능 (문장 분리 등, 필요 시 호출하여 사용) ---

    def _is_primarily_japanese(self, text: str) -> bool:
        """텍스트가 주로 일본어로 구성되었는지 확인합니다."""
        if not text:
            return False
        # Non-ASCII 문자를 기준으로 일본어 문자 비율을 계산
        non_ascii_chars = [c for c in text if ord(c) > 127]
        if not non_ascii_chars:
            return False
        japanese_matches = self.japanese_chars.findall(text)
        return len(japanese_matches) / len(non_ascii_chars) > 0.5

    def split_into_sentences(self, text: str) -> List[str]:
        """
        주어진 텍스트를 문장 단위로 분리합니다. (영어 및 일본어 지원)
        이 함수는 process_text()를 거친 filtered_text에 사용하는 것을 권장합니다.
        """
        if not text or not text.strip():
            return []

        if self._is_primarily_japanese(text):
            # 일본어 문장 분리 로직 (마침표, 물음표, 느낌표, 줄바꿈 등을 기준)
            sentences = re.split(r"(?<=[。！？\n])\s*", text)
        else:
            # 영어 문장 분리 로직 (마침표, 물음표, 느낌표, 줄바꿈 등을 기준)
            sentences = re.split(r"(?<=[.!?\n])\s*", text)

        # 비어있거나 공백만 있는 문장 제거 후 반환
        return [s.strip() for s in sentences if s and s.strip()]


if __name__ == "__main__":
    # --- 테스트 예제 ---
    processor = TTSTextProcessor()

    # 예제 1: 영어 텍스트 (감정 태그 + 내적 추론)
    text1 = "<think>I should check the user's mood first.</think> (curious) So, how are you feeling today? *smiles warmly*"
    processed1 = processor.process_text(text1)
    print("--- 예제 1 ---")
    print(f"원본 텍스트: '{text1}'")
    print(f"필터링된 텍스트: '{processed1.filtered_text}'")
    print(f"감정 태그: {processed1.emotion_tag}")
    print(f"내적 추론: '{processed1.reasoning_text}'")
    print("-" * 20)

    # 예제 2: 일본어 텍스트 (감정 태그 + 행동 지시)
    text2 = "(joyful)やったー！これで勝てる！ *ガッツポーズをする*"
    processed2 = processor.process_text(text2)
    print("--- 예제 2 ---")
    print(f"원본 텍스트: '{text2}'")
    print(f"필터링된 텍스트: '{processed2.filtered_text}'")
    print(f"감정 태그: {processed2.emotion_tag}")
    print(f"내적 추론: '{processed2.reasoning_text}'")
    print("-" * 20)

    # 예제 3: 내적 추론만 있는 경우
    text3 = "<think>This might be a complex query. I need to break it down.</think> Okay, let me analyze that for you."
    processed3 = processor.process_text(text3)
    print("--- 예제 3 ---")
    print(f"원본 텍스트: '{text3}'")
    print(f"필터링된 텍스트: '{processed3.filtered_text}'")
    print(f"감정 태그: {processed3.emotion_tag}")
    print(f"내적 추론: '{processed3.reasoning_text}'")
    print("-" * 20)

    # 예제 4: 톤 마커 및 웃음소리가 포함된 경우
    text4 = (
        "(whispering) I think I found a clue... (laughing) Ha,ha,ha, this is hilarious!"
    )
    processed4 = processor.process_text(text4)
    print("--- 예제 4 ---")
    print(f"원본 텍스트: '{text4}'")
    print(
        f"필터링된 텍스트: '{processed4.filtered_text}'"
    )  # "I think I found a clue... Ha,ha,ha, this is hilarious!"
    print(
        f"감정 태그: {processed4.emotion_tag}"
    )  # "(whispering)" - 첫 번째 태그만 추출
    print(f"내적 추론: '{processed4.reasoning_text}'")  # None
    print("-" * 20)

    # 예제 5: 처리 후 문장 분리 테스트
    final_text = processed1.filtered_text
    sentences = processor.split_into_sentences(final_text)
    print("--- 예제 5 (문장 분리) ---")
    print(f"분리된 문장: {sentences}")
    print("-" * 20)
