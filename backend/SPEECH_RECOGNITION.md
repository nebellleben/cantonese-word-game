# Speech Recognition Implementation

## Current Status

The speech recognition engine uses the **browser's Web Speech API** for client-side speech recognition. Server-side ML dependencies have been removed for a lighter Docker image.

## How It Works

1. **Audio Recording**: User records pronunciation in the browser
2. **Client-Side Recognition**:
   - Frontend uses Web Speech API to show real-time recognition to users
   - Recognition text is captured and sent to backend for evaluation
3. **Server-Side Evaluation**:
   - Backend receives the recognized text from the browser
   - Compares the recognized Chinese characters with expected Chinese characters
   - Returns match result and detailed feedback with Jyutping pronunciation
4. **Display**:
   - Jyutping is used for display purposes after evaluation
   - Shows the correct pronunciation in jyutping format to help users learn

## Advantages of Client-Side Recognition

- **Lighter Server**: No heavy ML dependencies (PyTorch, transformers, librosa) needed on the server
- **Faster Response**: Recognition happens in real-time on the client
- **Better UX**: Users see what they're saying as they speak
- **Cost Efficient**: No server-side GPU/CPU resources for speech recognition

## Dependencies

All speech recognition happens on the client side. The backend only needs:

```toml
# From pyproject.toml
fastapi = "Web framework"
uvicorn = "ASGI server"
sqlalchemy = "Database ORM"
alembic = "Database migrations"
```

No ML dependencies required!

## API Endpoint

The backend endpoint for pronunciation evaluation:

```
POST /api/pronunciation/evaluate
```

Request body:
```json
{
  "audio_data": "<base64 encoded audio - optional, kept for compatibility>",
  "expected_text": "你好",
  "expected_jyutping": "nei5 hou2",
  "real_time_recognition": "你好"  // Required - from Web Speech API
}
```

Response:
```json
{
  "is_correct": true,
  "feedback": "Correct! You pronounced '你好' correctly.",
  "recognized_text": "你好"
}
```

## Browser Compatibility

Web Speech API is supported in:
- Chrome/Edge (full support)
- Safari (partial support)
- Firefox (limited support)

For browsers without Web Speech API support, consider providing a text input fallback.

## Future Enhancements

If you need server-side speech recognition in the future, consider:

1. **OpenAI Whisper API**: Cloud-based, no need to host models
2. **Google Cloud Speech-to-Text**: Cloud-based ASR service
3. **Azure Speech Services**: Cloud-based with good Cantonese support
4. **Separate ML Service**: Deploy speech recognition as a separate microservice with GPU support

## Troubleshooting

### Recognition not working in browser?

1. Check browser compatibility (Chrome/Edge recommended)
2. Ensure microphone permissions are granted
3. Check that Web Speech API is enabled in browser settings

### Backend returns "No speech recognition result provided"?

- Ensure the frontend is sending `real_time_recognition` parameter
- Check that the Web Speech API is successfully recognizing speech
- Verify the API request includes the recognition text

## Testing

Test the pronunciation evaluation:

```bash
cd backend
uv run python -c "
from app.engines.speech_recognition_engine import speech_recognition_engine
result = speech_recognition_engine.evaluate_pronunciation(
    audio_data=b'',
    expected_text='你好',
    expected_jyutping='nei5 hou2',
    real_time_recognition='你好'
)
print('Is correct:', result[0])
print('Feedback:', result[1])
"
```

## Notes

- Speech recognition is entirely client-side using the Web Speech API
- No ML models are loaded on the server
- Docker image size is significantly reduced (~150MB vs ~800MB)
- The system uses Alpine Linux for minimal base image size
- Jyutping is only used for display purposes to show the correct pronunciation after evaluation
