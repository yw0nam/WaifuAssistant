import pytest

from src.utils.text_chunker import TextChunkProcessor


class TestTextChunkProcessor:
    @pytest.fixture
    def processor(self):
        """Returns a new TextChunkProcessor for each test."""
        return TextChunkProcessor()

    def test_add_chunk_simple_sentence(self, processor: TextChunkProcessor):
        """Verify that a chunk containing complete sentences yields each full sentence."""
        sentences = processor.add_chunk("Hello world. This is a test.")
        assert sentences == ["Hello world.", "This is a test."]
        assert processor._buffer == ""

    def test_add_chunk_incomplete_sentence(self, processor: TextChunkProcessor):
        """Ensure incomplete trailing fragments are buffered and only full sentences are returned."""
        sentences = processor.add_chunk("Hello world. This is a")
        assert sentences == ["Hello world."]
        assert processor._buffer == "This is a"

    def test_add_chunk_with_reasoning(self, processor: TextChunkProcessor):
        """Filter out text enclosed in reasoning tags when processing a single chunk."""
        chunk = "This is public. <think>This is private.</think> This is also public."
        sentences = processor.add_chunk(chunk)
        assert sentences == ["This is public.", "This is also public."]

    def test_add_chunk_with_split_reasoning_tags(self, processor: TextChunkProcessor):
        """Handle reasoning start and end tags that span across multiple chunks correctly."""
        sentences = processor.add_chunk("This is public. <think>This is")
        assert sentences == ["This is public."]
        sentences = processor.add_chunk(" private.</think> This is also public.")
        assert sentences == ["This is also public."]
        final_sentences = processor.finalize()
        assert final_sentences == []

    def test_add_chunk_with_tool_call(self, processor: TextChunkProcessor):
        """Remove embedded tool-call JSON patterns from the streaming buffer."""
        chunk = "Here is some text. {'type': 'tool_call', 'id': '123', 'args': {}} and more text."
        sentences = processor.add_chunk(chunk)
        assert sentences == ["Here is some text.", "and more text."]

    def test_finalize_with_remaining_text(self, processor: TextChunkProcessor):
        """Return any leftover text from finalize when buffer contains an incomplete sentence."""
        processor.add_chunk("This is an incomplete sentence")
        remaining = processor.finalize()
        assert remaining == ["This is an incomplete sentence"]
        assert processor._buffer == ""

    def test_finalize_on_empty_buffer(self, processor: TextChunkProcessor):
        """Ensure finalize returns empty list when there is no buffered text."""
        remaining = processor.finalize()
        assert remaining == []

    def test_reset(self, processor: TextChunkProcessor):
        """Verify that reset clears internal buffer and resets reasoning flag."""
        processor.add_chunk("Hello. <think>reasoning")
        processor.reset()
        assert processor._buffer == ""
        assert not processor._inside_reasoning
        sentences = processor.add_chunk("New sentence.")
        assert sentences == ["New sentence."]

    def test_multiple_sentence_boundaries(self, processor: TextChunkProcessor):
        """Detect sentence endings for a variety of punctuation marks correctly."""
        text = "First sentence. Second sentence! Third? Fourth。Fifth！Sixth？"
        sentences = processor.add_chunk(text)
        assert sentences == [
            "First sentence.",
            "Second sentence!",
            "Third?",
            "Fourth。",
            "Fifth！",
            "Sixth？",
        ]

    def test_empty_and_whitespace_chunks(self, processor: TextChunkProcessor):
        """Handle empty and whitespace-only chunks without producing sentences and preserve whitespace buffering."""
        sentences = processor.add_chunk("")
        assert sentences == []
        sentences = processor.add_chunk("   ")
        assert sentences == []
        assert (
            processor._buffer == "   "
        )  # Whitespace is preserved until a sentence is formed
        sentences = processor.add_chunk("Hello.  ")
        assert sentences == ["Hello."]
        assert processor._buffer == ""

    def test_complex_mixed_content(self, processor: TextChunkProcessor):
        """Process a mix of normal text, reasoning tags, and tool calls across multiple chunks."""
        chunk1 = "Okay, let's see. <think>I need to find the user's location.</think> "
        sentences1 = processor.add_chunk(chunk1)
        assert sentences1 == ["Okay, let's see."]
        assert processor._buffer == ""

        chunk2 = (
            "First, I'll call a tool. {'type': 'tool_call', 'id': 'loc', 'args': {}} "
        )
        sentences2 = processor.add_chunk(chunk2)
        assert sentences2 == ["First, I'll call a tool."]
        assert processor._buffer == ""

        chunk3 = "Now I have the location. <think>The user is in Seoul.</think>The weather is sunny."
        sentences3 = processor.add_chunk(chunk3)
        assert sentences3 == ["Now I have the location.", "The weather is sunny."]
        assert processor._buffer == ""

        remaining = processor.finalize()
        assert remaining == []
