import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/api';
import type { Deck } from '../types';
import './StudentDashboard.css';

const StudentDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDeck, setSelectedDeck] = useState<string>('');

  useEffect(() => {
    loadDecks();
  }, []);

  const loadDecks = async () => {
    try {
      const deckList = await apiClient.getDecks();
      setDecks(deckList);
      if (deckList.length > 0) {
        setSelectedDeck(deckList[0].id);
      }
    } catch (error) {
      console.error('Failed to load decks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartGame = () => {
    if (selectedDeck) {
      navigate(`/student/game?deckId=${selectedDeck}`);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="student-dashboard">
      <div className="header">
        <h1>Student Dashboard</h1>
        <div className="header-actions">
          <span className="user-info">Welcome, {user?.username}!</span>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </div>

      <div className="container">
        <div className="card">
          <h2>Start a Game</h2>
          <p>Choose a deck to practice and improve your Cantonese pronunciation!</p>

          <div className="form-group">
            <label htmlFor="deck-select">Select Deck</label>
            <select
              id="deck-select"
              value={selectedDeck}
              onChange={(e) => setSelectedDeck(e.target.value)}
              className="deck-select"
            >
              {decks.map((deck) => (
                <option key={deck.id} value={deck.id}>
                  {deck.name} ({deck.wordCount} words)
                </option>
              ))}
            </select>
            {decks.find((d) => d.id === selectedDeck)?.description && (
              <p className="deck-description">
                {decks.find((d) => d.id === selectedDeck)?.description}
              </p>
            )}
          </div>

          <button
            onClick={handleStartGame}
            className="btn btn-primary btn-large"
            disabled={!selectedDeck}
          >
            Start Game
          </button>
        </div>

        <div className="card">
          <h2>View Statistics</h2>
          <p>Review your progress and see how you're improving!</p>
          <button
            onClick={() => navigate('/student/statistics')}
            className="btn btn-secondary btn-large"
          >
            View Statistics
          </button>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;

