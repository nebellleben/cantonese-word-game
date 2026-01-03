# Installing ASR Dependencies

## ❌ Current Issue: Python 3.14 Not Supported

The ASR libraries (`faster-whisper`, `onnxruntime`) only support Python 3.11, 3.12, or 3.13.

**Your current Python version**: 3.14.0 (too new)

## ✅ Solution: Use Python 3.13 (or 3.11/3.12)

### Option 1: Using pyenv (Recommended)

```bash
# Install Python 3.13
pyenv install 3.13.0

# Navigate to backend directory
cd backend

# Set Python 3.13 for this project
pyenv local 3.13.0

# Verify
python3 --version  # Should show 3.13.0

# Install dependencies
uv sync
```

### Option 2: Using Homebrew Python

```bash
# Install Python 3.13 via Homebrew
brew install python@3.13

# Use it for this project
cd backend
python3.13 -m venv .venv
source .venv/bin/activate  # or: .venv/bin/activate

# Install uv with Python 3.13
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

### Option 3: Use System Python 3.11/3.12 (if available)

```bash
# Check if available
python3.13 --version
python3.12 --version
python3.11 --version

# If available, use it
cd backend
uv sync --python python3.13  # or python3.12, python3.11
```

## Verify Installation

After switching to Python 3.11-3.13:

```bash
cd backend
uv sync
```

You should see:
```
✓ Resolved X packages
✓ Installed faster-whisper
✓ Installed onnxruntime
```

## Test ASR

```bash
cd backend
uv run python -c "
from app.engines.speech_recognition_engine import speech_recognition_engine
print('Using real ASR:', speech_recognition_engine.use_whisper)
print('Model loaded:', speech_recognition_engine.model is not None)
"
```

**Expected output:**
```
Loading faster-whisper ASR model for Cantonese...
faster-whisper model loaded successfully!
Using real ASR: True
Model loaded: True
```

## Alternative: API-Based Solution (Works with Python 3.14)

If you can't change Python version, use cloud APIs:

### Google Cloud Speech-to-Text

```bash
uv add google-cloud-speech
```

### Azure Speech Services

```bash
uv add azure-cognitiveservices-speech
```

These work with any Python version but require API keys.

## Current Status

- ❌ Python 3.14: ASR dependencies cannot install
- ✅ Python 3.11-3.13: ASR dependencies will install successfully
- ✅ Code is ready: Just needs compatible Python version

## Quick Fix

```bash
# Install Python 3.13
pyenv install 3.13.0

# Switch to it
cd backend
pyenv local 3.13.0

# Install ASR
uv sync

# Test
uv run python -c "from app.engines.speech_recognition_engine import speech_recognition_engine; print('ASR ready:', speech_recognition_engine.use_whisper)"
```

