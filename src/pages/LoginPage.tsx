import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import LanguageSwitcher from '../components/LanguageSwitcher';
import './LoginPage.css';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ username, password });
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('loginFailed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="language-switcher-container">
        <LanguageSwitcher />
      </div>
      <div className="login-container">
        <div className="login-card">
          <div className="welcome-emoji">👋</div>
          <h1>{t('welcomeBack')}</h1>
          <p className="subtitle">{t('signInToContinue')}</p>

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
              <label htmlFor="password">{t('password')}</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <p className="hint">{t('adminDefaultPassword')}</p>
            </div>

            {error && <div className="error">{error}</div>}

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? t('signingIn') : t('signIn')}
            </button>
          </form>

          <p className="register-link">
            {t('dontHaveAccount')} <Link to="/register">{t('registerHere')}</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;

