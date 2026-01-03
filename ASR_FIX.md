# ASR Service Fix - Stuck Listening Issue

## Problem

The ASR service was getting stuck and kept listening even after the word was spoken. This was caused by the Web Speech API recognition automatically restarting itself in an infinite loop.

## Root Cause

1. **Web Speech API auto-restart**: The `onend` handler was restarting recognition whenever `isRecording` was true
2. **Race condition**: When MediaRecorder stopped, it set `isRecording` to false, but the Web Speech API might have already triggered `onend` and was trying to restart
3. **Missing stop flag**: No explicit flag to prevent recognition from restarting after it should stop

## Fixes Applied

### 1. Added Stop Flag
- Added `shouldStopRecognitionRef` to explicitly control when recognition should stop
- Set to `true` when MediaRecorder stops
- Reset to `false` when starting a new recording

### 2. Immediate Stop on MediaRecorder Stop
- Stop Web Speech API recognition immediately when MediaRecorder stops
- Set `isRecording` to false immediately
- Clear recognition ref to prevent restart

### 3. Updated onend Handler
- Check `shouldStopRecognitionRef` before restarting
- Check `showFeedback` state
- Verify recognition ref still points to current instance

### 4. Updated useEffect Dependencies
- Added `showFeedback` to dependency array
- Recognition stops when feedback is shown

### 5. Manual Stop Handling
- When user manually stops recording, set stop flag and stop recognition

## Changes Made

**File**: `src/pages/GamePage.tsx`

1. Added `shouldStopRecognitionRef` ref
2. Updated `mediaRecorder.onstop` to:
   - Set stop flag immediately
   - Stop Web Speech API recognition
   - Set `isRecording` to false
3. Updated `recognition.onend` to check stop flag before restarting
4. Updated `useEffect` to include `showFeedback` in dependencies
5. Reset stop flag when moving to next word

## Testing

After these fixes:
1. Start recording → Recognition starts
2. Speak word → Audio is recorded
3. Recording stops (after 5s or manual) → Recognition stops immediately
4. Processing → No recognition restart
5. Feedback shown → Recognition stays stopped
6. Next word → Ready for new recording

## Expected Behavior

- ✅ Recording stops after 5 seconds automatically
- ✅ Recording stops when user clicks stop button
- ✅ Web Speech API recognition stops immediately when recording stops
- ✅ Recognition does NOT restart after stopping
- ✅ Ready for next word after feedback is shown

