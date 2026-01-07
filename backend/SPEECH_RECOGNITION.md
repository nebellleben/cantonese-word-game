# Speech Recognition Implementation

## Current Status

The speech recognition engine now uses **HuggingFace Whisper** fine-tuned for Cantonese speech recognition.

## ASR Model: HuggingFace Whisper

- **Model**: `alvanlii/whisper-small-cantonese` (HuggingFace)
- **Architecture**: Whisper Small, fine-tuned specifically for Cantonese
- **Accuracy**: Character Error Rate (CER) of 7.93 on Common Voice 16.0
- **Output**: Chinese characters (Cantonese)

## How It Works

1. **Audio Input**: User records pronunciation (WAV format)
2. **Real-Time Recognition (Primary)**:
   - Frontend uses Web Speech API to show real-time recognition to users
   - Real-time recognition text is captured and sent to backend along with audio
   - **Comparison uses the real-time recognition text** - ensuring consistency with what the user sees
3. **HuggingFace Whisper Transcription (Fallback)**: 
   - If real-time recognition is not available or empty, falls back to HuggingFace Whisper
   - Audio is loaded from bytes and resampled to 16kHz
   - Processed with WhisperProcessor and transcribed using the Cantonese-optimized model
   - Model is specifically fine-tuned for Cantonese, providing better accuracy than general-purpose models
4. **Comparison**: 
   - Recognized Chinese characters (from real-time recognition or Whisper) are compared directly with expected Chinese characters
   - Returns match result and detailed feedback
5. **Display**: 
   - Jyutping is only used for display purposes after evaluation
   - Shows the correct pronunciation in jyutping format to help users learn

## Installation

The required dependencies are in `pyproject.toml`:

```bash
cd backend
uv sync
```

This will install:
- `transformers`: HuggingFace transformers library for Whisper models
- `torch`: PyTorch (required by transformers)
- `librosa`: Audio processing library for loading and resampling audio
- `numpy`: Numerical operations (required by librosa)

## Model Loading

On first use, the model will be downloaded from HuggingFace (~500MB for small model).
The model is cached in `~/.cache/huggingface/hub/` for subsequent uses.

## Fallback Behavior

If Whisper is not available or fails to load:
- The system falls back to a mock implementation
- Mock randomly selects from a list of Chinese character strings
- This allows development/testing without ASR dependencies

## Performance

- **Model Size**: ~500MB (small model)
- **Speed**: ~1-2 seconds per transcription (on CPU)
- **Accuracy**: Character Error Rate (CER) of 7.93 on Common Voice 16.0, optimized specifically for Cantonese

## Alternative Models

If you need better accuracy or different characteristics:

1. **Other Cantonese Whisper Models on HuggingFace**:
   - `alvanlii/distil-whisper-small-cantonese`: Distilled version, faster but slightly less accurate
   - `khleeloo/whisper-large-v3-cantonese`: Large model with better accuracy (larger size)
   
   Change in `speech_recognition_engine.py`:
   ```python
   self.processor = WhisperProcessor.from_pretrained("khleeloo/whisper-large-v3-cantonese")
   self.model = WhisperForConditionalGeneration.from_pretrained("khleeloo/whisper-large-v3-cantonese")
   ```

2. **Other Options**:
   - Google Cloud Speech-to-Text API
   - Azure Speech Services
   - Wav2Vec 2.0 Cantonese models (e.g., `alvanlii/wav2vec2-BERT-cantonese`)

## Troubleshooting

### Transformers not loading?

1. Check if dependencies are installed:
   ```bash
   cd backend
   uv sync
   ```

2. Check if PyTorch is installed correctly:
   ```bash
   uv run python -c "import torch; print(torch.__version__)"
   ```

3. Check if transformers is available:
   ```bash
   uv run python -c "from transformers import WhisperProcessor; print('transformers OK')"
   ```

4. Check if librosa is available:
   ```bash
   uv run python -c "import librosa; print('librosa OK')"
   ```

### Model download issues?

- First run will download the model (~500MB)
- Ensure internet connection is available
- Model is cached in `~/.cache/huggingface/hub/`
- If download fails, you can manually download from HuggingFace and place in cache directory

### Low accuracy?

- Ensure audio quality is good (clear recording, minimal background noise)
- Check that audio format is WAV and properly encoded
- Verify audio is being resampled to 16kHz correctly
- Consider using a larger model if needed

## Testing

Test the ASR engine:

```bash
cd backend
uv run python -c "
from app.engines.speech_recognition_engine import speech_recognition_engine
print('Using Whisper:', speech_recognition_engine.use_whisper)
print('Model loaded:', speech_recognition_engine.model is not None)
print('Processor loaded:', speech_recognition_engine.processor is not None)
"
```

## Real-Time Recognition Priority

The system prioritizes real-time recognition from the Web Speech API for comparison:

1. **Primary**: Real-time recognition text (from Web Speech API) is used for comparison if provided
2. **Fallback**: HuggingFace Whisper transcription is used if real-time recognition is missing or empty
3. **Final Fallback**: Mock implementation if both fail

This ensures that the comparison result matches what the user sees in real-time, providing a consistent user experience.

## Notes

- The model is specifically fine-tuned for Cantonese, providing better accuracy than general-purpose Whisper models
- No language detection needed - the model is optimized for Cantonese
- Output is in Chinese characters, which are compared directly with expected Chinese characters
- Jyutping is only used for display purposes to show the correct pronunciation after evaluation
- The model achieves a Character Error Rate (CER) of 7.93 on Common Voice 16.0, demonstrating strong Cantonese recognition capabilities
- **Real-time recognition takes precedence**: The system uses Web Speech API recognition for comparison when available, ensuring users' expectations match the evaluation results

