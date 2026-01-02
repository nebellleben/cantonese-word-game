import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { GameStatistics, Deck } from '../types';
import './StatisticsPage.css';

const StatisticsPage: React.FC = () => {
  const { user, logout } = useAuth();
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
        apiClient.getStatistics(undefined, 'all'),
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
    return <div className="loading">Loading statistics...</div>;
  }

  if (!statistics) {
    return <div className="error">Failed to load statistics</div>;
  }

  return (
    <div className="statistics-page">
      <div className="header">
        <h1>Statistics</h1>
        <div className="header-actions">
          <button onClick={() => navigate('/student')} className="btn btn-secondary">
            Back to Dashboard
          </button>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </div>

      <div className="container">
        <div className="card">
          <h2>Overview</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{statistics.totalGames}</div>
              <div className="stat-label">Total Games</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{Math.round(statistics.averageScore)}</div>
              <div className="stat-label">Average Score</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{statistics.bestScore}</div>
              <div className="stat-label">Best Score</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{statistics.currentStreak}</div>
              <div className="stat-label">Current Streak</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{statistics.longestStreak}</div>
              <div className="stat-label">Longest Streak</div>
            </div>
          </div>
        </div>

        <div className="card">
          <h2>Score History</h2>
          <div className="form-group">
            <label htmlFor="deck-filter">Filter by Deck</label>
            <select
              id="deck-filter"
              value={selectedDeckId}
              onChange={(e) => setSelectedDeckId(e.target.value)}
            >
              <option value="all">All Decks</option>
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
                <Bar dataKey="score" fill="#667eea" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No game data available yet. Start playing to see your progress!</p>
          )}
        </div>

        <div className="card">
          <h2>Top 20 Wrongly Pronounced Words</h2>
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
                      <span className="wrong-count">{word.wrongCount} times wrong</span>
                      <span className="wrong-ratio">
                        ({Math.round(word.ratio * 100)}% error rate)
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          ) : (
            <p className="no-data">No incorrect words recorded yet. Keep practicing!</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatisticsPage;

