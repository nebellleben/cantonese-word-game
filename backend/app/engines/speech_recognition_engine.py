"""
Speech Recognition Engine
Evaluates if user's pronunciation matches the expected Cantonese word.
Uses HuggingFace Whisper model fine-tuned for Cantonese speech recognition.
"""
from typing import Optional, Tuple
import io
import json
import random
import re
import time

# Try to import ML dependencies, fall back to mock if not available
try:
    import torch
    import librosa
    from transformers import WhisperProcessor, WhisperForConditionalGeneration
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    WhisperProcessor = None
    WhisperForConditionalGeneration = None


class SpeechRecognitionEngine:
    """Engine for evaluating pronunciation correctness."""
    
    def __init__(self):
        """Initialize the speech recognition engine."""
        self.processor = None
        self.model = None
        self.use_whisper = False
        self._model_loading = False
        self._model_loaded = False
        
        # Don't load model during initialization - load lazily on first use
        # This prevents blocking server startup
        if not TRANSFORMERS_AVAILABLE:
            print("Warning: transformers not installed. Using mock implementation.")
            print("Install with: uv add transformers torch librosa")
    
    def _ensure_model_loaded(self):
        """Lazily load the model on first use."""
        if self._model_loaded or self._model_loading:
            return
        
        if not TRANSFORMERS_AVAILABLE:
            return
        
        self._model_loading = True
        try:
            # Load HuggingFace Whisper model fine-tuned for Cantonese
            # Model: alvanlii/whisper-small-cantonese
            # This model is specifically optimized for Cantonese speech recognition
            print("Loading HuggingFace Whisper ASR model for Cantonese...")
            self.processor = WhisperProcessor.from_pretrained("alvanlii/whisper-small-cantonese")
            self.model = WhisperForConditionalGeneration.from_pretrained("alvanlii/whisper-small-cantonese")
            self.model.eval()  # Set to evaluation mode
            self.use_whisper = True
            self._model_loaded = True
            print("HuggingFace Whisper model loaded successfully!")
        except Exception as e:
            print(f"Warning: Failed to load HuggingFace Whisper model: {e}")
            print("Falling back to mock implementation")
            self.use_whisper = False
            self._model_loaded = True  # Mark as loaded even if failed to prevent retries
        finally:
            self._model_loading = False
    
    def _transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcribe audio to text using HuggingFace Whisper ASR model.
        
        Returns:
            Recognized text in Chinese characters (Cantonese)
        """
        # Load model lazily on first use
        if TRANSFORMERS_AVAILABLE and not self._model_loaded:
            self._ensure_model_loaded()
        
        if self.use_whisper and self.model and self.processor:
            try:
                # Load audio from bytes using librosa
                # librosa automatically resamples to 16kHz (required by Whisper)
                audio_array, sampling_rate = librosa.load(io.BytesIO(audio_data), sr=16000)
                
                # Process audio with WhisperProcessor
                input_features = self.processor(audio_array, sampling_rate=sampling_rate, return_tensors="pt").input_features
                
                # Generate transcription
                with torch.no_grad():
                    predicted_ids = self.model.generate(input_features)
                
                # Decode transcription
                transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
                
                # Return Chinese characters directly for comparison
                return transcription.strip()
                        
            except Exception as e:
                print(f"Error in HuggingFace Whisper transcription: {e}")
                # Fall back to mock if transcription fails
                return self._mock_transcribe()
        else:
            # Use mock implementation if transformers is not available
            return self._mock_transcribe()
    
    def _mock_transcribe(self) -> str:
        """
        Mock transcription for testing when transformers is not available.
        Returns Chinese characters for testing purposes.
        """
        mock_texts = [
            "你好",   # Correct
            "謝謝",   # Correct
            "再見",   # Correct
            "早晨",   # Correct
            "晚安",   # Correct
            "你好嗎",  # Variation
            "多謝",   # Variation
            "再會",   # Variation
        ]
        return random.choice(mock_texts)
    
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
            audio_data: Audio file bytes (WAV format)
            expected_text: Expected Chinese text
            expected_jyutping: Expected Jyutping transliteration (for display purposes only)
            real_time_recognition: Optional real-time recognition text from Web Speech API.
                                 If provided and non-empty, this will be used for comparison
                                 instead of transcribing the audio with HuggingFace Whisper.
            
        Returns:
            Tuple of (is_correct: bool, feedback: Optional[str], recognized_text: Optional[str])
            where recognized_text is Chinese characters
        """
        try:
            # Use real-time recognition if provided, otherwise transcribe with HuggingFace Whisper
            if real_time_recognition and real_time_recognition.strip():
                # Use real-time recognition from Web Speech API
                recognized_text = real_time_recognition.strip()
            else:
                # Fall back to HuggingFace Whisper transcription
                if audio_data and len(audio_data) > 0:
                    recognized_text = self._transcribe_audio(audio_data)
                else:
                    # No audio provided - for testing, we'll use a mock
                    recognized_text = self._transcribe_audio(b"mock")
            
            # Compare with expected Chinese characters
            is_correct = self._compare_pronunciation(recognized_text, expected_text)
            
            # Generate feedback (jyutping is included for display purposes)
            feedback = self._generate_feedback(
                is_correct,
                recognized_text,
                expected_text,
                expected_jyutping
            )
            
            return is_correct, feedback, recognized_text
            
        except Exception as e:
            # Error in processing
            return False, f"Error processing audio: {str(e)}", None


speech_recognition_engine = SpeechRecognitionEngine()

