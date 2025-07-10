import re
from typing import List, NamedTuple, Optional, Tuple
from src.configs.prompts import EMOTION_KEYWORDS


class ProcessedText(NamedTuple):
    """처리된 텍스트의 구조화된 결과 (reasoning_text 필드 제거)"""

    filtered_text: str
    emotion_tag: Optional[str]
    # reasoning_text 필드를 제거하여 구조를 더 간단하게 만들었어요.


class ProcessedText(NamedTuple):
    filtered_text: str
    emotion_tag: Optional[str]


class TTSTextProcessor:
    def __init__(self):
        # 감정 태그의 괄호 안 내용만 추출하도록 수정
        emotion_pattern_str = (
            r"\(((" + "|".join(re.escape(k) for k in EMOTION_KEYWORDS) + r"))\)"
        )
        self.emotion_pattern = re.compile(emotion_pattern_str, re.IGNORECASE)

        self.cleanup_patterns = [
            re.compile(r"\*[^*]*\*"),
            re.compile(r"\[[^\]]*\]"),
        ]

    def process_text(self, text: str) -> ProcessedText:
        """주인님께서 말씀하신, 문장 하나를 최종 가공하는 함수입니다."""
        if not text or not text.strip():
            return ProcessedText("", None)

        text_to_process = text
        emotion_tag = None

        # 1. 감정 태그 추출 및 제거
        emotion_match = self.emotion_pattern.search(text_to_process)
        if emotion_match:
            # group(1)을 사용해 괄호 안의 키워드만 가져옵니다.
            emotion_tag = emotion_match.group(1)
            # 원본 텍스트에서 태그 전체(group(0))를 제거합니다.
            # text_to_process = text_to_process.replace(emotion_match.group(0), "", 1)

        # 2. 나머지 텍스트 정리 (예: *행동 지시*)
        filtered_text = self._clean_text(text_to_process)

        return ProcessedText(filtered_text, emotion_tag)

    def _clean_text(self, text: str) -> str:
        """불필요한 패턴 제거 (기존과 동일)"""
        cleaned = text
        for pattern in self.cleanup_patterns:
            cleaned = pattern.sub("", cleaned)
        return re.sub(r"\s+", " ", cleaned).strip()


if __name__ == "__main__":
    # --- 테스트 예제 ---
    processor = TTSTextProcessor()

    # 예제 1: 영어 텍스트 (감정 태그)
    text1 = "I should check the user's mood first. (curious) So, how are you feeling today? *smiles warmly*"
    processed1 = processor.process_text(text1)
    print("--- 예제 1 ---")
    print(f"원본 텍스트: '{text1}'")
    print(f"필터링된 텍스트: '{processed1.filtered_text}'")
    print(f"감정 태그: {processed1.emotion_tag}")
    print("-" * 20)

    # 예제 2: 일본어 텍스트 (감정 태그 + 행동 지시)
    text2 = "(joyful)やったー！これで勝てる！ *ガッツポーズをする*"
    processed2 = processor.process_text(text2)
    print("--- 예제 2 ---")
    print(f"원본 텍스트: '{text2}'")
    print(f"필터링된 텍스트: '{processed2.filtered_text}'")
    print(f"감정 태그: {processed2.emotion_tag}")
    print("-" * 20)

    # TODO: 여러개의 감정태그를 처리할수 있도록 바꿔야할수도?
    # 예제 3: 톤 마커 및 웃음소리가 포함된 경우
    text3 = (
        "(whispering) I think I found a clue... (laughing) Ha,ha,ha, this is hilarious!"
    )
    processed3 = processor.process_text(text3)
    print("--- 예제 3 ---")
    print(f"원본 텍스트: '{text3}'")
    print(f"필터링된 텍스트: '{processed3.filtered_text}'")
    print(f"감정 태그: {processed3.emotion_tag}")
    print("-" * 20)
