import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Deck,
  Word,
  GameSession,
  GameStatistics,
  Student,
  WrongWord,
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  StartGameRequest,
  SubmitPronunciationRequest,
  PronunciationResponse,
  StudentTeacherAssociation,
} from '../types';

// Get API base URL from environment variable or use default
// @ts-ignore - Vite environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000, // 10 second timeout to prevent hanging
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        // Handle timeout errors (axios timeout or connection timeout)
        if (error.code === 'ECONNABORTED' || 
            error.code === 'ETIMEDOUT' ||
            error.message.includes('timeout') ||
            error.message.includes('TIMED_OUT')) {
          throw new Error('Request timed out. Please check if the backend server is running and accessible at ' + API_BASE_URL);
        }
        
        // Handle connection errors (refused, network errors, or no response)
        // ERR_NETWORK can occur for connection refused, timeout, or other network issues
        // If there's no response, it's likely the backend isn't running
        if (error.code === 'ECONNREFUSED' ||
            error.code === 'ERR_NETWORK' ||
            error.code === 'ERR_CONNECTION_REFUSED' ||
            error.code === 'ERR_CONNECTION_TIMED_OUT' ||
            (!error.response && error.message.includes('Network Error'))) {
          throw new Error('Cannot connect to server. Please ensure the backend is running on port 8000.');
        }
        
        if (error.response) {
          const data = error.response.data as any;
          const message =
            data?.detail ||
            data?.message ||
            data?.error ||
            error.message;
          throw new Error(message);
        }
        throw error;
      }
    );
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/register', data);
    return response.data;
  }

  // Decks
  async getDecks(): Promise<Deck[]> {
    const response = await this.client.get<Deck[]>('/decks');
    return response.data;
  }

  async getWordsByDeck(deckId: string): Promise<Word[]> {
    const response = await this.client.get<Word[]>(`/decks/${deckId}/words`);
    return response.data;
  }

  // Games
  async startGame(request: StartGameRequest): Promise<GameSession> {
    console.log('API: Starting game with request:', request);
    try {
      const response = await this.client.post<GameSession>('/games/start', request);
      console.log('API: Game started successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('API: Error starting game:', error);
      throw error;
    }
  }

  async submitPronunciation(request: SubmitPronunciationRequest): Promise<PronunciationResponse> {
    const formData = new FormData();
    formData.append('sessionId', request.sessionId);
    formData.append('wordId', request.wordId);
    formData.append('responseTime', request.responseTime.toString());
    
    if (request.audioData) {
      formData.append('audio', request.audioData, 'recording.wav');
    }
    
    if (request.realTimeRecognition) {
      formData.append('realTimeRecognition', request.realTimeRecognition);
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

  // Statistics
  async getStatistics(userId?: string, deckId?: string): Promise<GameStatistics> {
    const params = new URLSearchParams();
    if (userId) params.append('userId', userId);
    if (deckId) params.append('deckId', deckId);
    
    const response = await this.client.get<GameStatistics>(
      `/statistics${params.toString() ? `?${params.toString()}` : ''}`
    );
    return response.data;
  }

  async getStudents(): Promise<Student[]> {
    const response = await this.client.get<Student[]>('/students');
    return response.data;
  }

  async getTeachers(): Promise<User[]> {
    const response = await this.client.get<User[]>('/teachers');
    return response.data;
  }

  async getWordErrorRatios(): Promise<WrongWord[]> {
    const response = await this.client.get<WrongWord[]>('/words/error-ratios');
    return response.data;
  }

  // Admin endpoints
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

  async associateStudentTeacher(studentId: string, teacherId: string): Promise<void> {
    await this.client.post('/admin/associations', { studentId, teacherId });
  }

  async getAssociations(): Promise<StudentTeacherAssociation[]> {
    const response = await this.client.get<StudentTeacherAssociation[]>('/admin/associations');
    return response.data;
  }

  async resetPassword(userId: string, password: string): Promise<void> {
    await this.client.post(`/admin/users/${userId}/reset-password`, { password });
  }
}

export const apiClient = new ApiClient();
