import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

class LocalStorageMock {
  private store: Record<string, string> = {};

  clear() {
    this.store = {};
  }

  getItem(key: string) {
    return this.store[key] ?? null;
  }

  setItem(key: string, value: string) {
    this.store[key] = String(value);
  }

  removeItem(key: string) {
    delete this.store[key];
  }
}

const ensureLocalStorage = () => {
  const hasLocalStorage =
    typeof globalThis !== 'undefined' &&
    'localStorage' in globalThis &&
    typeof globalThis.localStorage?.clear === 'function';

  if (!hasLocalStorage) {
    const storage = new LocalStorageMock();
    if (typeof window !== 'undefined') {
      Object.defineProperty(window, 'localStorage', {
        value: storage,
        configurable: true,
      });
    }
    if (typeof globalThis !== 'undefined') {
      Object.defineProperty(globalThis, 'localStorage', {
        value: storage,
        configurable: true,
      });
    }
  }
};

ensureLocalStorage();

// Cleanup after each test
afterEach(() => {
  cleanup();
});
