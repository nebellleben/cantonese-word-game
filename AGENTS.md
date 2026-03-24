# AGENTS.md - Coding Agent Guidelines

This document provides essential information for AI coding agents working on the Cantonese Word Game codebase.

## Project Overview

A bilingual (English/Traditional Chinese) educational web application for Cantonese pronunciation practice, designed for students with dyslexia. The stack consists of:
- **Frontend**: React 18 + TypeScript + Vite + Vitest
- **Backend**: Python 3.11+ + FastAPI + SQLAlchemy + pytest
- **Database**: SQLite (dev) / PostgreSQL (prod)

## Build/Lint/Test Commands

### Frontend (from project root)

```bash
# Development server
npm run dev

# Build for production
npm run build

# Lint all files
npm run lint

# Run all tests
npm test

# Run tests with UI
npm run test:ui

# Run a single test file
npx vitest run src/services/__tests__/api.test.ts

# Run a single test by name pattern
npx vitest run -t "should login successfully"
```

### Backend (from `backend/` directory)

```bash
# Development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run a single test file
uv run pytest tests/test_auth.py

# Run a single test by name pattern
uv run pytest -k "test_login_success"

# Run with coverage
uv run pytest --cov=app
```

### Run Both Services

```bash
npm run dev:all
```

## Code Style Guidelines

### TypeScript/React

#### Imports Organization
```typescript
// 1. React imports first
import React, { useState, useEffect, useContext } from 'react';

// 2. External libraries
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

// 3. Type imports (use `import type` for type-only imports)
import type { User, LoginRequest } from '../types';

// 4. CSS imports last
import './ComponentName.css';
```

#### Component Structure
```typescript
// Use React.FC with explicit props interface
interface ComponentProps {
  title: string;
  onSubmit: (value: string) => void;
  disabled?: boolean;
}

const ComponentName: React.FC<ComponentProps> = ({ title, onSubmit, disabled = false }) => {
  const [state, setState] = useState<string>('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // ...
  };

  return (
    <div className="component-name">
      {/* JSX content */}
    </div>
  );
};

export default ComponentName;
```

#### Naming Conventions
- **Components**: PascalCase (`LoginPage`, `SwipeCard`)
- **Files**: PascalCase for components (`LoginPage.tsx`), camelCase for utilities (`api.ts`)
- **CSS files**: Match component name (`LoginPage.css`)
- **Functions/variables**: camelCase (`handleSubmit`, `isLoading`)
- **Constants**: UPPER_SNAKE_CASE for true constants, camelCase for config objects
- **Types/Interfaces**: PascalCase (`User`, `AuthContextType`)

#### Error Handling
```typescript
// Use try/catch with proper error type checking
try {
  await apiClient.login(credentials);
} catch (error) {
  if (error instanceof Error) {
    setError(error.message);
  } else {
    setError('An unexpected error occurred');
  }
}
```

#### Context Pattern
```typescript
// Define context type interface
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
}

// Create context with undefined default
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Export custom hook with null check
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### Python/Backend

#### Imports Organization
```python
# 1. Standard library
from datetime import datetime
from typing import Optional, List

# 2. Third-party libraries
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 3. Local imports (use absolute imports from app.*)
from app.api.models.schemas import User, LoginRequest
from app.core.dependencies import get_db_service
from app.services.auth_service import AuthService
```

#### Route Handler Pattern
```python
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Brief docstring describing endpoint."""
    auth_service = AuthService(db_service)
    user = auth_service.authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    return auth_service.create_auth_response(user)
```

#### Pydantic Models
```python
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class User(BaseModel):
    id: UUID
    username: str
    role: str
    created_at: datetime = Field(alias="createdAt")
    
    model_config = ConfigDict(populate_by_name=True)
```

#### Naming Conventions
- **Functions/variables**: snake_case (`get_user`, `user_id`)
- **Classes**: PascalCase (`AuthService`, `GameSession`)
- **Constants**: UPPER_SNAKE_CASE
- **Pydantic models**: PascalCase, use camelCase aliases for API responses

#### Error Handling
```python
# Use HTTPException for API errors
if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

# Use ValueError for service-level validation
if existing_user:
    raise ValueError("Username already exists")
```

### Testing

#### Frontend Tests (Vitest + React Testing Library)
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock external dependencies
vi.mock('../../services/api', () => ({
  apiClient: {
    login: vi.fn(),
  },
}));

describe('ComponentName', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render correctly', () => {
    render(<ComponentName />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('should handle user interaction', async () => {
    const user = userEvent.setup();
    render(<ComponentName />);
    await user.click(screen.getByRole('button'));
    await waitFor(() => {
      expect(screen.getByText('Result')).toBeInTheDocument();
    });
  });
});
```

#### Backend Tests (pytest)
```python
import pytest
from fastapi.testclient import TestClient

def test_endpoint_success(client):
    """Test description."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "cantonese"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data

def test_endpoint_failure(client):
    """Test error handling."""
    response = client.post("/api/auth/login", json={"username": "bad", "password": "bad"})
    assert response.status_code == 401
```

## TypeScript Configuration

- **Strict mode**: Enabled with `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`
- **Target**: ES2020
- **Module**: ESNext with bundler resolution

## ESLint Rules

- `@typescript-eslint/no-explicit-any`: warn
- `react-refresh/only-export-components`: warn with `allowConstantExport: true`
- React Hooks rules enforced

## Key Files

- `src/types/index.ts` - Central TypeScript type definitions
- `src/services/api.ts` - Centralized API client with axios
- `src/contexts/` - React Context providers (Auth, Language)
- `backend/app/api/routes/` - FastAPI route handlers
- `backend/app/api/models/schemas.py` - Pydantic request/response models
- `backend/tests/conftest.py` - pytest fixtures

## Before Committing

1. Run linting: `npm run lint`
2. Run frontend tests: `npm test`
3. Run backend tests: `cd backend && uv run pytest`
4. Ensure TypeScript compiles: `npm run build` (build step includes tsc)

## API Conventions

- All API routes prefixed with `/api`
- JWT authentication via `Authorization: Bearer <token>` header
- Request/response bodies use camelCase for JSON properties
- Error responses include `detail` field with message
