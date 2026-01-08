## Implementation Overview

This document describes the technical implementation of the Cantonese Word Game, including the frontend, backend, database, ASR engines, and integration tests. It condenses the content that was previously spread across `FRONTEND.md`, `BACKEND.md`, `BACKEND_AGENTS.md`, and `project_implementation.md`.

For high-level project context, see `README.md`. For detailed deployment and CI/CD, see `DEPLOYMENT.md`.

---

## Frontend Implementation

### Technology & Architecture

- **Tech stack**: React 18, TypeScript, Vite, React Router, Axios, Recharts, CSS Modules, Vitest.
- **State management**: React Context API for:
  - `AuthContext` – authentication state & JWT token.
  - `LanguageContext` – current language and translations.
- **API client**: `src/services/api.ts`
  - Centralized Axios instance with:
    - `VITE_API_BASE_URL` support.
    - Authorization header injection from `localStorage`.
    - Unified error handling and timeout handling.
    - `multipart/form-data` support for audio uploads.
- **Routing**:
  - Student: `/student`, `/student/game`, `/student/statistics`
  - Teacher: `/teacher`
  - Admin: `/admin`
  - Auth: `/login`, `/register`
  - Protected routes with role-based access.

### Structure

Key directories:

- `src/pages/`
  - `LoginPage.tsx`, `RegisterPage.tsx`
  - `StudentDashboard.tsx`, `GamePage.tsx`, `StatisticsPage.tsx`
  - `TeacherDashboard.tsx`, `AdminDashboard.tsx`
- `src/components/`
  - `SwipeCard.tsx` – swipeable game card component.
  - `LanguageSwitcher.tsx` – language toggle component.
- `src/contexts/`
  - `AuthContext.tsx`, `LanguageContext.tsx`
- `src/services/`
  - `api.ts` – all HTTP calls to the backend.
- `src/types/`
  - Shared TypeScript interfaces for decks, words, sessions, statistics, etc.

### Role-specific UIs

- **Student**
  - Dashboard: deck selection, start game, view statistics.
  - Game page:
    - Swipe card interface (mouse, touch, keyboard).
    - Recording controls with 5-second auto-stop.
    - Volume bar visualization using Web Audio API (RMS-based).
    - Real-time speech recognition preview using Web Speech API.
    - Immediate correct/incorrect feedback and progression through the deck.
  - Statistics page:
    - Totals, averages, streaks.
    - Score history chart (Recharts).
    - Top 20 wrong words list (word, wrong count, error ratio).

- **Teacher**
  - Student statistics:
    - Select from assigned students.
    - Per-student metrics and score history chart.
  - Word error ratios:
    - List of words sorted by error ratio.
    - Visual ratio bars and counts.

- **Admin**
  - Word & deck management:
    - Create/delete decks.
    - Add/delete words; backend generates jyutping.
  - Student–teacher associations.
  - Statistics (individual + global).
  - Password reset for users.

### Testing

- **Unit & component tests** with Vitest and Testing Library.
- Test files live under:
  - `src/components/__tests__/`
  - `src/pages/__tests__/`
  - `src/contexts/__tests__/`
  - `src/services/__tests__/`

---

## Backend Implementation

### Technology & Architecture

- **Tech stack**: Python 3.11, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, uv (dependency manager).
- **Auth**: JWT via `python-jose`, password hashing via `passlib[bcrypt]` / `bcrypt`.
- **Database**:
  - Dev: SQLite (`sqlite:///./cantonese_game.db`).
  - Prod: PostgreSQL via `DATABASE_URL`.
  - ORM: SQLAlchemy models in `backend/app/db/models.py`.
- **Configuration**: `backend/app/core/config.py`
  - Pydantic `BaseSettings` with `.env` support.
  - `database_url`, CORS origins, secret key, token expiry, optional AWS Secrets Manager integration.
- **App entrypoint**: `backend/app/main.py`
  - Adds CORS middleware.
  - Includes routers:
    - `auth`, `decks`, `games`, `statistics`, `admin`.
  - Health endpoint: `/health`.

### API Surface (Condensed)

From `BACKEND.md` and the implemented routes:

- **Auth**
  - `POST /api/auth/login`
  - `POST /api/auth/register`
- **Decks & words**
  - `GET /api/decks`
  - `GET /api/decks/{deckId}/words`
  - `POST /api/admin/decks`
  - `DELETE /api/admin/decks/{deckId}`
  - `POST /api/admin/decks/{deckId}/words`
  - `DELETE /api/admin/words/{wordId}`
- **Games**
  - `POST /api/games/start`
  - `POST /api/games/pronunciation` (multipart with audio)
  - `POST /api/games/{sessionId}/end`
- **Statistics**
  - `GET /api/statistics`
  - `GET /api/words/error-ratios`
  - `GET /api/students`
- **Admin**
  - `POST /api/admin/associations`
  - `POST /api/admin/users/{userId}/reset-password`

The backend adheres to the OpenAPI spec in `backend/openapi/openapi.yaml`. FastAPI’s automatic docs are available at `/docs` and `/redoc`.

### Services & Layers

- `backend/app/services/auth_service.py`
  - User registration and login.
  - Password hashing, JWT creation/validation.
