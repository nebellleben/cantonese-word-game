import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { apiClient } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { GameStatistics, Deck } from '../types';
import LanguageSwitcher from '../components/LanguageSwitcher';
import './StatisticsPage.css';

const StatisticsPage: React.FC = () => {
  const { logout } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [statistics, setStatistics] = useState<GameStatistics | null>(null);
  const [decks, setDecks] = useState<Deck[]>([]);
  const [selectedDeckId, setSelectedDeckId] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedDeckId) {
      loadStatistics();
    }
  }, [selectedDeckId]);

  const loadData = async () => {
    try {
      const [deckList, stats] = await Promise.all([
        apiClient.getDecks(),
        apiClient.getStatistics(undefined, undefined),
      ]);
      setDecks(deckList);
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const stats = await apiClient.getStatistics(
        undefined,
        selectedDeckId === 'all' ? undefined : selectedDeckId
      );
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="loading">{t('loading')}</div>;
  }

  if (!statistics) {
    return <div className="error">{t('error')}</div>;
  }

  return (
    <div className="statistics-page">
      <div className="header">
        <h1>📊 {t('statistics')}</h1>
        <div className="header-actions">
          <LanguageSwitcher />
          <button onClick={() => navigate('/student')} className="btn btn-secondary">
            {t('backToDashboard')}
          </button>
          <button onClick={handleLogout} className="btn btn-secondary">
            {t('logout')}
          </button>
        </div>
      </div>

      <div className="container">
        <div className="card">
          <h2>📈 {t('overview')}</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{statistics.totalGames}</div>
              <div className="stat-label">{t('totalGames')}</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{Math.round(statistics.averageScore)}</div>
              <div className="stat-label">{t('averageScore')}</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{statistics.bestScore}</div>
              <div className="stat-label">{t('bestScore')}</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{statistics.currentStreak}</div>
              <div className="stat-label">{t('currentStreak')}</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{statistics.longestStreak}</div>
              <div className="stat-label">{t('longestStreak')}</div>
            </div>
          </div>
        </div>

        <div className="card">
          <h2>📅 {t('scoreHistory')}</h2>
          <div className="form-group">
            <label htmlFor="deck-filter">{t('filterByDeck')}</label>
            <select
              id="deck-filter"
              value={selectedDeckId}
              onChange={(e) => setSelectedDeckId(e.target.value)}
            >
              <option value="all">{t('allDecks')}</option>
              {decks.map((deck) => (
                <option key={deck.id} value={deck.id}>
                  {deck.name}
                </option>
              ))}
            </select>
          </div>

          {statistics.scoresByDate.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={statistics.scoresByDate}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="score" fill="#ff6b9d" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">{t('noGameData')}</p>
          )}
        </div>

        <div className="card">
          <h2>⚠️ {t('top20WrongWords')}</h2>
          {statistics.topWrongWords.length > 0 ? (
            <div className="wrong-words-list">
              {statistics.topWrongWords
                .sort((a, b) => b.wrongCount - a.wrongCount)
                .slice(0, 20)
                .map((word, index) => (
                  <div key={word.wordId} className="wrong-word-item">
                    <div className="word-rank">#{index + 1}</div>
                    <div className="word-text">{word.word}</div>
                    <div className="word-stats">
                      <span className="wrong-count">{word.wrongCount} {t('timesWrong')}</span>
                      <span className="wrong-ratio">
                        ({Math.round(word.ratio * 100)}% {t('errorRate')})
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          ) : (
            <p className="no-data">{t('noIncorrectWords')}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatisticsPage;

