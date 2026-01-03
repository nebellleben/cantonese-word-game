"""
Speech Recognition Engine
Evaluates if user's pronunciation matches the expected Cantonese word.
"""
from typing import Optional, Tuple
import io
import random


class SpeechRecognitionEngine:
    """Engine for evaluating pronunciation correctness."""
    
    def __init__(self):
        # In production, this would initialize a Cantonese speech recognition model
        pass
    
    def _transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcribe audio to text/jyutping.
        
        In production, this would use a Cantonese ASR model.
        For now, this is a mock implementation.
        """
        # Mock implementation: Return a mock transcription
        # In production, replace with actual ASR:
        # import whisper or other ASR library
        # model = load_cantonese_asr_model()
        # transcription = model.transcribe(audio_data)
        # return transcription
        
        # For development: Generate a mock recognized jyutping
        # This simulates what an ASR system might recognize
        # We'll make it sometimes match, sometimes not, for testing
        mock_jyutpings = [
            "nei5 hou2",  # Correct for 你好
            "ze6 ze6",    # Correct for 謝謝
            "zoi3 gin3",  # Correct for 再見
            "zou2 san4",  # Correct for 早晨
            "maan5 on1",  # Correct for 晚安
            "nei5 hou3",  # Slight variation (wrong tone)
            "ze6 ze5",    # Slight variation
            "zoi2 gin3",  # Slight variation
        ]
        
        # Randomly select a mock transcription
        # In a real scenario, this would come from the ASR model
        return random.choice(mock_jyutpings)
    
    def _compare_pronunciation(
        self,
        recognized_jyutping: str,
        expected_jyutping: str
    ) -> bool:
        """
        Compare recognized pronunciation with expected pronunciation.
        
        Args:
            recognized_jyutping: The jyutping recognized from audio
            expected_jyutping: The expected jyutping for the word
            
        Returns:
            True if pronunciations match (with some tolerance)
        """
        # Normalize both jyutpings for comparison
        recognized = recognized_jyutping.strip().lower()
        expected = expected_jyutping.strip().lower()
        
        # Exact match
        if recognized == expected:
            return True
        
        # For now, we'll do exact matching
        # In production, you might want to:
        # - Handle tone variations (some tolerance)
        # - Handle similar sounds
        # - Use phonetic distance metrics
        
        return False
    
    def _generate_feedback(
        self,
        is_correct: bool,
        recognized_jyutping: str,
        expected_jyutping: str,
        expected_text: str
    ) -> str:
        """Generate feedback message for the user."""
        if is_correct:
            return f"Correct! You pronounced '{expected_text}' correctly."
        else:
            return f"Expected: {expected_jyutping} for '{expected_text}', but recognized: {recognized_jyutping}"
    
    def evaluate_pronunciation(
        self,
        audio_data: bytes,
        expected_text: str,
        expected_jyutping: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Evaluate if the pronunciation matches the expected word.
        
        Args:
            audio_data: Audio file bytes (WAV format)
            expected_text: Expected Chinese text
            expected_jyutping: Expected Jyutping transliteration
            
        Returns:
            Tuple of (is_correct: bool, feedback: Optional[str], recognized_jyutping: Optional[str])
        """
        try:
            # Transcribe audio to jyutping
            if audio_data and len(audio_data) > 0:
                recognized_jyutping = self._transcribe_audio(audio_data)
            else:
                # No audio provided - for testing, we'll use a mock
                recognized_jyutping = self._transcribe_audio(b"mock")
            
            # Compare with expected
            is_correct = self._compare_pronunciation(recognized_jyutping, expected_jyutping)
            
            # Generate feedback
            feedback = self._generate_feedback(
                is_correct,
                recognized_jyutping,
                expected_jyutping,
                expected_text
            )
            
            return is_correct, feedback, recognized_jyutping
            
        except Exception as e:
            # Error in processing
            return False, f"Error processing audio: {str(e)}", None


speech_recognition_engine = SpeechRecognitionEngine()

