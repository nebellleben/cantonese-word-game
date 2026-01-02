import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { apiClient } from '../services/api';
import SwipeCard from '../components/SwipeCard';
import type { GameSession, GameWord } from '../types';
import './GamePage.css';

const GamePage: React.FC = () => {
  const { user } = useAuth();
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

  const startTimeRef = useRef<number>(Date.now());
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  useEffect(() => {
    if (!deckId) {
      navigate('/student');
      return;
    }

    startGame();
  }, [deckId]);

  const startGame = async () => {
    try {
      setLoading(true);
      const gameSession = await apiClient.startGame({ deckId: deckId! });
      setSession(gameSession);
      startTimeRef.current = Date.now();
    } catch (err) {
      setError(err instanceof Error ? err.message : t('loadingGame'));
    } finally {
      setLoading(false);
    }
  };

  const handleRecord = async () => {
    if (!session) return;

    try {
      setIsRecording(true);
      
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const audioChunks: Blob[] = [];
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const responseTime = Date.now() - startTimeRef.current;

        try {
          const result = await apiClient.submitPronunciation({
            sessionId: session.id,
            wordId: session.words[currentWordIndex].wordId,
            audioData: audioBlob,
            responseTime,
          });

          // Update session
          const updatedWords = [...session.words];
          updatedWords[currentWordIndex] = {
            ...updatedWords[currentWordIndex],
            isCorrect: result.isCorrect,
            responseTime,
          };

          setSession({ ...session, words: updatedWords });

          // Move to next word
          moveToNextWord();
        } catch (err) {
          console.error('Failed to submit pronunciation:', err);
        } finally {
          stream.getTracks().forEach((track) => track.stop());
          setIsRecording(false);
        }
      };

      mediaRecorder.start();
      
      // Stop recording after 5 seconds or when user clicks again
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop();
        }
      }, 5000);
    } catch (err) {
      console.error('Failed to access microphone:', err);
      // Fallback: submit without audio (for testing)
      const responseTime = Date.now() - startTimeRef.current;
      const result = await apiClient.submitPronunciation({
        sessionId: session.id,
        wordId: session.words[currentWordIndex].wordId,
        responseTime,
      });

      const updatedWords = [...session.words];
      updatedWords[currentWordIndex] = {
        ...updatedWords[currentWordIndex],
        isCorrect: result.isCorrect,
        responseTime,
      };

      setSession({ ...session, words: updatedWords });
      setIsRecording(false);
      moveToNextWord();
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

  const handleSwipe = (direction: 'left' | 'right') => {
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
          word={currentWord.word}
          onSwipe={handleSwipe}
          onComplete={handleRecord}
          disabled={isRecording}
        />

        <div className="game-actions">
          <button
            onClick={handleRecord}
            className={`btn btn-primary btn-record ${isRecording ? 'recording' : ''}`}
            disabled={isRecording}
          >
            {isRecording ? `🎤 ${t('recording')}` : `🎤 ${t('recordPronunciation')}`}
          </button>
          <button
            onClick={handleSwipe.bind(null, 'left')}
            className="btn btn-secondary"
            disabled={isRecording}
          >
            ⏭️ {t('skipWord')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default GamePage;

