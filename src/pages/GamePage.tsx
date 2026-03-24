import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { apiClient } from '../services/api';
import SwipeCard from '../components/SwipeCard';
import type { GameSession } from '../types';
import './GamePage.css';

const GamePage: React.FC = () => {
  const { logout } = useAuth();
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

    // Check if Web Speech API is supported
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('Web Speech API not supported');
      return;
    }

    // Setup speech recognition
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'zh-HK';

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

      const recognitionText = finalTranscript || interimTranscript;
      if (recognitionText) {
        setRealTimeRecognition(recognitionText);
        realTimeRecognitionRef.current = recognitionText; // Store in ref
      }
    };

    recognition.onerror = (event: any) => {
      console.warn('Speech recognition error:', event.error);
    };

    recognition.onend = () => {
      if (isRecording && !shouldStopRecognitionRef.current) {
        try {
          recognition.start();
        } catch (e) {
          // Already started
        }
      }
    };

    try {
      recognition.start();
    } catch (e) {
      // Already started
    }

    return () => {
      if (recognitionRef.current) {
        shouldStopRecognitionRef.current = true;
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // Already stopped
        }
        recognitionRef.current = null;
      }
    };
  }, [isRecording, showFeedback]);

  // Recording functions
  const setupAudioContext = (stream: MediaStream) => {
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;

    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);

    audioContextRef.current = audioContext;
    analyserRef.current = analyser;
  };

  const cleanupAudioContext = () => {
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    analyserRef.current = null;
  };

  const handleRecord = async () => {
    if (isRecording) {
      stopRecording();
      return;
    }

    try {
      setError('');
      setIsStarting(true);

      let stream: MediaStream;

      // Use pre-requested stream if available
      if (preRequestedStreamRef.current) {
        stream = preRequestedStreamRef.current;
      } else {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      }

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      setupAudioContext(stream);

      const audioChunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        setRecordedAudioBlob(audioBlob);

        // Create audio URL for playback
        const url = URL.createObjectURL(audioBlob);
        audioUrlRef.current = url;
        setAudioUrl(url);

        // Stop all audio tracks
        stream.getTracks().forEach(track => track.stop());
        cleanupAudioContext();

        // Stop speech recognition
        shouldStopRecognitionRef.current = true;
        if (recognitionRef.current) {
          try {
            recognitionRef.current.stop();
          } catch (e) {
            // Already stopped
          }
          recognitionRef.current = null;
        }

        // Submit pronunciation after recording stops
        submitPronunciation(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setIsStarting(false);
    } catch (err) {
      console.error('Recording error:', err);
      setIsStarting(false);

      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          setError(t('microphonePermissionDenied'));
        } else if (err.name === 'NotFoundError') {
          setError(t('microphoneNotFound'));
        } else if (err.name === 'NotReadableError') {
          setError(t('microphoneInUse'));
        } else if (err.name === 'OverconstrainedError') {
          setError(t('microphoneConstraintsError'));
        } else {
          setError(t('microphoneAccessFailed'));
        }
      } else {
        setError(t('recordingError'));
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const submitPronunciation = async (audioBlob: Blob) => {
    if (!session) return;

    setIsProcessing(true);
    setShowFeedback(true);

    try {
      const currentWord = session.words[currentWordIndex];
      const responseTime = Date.now() - startTimeRef.current;

      const result = await apiClient.submitPronunciation({
        sessionId: session.id,
        wordId: currentWord.wordId,
        audioData: audioBlob,
        responseTime,
        realTimeRecognition: realTimeRecognitionRef.current || undefined,
      });

      const feedbackData = {
        isCorrect: result.isCorrect,
        feedback: result.feedback,
        recognizedText: result.recognizedText,
        expectedText: result.expectedText || currentWord.text,
        expectedJyutping: result.expectedJyutping || currentWord.jyutping,
      };

      setLastFeedback(feedbackData);

      const updatedSession = { ...session };
      updatedSession.words[currentWordIndex].isCorrect = result.isCorrect;
      setSession(updatedSession);
    } catch (err) {
      console.error('Failed to submit pronunciation:', err);
      setError(t('submissionFailed'));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSwipe = (direction: 'left' | 'right') => {
    if (!session) return;

    if (direction === 'right') {
      // Mark as correct
      const updatedSession = { ...session };
      updatedSession.words[currentWordIndex].isCorrect = true;
      setSession(updatedSession);
    }

    if (currentWordIndex < session.words.length - 1) {
      setCurrentWordIndex(currentWordIndex + 1);
    } else {
      endGame();
    }
  };

  const handleNextWord = () => {
    if (!session) return;

    if (currentWordIndex < session.words.length - 1) {
      setCurrentWordIndex(currentWordIndex + 1);
    } else {
      endGame();
    }
  };

  const handlePlayRecording = () => {
    if (!recordedAudioBlob) return;

    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current = null;
      setIsPlaying(false);
      return;
    }

    const audio = new Audio(audioUrl || URL.createObjectURL(recordedAudioBlob));
    audioPlayerRef.current = audio;
    setIsPlaying(true);

    audio.onended = () => {
      audioPlayerRef.current = null;
      setIsPlaying(false);
    };

    audio.play();
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

  const handleLogout = async () => {
    await logout();
    navigate('/login');
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
          <div className="summary-mark" aria-hidden="true">Result</div>
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
        <div className="header-right">
          <button onClick={handleLogout} className="btn btn-secondary btn-logout">
            {t('logout')}
          </button>
        </div>
      </div>

      <div className="game-content">
        {error && (
          <div className="error-message" style={{ marginBottom: '1rem' }}>
            {error}
            <button
              onClick={() => setError('')}
              className="inline-dismiss"
              type="button"
            >
              Close
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

        {/* Processing Message */}
        {isProcessing && (
          <div className="processing-message">
            <div className="processing-spinner">...</div>
            <div className="processing-text">{t('processingPronunciation')}</div>
          </div>
        )}

        {/* Playback Container */}
        {audioUrl && showFeedback && (
          <div className="playback-container">
            <button
              onClick={isPlaying ? handleStopPlayback : handlePlayRecording}
              className={`btn btn-secondary btn-playback ${isPlaying ? 'playing' : ''}`}
            >
              {isPlaying ? t('stop') : t('playRecording')}
            </button>
          </div>
        )}

        <div className="game-actions">
          <button
            onClick={handleRecord}
            className={`btn btn-primary btn-record ${isRecording ? 'recording' : ''}`}
            disabled={isProcessing || isStarting}
          >
            {isStarting
              ? t('loading')
              : isRecording
              ? t('stopRecording')
              : t('recordPronunciation')}
          </button>
          <button
            onClick={() => handleSwipe('left')}
            className="btn btn-secondary"
            disabled={isRecording || isProcessing || isStarting}
          >
            {t('skipWord')}
          </button>
          {showFeedback && (
            <button
              onClick={handleNextWord}
              className="btn btn-primary btn-next"
              disabled={isProcessing}
            >
              {t('nextWord')}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default GamePage;
