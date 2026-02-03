import { describe, it, expect, beforeEach, vi } from 'vitest';
import { apiClient } from '../api';

const mockPost = vi.hoisted(() => vi.fn());
const mockGet = vi.hoisted(() => vi.fn());

vi.mock('axios', () => ({
  default: {
    create: () => ({
      post: mockPost,
      get: mockGet,
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    }),
  },
  AxiosError: class AxiosError extends Error {},
}));

describe('API Client', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    mockPost.mockReset();
    mockGet.mockReset();

    const registeredUsers = new Set<string>();

    mockPost.mockImplementation((url: string, body?: any) => {
      if (url === '/auth/login') {
        if (body?.username === 'student1' && body?.password === 'password123') {
          return Promise.resolve({
            data: { token: 'token-1', user: { id: 'u1', username: 'student1', role: 'student' } },
          });
        }
        return Promise.reject(new Error('Invalid credentials'));
      }

      if (url === '/auth/register') {
        if (registeredUsers.has(body?.username)) {
          return Promise.reject(new Error('Duplicate username'));
        }
        registeredUsers.add(body?.username);
        return Promise.resolve({
          data: {
            token: 'token-2',
            user: { id: 'u2', username: body?.username, role: body?.role ?? 'student' },
          },
        });
      }

      if (url === '/games/start') {
        return Promise.resolve({
          data: {
            id: 'session-1',
            words: [{ wordId: 'word-1', text: '你好', jyutping: 'nei5 hou2' }],
          },
        });
      }

      if (url === '/games/pronunciation') {
        return Promise.resolve({
          data: { isCorrect: true },
        });
      }

      return Promise.reject(new Error(`Unhandled POST ${url}`));
    });

    mockGet.mockImplementation((url: string) => {
      if (url === '/decks') {
        return Promise.resolve({
          data: [{ id: 'deck-1', name: 'Basics', wordCount: 2 }],
        });
      }

      if (url.startsWith('/decks/') && url.endsWith('/words')) {
        return Promise.resolve({
          data: [{ id: 'word-1', text: '你好' }],
        });
      }

      return Promise.reject(new Error(`Unhandled GET ${url}`));
    });
  });

  describe('Authentication', () => {
    it('should login successfully with valid credentials', async () => {
      const response = await apiClient.login({
        username: 'student1',
        password: 'password123',
      });

      expect(response.user).toBeDefined();
      expect(response.user.username).toBe('student1');
      expect(response.token).toBeDefined();
    });

    it('should fail login with invalid credentials', async () => {
      await expect(
        apiClient.login({
          username: 'nonexistent',
          password: 'wrong',
        })
      ).rejects.toThrow();
    });

    it('should register a new user', async () => {
      const response = await apiClient.register({
        username: 'newuser',
        password: 'password123',
        email: 'newuser@example.com',
        role: 'student',
      });

      expect(response.user).toBeDefined();
      expect(response.user.username).toBe('newuser');
      expect(response.user.role).toBe('student');
    });

    it('should fail registration with duplicate username', async () => {
      await apiClient.register({
        username: 'duplicate',
        password: 'password123',
        role: 'student',
      });

      await expect(
        apiClient.register({
          username: 'duplicate',
          password: 'password123',
          role: 'student',
        })
      ).rejects.toThrow();
    });
  });

  describe('Decks', () => {
    it('should get list of decks', async () => {
      const decks = await apiClient.getDecks();
      expect(Array.isArray(decks)).toBe(true);
      expect(decks.length).toBeGreaterThan(0);
    });

    it('should get words from a deck', async () => {
      const decks = await apiClient.getDecks();
      if (decks.length > 0) {
        const words = await apiClient.getWordsByDeck(decks[0].id);
        expect(Array.isArray(words)).toBe(true);
      }
    });
  });

  describe('Game', () => {
    beforeEach(async () => {
      // Login as a student to set up auth context
      await apiClient.login({
        username: 'student1',
        password: 'password123',
      });
    });

    it('should start a game', async () => {
      const decks = await apiClient.getDecks();
      if (decks.length > 0) {
        const session = await apiClient.startGame({ deckId: decks[0].id });
        expect(session.id).toBeDefined();
        expect(session.words.length).toBeGreaterThan(0);
      }
    });

    it('should submit pronunciation', async () => {
      const decks = await apiClient.getDecks();
      if (decks.length > 0) {
        const session = await apiClient.startGame({ deckId: decks[0].id });
        const response = await apiClient.submitPronunciation({
          sessionId: session.id,
          wordId: session.words[0].wordId,
          responseTime: 2000,
        });

        expect(response.isCorrect).toBeDefined();
        expect(typeof response.isCorrect).toBe('boolean');
      }
    });
  });
});
