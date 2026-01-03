import React, { useState, useEffect, useRef } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import './SwipeCard.css';

interface SwipeCardProps {
  word: string;
  onSwipe: (direction: 'left' | 'right') => void;
  onComplete: () => void;
  disabled?: boolean;
  showFeedback?: boolean;
  feedback?: { 
    isCorrect: boolean; 
    feedback?: string;
    recognizedText?: string;
    expectedText?: string;
    expectedJyutping?: string;
  } | null;
}

const SwipeCard: React.FC<SwipeCardProps> = ({
  word,
  onSwipe,
  onComplete,
  disabled = false,
  showFeedback = false,
  feedback = null,
}) => {
  const { t } = useLanguage();
  const [startX, setStartX] = useState(0);
  const [startY, setStartY] = useState(0);
  const [currentX, setCurrentX] = useState(0);
  const [currentY, setCurrentY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const handleStart = (clientX: number, clientY: number) => {
    if (disabled) return;
    setStartX(clientX);
    setStartY(clientY);
    setIsDragging(true);
  };

  const handleMove = (clientX: number, clientY: number) => {
    if (!isDragging || disabled) return;
    setCurrentX(clientX - startX);
    setCurrentY(clientY - startY);
  };

  const handleEnd = () => {
    if (!isDragging || disabled) return;

    const threshold = 100;
    const absX = Math.abs(currentX);
    const absY = Math.abs(currentY);

    if (absX > threshold && absX > absY) {
      // Horizontal swipe
      if (currentX > 0) {
        onSwipe('right');
      } else {
        onSwipe('left');
      }
    }

    // Reset
    setCurrentX(0);
    setCurrentY(0);
    setIsDragging(false);
  };

  // Mouse events
  const handleMouseDown = (e: React.MouseEvent) => {
    handleStart(e.clientX, e.clientY);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    handleMove(e.clientX, e.clientY);
  };

  const handleMouseUp = () => {
    handleEnd();
  };

  // Touch events
  const handleTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    handleStart(touch.clientX, touch.clientY);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    handleMove(touch.clientX, touch.clientY);
  };

  const handleTouchEnd = () => {
    handleEnd();
  };

  // Keyboard events
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (disabled) return;
      if (e.key === 'ArrowLeft') {
        onSwipe('left');
      } else if (e.key === 'ArrowRight') {
        onSwipe('right');
      } else if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onComplete();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [disabled, onSwipe, onComplete]);

  const rotation = currentX * 0.1;
  const opacity = 1 - Math.abs(currentX) / 300;

  return (
    <div
      ref={cardRef}
      className={`swipe-card ${isDragging ? 'dragging' : ''} ${disabled ? 'disabled' : ''}`}
      style={{
        transform: `translate(${currentX}px, ${currentY}px) rotate(${rotation}deg)`,
        opacity: Math.max(0.5, opacity),
      }}
      onMouseDown={handleMouseDown}
      onMouseMove={isDragging ? handleMouseMove : undefined}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <div className="card-content">
        <div className="word-display">{word}</div>
        
        {/* Feedback Display */}
        {showFeedback && feedback && (
          <div className={`feedback-container ${feedback.isCorrect ? 'correct' : 'incorrect'}`}>
            <div className="feedback-icon">
              {feedback.isCorrect ? '✓' : '✗'}
            </div>
            <div className="feedback-text">
              <div className="feedback-status">
                {feedback.isCorrect ? t('pronunciationCorrect') : t('pronunciationIncorrect')}
              </div>
              
              {/* Comparison Details */}
              <div className="feedback-comparison">
                {feedback.expectedText && (
                  <div className="comparison-row">
                    <span className="comparison-label">Expected word:</span>
                    <span className="comparison-value">{feedback.expectedText}</span>
                  </div>
                )}
                {feedback.expectedJyutping && (
                  <div className="comparison-row">
                    <span className="comparison-label">Expected pronunciation:</span>
                    <span className="comparison-value">{feedback.expectedJyutping}</span>
                  </div>
                )}
                {feedback.recognizedText && (
                  <div className="comparison-row">
                    <span className="comparison-label">Recognized pronunciation:</span>
                    <span className={`comparison-value ${feedback.isCorrect ? 'match' : 'mismatch'}`}>
                      {feedback.recognizedText}
                    </span>
                  </div>
                )}
              </div>
              
              {feedback.feedback && (
                <div className="feedback-message">
                  {feedback.feedback}
                </div>
              )}
            </div>
          </div>
        )}

        <div className="card-hint">
          {!disabled && !showFeedback && (
            <>
              <p>{t('swipeLeftToSkip')}</p>
              <p>{t('swipeRightToSkip')}</p>
              <p>{t('pressSpaceToRecord')}</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SwipeCard;

