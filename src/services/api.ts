/**
 * Centralized API Client
 * 
 * This file contains all backend API calls.
 * Currently all methods are mocked, but they will be replaced with actual API calls later.
 */

import axios, { AxiosInstance } from 'axios';
import type {
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  Deck,
  Word,
  StartGameRequest,
  GameSession,
  SubmitPronunciationRequest,
  PronunciationResponse,
  GameStatistics,
  Student,
  Teacher,
  WrongWord,
} from '../types';

// Mock data storage (in-memory)
let mockUsers: User[] = [
  { id: 'admin-1', username: 'admin', role: 'admin', email: 'admin@example.com' },
  { id: 'student-1', username: 'student1', role: 'student', email: 'student1@example.com' },
  { id: 'teacher-1', username: 'teacher1', role: 'teacher', email: 'teacher1@example.com' },
];

let mockDecks: Deck[] = [
  { id: 'deck-1', name: 'Basic Words', description: 'Common everyday words', wordCount: 20 },
  { id: 'deck-2', name: 'School Words', description: 'Words related to school', wordCount: 15 },
  { id: 'deck-3', name: 'Family Words', description: 'Family-related vocabulary', wordCount: 18 },
];

let mockWords: Word[] = [
  { id: 'word-1', text: '你好', deckId: 'deck-1' },
  { id: 'word-2', text: '謝謝', deckId: 'deck-1' },
  { id: 'word-3', text: '再見', deckId: 'deck-1' },
  { id: 'word-4', text: '學校', deckId: 'deck-2' },
  { id: 'word-5', text: '老師', deckId: 'deck-2' },
  { id: 'word-6', text: '爸爸', deckId: 'deck-3' },
  { id: 'word-7', text: '媽媽', deckId: 'deck-3' },
];

let mockGameSessions: GameSession[] = [];
let mockStatistics: Map<string, GameStatistics> = new Map();

