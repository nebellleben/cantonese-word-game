import React, { useState, useEffect, useRef } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import './SwipeCard.css';

interface SwipeCardProps {
  word: string;
  onSwipe: (direction: 'left' | 'right') => void;
  onComplete: () => void;
  disabled?: boolean;
}

const SwipeCard: React.FC<SwipeCardProps> = ({
  word,
  onSwipe,
  onComplete,
  disabled = false,
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
        <div className="card-hint">
          {!disabled && (
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

