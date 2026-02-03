import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from '../AuthContext';

vi.mock('../../services/api', () => ({
  apiClient: {
    login: vi.fn(),
    register: vi.fn(),
  },
}));

import { apiClient } from '../../services/api';

const mockedApiClient = apiClient as unknown as {
  login: ReturnType<typeof vi.fn>;
  register: ReturnType<typeof vi.fn>;
};

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <AuthProvider>{children}</AuthProvider>
  </BrowserRouter>
);

describe('AuthContext', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should provide auth context', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current).toBeDefined();
    expect(result.current.user).toBeNull();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });

  it('should login successfully', async () => {
    mockedApiClient.login.mockResolvedValueOnce({
      token: 'test-token',
      user: { id: 'u1', username: 'student1', role: 'student' },
    });
    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.login({
        username: 'student1',
        password: 'password123',
      });
    });

    expect(result.current.user).toBeDefined();
    expect(result.current.user?.username).toBe('student1');
  });

  it('should register new user', async () => {
    mockedApiClient.register.mockResolvedValueOnce({
      token: 'test-token',
      user: { id: 'u2', username: 'newuser', role: 'student' },
    });
    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.register({
        username: 'newuser',
        password: 'password123',
        role: 'student',
      });
    });

    expect(result.current.user).toBeDefined();
    expect(result.current.user?.username).toBe('newuser');
  });

  it('should logout', async () => {
    mockedApiClient.login.mockResolvedValueOnce({
      token: 'test-token',
      user: { id: 'u1', username: 'student1', role: 'student' },
    });
    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.login({
        username: 'student1',
        password: 'password123',
      });
    });

    expect(result.current.user).toBeDefined();

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.user).toBeNull();
  });
});
