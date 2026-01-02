import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { Student, WrongWord, GameStatistics } from '../types';
import './TeacherDashboard.css';

const TeacherDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [students, setStudents] = useState<Student[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<string>('');
  const [studentStats, setStudentStats] = useState<GameStatistics | null>(null);
  const [wordErrorRatios, setWordErrorRatios] = useState<WrongWord[]>([]);
  const [activeTab, setActiveTab] = useState<'students' | 'words'>('students');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedStudentId && activeTab === 'students') {
      loadStudentStatistics();
    }
  }, [selectedStudentId, activeTab]);

  const loadData = async () => {
    try {
      const [studentList, wordRatios] = await Promise.all([
        apiClient.getStudents(),
        apiClient.getWordErrorRatios(),
      ]);
      setStudents(studentList);
      setWordErrorRatios(wordRatios);
      if (studentList.length > 0) {
        setSelectedStudentId(studentList[0].id);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStudentStatistics = async () => {
    try {
      const stats = await apiClient.getStatistics(selectedStudentId);
      setStudentStats(stats);
    } catch (error) {
      console.error('Failed to load student statistics:', error);
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
    <div className="teacher-dashboard">
      <div className="header">
        <h1>Teacher Dashboard</h1>
        <div className="header-actions">
          <span className="user-info">Welcome, {user?.username}!</span>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </div>

      <div className="container">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'students' ? 'active' : ''}`}
            onClick={() => setActiveTab('students')}
          >
            Student Statistics
          </button>
          <button
            className={`tab ${activeTab === 'words' ? 'active' : ''}`}
            onClick={() => setActiveTab('words')}
          >
            Word Error Ratios
          </button>
        </div>

        {activeTab === 'students' && (
          <>
            <div className="card">
              <h2>My Students</h2>
              {students.length > 0 ? (
                <>
                  <div className="form-group">
                    <label htmlFor="student-select">Select Student</label>
                    <select
                      id="student-select"
                      value={selectedStudentId}
                      onChange={(e) => setSelectedStudentId(e.target.value)}
                    >
                      {students.map((student) => (
                        <option key={student.id} value={student.id}>
                          {student.username} (Streak: {student.streak}, Total Score: {student.totalScore})
                        </option>
                      ))}
                    </select>
                  </div>

                  {studentStats && (
                    <div className="student-stats">
                      <h3>Statistics for {students.find((s) => s.id === selectedStudentId)?.username}</h3>
                      <div className="stats-grid">
                        <div className="stat-card">
                          <div className="stat-value">{studentStats.totalGames}</div>
                          <div className="stat-label">Total Games</div>
                        </div>
                        <div className="stat-card">
                          <div className="stat-value">{Math.round(studentStats.averageScore)}</div>
                          <div className="stat-label">Average Score</div>
                        </div>
                        <div className="stat-card">
                          <div className="stat-value">{studentStats.bestScore}</div>
                          <div className="stat-label">Best Score</div>
                        </div>
                        <div className="stat-card">
                          <div className="stat-value">{studentStats.currentStreak}</div>
                          <div className="stat-label">Current Streak</div>
                        </div>
                      </div>

                      {studentStats.scoresByDate.length > 0 && (
                        <div className="chart-container">
                          <h4>Score History</h4>
                          <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={studentStats.scoresByDate}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="date" />
                              <YAxis />
                              <Tooltip />
                              <Bar dataKey="score" fill="#667eea" />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      )}
                    </div>
                  )}
                </>
              ) : (
                <p className="no-data">No students assigned to you yet.</p>
              )}
            </div>
          </>
        )}

        {activeTab === 'words' && (
          <div className="card">
            <h2>Word Error Ratios</h2>
            <p>Words sorted by error ratio (descending)</p>
            {wordErrorRatios.length > 0 ? (
              <div className="word-error-list">
                {wordErrorRatios.map((word, index) => (
                  <div key={word.wordId} className="word-error-item">
                    <div className="word-rank">#{index + 1}</div>
                    <div className="word-text">{word.word}</div>
                    <div className="error-ratio">
                      <div className="ratio-bar">
                        <div
                          className="ratio-fill"
                          style={{ width: `${word.ratio * 100}%` }}
                        ></div>
                      </div>
                      <span className="ratio-text">
                        {Math.round(word.ratio * 100)}% ({word.wrongCount}/{word.totalAttempts})
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-data">No error data available yet.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherDashboard;