- `backend/app/services/game_service.py`
  - Game session lifecycle: start, pronunciation submission, end.
  - Response time tracking and score calculation.
  - Integration with the ASR engine.
- `backend/app/services/statistics_service.py`
  - Aggregates user statistics (totals, averages, best scores, streaks).
  - Top wrong words and error ratios.
- `backend/app/db/database_service.py`
  - Higher-level DB operations composed from SQLAlchemy models and sessions.
- `backend/app/db/base.py`
  - Engine and `SessionLocal` creation.
  - `init_db()` utility (creates tables, default admin).

### Database Schema (Conceptual)

As specified in `BACKEND.md` and implemented via SQLAlchemy models:

- `users` – id, username, password_hash, role, created_at.
- `decks` – id, name, description, created_at.
- `words` – id, text, jyutping, deck_id, created_at.
- `game_sessions` – id, user_id, deck_id, score, started_at, ended_at.
- `game_attempts` – id, session_id, word_id, is_correct, response_time, attempted_at.
- `student_teacher_associations` – id, student_id, teacher_id, created_at.
- `user_streaks` (or equivalent) – user_id, date, games_completed.

Alembic migrations under `backend/alembic/` handle schema evolution.

### Business Logic Highlights

- **Auth & roles**
  - Default admin: `admin` / `cantonese`.
  - JWT tokens with configurable expiry (24 hours by default).
  - Role-based access enforced in routers using FastAPI dependencies.

- **Game sessions**
  - Start:
    - Validates deck and user.
    - Shuffles deck words, removes duplicates.
    - Persists `game_sessions` row and associated game words context.
  - Pronunciation submission:
    - Records each attempt with response time and correctness.
    - Delegates to speech recognition engine to determine correctness.
  - End:
    - Computes score from correctness and response times (see `game_service`).
    - Updates streaks and statistics.

- **Streaks**
  - Track continuous days with at least one completed game.
  - Maintain `currentStreak` and `longestStreak` per user.

- **Statistics & wrong word analysis**
  - Uses `game_attempts` to compute:
    - Totals, averages, best score.
    - Per-day score history.
    - Error ratio per word = incorrect_attempts / total_attempts.
    - Top 20 wrong words, optionally filtered by teacher’s students.

---

## ASR and Engines

Detailed requirements come from `BACKEND.md` and `SPEECH_RECOGNITION.md`:

### Speech Recognition Engine

- Implemented in `backend/app/engines/speech_recognition_engine.py`.
- Responsibilities:
  - Accept WAV audio and the expected Chinese word + jyutping.
  - Use `faster-whisper` (or similar) for Cantonese recognition.
  - Compare recognized jyutping vs expected jyutping with tolerance.
  - Return boolean correctness (and optionally confidence score).

### Jyutping Mapping

- Implemented via `pycantonese` in `backend/app/engines/jyutping_engine.py`.
- Used when admin adds new words:
  - Input: Chinese word text.
  - Output: jyutping string.
  - Integrated into admin word creation endpoint.

### Mispronunciation Analysis

- Implemented via `statistics_service` + DB queries on `game_attempts`.
- Produces error ratios and top wrong words for:
  - Global view (admin).
  - Teacher-specific view (only their students).

For further engine/ASR-specific notes, see `backend/SPEECH_RECOGNITION.md` (if present) and `ASR_FIX.md`.

---

## Integration & Testing

### Frontend–Backend Integration

- `src/services/api.ts` talks to the FastAPI backend at `VITE_API_BASE_URL` (e.g. `http://localhost:8000/api`).
- Auth flows:
  - Login/register call backend auth endpoints.
  - JWT is stored in `localStorage` and attached to subsequent requests.
- Game & statistics:
  - Game-related methods call `/games/*` and `/statistics` endpoints.
  - Admin and teacher views call `/admin/*`, `/students`, `/words/error-ratios`.

### Backend Tests

- Unit tests:
  - Located in `backend/tests/`.
  - Cover auth, decks, games, statistics, admin endpoints, etc.
- Integration tests:
  - Located in `backend/tests_integration/`.
  - Use SQLite in-memory / temporary DB.
  - Validate database models and operations, including migrations.

### Frontend Tests

- Vitest + Testing Library tests:
  - Components (`SwipeCard`, `LanguageSwitcher`, etc.).
  - Pages (`LoginPage`, `AdminDashboard`, etc.).
  - Context behavior.

---

## Requirements Mapping

The original high-level requirements in `project_requirements.md` and `project_implementation.md` are now implemented as follows:

- **Frontend requirements** (`FRONTEND.md`):
  - All core pages, roles, statistics views, and interactive game UI are implemented and wired to the real backend.
- **Backend requirements** (`BACKEND.md`):
  - FastAPI-based API with JWT auth, deck & word management, game sessions, statistics, and admin features.
- **Agents & MCP guidance** (`BACKEND_AGENTS.md`):
  - Admin-focused jyutping generation is implemented via `pycantonese`.
  - Additional MCP integration can be layered on top of the existing engine services if desired.

For the exhaustive requirement list, continue to use `project_requirements.md` as the canonical reference; this document explains how those requirements are realized in code.


