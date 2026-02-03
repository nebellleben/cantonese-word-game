"""
Speech Recognition Engine
Evaluates if user's pronunciation matches the expected Cantonese word.
Uses browser's Web Speech API for client-side speech recognition.
"""
from typing import Optional, Tuple
import re


class SpeechRecognitionEngine:
    """Engine for evaluating pronunciation correctness."""

    def _compare_pronunciation(
        self,
        recognized_text: str,
        expected_text: str
    ) -> bool:
        """
        Compare recognized Chinese characters with expected Chinese characters.

        Args:
            recognized_text: The Chinese characters recognized from audio
            expected_text: The expected Chinese characters for the word

        Returns:
            True if the Chinese characters match
        """
        # Normalize whitespace for comparison
        recognized = re.sub(r'\s+', '', recognized_text.strip())
        expected = re.sub(r'\s+', '', expected_text.strip())

        # Exact match
        if recognized == expected:
            return True

        # For now, we'll do exact matching
        # In production, you might want to:
        # - Handle character variations
        # - Handle traditional vs simplified characters
        # - Use fuzzy matching for similar characters

        return False

    def _generate_feedback(
        self,
        is_correct: bool,
        recognized_text: str,
        expected_text: str,
        expected_jyutping: str
    ) -> str:
        """
        Generate feedback message for the user.

        Args:
            is_correct: Whether the pronunciation matches
            recognized_text: The Chinese characters recognized from audio
            expected_text: The expected Chinese characters
            expected_jyutping: The expected jyutping (for display purposes only)
        """
        if is_correct:
            return f"Correct! You pronounced '{expected_text}' correctly."
        else:
            return f"Expected: '{expected_text}' ({expected_jyutping}), but recognized: '{recognized_text}'"

    def evaluate_pronunciation(
        self,
        audio_data: bytes,
        expected_text: str,
        expected_jyutping: str,
        real_time_recognition: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Evaluate if the pronunciation matches the expected word.

        Args:
            audio_data: Audio file bytes (WAV format) - not used, kept for API compatibility
            expected_text: Expected Chinese text
            expected_jyutping: Expected Jyutping transliteration (for display purposes only)
            real_time_recognition: Real-time recognition text from browser's Web Speech API.
                                 This parameter is required for pronunciation evaluation.

        Returns:
            Tuple of (is_correct: bool, feedback: Optional[str], recognized_text: Optional[str])
            where recognized_text is Chinese characters
        """
        # Use real-time recognition from browser's Web Speech API
        if real_time_recognition and real_time_recognition.strip():
            recognized_text = real_time_recognition.strip()

            # Compare with expected Chinese characters
            is_correct = self._compare_pronunciation(recognized_text, expected_text)

            # Generate feedback
            feedback = self._generate_feedback(
                is_correct,
                recognized_text,
                expected_text,
                expected_jyutping
            )

            return is_correct, feedback, recognized_text
        else:
            # No recognition provided
            return False, "No speech recognition result provided. Please use the browser's Web Speech API.", None


speech_recognition_engine = SpeechRecognitionEngine()
