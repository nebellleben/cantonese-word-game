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
  const [realTimeRecognition, setRealTimeRecognition] = useState<string>('');

  const startTimeRef = useRef<number>(Date.now());
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const recognitionRef = useRef<any>(null);
  const shouldStopRecognitionRef = useRef<boolean>(false);

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

  // Audio level monitoring - use time domain data for accurate volume
  useEffect(() => {
    if (!isRecording || !audioContextRef.current || !analyserRef.current) {
      setAudioLevel(0);
      return;
    }

    const updateAudioLevel = () => {
      if (!analyserRef.current) return;

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

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isRecording]);

  // Clear feedback and recognition when moving to next word
  useEffect(() => {
    if (currentWordIndex >= 0) {
      setLastFeedback(null);
      setShowFeedback(false);
      setRealTimeRecognition('');
      shouldStopRecognitionRef.current = false; // Reset stop flag for next word
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

  // Cleanup audio context on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
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
      setIsRecording(true);
      setLastFeedback(null);
      setShowFeedback(false);
      setAudioLevel(0);
      setRealTimeRecognition('');
      
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      // Set up audio analysis for volume bar
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      const audioChunks: Blob[] = [];
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
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
        
        // Clean up audio analysis
        if (audioContextRef.current) {
          audioContextRef.current.close();
          audioContextRef.current = null;
        }
        analyserRef.current = null;
        setAudioLevel(0);

        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const responseTime = Date.now() - startTimeRef.current;

        try {
          const result = await apiClient.submitPronunciation({
            sessionId: session.id,
            wordId: session.words[currentWordIndex].wordId,
            audioData: audioBlob,
            responseTime,
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
          setRealTimeRecognition(''); // Clear real-time recognition after showing feedback

          // Update session
          const updatedWords = [...session.words];
          updatedWords[currentWordIndex] = {
            ...updatedWords[currentWordIndex],
            isCorrect: result.isCorrect,
            responseTime,
          };

          setSession({ ...session, words: updatedWords });

          // Move to next word after showing feedback for 2 seconds
          setTimeout(() => {
            moveToNextWord();
          }, 2000);
        } catch (err) {
          console.error('Failed to submit pronunciation:', err);
        } finally {
          // Stop all media tracks
          stream.getTracks().forEach((track) => track.stop());
        }
      };

      mediaRecorder.start();
      
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
    } catch (err) {
      console.error('Failed to access microphone:', err);
      setIsRecording(false);
      setAudioLevel(0);
      
      // Fallback: submit without audio (for testing)
      const responseTime = Date.now() - startTimeRef.current;
      try {
        const result = await apiClient.submitPronunciation({
          sessionId: session.id,
          wordId: session.words[currentWordIndex].wordId,
          responseTime,
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
        setRealTimeRecognition(''); // Clear real-time recognition after showing feedback

        const updatedWords = [...session.words];
        updatedWords[currentWordIndex] = {
          ...updatedWords[currentWordIndex],
          isCorrect: result.isCorrect,
          responseTime,
        };

        setSession({ ...session, words: updatedWords });

        // Move to next word after showing feedback for 2 seconds
        setTimeout(() => {
          moveToNextWord();
        }, 2000);
      } catch (submitErr) {
        console.error('Failed to submit pronunciation:', submitErr);
      }
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
        <SwipeCard
          word={currentWord.text}
          onSwipe={handleSwipe}
          onComplete={handleRecord}
          disabled={isRecording}
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

        <div className="game-actions">
          <button
            onClick={handleRecord}
            className={`btn btn-primary btn-record ${isRecording ? 'recording' : ''}`}
            disabled={showFeedback}
          >
            {isRecording ? `🎤 ${t('recording')}` : `🎤 ${t('recordPronunciation')}`}
          </button>
          <button
            onClick={handleSwipe.bind(null, 'left')}
            className="btn btn-secondary"
            disabled={isRecording || showFeedback}
          >
            ⏭️ {t('skipWord')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default GamePage;

