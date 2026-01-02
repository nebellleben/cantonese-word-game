import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import LanguageSwitcher from '../components/LanguageSwitcher';
import './RegisterPage.css';

const RegisterPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<'student' | 'teacher'>('student');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password.length < 3) {
      setError(t('passwordMinLength'));
      return;
    }

    setLoading(true);

    try {
      await register({ username, password, email, role });
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('registrationFailed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <div className="language-switcher-container">
        <LanguageSwitcher />
      </div>
      <div className="register-container">
        <div className="register-card">
          <div className="welcome-emoji">🎉</div>
          <h1>{t('createAccount')}</h1>
          <p className="subtitle">{t('joinGame')}</p>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="username">{t('username')}</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoFocus
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">{t('email')}</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">{t('password')}</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={3}
              />
            </div>

            <div className="form-group">
              <label htmlFor="role">{t('iamA')}</label>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value as 'student' | 'teacher')}
                required
              >
                <option value="student">{t('student')}</option>
                <option value="teacher">{t('teacher')}</option>
              </select>
            </div>

            {error && <div className="error">{error}</div>}

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? t('creatingAccount') : t('register')}
            </button>
          </form>

          <p className="login-link">
            {t('alreadyHaveAccount')} <Link to="/login">{t('signInHere')}</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;

