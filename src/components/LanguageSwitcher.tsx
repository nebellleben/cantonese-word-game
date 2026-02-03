import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import './LanguageSwitcher.css';

const LanguageSwitcher: React.FC = () => {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="language-switcher" role="group" aria-label="Language selection">
      <button
        className={`lang-btn ${language === 'en' ? 'active' : ''}`}
        onClick={() => setLanguage('en')}
        aria-pressed={language === 'en'}
      >
        English
      </button>
      <button
        className={`lang-btn ${language === 'zh-TW' ? 'active' : ''}`}
        onClick={() => setLanguage('zh-TW')}
        aria-pressed={language === 'zh-TW'}
      >
        繁體中文
      </button>
    </div>
  );
};

export default LanguageSwitcher;
