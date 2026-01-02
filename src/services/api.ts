import axios, { AxiosInstance } from 'axios';
import type {
  User,
  Deck,
  Word,
  GameSession,
  GameStatistics,
  Student,
  WrongWord,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  StartGameRequest,
  SubmitPronunciationRequest,
  PronunciationResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000, // 10 second timeout
    });

    // Add token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle errors globally
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
          throw new Error('Cannot connect to server. Please make sure the backend is running on port 8000.');
        }
        if (error.response) {
          // Server responded with error status
          const message = error.response.data?.message || error.response.data?.error || 'An error occurred';
          throw new Error(message);
        }
        throw error;
      }
    );
  }

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/register', data);
    return response.data;
  }

  async getDecks(): Promise<Deck[]> {
    const response = await this.client.get<Deck[]>('/decks');
    return response.data;
  }

  async getWordsByDeck(deckId: string): Promise<Word[]> {
    const response = await this.client.get<Word[]>(`/decks/${deckId}/words`);
    return response.data;
  }

  async startGame(request: StartGameRequest): Promise<GameSession> {
    const response = await this.client.post<GameSession>('/games/start', request);
    return response.data;
  }

  async submitPronunciation(request: SubmitPronunciationRequest): Promise<PronunciationResponse> {
    const formData = new FormData();
    formData.append('sessionId', request.sessionId);
    formData.append('wordId', request.wordId);
    formData.append('responseTime', request.responseTime.toString());
    if (request.audioData) {
      formData.append('audio', request.audioData, 'audio.wav');
    }

    const response = await this.client.post<PronunciationResponse>(
      '/games/pronunciation',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async endGame(sessionId: string): Promise<GameSession> {
    const response = await this.client.post<GameSession>(`/games/${sessionId}/end`);
    return response.data;
  }

  async getStatistics(userId?: string, deckId?: string): Promise<GameStatistics> {
    const params: Record<string, string> = {};
    if (userId) params.userId = userId;
    if (deckId) params.deckId = deckId;

    const response = await this.client.get<GameStatistics>('/statistics', { params });
    return response.data;
  }

  async getStudents(): Promise<Student[]> {
    const response = await this.client.get<Student[]>('/students');
    return response.data;
  }

  async getWordErrorRatios(): Promise<WrongWord[]> {
    const response = await this.client.get<WrongWord[]>('/words/error-ratios');
    return response.data;
  }

  // Admin methods
  async createDeck(name: string, description?: string): Promise<Deck> {
    const response = await this.client.post<Deck>('/admin/decks', { name, description });
    return response.data;
  }

  async deleteDeck(deckId: string): Promise<void> {
    await this.client.delete(`/admin/decks/${deckId}`);
  }

  async addWord(deckId: string, text: string): Promise<Word> {
    const response = await this.client.post<Word>(`/admin/decks/${deckId}/words`, { text });
    return response.data;
  }

  async deleteWord(wordId: string): Promise<void> {
    await this.client.delete(`/admin/words/${wordId}`);
  }

  async associateStudentWithTeacher(studentId: string, teacherId: string): Promise<void> {
    await this.client.post('/admin/associations', { studentId, teacherId });
  }

  async resetPassword(userId: string, newPassword: string): Promise<void> {
    await this.client.post(`/admin/users/${userId}/reset-password`, { password: newPassword });
  }
}

export const apiClient = new ApiClient();

