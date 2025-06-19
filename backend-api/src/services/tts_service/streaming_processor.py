"""
Streaming text processor for real-time TTS
Processes text chunks incrementally and detects complete sentences
"""

import re
from typing import List, Optional, Tuple
from src.core.logging import setup_logging
from .text_processor import TTSTextProcessor

logger = setup_logging("streaming_processor")


class StreamingTTSProcessor:
    """Processes text chunks in real-time and detects complete sentences for immediate TTS"""

    def __init__(
        self,
        skip_internal_reasoning: bool = True,
        reasoning_start_tag: str = "<think>",
        reasoning_end_tag: str = "</think>",
    ):
        self.text_processor = TTSTextProcessor()
        self.skip_internal_reasoning = skip_internal_reasoning
        self.accumulated_text = ""
        self.processed_length = 0  # Track how much we've already processed

        # State-based reasoning filter with nesting support
        self.reasoning_stack = []  # Stack to handle nested reasoning blocks
        self.reasoning_buffer = ""

        # Dynamic reasoning tag patterns
        self.reasoning_start_tag = reasoning_start_tag
        self.reasoning_end_tag = reasoning_end_tag

        # Compile patterns for the specified tags
        self.reasoning_start_pattern = re.compile(
            re.escape(reasoning_start_tag), re.IGNORECASE
        )
        self.reasoning_end_pattern = re.compile(
            re.escape(reasoning_end_tag), re.IGNORECASE
        )

        logger.debug(
            f"Initialized with reasoning tags: start='{reasoning_start_tag}', end='{reasoning_end_tag}'"
        )

        # Sentence ending patterns (more comprehensive)
        self.sentence_endings = re.compile(r"[.!?]+(?:\s|$)")

        # Sentence boundary markers for streaming (support Japanese and Western)
        # Be conservative - only split on clear sentence endings, not pause markers
        self.sentence_boundaries = re.compile(r"[.!?。！？]+(?:\s|$)|[\n\r]+")

        # NOTE: Removed ellipsis (…) and tilde (~) from boundaries as they are often
        # used for emphasis or pauses within sentences in Japanese

    @property
    def inside_reasoning(self) -> bool:
        """Check if currently inside any reasoning block"""
        return len(self.reasoning_stack) > 0

    def _filter_reasoning_realtime(self, chunk: str) -> str:
        """
        Real-time reasoning filter using state machine
        Handles cases where reasoning tags span multiple chunks

        Args:
            chunk: New text chunk to filter

        Returns:
            Filtered text chunk (empty if inside reasoning block)
        """
        if not self.skip_internal_reasoning:
            return chunk

        filtered_text = ""
        i = 0
        text = chunk

        while i < len(text):
            if not self.inside_reasoning:
                # Look for reasoning start tag anywhere from current position
                match = self.reasoning_start_pattern.search(text, i)
                if match:
                    # Add text before the tag to output
                    filtered_text += text[i : match.start()]
                    # Found reasoning start tag
                    self.reasoning_stack.append(self.reasoning_start_tag)
                    self.reasoning_buffer = ""
                    i = match.end()
                    logger.debug(
                        f"Reasoning start detected at position {match.start()}: {match.group()}"
                    )
                else:
                    # No start tag found, add remaining text to output
                    filtered_text += text[i:]
                    break
            else:
                # Inside reasoning block, look for end tag anywhere from current position
                match = self.reasoning_end_pattern.search(text, i)
                if match:
                    # Skip text before the end tag (it's inside reasoning block)
                    # Found reasoning end tag
                    if self.reasoning_stack:
                        self.reasoning_stack.pop()
                    self.reasoning_buffer = ""
                    i = match.end()
                    logger.debug(
                        f"Reasoning end detected at position {match.start()}: {match.group()}"
                    )
                    # Continue processing after the end tag (might have more text)
                else:
                    # No end tag found, skip remaining text (still inside reasoning)
                    self.reasoning_buffer += text[i:]
                    break

        return filtered_text

    def add_chunk(self, chunk: str) -> List[str]:
        """
        Add a new text chunk and return any complete sentences ready for TTS

        Args:
            chunk: New text chunk from LLM stream

        Returns:
            List of complete sentences ready for TTS
        """
        if not chunk:
            return []

        # Apply real-time reasoning filter first
        filtered_chunk = self._filter_reasoning_realtime(chunk)

        if not filtered_chunk:
            # Chunk was completely filtered out (inside reasoning block)
            logger.debug(
                f"Chunk completely filtered: '{chunk}' (inside reasoning: {self.inside_reasoning})"
            )
            return []

        # Add filtered chunk to accumulated text
        self.accumulated_text += filtered_chunk
        logger.debug(
            f"Added filtered chunk: '{filtered_chunk}' (total length: {len(self.accumulated_text)})"
        )

        # Extract new complete sentences
        return self._extract_complete_sentences()

    def _extract_complete_sentences(self) -> List[str]:
        """Extract complete sentences from accumulated text"""
        # Get the unprocessed portion
        unprocessed_text = self.accumulated_text[self.processed_length :]

        if not unprocessed_text:
            return []

        logger.debug(
            f"Processing unprocessed text: '{unprocessed_text}' (length: {len(unprocessed_text)})"
        )
        logger.debug(f"Current processed_length: {self.processed_length}")

        # Detect if text is primarily Japanese for conservative sentence splitting
        japanese_chars = len(
            [
                c
                for c in unprocessed_text
                if "\u3040" <= c <= "\u309f"
                or "\u30a0" <= c <= "\u30ff"
                or "\u4e00" <= c <= "\u9faf"
            ]
        )
        total_chars = len([c for c in unprocessed_text if c.isalnum() or ord(c) > 127])
        is_japanese = total_chars > 0 and (japanese_chars / total_chars) > 0.3

        # For Japanese text, be more conservative - only split on clear sentence endings
        if is_japanese:
            # Only split on definitive Japanese sentence endings
            conservative_boundaries = re.compile(r"[。！？]+(?:\s|$)")
        else:
            # Use normal boundaries for Western text
            conservative_boundaries = self.sentence_boundaries

        # Find sentence boundaries in the unprocessed text
        sentences = []
        last_processed_pos = 0  # Position in unprocessed_text where we last processed

        # Find all sentence boundary matches with their positions
        for match in conservative_boundaries.finditer(unprocessed_text):
            start_pos = match.start()
            end_pos = match.end()

            # Extract the sentence part from last position to this boundary
            sentence_part = unprocessed_text[last_processed_pos:start_pos].strip()

            if sentence_part and len(sentence_part) > 2:
                # This is a complete sentence
                # Add back the sentence ending punctuation
                full_sentence = sentence_part + match.group().strip()

                logger.debug(f"Found complete sentence: '{full_sentence}'")

                # Clean the sentence for TTS (skip reasoning filter since already applied)
                cleaned_sentences = self.text_processor.process_for_tts(
                    full_sentence, skip_internal_reasoning=False  # Already filtered
                )

                if cleaned_sentences:
                    sentences.extend(cleaned_sentences)
                    logger.debug(f"Added cleaned sentences: {cleaned_sentences}")

            # Move position to after this boundary
            last_processed_pos = end_pos

        # Update the overall processed length to include the processed part of unprocessed_text
        if last_processed_pos > 0:
            self.processed_length += last_processed_pos
            logger.debug(f"Updated processed_length to: {self.processed_length}")

        if sentences:
            logger.info(
                f"Extracted {len(sentences)} complete sentences for TTS: {sentences}"
            )

        return sentences

    def finalize(self) -> List[str]:
        """
        Finalize processing and return any remaining text as sentences
        Called when LLM streaming is complete

        Returns:
            List of final sentences ready for TTS
        """
        # Get any remaining unprocessed text
        remaining_text = self.accumulated_text[self.processed_length :].strip()

        if not remaining_text:
            return []

        logger.info(f"Finalizing remaining text: '{remaining_text[:50]}...'")

        # Process remaining text as complete sentences (skip reasoning filter since already applied)
        cleaned_sentences = self.text_processor.process_for_tts(
            remaining_text, skip_internal_reasoning=False  # Already filtered
        )

        # Mark everything as processed
        self.processed_length = len(self.accumulated_text)

        return cleaned_sentences

    def should_process_chunk_for_tts(self, chunk: str) -> bool:
        """
        Quick check if a chunk might contain TTS-worthy content
        Used for early filtering before accumulation

        Args:
            chunk: Text chunk to check

        Returns:
            True if chunk should be processed
        """
        if not chunk or not chunk.strip():
            return False

        # Always process non-empty chunks - let the internal reasoning filter handle <think> tags
        # The previous logic was incorrectly filtering out chunks with reasoning tags
        # which prevented proper sentence extraction
        return True

    def reset(self):
        """Reset the processor for a new conversation"""
        self.accumulated_text = ""
        self.processed_length = 0
        self.inside_reasoning = False
        self.reasoning_buffer = ""
        logger.debug("Streaming processor reset")

    def get_status(self) -> dict:
        """Get current processing status for debugging"""
        return {
            "accumulated_length": len(self.accumulated_text),
            "processed_length": self.processed_length,
            "pending_length": len(self.accumulated_text) - self.processed_length,
            "inside_reasoning": self.inside_reasoning,
            "reasoning_buffer_length": len(self.reasoning_buffer),
            "skip_internal_reasoning": self.skip_internal_reasoning,
            "accumulated_preview": (
                self.accumulated_text[:100] + "..."
                if len(self.accumulated_text) > 100
                else self.accumulated_text
            ),
        }
