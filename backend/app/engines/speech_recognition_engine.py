"""
Speech Recognition Engine
Evaluates if user's pronunciation matches the expected Cantonese word.
Uses OpenAI Whisper for Cantonese speech recognition.
"""
from typing import Optional, Tuple
import io
import random
import tempfile
import os

# Try to import faster-whisper (compatible with Python 3.14), fall back to mock if not available
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    WhisperModel = None


class SpeechRecognitionEngine:
    """Engine for evaluating pronunciation correctness."""
    
    def __init__(self):
        """Initialize the speech recognition engine."""
        self.model = None
        self.use_whisper = False
        
        if FASTER_WHISPER_AVAILABLE:
            try:
                # Load faster-whisper model (base model is good balance of speed/accuracy)
                # For Cantonese, we use 'base' model which supports multilingual including Cantonese
                # faster-whisper is compatible with Python 3.14 and faster than openai-whisper
                print("Loading faster-whisper ASR model for Cantonese...")
                self.model = WhisperModel("base", device="cpu", compute_type="int8")
                self.use_whisper = True
                print("faster-whisper model loaded successfully!")
            except Exception as e:
                print(f"Warning: Failed to load faster-whisper model: {e}")
                print("Falling back to mock implementation")
                self.use_whisper = False
        else:
            print("Warning: faster-whisper not installed. Using mock implementation.")
            print("Install with: uv add faster-whisper")
            self.use_whisper = False
    
    def _transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcribe audio to text using faster-whisper ASR model.
        
        Returns:
            Recognized text in Chinese characters (Cantonese), then converted to jyutping
        """
        if self.use_whisper and self.model:
            try:
                # Save audio data to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_file_path = tmp_file.name
                
                try:
                    # Transcribe with faster-whisper
                    # Language is set to 'zh' (Chinese) which includes Cantonese
                    # faster-whisper will detect Cantonese automatically
                    segments, info = self.model.transcribe(
                        tmp_file_path,
                        language='zh',  # Chinese (includes Cantonese)
                        task='transcribe',
                        beam_size=5
                    )
                    
                    # Extract the transcribed text from segments
                    recognized_text = "".join([segment.text for segment in segments]).strip()
                    
                    # Convert Chinese text to jyutping using pycantonese
                    # This is a two-step process: ASR gives us Chinese characters,
                    # then we convert to jyutping for comparison
                    try:
                        import pycantonese
                        jyutping = pycantonese.characters_to_jyutping(recognized_text)
                        if jyutping:
                            # Join jyutping syllables with spaces
                            return " ".join(jyutping)
                        else:
                            # If conversion fails, return the Chinese text
                            # (comparison will need to handle this)
                            return recognized_text
                    except Exception as e:
                        print(f"Warning: Failed to convert to jyutping: {e}")
                        # Return Chinese text if jyutping conversion fails
                        return recognized_text
                        
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)
                        
            except Exception as e:
                print(f"Error in faster-whisper transcription: {e}")
                # Fall back to mock if faster-whisper fails
                return self._mock_transcribe()
        else:
            # Use mock implementation if faster-whisper is not available
            return self._mock_transcribe()
    
    def _mock_transcribe(self) -> str:
        """
        Mock transcription for testing when faster-whisper is not available.
        """
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

