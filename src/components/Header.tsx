import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import LanguageSwitcher from './LanguageSwitcher';
import './Header.css';

interface HeaderProps {
  title: string;
  showBackButton?: boolean;
  backPath?: string;
}

const Header: React.FC<HeaderProps> = ({ title, showBackButton = false, backPath }) => {
  const { logout } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleBack = () => {
    navigate(backPath || '/');
  };

  return (
    <div className="header">
      <div className="header-left">
        {showBackButton && (
          <button onClick={handleBack} className="btn btn-secondary">
            {t('backToDashboard')}
          </button>
        )}
        <h1>{title}</h1>
      </div>
      <div className="header-right">
        <LanguageSwitcher />
        <button onClick={handleLogout} className="btn-icon btn-logout" title={t('logout')}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default Header;
