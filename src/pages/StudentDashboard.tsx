import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { apiClient } from '../services/api';
import type { Deck } from '../types';
import LanguageSwitcher from '../components/LanguageSwitcher';
import './StudentDashboard.css';

const StudentDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const { t } = useLanguage();
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
    console.log('StudentDashboard: Start game clicked, selectedDeck:', selectedDeck);
    if (selectedDeck) {
      console.log('StudentDashboard: Navigating to game with deckId:', selectedDeck);
      navigate(`/student/game?deckId=${selectedDeck}`);
    } else {
      console.warn('StudentDashboard: No deck selected');
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="loading">{t('loading')}</div>;
  }

  return (
    <div className="student-dashboard">
      <div className="header">
        <h1>🎮 {t('studentDashboard')}</h1>
        <div className="header-actions">
          <LanguageSwitcher />
          <span className="user-info">{t('welcome')}, {user?.username}! 👋</span>
          <button onClick={handleLogout} className="btn btn-secondary">
            {t('logout')}
          </button>
        </div>
      </div>

      <div className="container">
        <div className="card">
          <h2>🎯 {t('startGame')}</h2>
          <p>{t('chooseDeck')}</p>

          <div className="form-group">
            <label htmlFor="deck-select">{t('selectDeck')}</label>
            <select
              id="deck-select"
              value={selectedDeck}
              onChange={(e) => setSelectedDeck(e.target.value)}
              className="deck-select"
            >
              {decks.map((deck) => (
                <option key={deck.id} value={deck.id}>
                  {deck.name} ({deck.wordCount} {t('words')})
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
            🚀 {t('startGame')}
          </button>
        </div>

        <div className="card">
          <h2>📊 {t('viewStatistics')}</h2>
          <p>{t('reviewProgress')}</p>
          <button
            onClick={() => navigate('/student/statistics')}
            className="btn btn-secondary btn-large"
          >
            📈 {t('viewStatistics')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;

