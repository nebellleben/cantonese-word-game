import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { apiClient } from '../services/api';
import type { Deck, Word, Student, Teacher, GameStatistics } from '../types';
import LanguageSwitcher from '../components/LanguageSwitcher';
import './AdminDashboard.css';

const AdminDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'words' | 'associations' | 'statistics' | 'passwords'>('words');
  
  // Word management state
  const [decks, setDecks] = useState<Deck[]>([]);
  const [selectedDeckId, setSelectedDeckId] = useState<string>('');
  const [words, setWords] = useState<Word[]>([]);
  const [newDeckName, setNewDeckName] = useState('');
  const [newDeckDescription, setNewDeckDescription] = useState('');
  const [newWordText, setNewWordText] = useState('');
  
  // Association state
  const [students, setStudents] = useState<Student[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<string>('');
  const [selectedTeacherId, setSelectedTeacherId] = useState<string>('');
  
  // Statistics state
  const [selectedStudentForStats, setSelectedStudentForStats] = useState<string>('');
  const [studentStats, setStudentStats] = useState<GameStatistics | null>(null);
  const [allStudentsStats, setAllStudentsStats] = useState<GameStatistics | null>(null);
  
  // Password management state
  const [selectedUserForPassword, setSelectedUserForPassword] = useState<string>('');
  const [newPassword, setNewPassword] = useState('');
  
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedDeckId && activeTab === 'words') {
      loadWords();
    }
  }, [selectedDeckId, activeTab]);

  useEffect(() => {
    if (selectedStudentForStats && activeTab === 'statistics') {
      loadStudentStatistics();
    }
  }, [selectedStudentForStats, activeTab]);

  const loadInitialData = async () => {
    try {
      const [deckList, studentList, teacherList, allStats] = await Promise.all([
        apiClient.getDecks(),
        apiClient.getStudents(),
        apiClient.getStudents().then(students => 
          students.map(s => ({ ...s, role: 'teacher' as const, studentIds: [] }))
        ),
        apiClient.getStatistics(),
      ]);
      setDecks(deckList);
      setStudents(studentList);
      setTeachers(teacherList as Teacher[]);
      setAllStudentsStats(allStats);
      if (deckList.length > 0) {
        setSelectedDeckId(deckList[0].id);
      }
      if (studentList.length > 0) {
        setSelectedStudentForStats(studentList[0].id);
        setSelectedStudentId(studentList[0].id);
        setSelectedUserForPassword(studentList[0].id);
      }
      if (teacherList.length > 0) {
        setSelectedTeacherId((teacherList as Teacher[])[0].id);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
      showMessage('error', 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadWords = async () => {
    try {
      const wordList = await apiClient.getWordsByDeck(selectedDeckId);
      setWords(wordList);
    } catch (error) {
      console.error('Failed to load words:', error);
    }
  };

  const loadStudentStatistics = async () => {
    try {
      const stats = await apiClient.getStatistics(selectedStudentForStats);
      setStudentStats(stats);
    } catch (error) {
      console.error('Failed to load student statistics:', error);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  const handleCreateDeck = async () => {
    if (!newDeckName.trim()) {
      showMessage('error', t('deckName') + ' is required');
      return;
    }

    try {
      const newDeck = await apiClient.createDeck(newDeckName, newDeckDescription);
      setDecks([...decks, newDeck]);
      setSelectedDeckId(newDeck.id);
      setNewDeckName('');
      setNewDeckDescription('');
      showMessage('success', 'Deck created successfully');
    } catch (error) {
      showMessage('error', 'Failed to create deck');
    }
  };

  const handleDeleteDeck = async (deckId: string) => {
    if (!confirm('Are you sure you want to delete this deck? All words in it will be deleted.')) {
      return;
    }

    try {
      await apiClient.deleteDeck(deckId);
      setDecks(decks.filter((d) => d.id !== deckId));
      if (selectedDeckId === deckId && decks.length > 1) {
        setSelectedDeckId(decks.find((d) => d.id !== deckId)?.id || '');
      }
      showMessage('success', 'Deck deleted successfully');
    } catch (error) {
      showMessage('error', 'Failed to delete deck');
    }
  };

  const handleAddWord = async () => {
    if (!newWordText.trim() || !selectedDeckId) {
      showMessage('error', t('addNewWord') + ' and ' + t('selectDeck') + ' are required');
      return;
    }

    try {
      const newWord = await apiClient.addWord(selectedDeckId, newWordText);
      setWords([...words, newWord]);
      setNewWordText('');
      showMessage('success', 'Word added successfully');
    } catch (error) {
      showMessage('error', 'Failed to add word');
    }
  };

  const handleDeleteWord = async (wordId: string) => {
    if (!confirm('Are you sure you want to delete this word?')) {
      return;
    }

    try {
      await apiClient.deleteWord(wordId);
      setWords(words.filter((w) => w.id !== wordId));
      showMessage('success', 'Word deleted successfully');
    } catch (error) {
      showMessage('error', 'Failed to delete word');
    }
  };

  const handleAssociate = async () => {
    if (!selectedStudentId || !selectedTeacherId) {
      showMessage('error', 'Please select both ' + t('student') + ' and ' + t('teacher'));
      return;
    }

    try {
      await apiClient.associateStudentWithTeacher(selectedStudentId, selectedTeacherId);
      showMessage('success', 'Student associated with teacher successfully');
    } catch (error) {
      showMessage('error', 'Failed to associate student with teacher');
    }
  };

  const handleResetPassword = async () => {
    if (!selectedUserForPassword || !newPassword.trim()) {
      showMessage('error', 'Please select a user and enter ' + t('newPassword'));
      return;
    }

    if (newPassword.length < 3) {
      showMessage('error', t('passwordMinLength'));
      return;
    }

    try {
      await apiClient.resetPassword(selectedUserForPassword, newPassword);
      setNewPassword('');
      showMessage('success', 'Password reset successfully');
    } catch (error) {
      showMessage('error', 'Failed to reset password');
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="loading">{t('loading')}</div>;
  }

  const allUsers = [...students, ...teachers];

  return (
    <div className="admin-dashboard">
      <div className="header">
        <h1>👑 {t('adminDashboard')}</h1>
        <div className="header-actions">
          <LanguageSwitcher />
          <span className="user-info">{t('welcome')}, {user?.username}! 👋</span>
          <button onClick={handleLogout} className="btn btn-secondary">
            {t('logout')}
          </button>
        </div>
      </div>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="container">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'words' ? 'active' : ''}`}
            onClick={() => setActiveTab('words')}
          >
            📝 {t('wordManagement')}
          </button>
          <button
            className={`tab ${activeTab === 'associations' ? 'active' : ''}`}
            onClick={() => setActiveTab('associations')}
          >
            👥 {t('studentTeacherAssociation')}
          </button>
          <button
            className={`tab ${activeTab === 'statistics' ? 'active' : ''}`}
            onClick={() => setActiveTab('statistics')}
          >
            📊 {t('statistics')}
          </button>
          <button
            className={`tab ${activeTab === 'passwords' ? 'active' : ''}`}
            onClick={() => setActiveTab('passwords')}
          >
            🔐 {t('passwordManagement')}
          </button>
        </div>

        {activeTab === 'words' && (
          <div className="card">
            <h2>📚 {t('wordDatabaseManagement')}</h2>

            <div className="section">
              <h3>✨ {t('createNewDeck')}</h3>
              <div className="form-group">
                <label htmlFor="deck-name">{t('deckName')}</label>
                <input
                  id="deck-name"
                  type="text"
                  value={newDeckName}
                  onChange={(e) => setNewDeckName(e.target.value)}
                  placeholder="e.g., Family Words"
                />
              </div>
              <div className="form-group">
                <label htmlFor="deck-description">{t('description')}</label>
                <input
                  id="deck-description"
                  type="text"
                  value={newDeckDescription}
                  onChange={(e) => setNewDeckDescription(e.target.value)}
                  placeholder="e.g., Words related to family"
                />
              </div>
              <button onClick={handleCreateDeck} className="btn btn-primary">
                {t('createDeck')}
              </button>
            </div>

            <div className="section">
              <h3>📋 {t('manageDecks')}</h3>
              <div className="form-group">
                <label htmlFor="deck-select">{t('selectDeck')}</label>
                <select
                  id="deck-select"
                  value={selectedDeckId}
                  onChange={(e) => setSelectedDeckId(e.target.value)}
                >
                  {decks.map((deck) => (
                    <option key={deck.id} value={deck.id}>
                      {deck.name} ({deck.wordCount} {t('words')})
                    </option>
                  ))}
                </select>
              </div>

              {selectedDeckId && (
                <>
                  <div className="deck-actions">
                    <button
                      onClick={() => handleDeleteDeck(selectedDeckId)}
                      className="btn btn-danger"
                    >
                      {t('deleteDeck')}
                    </button>
                  </div>

                  <div className="section">
                    <h3>📝 {t('wordsInDeck')}</h3>
                    <div className="form-group">
                      <label htmlFor="new-word">{t('addNewWord')}</label>
                      <div className="input-group">
                        <input
                          id="new-word"
                          type="text"
                          value={newWordText}
                          onChange={(e) => setNewWordText(e.target.value)}
                          placeholder={t('enterWord')}
                          onKeyPress={(e) => e.key === 'Enter' && handleAddWord()}
                        />
                        <button onClick={handleAddWord} className="btn btn-success">
                          {t('addWord')}
                        </button>
                      </div>
                    </div>

                    <div className="words-list">
                      {words.map((word) => (
                        <div key={word.id} className="word-item">
                          <span className="word-text">{word.text}</span>
                          <button
                            onClick={() => handleDeleteWord(word.id)}
                            className="btn btn-danger btn-sm"
                          >
                            {t('delete')}
                          </button>
                        </div>
                      ))}
                      {words.length === 0 && (
                        <p className="no-data">{t('noWordsInDeck')}</p>
                      )}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {activeTab === 'associations' && (
          <div className="card">
            <h2>👥 {t('associateStudentsWithTeachers')}</h2>
            <div className="form-group">
              <label htmlFor="student-select">{t('selectStudent')}</label>
              <select
                id="student-select"
                value={selectedStudentId}
                onChange={(e) => setSelectedStudentId(e.target.value)}
              >
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.username}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="teacher-select">{t('selectTeacher')}</label>
              <select
                id="teacher-select"
                value={selectedTeacherId}
                onChange={(e) => setSelectedTeacherId(e.target.value)}
              >
                {teachers.map((teacher) => (
                  <option key={teacher.id} value={teacher.id}>
                    {teacher.username}
                  </option>
                ))}
              </select>
            </div>
            <button onClick={handleAssociate} className="btn btn-primary">
              {t('associate')}
            </button>
          </div>
        )}

        {activeTab === 'statistics' && (
          <div className="card">
            <h2>📊 {t('viewStatistics')}</h2>
            <div className="form-group">
              <label htmlFor="student-stats-select">{t('selectStudent')}</label>
              <select
                id="student-stats-select"
                value={selectedStudentForStats}
                onChange={(e) => setSelectedStudentForStats(e.target.value)}
              >
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.username}
                  </option>
                ))}
              </select>
            </div>

            {studentStats && (
              <div className="stats-section">
                <h3>👤 {t('individualStudentStatistics')}</h3>
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-value">{studentStats.totalGames}</div>
                    <div className="stat-label">{t('totalGames')}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{Math.round(studentStats.averageScore)}</div>
                    <div className="stat-label">{t('averageScore')}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{studentStats.bestScore}</div>
                    <div className="stat-label">{t('bestScore')}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{studentStats.currentStreak}</div>
                    <div className="stat-label">{t('currentStreak')}</div>
                  </div>
                </div>
              </div>
            )}

            {allStudentsStats && (
              <div className="stats-section">
                <h3>👥 {t('collectiveStatistics')}</h3>
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-value">{allStudentsStats.totalGames}</div>
                    <div className="stat-label">{t('totalGames')}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{Math.round(allStudentsStats.averageScore)}</div>
                    <div className="stat-label">{t('averageScore')}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{allStudentsStats.bestScore}</div>
                    <div className="stat-label">{t('bestScore')}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'passwords' && (
          <div className="card">
            <h2>🔐 {t('passwordManagement')}</h2>
            <div className="form-group">
              <label htmlFor="user-password-select">{t('selectUser')}</label>
              <select
                id="user-password-select"
                value={selectedUserForPassword}
                onChange={(e) => setSelectedUserForPassword(e.target.value)}
              >
                {allUsers.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.username} ({user.role})
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="new-password">{t('newPassword')}</label>
              <input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder={t('enterNewPassword')}
                minLength={3}
              />
            </div>
            <button onClick={handleResetPassword} className="btn btn-primary">
              {t('resetPassword')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;

