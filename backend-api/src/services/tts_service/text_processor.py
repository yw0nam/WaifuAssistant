"""
Text processing service for TTS optimization
Handles filtering unwanted text and sentence segmentation
"""

import re
from typing import List, Tuple
from src.core.logging import setup_logging

logger = setup_logging("text_processor")


class TTSTextProcessor:
    """Text processor for optimizing text before TTS conversion"""

    def __init__(self):
        # Patterns to remove from text before TTS
        self.remove_patterns = [
            # Thinking tags (with DOTALL flag for multiline support)
            r"<think>.*?</think>",
            r"<thinking>.*?</thinking>",
            r"\[thinking\].*?\[/thinking\]",
            r"\[think\].*?\[/think\]",
            # Emotional tags in parentheses
            r"\([^)]*(?:angry|sad|happy|excited|nervous|confused|surprised|disgusted|"
            r"fear|joy|love|hate|tired|sleepy|awake|bored|interested|curious|"
            r"annoyed|frustrated|calm|relaxed|stressed|worried|anxious|proud|"
            r"embarrassed|shy|confident|disappointed|hopeful|grateful|"
            r"jealous|envious|guilty|ashamed|relieved|satisfied|content|"
            r"nostalgic|melancholic|euphoric|ecstatic|depressed|cheerful|"
            r"gloomy|optimistic|pessimistic|sarcastic|ironic|serious|playful|"
            r"flirty|romantic|seductive|innocent|mischievous|evil|kind|mean|"
            r"gentle|rough|soft|loud|quiet|whisper|shout|laugh|cry|sigh|gasp|"
            r"giggle|chuckle|sob|wail|scream|moan|groan|grunt|hum|sing)[^)]*\)",
            # Action descriptions in asterisks
            r"\*[^*]*\*",
            # Stage directions in brackets
            r"\[[^\]]*(?:action|movement|gesture|expression|look|stare|glance|"
            r"smile|frown|nod|shake|turn|walk|run|sit|stand|lie|kneel|"
            r"touch|grab|hold|release|point|wave|clap|snap)[^\]]*\]",
            # Markdown formatting
            r"\*\*([^*]+)\*\*",  # Bold - keep content
            r"\*([^*]+)\*",  # Italic - keep content
            r"`([^`]+)`",  # Code - keep content
            r"~~([^~]+)~~",  # Strikethrough - keep content
            # HTML-like tags
            r"<[^>]+>",
        ]

        # Compile patterns for efficiency
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE | re.DOTALL)
            for pattern in self.remove_patterns
        ]

        # Special handling for character filtering - be more permissive for international text
        # Instead of aggressive filtering, only remove truly problematic characters
        self.problematic_chars_pattern = re.compile(
            r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]"  # Control characters only
        )

        # Sentence splitting patterns - support for multiple languages
        # English/Western punctuation
        self.western_sentence_endings = re.compile(r"[.!?]+\s*")

        # Japanese punctuation - includes ellipsis as potential sentence ending
        self.japanese_sentence_endings = re.compile(
            r"[。！？]+\s*|…+\s*(?=[A-Z\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf])"
        )

        # Combined sentence endings for multilingual support
        self.sentence_endings = re.compile(r"[.!?。！？]+\s*")

        # Japanese ellipsis and pause markers (for more natural breaking)
        self.japanese_pause_markers = re.compile(r"[…～♪♡💕✨😊]+\s*")

        # Line breaks and paragraph separators
        self.line_breaks = re.compile(r"\n+")

        # Japanese quotation marks that can indicate sentence boundaries
        self.japanese_quotes = re.compile(r"[」』】】]")

        # Detect if text is primarily Japanese
        self.japanese_chars = re.compile(r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]")

    def clean_text_for_tts(
        self, text: str, skip_internal_reasoning: bool = True
    ) -> str:
        """
        Clean text by removing unwanted elements for TTS

        Args:
            text: Raw text from LLM
            skip_internal_reasoning: Whether to filter out thinking tags and internal reasoning

        Returns:
            Cleaned text suitable for TTS
        """
        if not text or not text.strip():
            return ""

        cleaned_text = text

        # Apply all remove patterns
        for pattern in self.compiled_patterns:
            # Apply thinking/reasoning patterns only if skip_internal_reasoning is True
            if skip_internal_reasoning and pattern.pattern in [
                r"<think>.*?</think>",
                r"<thinking>.*?</thinking>",
                r"\[thinking\].*?\[/thinking\]",
                r"\[think\].*?\[/think\]",
            ]:
                # Remove thinking patterns completely with multiline support
                cleaned_text = pattern.sub(" ", cleaned_text)
                continue
            elif not skip_internal_reasoning and pattern.pattern in [
                r"<think>.*?</think>",
                r"<thinking>.*?</thinking>",
                r"\[thinking\].*?\[/thinking\]",
                r"\[think\].*?\[/think\]",
            ]:
                # Keep thinking patterns when skip_internal_reasoning is False
                continue

            if pattern.pattern in [
                r"\*\*([^*]+)\*\*",
                r"\*([^*]+)\*",
                r"`([^`]+)`",
                r"~~([^~]+)~~",
            ]:
                # For markdown, keep the content but remove formatting
                cleaned_text = pattern.sub(r"\1", cleaned_text)
            else:
                # For other patterns, remove completely
                cleaned_text = pattern.sub(" ", cleaned_text)

        # Clean up extra whitespace
        cleaned_text = re.sub(r"\s+", " ", cleaned_text)
        cleaned_text = cleaned_text.strip()

        logger.debug(
            f"Text cleaned for TTS: '{text[:50]}...' -> '{cleaned_text[:50]}...'"
        )
        return cleaned_text

    def _is_primarily_japanese(self, text: str) -> bool:
        """
        Detect if text contains primarily Japanese characters

        Args:
            text: Text to analyze

        Returns:
            True if text is primarily Japanese
        """
        if not text:
            return False

        japanese_matches = self.japanese_chars.findall(text)
        total_chars = len(
            [c for c in text if c.isalnum() or ord(c) > 127]
        )  # Count non-ASCII chars

        if total_chars == 0:
            return False

        japanese_ratio = len(japanese_matches) / total_chars
        return japanese_ratio > 0.3  # If >30% Japanese chars, treat as Japanese text

    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences for better TTS processing
        Supports both Western and Japanese punctuation

        Args:
            text: Cleaned text

        Returns:
            List of sentences
        """
        if not text or not text.strip():
            return []

        is_japanese = self._is_primarily_japanese(text)
        sentences = []

        if is_japanese:
            # Japanese-specific splitting logic
            # Split by obvious sentence endings first
            parts = re.split(r"([。！？]+)", text)
            current_sentence = ""

            for part in parts:
                if not part.strip():
                    continue

                current_sentence += part

                # If this part is a sentence ending punctuation
                if re.match(r"^[。！？]+$", part):
                    sentences.append(current_sentence.strip())
                    current_sentence = ""

            # Handle remaining text (no sentence endings found)
            if current_sentence.strip():
                # For long text without obvious endings, split by natural breaks
                remaining_text = current_sentence.strip()

                # Split by ellipsis, quotation marks, and emotional markers
                # Pattern includes: ...  ～  」』  💕✨😊 etc.
                natural_breaks = re.split(
                    r"(…+|～+|[」』】]+|[💕✨😊♪♡]+|（[^）]*）)", remaining_text
                )

                temp_sentence = ""
                for i, segment in enumerate(natural_breaks):
                    if not segment.strip():
                        continue

                    temp_sentence += segment

                    # Check if this is a natural break point
                    is_break_point = False

                    # If we hit ellipsis or emotional markers
                    if re.match(r"^(…+|～+|[💕✨😊♪♡]+)$", segment):
                        # Only break if sentence is reasonably long (>30 chars for Japanese)
                        if len(temp_sentence) > 30:
                            is_break_point = True

                    # If we hit closing quotation marks
                    elif re.match(r"^[」』】]+$", segment):
                        # Break after quotation marks if there's more text coming
                        if i < len(natural_breaks) - 1 and any(
                            nb.strip() for nb in natural_breaks[i + 1 :]
                        ):
                            is_break_point = True

                    # If we hit parenthetical content
                    elif re.match(r"^（[^）]*）$", segment):
                        # Break after parenthetical if sentence is getting long
                        if len(temp_sentence) > 40:
                            is_break_point = True

                    if is_break_point:
                        # Ensure proper sentence ending
                        if not temp_sentence.rstrip()[-1] in "。！？":
                            temp_sentence += "。"
                        sentences.append(temp_sentence.strip())
                        temp_sentence = ""

                # Add any remaining text
                if temp_sentence.strip():
                    if not temp_sentence.rstrip()[-1] in "。！？":
                        temp_sentence += "。"
                    sentences.append(temp_sentence.strip())
        else:
            # Western-style splitting
            # First split by line breaks (preserves intentional pauses)
            lines = self.line_breaks.split(text)

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Split each line by sentence endings
                line_sentences = self.western_sentence_endings.split(line)

                for sentence in line_sentences:
                    sentence = sentence.strip()
                    if sentence:
                        # Ensure sentence ends with proper punctuation for TTS
                        if not sentence[-1] in ".!?":
                            sentence += "."
                        sentences.append(sentence)

        # Filter out very short sentences (likely artifacts)
        # For Japanese, be more lenient as characters can be more dense
        min_length = 3 if is_japanese else 5
        sentences = [s for s in sentences if len(s.strip()) > min_length]

        logger.debug(
            f"Text split into {len(sentences)} sentences (Japanese: {is_japanese})"
        )
        return sentences

    def process_for_tts(
        self, text: str, skip_internal_reasoning: bool = True
    ) -> List[str]:
        """
        Complete text processing pipeline for TTS

        Args:
            text: Raw text from LLM
            skip_internal_reasoning: Whether to filter out thinking tags and internal reasoning

        Returns:
            List of cleaned sentences ready for TTS
        """
        # Step 1: Clean the text
        cleaned_text = self.clean_text_for_tts(text, skip_internal_reasoning)

        if not cleaned_text:
            return []

        # Step 2: Split into sentences
        sentences = self.split_into_sentences(cleaned_text)

        logger.info(
            f"Processed text for TTS: {len(sentences)} sentences from '{text[:50]}...'"
        )
        return sentences

    def should_process_for_tts(self, text: str) -> bool:
        """
        Determine if text should be processed for TTS

        Args:
            text: Text to evaluate

        Returns:
            True if text should be converted to speech
        """
        if not text or not text.strip():
            return False

        # Check if text is mostly thinking/action tags
        cleaned = self.clean_text_for_tts(text)
        if not cleaned or len(cleaned.strip()) < 3:
            return False

        # Check if original text is significantly different from cleaned
        # If >80% was removed, probably not suitable for TTS
        ratio = len(cleaned) / len(text) if text else 0
        if ratio < 0.2:
            logger.debug(f"Text not suitable for TTS (too much removed): {ratio:.2%}")
            return False

        return True
