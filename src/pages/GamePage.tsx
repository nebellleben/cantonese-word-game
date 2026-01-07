import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { apiClient } from '../services/api';
import SwipeCard from '../components/SwipeCard';
import type { GameSession } from '../types';
import './GamePage.css';

const GamePage: React.FC = () => {
  useAuth(); // Keep auth context active
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const deckId = searchParams.get('deckId');

  const [session, setSession] = useState<GameSession | null>(null);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [gameComplete, setGameComplete] = useState(false);
  const [finalScore, setFinalScore] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [audioLevel, setAudioLevel] = useState(0);
  const [lastFeedback, setLastFeedback] = useState<{ 
    isCorrect: boolean; 
    feedback?: string;
    recognizedText?: string;
    expectedText?: string;
    expectedJyutping?: string;
  } | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isStarting, setIsStarting] = useState(false); // Indicates microphone access is being requested
  const [realTimeRecognition, setRealTimeRecognition] = useState<string>('');
  const [recordedAudioBlob, setRecordedAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const startTimeRef = useRef<number>(Date.now());
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const recognitionRef = useRef<any>(null);
  const shouldStopRecognitionRef = useRef<boolean>(false);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const audioUrlRef = useRef<string | null>(null);
  const realTimeRecognitionRef = useRef<string>(''); // Ref to preserve recognition value
  const preRequestedStreamRef = useRef<MediaStream | null>(null); // Pre-requested microphone stream

  const startGame = useCallback(async () => {
    if (!deckId) {
      navigate('/student');
      return;
    }

    try {
      setLoading(true);
      setError('');
      console.log('Starting game with deckId:', deckId);
      const gameSession = await apiClient.startGame({ deckId: deckId });
      console.log('Game session received:', gameSession);
      setSession(gameSession);
      startTimeRef.current = Date.now();
    } catch (err) {
      console.error('Error starting game:', err);
      const errorMessage = err instanceof Error ? err.message : t('loadingGame');
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [deckId, navigate, t]);

  useEffect(() => {
    startGame();
  }, [startGame]);

  // Check browser compatibility on mount (but don't show error until user tries to record)
  useEffect(() => {
    // Check if MediaRecorder is supported
    if (typeof MediaRecorder === 'undefined') {
      console.warn('MediaRecorder is not supported in this browser');
    }

    // Check if getUserMedia is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn('getUserMedia is not supported in this browser');
      return;
    }

    // Check if we're on HTTPS or localhost (required for getUserMedia)
    const isSecureContext = window.isSecureContext || 
      window.location.protocol === 'https:' || 
      window.location.hostname === 'localhost' || 
      window.location.hostname === '127.0.0.1';
    
    if (!isSecureContext) {
      console.warn('getUserMedia requires HTTPS or localhost');
      return;
    }

    // Pre-request microphone access to reduce delay when user clicks record
    // This requests permission early so it's already granted when needed
    const preRequestMicrophone = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        preRequestedStreamRef.current = stream;
        console.log('Microphone access pre-requested successfully');
        // Don't stop the stream - keep it active for immediate use
      } catch (err) {
        // Permission denied or error - that's okay, we'll request again when user clicks
        console.log('Pre-requesting microphone access failed (this is okay):', err);
        preRequestedStreamRef.current = null;
      }
    };

    // Request after a short delay to not block page load
    const timeoutId = setTimeout(preRequestMicrophone, 500);
    
    return () => {
      clearTimeout(timeoutId);
      // Clean up pre-requested stream on unmount
      if (preRequestedStreamRef.current) {
        preRequestedStreamRef.current.getTracks().forEach(track => track.stop());
        preRequestedStreamRef.current = null;
      }
    };
  }, []);

  // Audio level monitoring - use time domain data for accurate volume
  useEffect(() => {
    if (!isRecording) {
      setAudioLevel(0);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      return;
    }

    // Wait a bit for audio context and analyser to be set up
    // Check periodically if they're ready
    const checkAndStartMonitoring = () => {
      if (!audioContextRef.current || !analyserRef.current) {
        // If not ready yet, check again in a short time
        setTimeout(checkAndStartMonitoring, 50);
        return;
      }

      // Now start monitoring
      const updateAudioLevel = () => {
        if (!analyserRef.current || !isRecording) {
          if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
            animationFrameRef.current = null;
          }
          return;
        }

        // Use time domain data for accurate volume/amplitude measurement
        const bufferLength = analyserRef.current.fftSize;
        const dataArray = new Uint8Array(bufferLength);
        analyserRef.current.getByteTimeDomainData(dataArray);
        
        // Calculate RMS (Root Mean Square) for accurate volume
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          const normalized = (dataArray[i] - 128) / 128;
          sum += normalized * normalized;
        }
        const rms = Math.sqrt(sum / bufferLength);
        
        // Normalize to 0-1 and apply smoothing
        const normalizedLevel = Math.min(rms * 2, 1); // Multiply by 2 for better sensitivity
        setAudioLevel(normalizedLevel);

        animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
      };

      updateAudioLevel();
    };

    // Start checking
    checkAndStartMonitoring();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    };
  }, [isRecording]);

  // Clear feedback and recognition when moving to next word
  useEffect(() => {
    if (currentWordIndex >= 0) {
      setLastFeedback(null);
      setShowFeedback(false);
      setIsProcessing(false);
      setRealTimeRecognition('');
      realTimeRecognitionRef.current = ''; // Clear ref when moving to next word
      setIsPlaying(false);
      setError(''); // Clear any errors
      shouldStopRecognitionRef.current = false; // Reset stop flag for next word
      
      // Stop and cleanup audio player
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current = null;
      }
      
      // Clean up old audio URL before clearing state
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
        audioUrlRef.current = null;
      }
      setAudioUrl(null);
      setRecordedAudioBlob(null);
    }
  }, [currentWordIndex]);

  // Web Speech API for real-time recognition
  useEffect(() => {
    if (!isRecording || showFeedback) {
      // Stop recognition when not recording or when showing feedback
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // Already stopped
        }
        recognitionRef.current = null;
      }
      if (!isRecording) {
        setRealTimeRecognition('');
        // Don't clear the ref here - we need it for capture in onstop
      }
      return;
    }

    // Check if browser supports Web Speech API
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.log('Web Speech API not supported in this browser');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'zh-HK'; // Try Cantonese (Hong Kong), fallback to zh-CN if not available

    recognition.onresult = (event: any) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      // Show both interim and final results
      const displayText = finalTranscript || interimTranscript;
      if (displayText) {
        setRealTimeRecognition(displayText);
        realTimeRecognitionRef.current = displayText; // Store in ref for reliable access
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      // If language not supported, try Chinese
      if (event.error === 'language-not-supported' && recognition.lang === 'zh-HK') {
        recognition.lang = 'zh-CN';
        try {
          recognition.start();
        } catch (e) {
          console.log('Speech recognition not available');
        }
      }
    };

    recognition.onend = () => {
      // Only restart if:
      // 1. Still recording
      // 2. Not showing feedback
      // 3. Recognition ref still points to this instance
      // 4. We haven't explicitly requested to stop
      if (isRecording && !showFeedback && !shouldStopRecognitionRef.current && recognitionRef.current === recognition) {
        try {
          recognition.start();
        } catch (e) {
          // Already started or error - don't restart
          console.log('Could not restart recognition:', e);
        }
      } else {
        // Recognition should stop, clear the ref
        if (recognitionRef.current === recognition) {
          recognitionRef.current = null;
        }
      }
    };

    recognitionRef.current = recognition;
    try {
      recognition.start();
    } catch (e) {
      console.log('Could not start speech recognition:', e);
    }

    return () => {
      if (recognitionRef.current === recognition) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // Already stopped
        }
        recognitionRef.current = null;
      }
    };
  }, [isRecording, showFeedback]);

  // Cleanup audio context and audio URL on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current = null;
      }
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
        audioUrlRef.current = null;
      }
    };
  }, []);

  const handleRecord = async () => {
    if (!session) return;

    // If already recording, stop it
    if (isRecording && mediaRecorderRef.current) {
      // Set flag to prevent recognition from restarting
      shouldStopRecognitionRef.current = true;
      
      // Clear auto-stop timeout if exists
      if ((mediaRecorderRef.current as any)._autoStopTimeout) {
        clearTimeout((mediaRecorderRef.current as any)._autoStopTimeout);
      }
      if (mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
      // Stop Web Speech API recognition
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
          recognitionRef.current = null;
        } catch (e) {
          // Already stopped
        }
      }
      return;
    }

    try {
      setLastFeedback(null);
      setShowFeedback(false);
      setError(''); // Clear any previous errors
      setAudioLevel(0);
      setRealTimeRecognition('');
      realTimeRecognitionRef.current = ''; // Clear ref when starting new recording
      
      // Stop any ongoing audio playback
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current = null;
        setIsPlaying(false);
      }
      
      // Clear previous recording data
      setRecordedAudioBlob(null);
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
        audioUrlRef.current = null;
      }
      setAudioUrl(null);
      
      // Only show "Starting..." if we don't have a pre-requested stream
      // (if we have one, it should be instant)
      if (!preRequestedStreamRef.current || !preRequestedStreamRef.current.active) {
        setIsStarting(true);
      }
      
      // Always get a fresh stream for recording (MediaRecorder works better with fresh streams)
      // But if we have a pre-requested stream, permission is already granted so this should be fast
      const hasPreRequested = preRequestedStreamRef.current && preRequestedStreamRef.current.active;
      
      if (hasPreRequested) {
        // Permission already granted, so this should be very fast
        // Clear "Starting..." immediately since permission is already granted
        setIsStarting(false);
      }
      
      // Always get a fresh stream for the actual recording
      // This ensures MediaRecorder works correctly
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Hide "Starting..." if we didn't already (in case pre-request failed)
      setIsStarting(false);
      
      // Update pre-requested stream for next time (but don't use it for recording)
      if (preRequestedStreamRef.current) {
        // Stop the old pre-requested stream since we have a new one
        preRequestedStreamRef.current.getTracks().forEach(track => track.stop());
      }
      preRequestedStreamRef.current = stream;
      
      // Show recording state
      setIsRecording(true);
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      // Create a fresh audioChunks array for this recording session
      const audioChunks: Blob[] = [];
      
      // Store stream reference for cleanup
      const streamRef = stream;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Capture real-time recognition from ref (more reliable than state)
        const capturedRealTimeRecognition = realTimeRecognitionRef.current || realTimeRecognition;
        // Set flag to prevent recognition from restarting
        shouldStopRecognitionRef.current = true;
        
        // Stop Web Speech API recognition immediately
        if (recognitionRef.current) {
          try {
            recognitionRef.current.stop();
            recognitionRef.current = null;
          } catch (e) {
            // Already stopped
          }
        }
        
        // Set recording to false immediately to prevent recognition from restarting
        setIsRecording(false);
        
        // Show processing message
        setIsProcessing(true);
        
        // Clean up audio analysis
        if (audioContextRef.current) {
          audioContextRef.current.close();
          audioContextRef.current = null;
        }
        analyserRef.current = null;
        setAudioLevel(0);

        // Check if we actually have audio data
        if (audioChunks.length === 0) {
          console.error('No audio data recorded');
          // Stop all media tracks
          streamRef.getTracks().forEach((track) => track.stop());
          setIsProcessing(false); // Clear processing state on error
          setError(t('recordingFailed') || 'Recording failed. Please try again.');
          return;
        }

        // Create a fresh blob from the chunks
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        
        // Verify blob has data
        if (audioBlob.size === 0) {
          console.error('Audio blob is empty');
          // Stop all media tracks
          streamRef.getTracks().forEach((track) => track.stop());
          setIsProcessing(false); // Clear processing state on error
          setError(t('recordingFailed') || 'Recording failed. Please try again.');
          return;
        }

        console.log('Recording complete:', { 
          chunks: audioChunks.length, 
          blobSize: audioBlob.size,
          wordIndex: currentWordIndex 
        });

        const responseTime = Date.now() - startTimeRef.current;

        // Clean up previous audio URL and blob before creating new ones
        if (audioUrlRef.current) {
          URL.revokeObjectURL(audioUrlRef.current);
          audioUrlRef.current = null;
        }
        setRecordedAudioBlob(null);
        setAudioUrl(null);
        
        // Create new audio URL for this recording
        const url = URL.createObjectURL(audioBlob);
        audioUrlRef.current = url;
        setRecordedAudioBlob(audioBlob);
        setAudioUrl(url);

        try {
          const result = await apiClient.submitPronunciation({
            sessionId: session.id,
            wordId: session.words[currentWordIndex].wordId,
            audioData: audioBlob,
            responseTime,
            realTimeRecognition: capturedRealTimeRecognition,
          });

          // Show feedback immediately with comparison details
          setLastFeedback({
            isCorrect: result.isCorrect,
            feedback: result.feedback,
            recognizedText: result.recognizedText,
            expectedText: result.expectedText,
            expectedJyutping: result.expectedJyutping,
          });
          setShowFeedback(true);
          setIsProcessing(false); // Hide processing message when feedback is shown
          setRealTimeRecognition(''); // Clear real-time recognition after showing feedback
          realTimeRecognitionRef.current = ''; // Clear ref after showing feedback

          // Update session
          const updatedWords = [...session.words];
          updatedWords[currentWordIndex] = {
            ...updatedWords[currentWordIndex],
            isCorrect: result.isCorrect,
            responseTime,
          };

          setSession({ ...session, words: updatedWords });

          // Don't auto-advance - user will click Next button
        } catch (err) {
          console.error('Failed to submit pronunciation:', err);
          setIsProcessing(false); // Hide processing message on error
          setError(t('submissionFailed') || 'Failed to submit pronunciation. Please try again.');
        } finally {
          // Stop all media tracks
          streamRef.getTracks().forEach((track) => track.stop());
        }
      };

      // Handle MediaRecorder errors
      mediaRecorder.onerror = (event: any) => {
        console.error('MediaRecorder error:', event);
        setIsRecording(false);
        setAudioLevel(0);
        setError(t('recordingError') || 'An error occurred during recording. Please try again.');
        // Stop all media tracks
        stream.getTracks().forEach((track) => track.stop());
      };

      // Start recording IMMEDIATELY - don't wait for AudioContext setup
      // Using timeslice of 100ms to ensure data chunks are collected regularly
      try {
        mediaRecorder.start(100);
      } catch (startErr) {
        console.error('Failed to start MediaRecorder:', startErr);
        setIsStarting(false);
        setIsRecording(false);
        setAudioLevel(0);
        setError(t('recordingStartFailed') || 'Failed to start recording. Please try again.');
        stream.getTracks().forEach((track) => track.stop());
        return;
      }
      
      // Stop recording after 5 seconds (or user can stop manually)
      const autoStopTimeout = setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop();
        }
      }, 5000);
      
      // Store timeout so we can clear it if user stops manually
      (mediaRecorder as any)._autoStopTimeout = autoStopTimeout;
      
      // Reset stop flag when starting new recording
      shouldStopRecognitionRef.current = false;
      
      // Set up audio analysis for volume bar ASYNCHRONOUSLY (non-blocking)
      // This allows recording to start immediately while volume bar setup happens in background
      (async () => {
        try {
          const audioContext = new AudioContext();
          
          // Resume audio context if suspended (required in some browsers)
          if (audioContext.state === 'suspended') {
            await audioContext.resume();
          }
          
          const analyser = audioContext.createAnalyser();
          analyser.fftSize = 256;
          analyser.smoothingTimeConstant = 0.8; // Smooth the volume readings
          const source = audioContext.createMediaStreamSource(stream);
          source.connect(analyser);
          
          audioContextRef.current = audioContext;
          analyserRef.current = analyser;
          
          console.log('Audio context set up:', { 
            state: audioContext.state, 
            analyserReady: !!analyser 
          });
        } catch (err) {
          console.error('Failed to set up audio analysis:', err);
          // Don't fail recording if audio analysis setup fails
        }
      })();
    } catch (err: any) {
      console.error('Failed to access microphone:', err);
      setIsStarting(false);
      setIsRecording(false);
      setAudioLevel(0);
      
      // Check if browser supports getUserMedia
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError(t('browserNotSupported') || 'Your browser does not support audio recording. Please use a modern browser like Chrome, Firefox, or Safari.');
        return;
      }
      
      // Check if we're on HTTPS or localhost (required for getUserMedia)
      const isSecureContext = window.isSecureContext || 
        window.location.protocol === 'https:' || 
        window.location.hostname === 'localhost' || 
        window.location.hostname === '127.0.0.1';
      
      if (!isSecureContext) {
        setError(t('httpsRequired') || 'Microphone access requires HTTPS. Please access this site over HTTPS or use localhost.');
        return;
      }
      
      // Provide specific error messages based on error type
      let errorMessage = t('microphoneAccessFailed') || 'Failed to access microphone. Please check your permissions and try again.';
      
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        errorMessage = t('microphonePermissionDenied') || 'Microphone permission was denied. Please allow microphone access in your browser settings and try again.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        errorMessage = t('microphoneNotFound') || 'No microphone found. Please connect a microphone and try again.';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        errorMessage = t('microphoneInUse') || 'Microphone is already in use by another application. Please close other applications using the microphone and try again.';
      } else if (err.name === 'OverconstrainedError') {
        errorMessage = t('microphoneConstraintsError') || 'Microphone constraints could not be satisfied. Please try a different microphone.';
      } else if (err.message) {
        errorMessage = `${t('microphoneAccessFailed') || 'Failed to access microphone'}: ${err.message}`;
      }
      
      setError(errorMessage);
    }
  };

  const moveToNextWord = () => {
    if (!session) return;

    if (currentWordIndex < session.words.length - 1) {
      setCurrentWordIndex(currentWordIndex + 1);
      startTimeRef.current = Date.now();
    } else {
      endGame();
    }
  };

  const handleSwipe = (_direction: 'left' | 'right') => {
    // Skip current word
    moveToNextWord();
  };

  const handlePlayRecording = () => {
    if (!audioUrl || !recordedAudioBlob) return;

    // Clean up previous audio if exists
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current = null;
    }

    // Create new audio element from the current audio URL
    const audio = new Audio(audioUrl);
    audioPlayerRef.current = audio;

    audio.onplay = () => {
      console.log('Playing audio:', { url: audioUrl, blobSize: recordedAudioBlob.size });
      setIsPlaying(true);
    };
    audio.onended = () => {
      setIsPlaying(false);
      audioPlayerRef.current = null;
    };
    audio.onerror = (err) => {
      console.error('Audio playback error:', err);
      setIsPlaying(false);
      audioPlayerRef.current = null;
    };

    audio.play().catch((err) => {
      console.error('Failed to play audio:', err);
      setIsPlaying(false);
      audioPlayerRef.current = null;
    });
  };

  const handleStopPlayback = () => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current.currentTime = 0;
      audioPlayerRef.current = null;
      setIsPlaying(false);
    }
  };

  const endGame = async () => {
    if (!session) return;

    try {
      const completedSession = await apiClient.endGame(session.id);
      setFinalScore(completedSession.score || 0);
      setGameComplete(true);
    } catch (err) {
      console.error('Failed to end game:', err);
    }
  };

  const handleBackToDashboard = () => {
    navigate('/student');
  };

  if (loading) {
    return <div className="loading">{t('loadingGame')}</div>;
  }

  if (error) {
    return (
      <div className="game-page">
        <div className="error-message">{error}</div>
        <button onClick={() => navigate('/student')} className="btn btn-primary">
          {t('backToDashboard')}
        </button>
      </div>
    );
  }

  if (gameComplete && finalScore !== null) {
    const correctCount = session?.words.filter((w) => w.isCorrect).length || 0;
    const totalWords = session?.words.length || 0;

    return (
      <div className="game-page">
        <div className="game-complete">
          <div className="celebration-emoji">🎉</div>
          <h1>{t('gameComplete')}</h1>
          <div className="score-display">
            <div className="score-value">{finalScore}</div>
            <div className="score-label">{t('finalScore')}</div>
          </div>
          <div className="stats">
            <div className="stat-item">
              <div className="stat-value">{correctCount}</div>
              <div className="stat-label">{t('correct')}</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{totalWords - correctCount}</div>
              <div className="stat-label">{t('incorrect')}</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{totalWords}</div>
              <div className="stat-label">{t('totalWords')}</div>
            </div>
          </div>
          <button onClick={handleBackToDashboard} className="btn btn-primary btn-large">
            {t('backToDashboard')}
          </button>
        </div>
      </div>
    );
  }

  if (!session || currentWordIndex >= session.words.length) {
    return <div className="loading">{t('loading')}</div>;
  }

  const currentWord = session.words[currentWordIndex];
  const progress = ((currentWordIndex + 1) / session.words.length) * 100;

  return (
    <div className="game-page">
      <div className="game-header">
        <button onClick={handleBackToDashboard} className="btn btn-secondary">
          {t('exitGame')}
        </button>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
        </div>
        <div className="word-counter">
          {t('wordCounter').replace('{current}', String(currentWordIndex + 1)).replace('{total}', String(session.words.length))}
        </div>
      </div>

      <div className="game-content">
        {error && (
          <div className="error-message" style={{ marginBottom: '1rem' }}>
            {error}
            <button 
              onClick={() => setError('')} 
              style={{ marginLeft: '1rem', padding: '0.25rem 0.5rem', fontSize: '0.9rem' }}
            >
              ✕
            </button>
          </div>
        )}
        <SwipeCard
          word={currentWord.text}
          onSwipe={handleSwipe}
          onComplete={handleRecord}
          disabled={isRecording || isStarting}
          showFeedback={showFeedback}
          feedback={lastFeedback}
          realTimeRecognition={isRecording ? realTimeRecognition : ''}
        />

        {/* Volume Bar */}
        {isRecording && (
          <div className="volume-bar-container">
            <div className="volume-bar-label">{t('speechDetected')}</div>
            <div className="volume-bar">
              <div 
                className="volume-bar-fill" 
                style={{ width: `${audioLevel * 100}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Starting Message - shown while requesting microphone access */}
        {isStarting && (
          <div className="processing-message">
            <div className="processing-spinner">🎤</div>
            <div className="processing-text">{t('startingRecording') || 'Starting recording...'}</div>
          </div>
        )}

        {/* Processing Message */}
        {isProcessing && (
          <div className="processing-message">
            <div className="processing-spinner">⏳</div>
            <div className="processing-text">{t('processingPronunciation')}</div>
          </div>
        )}

        {/* Playback Button - shown after recording when feedback is displayed */}
        {showFeedback && recordedAudioBlob && audioUrl && (
          <div className="playback-container">
            <button
              onClick={isPlaying ? handleStopPlayback : handlePlayRecording}
              className={`btn btn-secondary btn-playback ${isPlaying ? 'playing' : ''}`}
            >
              {isPlaying ? '⏸️ ' + t('stop') : '▶️ ' + t('playRecording')}
            </button>
          </div>
        )}

        <div className="game-actions">
          {!showFeedback && !isProcessing ? (
            <>
              {isRecording ? (
                <>
                  <button
                    onClick={handleRecord}
                    className="btn btn-primary btn-record recording"
                  >
                    ⏹️ {t('stopRecording')}
                  </button>
                  <button
                    onClick={handleSwipe.bind(null, 'left')}
                    className="btn btn-secondary"
                    disabled={true}
                  >
                    ⏭️ {t('skipWord')}
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={handleRecord}
                    className="btn btn-primary btn-record"
                    disabled={showFeedback || isProcessing}
                  >
                    🎤 {t('recordPronunciation')}
                  </button>
                  <button
                    onClick={handleSwipe.bind(null, 'left')}
                    className="btn btn-secondary"
                    disabled={isRecording || showFeedback || isProcessing}
                  >
                    ⏭️ {t('skipWord')}
                  </button>
                </>
              )}
            </>
          ) : (
            <button
              onClick={moveToNextWord}
              className="btn btn-primary btn-next"
            >
              ➡️ {t('nextWord')}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default GamePage;

