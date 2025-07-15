import pytest

from src.utils.text_chunker import TextChunkProcessor, process_stream_pipeline
from src.utils.text_processor import ProcessedText, TTSTextProcessor


class TestTTSTextProcessor:
    @pytest.fixture
    def processor(self):
        return TTSTextProcessor()

    def test_empty_input(self, processor: TTSTextProcessor):
        """Return empty ProcessedText when input is empty string."""
        result = processor.process_text("")
        assert isinstance(result, ProcessedText)
        assert result.filtered_text == ""
        assert result.emotion_tag is None

    def test_whitespace_input(self, processor: TTSTextProcessor):
        """Return empty ProcessedText when input is only whitespace."""
        result = processor.process_text("   \n  ")
        assert result.filtered_text == ""
        assert result.emotion_tag is None

    def test_single_emotion_tag(self, processor: TTSTextProcessor):
        """Extract the first emotion tag and retain it in filtered_text."""
        text = "Hello (joyful) world."
        result = processor.process_text(text)
        assert result.emotion_tag.lower() == "joyful"
        assert "(joyful)" in result.filtered_text
        assert "Hello" in result.filtered_text

    def test_multiple_emotion_tags(self, processor: TTSTextProcessor):
        """Only the first emotion tag should be captured; later tags remain in filtered_text."""
        text = "Start (sad) mid (happy) end."
        result = processor.process_text(text)
        assert result.emotion_tag.lower() == "sad"
        assert "(sad)" in result.filtered_text
        assert "(happy)" in result.filtered_text

    def test_cleanup_brackets_and_stars(self, processor: TTSTextProcessor):
        """Remove bracketed and starred content and collapse extra whitespace."""
        text = "This is [remove] cleaned *text* example."
        result = processor.process_text(text)
        assert "[remove]" not in result.filtered_text
        assert "*text*" not in result.filtered_text
        assert result.filtered_text == "This is cleaned example."


class TestProcessStreamPipeline:
    @pytest.fixture
    def chunk_processor(self):
        return TextChunkProcessor()

    @pytest.fixture
    def text_processor(self):
        return TTSTextProcessor()

    def test_pipeline_simple(self, chunk_processor, text_processor):
        """Process a simple single-chunk stream and return one ProcessedText."""
        stream = ["Hello world."]
        results = list(process_stream_pipeline(stream, chunk_processor, text_processor))
        assert len(results) == 1
        assert isinstance(results[0], ProcessedText)
        assert results[0].filtered_text.strip() == "Hello world."
        assert results[0].emotion_tag is None

    def test_pipeline_chunked(self, chunk_processor, text_processor):
        """Process a multi-chunk sentence split across two stream entries."""
        stream = ["This is", " a test."]
        results = list(process_stream_pipeline(stream, chunk_processor, text_processor))
        assert len(results) == 1
        assert results[0].filtered_text == "This is a test."

    def test_pipeline_with_reasoning_and_tool(self, chunk_processor, text_processor):
        """Filter out reasoning and tool calls across multiple stream chunks."""
        stream = [
            "Keep this. <think>secret</think> And this.",
            " Next {'type': 'tool_call', 'id': 'x', 'args': {}} end.",
        ]
        results = list(process_stream_pipeline(stream, chunk_processor, text_processor))
        texts = [r.filtered_text for r in results]
        assert any("Keep this." in t for t in texts)
        assert any("And this." in t for t in texts)
        assert all("tool_call" not in t for t in texts)
