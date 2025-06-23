import re
from typing import List, Optional
from src.core.logging import setup_logging

# TTSTextProcessor와 ProcessedText는 외부에서 사용되므로 그대로 둡니다.
from src.utils.text_processor import TTSTextProcessor, ProcessedText

logger = setup_logging("streaming_processor")


class StreamingTTSProcessor:
    """
    텍스트 청크를 실시간으로 처리하여 TTS에 적합한 완성된 문장을 감지하고 반환합니다.
    내적 추론 필터링은 스트리밍 방식으로 처리하며, 문장 경계 감지에 중점을 둡니다.
    """

    def __init__(
        self,
        reasoning_start_tag: str = "<think>",
        reasoning_end_tag: str = "</think>",
    ):
        # 스트리밍 처리에 필요한 상태 변수들
        self._buffer = ""
        self._inside_reasoning = False

        # 내적 추론 태그 패턴
        # split을 사용하기 위해 시작 태그와 끝 태그를 캡처 그룹으로 묶습니다.
        self._reasoning_pattern = re.compile(
            f"({re.escape(reasoning_start_tag)}|{re.escape(reasoning_end_tag)})",
            re.IGNORECASE,
        )

        # 문장 경계 감지 패턴 (일본어 및 서양권 언어 모두 지원)
        # 줄바꿈도 중요한 문장 경계로 취급합니다.
        self._sentence_boundaries = re.compile(r"(?<=[.!?。！？\n])\s*")

        logger.debug(
            f"StreamingTTSProcessor 초기화 완료. 추론 태그: '{reasoning_start_tag}', '{reasoning_end_tag}'"
        )

    def _filter_reasoning_stream(self, chunk: str) -> str:
        """
        스트리밍 상태를 유지하며 내적 추론 태그를 필터링합니다.
        re.split을 사용하여 더 안정적으로 처리합니다.

        Args:
            chunk: 새로 들어온 텍스트 청크

        Returns:
            내적 추론 부분이 필터링된 텍스트 청크
        """
        parts = self._reasoning_pattern.split(chunk)
        filtered_chunk = ""

        for part in parts:
            if not part:
                continue

            # part가 시작 태그와 일치하는지 확인 (대소문자 무시)
            if part.lower() == "<think>":
                self._inside_reasoning = True
            # part가 종료 태그와 일치하는지 확인
            elif part.lower() == "</think>":
                self._inside_reasoning = False
            # 태그가 아닌 일반 텍스트 부분
            elif not self._inside_reasoning:
                filtered_chunk += part

        return filtered_chunk

    def add_chunk(self, chunk: str) -> List[str]:
        """
        새로운 텍스트 청크를 추가하고, 감지된 완성된 문장들을 반환합니다.

        Args:
            chunk: LLM 스트림에서 온 새로운 텍스트 청크

        Returns:
            TTS 처리가 필요한 완성된 문장(들)의 리스트.
            (이후 이 리스트를 TTSTextProcessor로 처리해야 합니다.)
        """
        if not chunk:
            return []

        # 1. 실시간 내적 추론 필터링
        filtered_chunk = self._filter_reasoning_stream(chunk)
        if not filtered_chunk:
            return []

        # 2. 필터링된 청크를 내부 버퍼에 추가
        self._buffer += filtered_chunk

        # 3. 버퍼에서 완성된 문장 추출
        # 문장 경계 패턴으로 버퍼를 나눔. 마지막 부분은 완성되지 않았을 수 있으므로 보관.
        sentences = self._sentence_boundaries.split(self._buffer)

        # 마지막 요소는 다음 청크를 위해 버퍼에 남겨둠 (문장 경계로 끝나지 않았을 경우)
        self._buffer = sentences.pop()

        # 비어있지 않은 문장들만 필터링하여 반환
        complete_sentences = [s.strip() for s in sentences if s and s.strip()]

        if complete_sentences:
            logger.info(
                f"{len(complete_sentences)}개의 완성된 문장 추출: {complete_sentences}"
            )

        return complete_sentences

    def finalize(self) -> List[str]:
        """
        스트리밍이 끝났을 때, 버퍼에 남아있는 모든 텍스트를 문장으로 처리하여 반환합니다.

        Returns:
            남아있는 마지막 문장(들)의 리스트.
        """
        remaining_text = self._buffer.strip()
        self.reset()  # 상태 초기화

        if not remaining_text:
            return []

        logger.info(f"마지막 남은 텍스트 처리: '{remaining_text[:50]}...'")
        return [remaining_text]

    def reset(self):
        """프로세서의 상태를 초기화하여 새 대화를 시작할 수 있도록 합니다."""
        self._buffer = ""
        self._inside_reasoning = False
        logger.debug("StreamingTTSProcessor 상태 초기화됨.")


# --- 사용 예제 ---
if __name__ == "__main__":
    # 1. 프로세서 인스턴스 생성
    streaming_processor = StreamingTTSProcessor()
    text_processor = TTSTextProcessor()  # 내용 처리용 프로세서는 별도로 관리

    llm_stream = [
        "Okay, let me think about that. <think>The user is asking about a complex topic.",
        """{'type': 'tool_call', 'tool_name': 'search_documents', 'args': '{"index": "example_index", "body": {"query": {"query_string": {"query": "example_query"}}}}', '}}}""",
        " I need to check my knowledge base first.</think> (curious) That's an interesting question!\n",
        "Give me a moment to process. It might take some time.",
        " (laughing) Just kidding!",
    ]

    print("--- 스트리밍 처리 시작 ---")
    print("입력 스트림:", llm_stream)
    all_processed_results: List[ProcessedText] = []

    # 2. 스트림 청크별 처리
    for chunk in llm_stream:
        # StreamingTTSProcessor는 완성된 '원본' 문장을 반환
        complete_sentences = streaming_processor.add_chunk(chunk)

        # 완성된 문장이 있을 경우, TTSTextProcessor로 내용을 처리
        if complete_sentences:
            print(f"\n[Stream] 완성된 문장 감지: {complete_sentences}")
            for sentence in complete_sentences:
                # 각 문장을 내용 처리기에 전달하여 구조화된 데이터 획득
                processed_data = text_processor.process_text(sentence)
                all_processed_results.append(processed_data)
                print(f"  [TTS] 처리 결과: {processed_data}")

    # 3. 스트림 종료 후 남은 데이터 처리
    final_sentences = streaming_processor.finalize()
    if final_sentences:
        print(f"\n[Stream] 마지막 문장 감지: {final_sentences}")
        for sentence in final_sentences:
            processed_data = text_processor.process_text(sentence)
            all_processed_results.append(processed_data)
            print(f"  [TTS] 처리 결과: {processed_data}")

    print("\n--- 최종 처리 결과 ---")
    for result in all_processed_results:
        # 이 result.filtered_text를 TTS 엔진으로 보낼 수 있습니다.
        print(f"TTS 전송 텍스트: '{result.filtered_text}', 감정: {result.emotion_tag}")
