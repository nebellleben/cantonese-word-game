import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import SwipeCard from '../SwipeCard';

describe('SwipeCard', () => {
  it('should render the word', () => {
    const onSwipe = vi.fn();
    const onComplete = vi.fn();

    render(
      <SwipeCard
        word="你好"
        onSwipe={onSwipe}
        onComplete={onComplete}
      />
    );

    expect(screen.getByText('你好')).toBeInTheDocument();
  });

  it('should show hints when not disabled', () => {
    const onSwipe = vi.fn();
    const onComplete = vi.fn();

    render(
      <SwipeCard
        word="你好"
        onSwipe={onSwipe}
        onComplete={onComplete}
        disabled={false}
      />
    );

    expect(screen.getByText(/Swipe left to skip/)).toBeInTheDocument();
    expect(screen.getByText(/Swipe right to skip/)).toBeInTheDocument();
  });

  it('should not show hints when disabled', () => {
    const onSwipe = vi.fn();
    const onComplete = vi.fn();

    render(
      <SwipeCard
        word="你好"
        onSwipe={onSwipe}
        onComplete={onComplete}
        disabled={true}
      />
    );

    expect(screen.queryByText(/Swipe left to skip/)).not.toBeInTheDocument();
  });
});

