# Speech Recognition Implementation

## Current Status

The speech recognition engine now uses **OpenAI Whisper** for Cantonese speech recognition.

## ASR Model: OpenAI Whisper

- **Model**: Whisper `base` model
- **Language Support**: Multilingual, including Cantonese (detected automatically)
- **Accuracy**: High accuracy for Cantonese speech recognition
- **Output**: Chinese characters (Cantonese), then converted to Jyutping

## How It Works

1. **Audio Input**: User records pronunciation (WAV format)
2. **Whisper Transcription**: 
   - Audio is transcribed to Chinese characters (Cantonese)
   - Language is set to 'zh' (Chinese) which includes Cantonese
3. **Jyutping Conversion**: 
   - Chinese text is converted to Jyutping using `pycantonese`
   - This allows comparison with expected pronunciation
4. **Comparison**: 
   - Recognized jyutping is compared with expected jyutping
   - Returns match result and detailed feedback

## Installation

The required dependencies are in `pyproject.toml`:

```bash
cd backend
uv sync
```

This will install:
- `openai-whisper`: The Whisper ASR model
- `torch`: PyTorch (required by Whisper)
- `numpy`: Numerical operations

## Model Loading

On first use, Whisper will download the model (~150MB for base model).
The model is cached for subsequent uses.

## Fallback Behavior

If Whisper is not available or fails to load:
- The system falls back to a mock implementation
- Mock randomly selects from a list of jyutping values
- This allows development/testing without ASR dependencies

## Performance

- **Model Size**: ~150MB (base model)
- **Speed**: ~1-2 seconds per transcription (on CPU)
- **Accuracy**: High for Cantonese speech

## Alternative Models

If you need better accuracy or different characteristics:

1. **Whisper Models** (in order of accuracy/speed):
   - `tiny`: Fastest, least accurate
   - `base`: Good balance (current)
   - `small`: Better accuracy
   - `medium`: High accuracy
   - `large`: Best accuracy, slowest

   Change in `speech_recognition_engine.py`:
   ```python
   self.model = whisper.load_model("small")  # or "medium", "large"
   ```

2. **Other Options**:
   - Google Cloud Speech-to-Text API
   - Azure Speech Services
   - Wav2Vec 2.0 (requires custom training)

## Troubleshooting

### Whisper not loading?

1. Check if dependencies are installed:
   ```bash
   cd backend
   uv sync
   ```

2. Check if PyTorch is installed correctly:
   ```bash
   uv run python -c "import torch; print(torch.__version__)"
   ```

3. Check if Whisper is available:
   ```bash
   uv run python -c "import whisper; print('Whisper OK')"
   ```

### Model download issues?

- First run will download the model (~150MB)
- Ensure internet connection is available
- Model is cached in `~/.cache/whisper/`

### Low accuracy?

- Try a larger model (`small`, `medium`, or `large`)
- Ensure audio quality is good
- Check that audio format is WAV and properly encoded

## Testing

Test the ASR engine:

```bash
cd backend
uv run python -c "
from app.engines.speech_recognition_engine import speech_recognition_engine
print('Using Whisper:', speech_recognition_engine.use_whisper)
print('Model loaded:', speech_recognition_engine.model is not None)
"
```

## Notes

- Whisper supports Cantonese natively
- The model automatically detects Cantonese vs Mandarin
- Output is in Chinese characters, which we convert to Jyutping
- For production, consider using a larger model or fine-tuning

