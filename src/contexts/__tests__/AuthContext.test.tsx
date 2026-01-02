import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from '../AuthContext';

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <AuthProvider>{children}</AuthProvider>
  </BrowserRouter>
);

describe('AuthContext', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should provide auth context', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    expect(result.current).toBeDefined();
    expect(result.current.user).toBeNull();
    expect(result.current.loading).toBe(true);
  });

  it('should login successfully', async () => {
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

