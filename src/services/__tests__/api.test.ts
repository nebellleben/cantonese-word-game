import { describe, it, expect, beforeEach } from 'vitest';
import { apiClient } from '../api';

describe('API Client', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
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

