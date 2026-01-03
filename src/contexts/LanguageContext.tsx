import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type Language = 'en' | 'zh-TW';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Translation dictionary
const translations: Record<Language, Record<string, string>> = {
  'en': {
    // Common
    'loading': 'Loading...',
    'logout': 'Logout',
    'back': 'Back',
    'welcome': 'Welcome',
    'welcomeBack': 'Welcome Back',
    'signIn': 'Sign In',
    'signingIn': 'Signing in...',
    'register': 'Register',
    'creatingAccount': 'Creating account...',
    'createAccount': 'Create Account',
    'joinGame': 'Join the Cantonese Word Game',
    'signInToContinue': 'Sign in to continue',
    'dontHaveAccount': "Don't have an account?",
    'registerHere': 'Register here',
    'alreadyHaveAccount': 'Already have an account?',
    'signInHere': 'Sign in here',
    'username': 'Username',
    'password': 'Password',
    'email': 'Email (optional)',
    'iamA': 'I am a',
    'student': 'Student',
    'teacher': 'Teacher',
    'admin': 'Admin',
    'adminDefaultPassword': 'Admin default password: "cantonese"',
    'error': 'Error',
    'loginFailed': 'Login failed',
    'registrationFailed': 'Registration failed',
    'passwordMinLength': 'Password must be at least 3 characters',
    
    // Student Dashboard
    'studentDashboard': 'Student Dashboard',
    'startGame': 'Start Game',
    'chooseDeck': 'Choose a deck to practice and improve your Cantonese pronunciation!',
    'selectDeck': 'Select Deck',
    'viewStatistics': 'View Statistics',
    'reviewProgress': "Review your progress and see how you're improving!",
    
    // Game Page
    'exitGame': 'Exit Game',
    'wordCounter': 'Word {current} of {total}',
    'recordPronunciation': 'Record Pronunciation',
    'recording': 'Recording...',
    'skipWord': 'Skip Word',
    'gameComplete': 'Game Complete!',
    'finalScore': 'Final Score',
    'correct': 'Correct',
    'incorrect': 'Incorrect',
    'totalWords': 'Total Words',
    'backToDashboard': 'Back to Dashboard',
    'loadingGame': 'Loading game...',
    'swipeLeftToSkip': '← Swipe left to skip',
    'swipeRightToSkip': '→ Swipe right to skip',
    'pressSpaceToRecord': 'Press Space/Enter to record',
    'speechDetected': 'Speech detected',
    'pronunciationCorrect': 'Correct!',
    'pronunciationIncorrect': 'Incorrect',
    'recognizedAs': 'Recognized as',
    'recognizing': 'Recognizing',
    'playRecording': 'Play Recording',
    'nextWord': 'Next Word',
    'stop': 'Stop',
    
    // Statistics Page
    'statistics': 'Statistics',
    'overview': 'Overview',
    'totalGames': 'Total Games',
    'averageScore': 'Average Score',
    'bestScore': 'Best Score',
    'currentStreak': 'Current Streak',
    'longestStreak': 'Longest Streak',
    'scoreHistory': 'Score History',
    'filterByDeck': 'Filter by Deck',
    'allDecks': 'All Decks',
    'noGameData': 'No game data available yet. Start playing to see your progress!',
    'top20WrongWords': 'Top 20 Wrongly Pronounced Words',
    'timesWrong': 'times wrong',
    'errorRate': 'error rate',
    'noIncorrectWords': 'No incorrect words recorded yet. Keep practicing!',
    
    // Teacher Dashboard
    'teacherDashboard': 'Teacher Dashboard',
    'studentStatistics': 'Student Statistics',
    'wordErrorRatios': 'Word Error Ratios',
    'myStudents': 'My Students',
    'selectStudent': 'Select Student',
    'statisticsFor': 'Statistics for',
    'wordsSortedByError': 'Words sorted by error ratio (descending)',
    'noStudentsAssigned': 'No students assigned to you yet.',
    'noErrorData': 'No error data available yet.',
    
    // Admin Dashboard
    'adminDashboard': 'Admin Dashboard',
    'wordManagement': 'Word Management',
    'studentTeacherAssociation': 'Student-Teacher Association',
    'passwordManagement': 'Password Management',
    'wordDatabaseManagement': 'Word Database Management',
    'createNewDeck': 'Create New Deck',
    'deckName': 'Deck Name',
    'description': 'Description (optional)',
    'createDeck': 'Create Deck',
    'manageDecks': 'Manage Decks',
    'deleteDeck': 'Delete Deck',
    'wordsInDeck': 'Words in Deck',
    'addNewWord': 'Add New Word',
    'enterWord': 'Enter word (e.g., 你好)',
    'addWord': 'Add Word',
    'noWordsInDeck': 'No words in this deck yet.',
    'associateStudentsWithTeachers': 'Associate Students with Teachers',
    'selectTeacher': 'Select Teacher',
    'associate': 'Associate',
    'individualStudentStatistics': 'Individual Student Statistics',
    'collectiveStatistics': 'Collective Statistics (All Students)',
    'selectUser': 'Select User',
    'newPassword': 'New Password',
    'enterNewPassword': 'Enter new password',
    'resetPassword': 'Reset Password',
    'delete': 'Delete',
    'words': 'words',
  },
  'zh-TW': {
    // Common
    'loading': '載入中...',
    'logout': '登出',
    'back': '返回',
    'welcome': '歡迎',
    'welcomeBack': '歡迎回來',
    'signIn': '登入',
    'signingIn': '登入中...',
    'register': '註冊',
    'creatingAccount': '正在建立帳戶...',
    'createAccount': '建立帳戶',
    'joinGame': '加入粵語詞彙遊戲',
    'signInToContinue': '登入以繼續',
    'dontHaveAccount': '還沒有帳戶？',
    'registerHere': '在此註冊',
    'alreadyHaveAccount': '已有帳戶？',
    'signInHere': '在此登入',
    'username': '用戶名稱',
    'password': '密碼',
    'email': '電郵（可選）',
    'iamA': '我是',
    'student': '學生',
    'teacher': '老師',
    'admin': '管理員',
    'adminDefaultPassword': '管理員預設密碼："cantonese"',
    'error': '錯誤',
    'loginFailed': '登入失敗',
    'registrationFailed': '註冊失敗',
    'passwordMinLength': '密碼必須至少3個字符',
    
    // Student Dashboard
    'studentDashboard': '學生儀表板',
    'startGame': '開始遊戲',
    'chooseDeck': '選擇一個牌組來練習並改善您的粵語發音！',
    'selectDeck': '選擇牌組',
    'viewStatistics': '查看統計',
    'reviewProgress': '查看您的進度，看看您如何進步！',
    
    // Game Page
    'exitGame': '退出遊戲',
    'wordCounter': '第 {current} 個詞彙，共 {total} 個',
    'recordPronunciation': '錄音發音',
    'recording': '錄音中...',
    'skipWord': '跳過詞彙',
    'gameComplete': '遊戲完成！',
    'finalScore': '最終分數',
    'correct': '正確',
    'incorrect': '錯誤',
    'totalWords': '總詞彙數',
    'backToDashboard': '返回儀表板',
    'loadingGame': '載入遊戲中...',
    'swipeLeftToSkip': '← 向左滑動跳過',
    'swipeRightToSkip': '→ 向右滑動跳過',
    'pressSpaceToRecord': '按空格鍵/Enter鍵錄音',
    'speechDetected': '檢測到語音',
    'pronunciationCorrect': '正確！',
    'pronunciationIncorrect': '錯誤',
    'recognizedAs': '識別為',
    'recognizing': '識別中',
    'playRecording': '播放錄音',
    'nextWord': '下一個詞彙',
    'stop': '停止',
    
    // Statistics Page
    'statistics': '統計',
    'overview': '概覽',
    'totalGames': '總遊戲數',
    'averageScore': '平均分數',
    'bestScore': '最佳分數',
    'currentStreak': '當前連勝',
    'longestStreak': '最長連勝',
    'scoreHistory': '分數歷史',
    'filterByDeck': '按牌組篩選',
    'allDecks': '所有牌組',
    'noGameData': '還沒有遊戲數據。開始遊戲以查看您的進度！',
    'top20WrongWords': '前20個錯誤發音的詞彙',
    'timesWrong': '次錯誤',
    'errorRate': '錯誤率',
    'noIncorrectWords': '還沒有記錄錯誤的詞彙。繼續練習！',
    
    // Teacher Dashboard
    'teacherDashboard': '老師儀表板',
    'studentStatistics': '學生統計',
    'wordErrorRatios': '詞彙錯誤率',
    'myStudents': '我的學生',
    'selectStudent': '選擇學生',
    'statisticsFor': '統計資料：',
    'wordsSortedByError': '按錯誤率排序的詞彙（降序）',
    'noStudentsAssigned': '還沒有分配學生給您。',
    'noErrorData': '還沒有錯誤數據。',
    
    // Admin Dashboard
    'adminDashboard': '管理員儀表板',
    'wordManagement': '詞彙管理',
    'studentTeacherAssociation': '學生-老師關聯',
    'passwordManagement': '密碼管理',
    'wordDatabaseManagement': '詞彙數據庫管理',
    'createNewDeck': '建立新牌組',
    'deckName': '牌組名稱',
    'description': '描述（可選）',
    'createDeck': '建立牌組',
    'manageDecks': '管理牌組',
    'deleteDeck': '刪除牌組',
    'wordsInDeck': '牌組中的詞彙',
    'addNewWord': '新增詞彙',
    'enterWord': '輸入詞彙（例如：你好）',
    'addWord': '新增詞彙',
    'noWordsInDeck': '此牌組中還沒有詞彙。',
    'associateStudentsWithTeachers': '將學生與老師關聯',
    'selectTeacher': '選擇老師',
    'associate': '關聯',
    'individualStudentStatistics': '個別學生統計',
    'collectiveStatistics': '整體統計（所有學生）',
    'selectUser': '選擇用戶',
    'newPassword': '新密碼',
    'enterNewPassword': '輸入新密碼',
    'resetPassword': '重設密碼',
    'delete': '刪除',
    'words': '個詞彙',
  },
};

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    // Load from localStorage or default to English
    const saved = localStorage.getItem('language') as Language;
    return saved && (saved === 'en' || saved === 'zh-TW') ? saved : 'en';
  });

  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
  };

  const t = (key: string): string => {
    return translations[language][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

