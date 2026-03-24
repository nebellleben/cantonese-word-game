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
        <button onClick={handleLogout} className="btn btn-secondary btn-logout">
          {t('logout')}
        </button>
      </div>
    </div>
  );
};

export default Header;
