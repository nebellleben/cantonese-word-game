export type UserRole = 'student' | 'teacher' | 'admin';

export interface User {
  id: string;
  username: string;
  role: UserRole;
  email?: string;
}

export interface Student extends User {
  role: 'student';
  streak: number;
  totalScore: number;
}

export interface Teacher extends User {
  role: 'teacher';
  studentIds: string[];
}

export interface Admin extends User {
  role: 'admin';
}

export interface Word {
  id: string;
  text: string;
  pronunciation?: string;
  deckId: string;
}

export interface Deck {
  id: string;
  name: string;
  description?: string;
  wordCount: number;
}

export interface GameSession {
  id: string;
  userId: string;
  deckId: string;
  startTime: string;
  endTime?: string;
  score?: number;
  words: GameWord[];
}

export interface GameWord {
  wordId: string;
  text: string;
  responseTime?: number;
  isCorrect?: boolean;
  timestamp?: string;
}

export interface GameStatistics {
  totalGames: number;
  averageScore: number;
  bestScore: number;
  currentStreak: number;
  longestStreak: number;
  scoresByDate: ScoreByDate[];
  topWrongWords: WrongWord[];
}

export interface ScoreByDate {
  date: string;
  score: number;
  deckId?: string;
  deckName?: string;
}

export interface WrongWord {
  wordId: string;
  word: string;
  wrongCount: number;
  totalAttempts: number;
  ratio: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
  role: 'student' | 'teacher';
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface StartGameRequest {
  deckId: string;
}

export interface SubmitPronunciationRequest {
  sessionId: string;
  wordId: string;
  audioData?: Blob;
  responseTime: number;
}

export interface PronunciationResponse {
  isCorrect: boolean;
  feedback?: string;
}

