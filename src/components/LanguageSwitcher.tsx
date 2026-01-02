import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import './LanguageSwitcher.css';

const LanguageSwitcher: React.FC = () => {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="language-switcher">
      <button
        className={`lang-btn ${language === 'en' ? 'active' : ''}`}
        onClick={() => setLanguage('en')}
        aria-label="Switch to English"
      >
        🇬🇧 English
      </button>
      <button
        className={`lang-btn ${language === 'zh-TW' ? 'active' : ''}`}
        onClick={() => setLanguage('zh-TW')}
        aria-label="Switch to Traditional Chinese"
      >
        🇭🇰 繁體中文
      </button>
    </div>
  );
};

export default LanguageSwitcher;