class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    // Mock implementation
    await this.delay(500);
    
    const user = mockUsers.find(
      (u) => u.username === credentials.username
    );

    if (!user) {
      throw new Error('Invalid username or password');
    }

    // Admin default password check
    if (user.role === 'admin' && credentials.password !== 'cantonese') {
      throw new Error('Invalid username or password');
    }

    // For other users, accept any password in mock mode
    if (user.role !== 'admin' && credentials.password.length < 3) {
      throw new Error('Invalid username or password');
    }

    const token = `mock-token-${user.id}`;
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(user));

    return { user, token };
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    // Mock implementation
    await this.delay(500);

    if (mockUsers.some((u) => u.username === data.username)) {
      throw new Error('Username already exists');
    }

    const newUser: User = {
      id: `${data.role}-${Date.now()}`,
      username: data.username,
      role: data.role,
      email: data.email,
    };

    mockUsers.push(newUser);

    const token = `mock-token-${newUser.id}`;
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(newUser));

    return { user: newUser, token };
  }

  async logout(): Promise<void> {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  }

  // Decks
  async getDecks(): Promise<Deck[]> {
    await this.delay(300);
    return [...mockDecks];
  }

  async getDeck(deckId: string): Promise<Deck> {
    await this.delay(200);
    const deck = mockDecks.find((d) => d.id === deckId);
    if (!deck) throw new Error('Deck not found');
    return deck;
  }

  // Words
  async getWordsByDeck(deckId: string): Promise<Word[]> {
    await this.delay(300);
    return mockWords.filter((w) => w.deckId === deckId);
  }

  // Game
  async startGame(request: StartGameRequest): Promise<GameSession> {
    await this.delay(400);
    const words = await this.getWordsByDeck(request.deckId);
    
    // Shuffle words
    const shuffledWords = [...words].sort(() => Math.random() - 0.5);

    const session: GameSession = {
      id: `session-${Date.now()}`,
      userId: this.getCurrentUserId(),
      deckId: request.deckId,
      startTime: new Date().toISOString(),
      words: shuffledWords.map((w) => ({
        wordId: w.id,
        word: w.text,
        responseTime: 0,
        isCorrect: false,
        timestamp: new Date().toISOString(),
      })),
    };

    mockGameSessions.push(session);
    return session;
  }

  async submitPronunciation(
    request: SubmitPronunciationRequest
  ): Promise<PronunciationResponse> {
    await this.delay(800); // Simulate processing time

    // Mock: Randomly determine correctness (80% correct for demo)
    const isCorrect = Math.random() > 0.2;

    // Update session
    const session = mockGameSessions.find((s) => s.id === request.sessionId);
    if (session) {
      const word = session.words.find((w) => w.wordId === request.wordId);
      if (word) {
        word.isCorrect = isCorrect;
        word.responseTime = request.responseTime;
      }
    }

    return {
      isCorrect,
      feedback: isCorrect ? 'Correct!' : 'Try again',
    };
  }

  async endGame(sessionId: string): Promise<GameSession> {
    await this.delay(300);
    const session = mockGameSessions.find((s) => s.id === sessionId);
    if (!session) throw new Error('Session not found');

    const correctCount = session.words.filter((w) => w.isCorrect).length;
    const totalTime = session.words.reduce((sum, w) => sum + w.responseTime, 0);
    const avgTime = totalTime / session.words.length;
    
    // Score calculation: correct words * 100 - (avg time in seconds * 10)
    session.score = Math.max(0, correctCount * 100 - Math.floor(avgTime / 1000) * 10);
    session.endTime = new Date().toISOString();

    // Update statistics
    this.updateStatistics(session);

    return session;
  }

  // Statistics
  async getStatistics(userId?: string, deckId?: string): Promise<GameStatistics> {
    await this.delay(400);
    const targetUserId = userId || this.getCurrentUserId();
    const key = `${targetUserId}-${deckId || 'all'}`;

    if (!mockStatistics.has(key)) {
      // Generate mock statistics
      const stats: GameStatistics = {
        totalGames: 5,
        averageScore: 750,
        bestScore: 950,
        currentStreak: 3,
        longestStreak: 5,
        scoresByDate: this.generateMockScores(deckId),
        topWrongWords: this.generateMockWrongWords(),
      };
      mockStatistics.set(key, stats);
    }

    return mockStatistics.get(key)!;
  }

  // Teacher: Get students
  async getStudents(): Promise<Student[]> {
    await this.delay(300);
    return mockUsers
      .filter((u) => u.role === 'student')
      .map((u) => ({
        ...u,
        role: 'student' as const,
        streak: Math.floor(Math.random() * 10),
        totalScore: Math.floor(Math.random() * 5000),
      }));
  }

  // Teacher: Get word error ratios
  async getWordErrorRatios(): Promise<WrongWord[]> {
    await this.delay(300);
    return this.generateMockWrongWords().sort((a, b) => b.ratio - a.ratio);
  }

  // Admin: Word management
  async createDeck(name: string, description?: string): Promise<Deck> {
    await this.delay(400);
    const deck: Deck = {
      id: `deck-${Date.now()}`,
      name,
      description,
      wordCount: 0,
    };
    mockDecks.push(deck);
    return deck;
  }

  async deleteDeck(deckId: string): Promise<void> {
    await this.delay(300);
    mockDecks = mockDecks.filter((d) => d.id !== deckId);
    mockWords = mockWords.filter((w) => w.deckId !== deckId);
  }

  async addWord(deckId: string, text: string): Promise<Word> {
    await this.delay(300);
    const word: Word = {
      id: `word-${Date.now()}`,
      text,
      deckId,
    };
    mockWords.push(word);
    
    const deck = mockDecks.find((d) => d.id === deckId);
    if (deck) deck.wordCount++;

    return word;
  }

  async deleteWord(wordId: string): Promise<void> {
    await this.delay(300);
    const word = mockWords.find((w) => w.id === wordId);
    if (word) {
      const deck = mockDecks.find((d) => d.id === word.deckId);
      if (deck) deck.wordCount--;
    }
    mockWords = mockWords.filter((w) => w.id !== wordId);
  }

  // Admin: Student-Teacher association
  async associateStudentWithTeacher(
    studentId: string,
    teacherId: string
  ): Promise<void> {
    await this.delay(300);
    // Mock: In real implementation, this would update the database
    console.log(`Associating student ${studentId} with teacher ${teacherId}`);
  }

  // Admin: Password management
  async resetPassword(userId: string, newPassword: string): Promise<void> {
    await this.delay(300);
    // Mock: In real implementation, this would update the database
    console.log(`Resetting password for user ${userId}`);
  }

  // Helper methods
  private getCurrentUserId(): string {
    const userStr = localStorage.getItem('user');
    if (!userStr) throw new Error('Not authenticated');
    const user = JSON.parse(userStr);
    return user.id;
  }

  private updateStatistics(session: GameSession): void {
    const key = `${session.userId}-all`;
    let stats = mockStatistics.get(key);

    if (!stats) {
      stats = {
        totalGames: 0,
        averageScore: 0,
        bestScore: 0,
        currentStreak: 0,
        longestStreak: 0,
        scoresByDate: [],
        topWrongWords: [],
      };
    }

    stats.totalGames++;
    if (session.score) {
      stats.averageScore = (stats.averageScore * (stats.totalGames - 1) + session.score) / stats.totalGames;
      stats.bestScore = Math.max(stats.bestScore, session.score);
    }

    // Update wrong words
    session.words.forEach((w) => {
      if (!w.isCorrect) {
        const existing = stats.topWrongWords.find((tw) => tw.wordId === w.wordId);
        if (existing) {
          existing.wrongCount++;
          existing.totalAttempts++;
          existing.ratio = existing.wrongCount / existing.totalAttempts;
        } else {
          stats.topWrongWords.push({
            wordId: w.wordId,
            word: w.word,
            wrongCount: 1,
            totalAttempts: 1,
            ratio: 1.0,
          });
        }
      }
    });

    mockStatistics.set(key, stats);
  }

  private generateMockScores(deckId?: string): ScoreByDate[] {
    const scores: ScoreByDate[] = [];
    const today = new Date();
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      scores.push({
        date: date.toISOString().split('T')[0],
        score: Math.floor(Math.random() * 200) + 700,
        deckId: deckId,
        deckName: deckId ? mockDecks.find((d) => d.id === deckId)?.name : undefined,
      });
    }
    return scores;
  }

  private generateMockWrongWords(): WrongWord[] {
    return mockWords.slice(0, 5).map((w, i) => ({
      wordId: w.id,
      word: w.text,
      wrongCount: Math.floor(Math.random() * 5) + 1,
      totalAttempts: Math.floor(Math.random() * 10) + 5,
      ratio: Math.random() * 0.5 + 0.3,
    }));
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

export const apiClient = new ApiClient();

