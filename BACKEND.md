# Backend Requirements

## Technical Requirements

- **Language**: Python
- **Framework**: FastAPI (recommended) or Flask for REST API
- **Database**: PostgreSQL or SQLite (for development)
- **Authentication**: JWT (JSON Web Tokens) with Bearer token authentication
- **API Base URL**: `http://localhost:8000/api`
- **Dependency Management**: Use `uv` (see BACKEND_AGENTS.md)
- **Audio Processing**: Support for WAV audio format (multipart/form-data)

## API Endpoints Specification

### Authentication Endpoints

#### POST `/api/auth/login`
- **Request Body**: `{ "username": string, "password": string }`
- **Response**: `{ "token": string, "user": User }`
- **Description**: Authenticate user and return JWT token

#### POST `/api/auth/register`
- **Request Body**: `{ "username": string, "password": string, "role": "student" | "teacher" }`
- **Response**: `{ "token": string, "user": User }`
- **Description**: Register new student or teacher account

### Deck Management Endpoints

#### GET `/api/decks`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `Deck[]`
- **Description**: Get all available decks (accessible to all authenticated users)

#### GET `/api/decks/{deckId}/words`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `Word[]`
- **Description**: Get all words in a specific deck

### Game Session Endpoints

#### POST `/api/games/start`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: `{ "deckId": string }`
- **Response**: `GameSession`
- **Description**: Start a new game session with randomly shuffled words from the deck (no duplicates)

#### POST `/api/games/pronunciation`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: `FormData` with:
  - `sessionId`: string
  - `wordId`: string
  - `responseTime`: number (milliseconds)
  - `audio`: File (WAV format, optional for testing)
- **Response**: `{ "isCorrect": boolean }`
- **Description**: Submit pronunciation attempt for a word in the current session. Uses speech recognition engine to evaluate correctness.

#### POST `/api/games/{sessionId}/end`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `GameSession` (with final score calculated)
- **Description**: End the game session and calculate final score based on:
  - Number of correctly pronounced words
  - Average response time
  - Update user streak if game completed today

### Statistics Endpoints

#### GET `/api/statistics`
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**: 
  - `userId`: string (optional, for teachers/admins viewing specific student)
  - `deckId`: string (optional, filter by deck)
- **Response**: `GameStatistics`
- **Description**: Get game statistics for the authenticated user (or specified user if admin/teacher)

#### GET `/api/students`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `Student[]`
- **Description**: 
  - For teachers: Returns list of students associated with the teacher
  - For admins: Returns all students
  - For students: Returns empty array or error

#### GET `/api/words/error-ratios`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `WrongWord[]`
- **Description**: Get word error ratios sorted by error rate (descending). For teachers, shows errors from their students. For admins, shows all errors.

### Admin Endpoints

#### POST `/api/admin/decks`
- **Headers**: `Authorization: Bearer <token>` (admin only)
- **Request Body**: `{ "name": string, "description": string }`
- **Response**: `Deck`
- **Description**: Create a new word deck

#### DELETE `/api/admin/decks/{deckId}`
- **Headers**: `Authorization: Bearer <token>` (admin only)
- **Response**: `204 No Content`
- **Description**: Delete a deck

#### POST `/api/admin/decks/{deckId}/words`
- **Headers**: `Authorization: Bearer <token>` (admin only)
- **Request Body**: `{ "text": string }` (Chinese word)
- **Response**: `Word`
- **Description**: Add a word to a deck. Backend should automatically generate jyutping using the jyutping mapping agent.

#### DELETE `/api/admin/words/{wordId}`
- **Headers**: `Authorization: Bearer <token>` (admin only)
- **Response**: `204 No Content`
- **Description**: Delete a word from any deck

#### POST `/api/admin/associations`
- **Headers**: `Authorization: Bearer <token>` (admin only)
- **Request Body**: `{ "studentId": string, "teacherId": string }`
- **Response**: `204 No Content`
- **Description**: Associate a student with a teacher

#### POST `/api/admin/users/{userId}/reset-password`
- **Headers**: `Authorization: Bearer <token>` (admin only)
- **Request Body**: `{ "password": string }`
- **Response**: `204 No Content`
- **Description**: Reset password for any user (student or teacher)

## Data Models

### User
```python
{
  "id": string (UUID),
  "username": string,
  "role": "student" | "teacher" | "admin",
  "createdAt": datetime
}
```

### Deck
```python
{
  "id": string (UUID),
  "name": string,
  "description": string,
  "createdAt": datetime
}
```

### Word
```python
{
  "id": string (UUID),
  "text": string,  # Chinese characters
  "jyutping": string,  # Jyutping transliteration
  "deckId": string,
  "createdAt": datetime
}
```

### GameSession
```python
{
  "id": string (UUID),
  "userId": string,
  "deckId": string,
  "words": GameWord[],
  "score": number | null,  # Calculated when game ends
  "startedAt": datetime,
  "endedAt": datetime | null
}
```

### GameWord
```python
{
  "wordId": string,
  "text": string,  # Optional, for display
  "isCorrect": boolean | null,  # null until pronunciation submitted
  "responseTime": number | null  # milliseconds
}
```

### GameStatistics
```python
{
  "totalGames": number,
  "averageScore": number,
  "bestScore": number,
  "currentStreak": number,  # Consecutive days with completed games
  "longestStreak": number,
  "scoresByDate": [
    {
      "date": string (ISO date),
      "score": number
    }
  ],
  "topWrongWords": [
    {
      "wordId": string,
      "word": string,
      "wrongCount": number,
      "ratio": number  # error ratio (0.0 to 1.0)
    }
  ]
}
```

### Student
```python
{
  "id": string (UUID),
  "username": string,
  "streak": number,
  "totalScore": number  # Sum of all game scores
}
```

### WrongWord
```python
{
  "wordId": string,
  "text": string,
  "errorCount": number,
  "totalAttempts": number,
  "errorRatio": number  # errorCount / totalAttempts
}
```

## Core Engines

### 1. Speech Recognition Engine
- **Purpose**: Evaluate if user's pronunciation matches the expected Cantonese word
- **Input**: 
  - Audio file (WAV format) from user's microphone
  - Expected word (Chinese text and jyutping)
- **Output**: Boolean indicating correctness
- **Requirements**:
  - High fidelity Cantonese speech recognition model
  - Compare user's pronunciation with expected jyutping
  - Handle variations in pronunciation (tolerance for minor differences)
  - Return confidence score if possible (for future enhancements)

### 2. Speech Synthesis Engine
- **Purpose**: Generate audio pronunciation of Cantonese words (for future features like audio hints)
- **Input**: Chinese word and jyutping
- **Output**: Audio file (WAV format)
- **Note**: May not be immediately required by frontend, but should be designed for future use

### 3. Jyutping Mapping Agent
- **Purpose**: Automatically generate jyutping transliteration for Chinese words
- **Input**: Chinese word (text)
- **Output**: Jyutping transliteration string
- **Requirements**:
  - Should be called automatically when admin adds a new word
  - Use a reliable Cantonese-to-Jyutping conversion library or API
  - Handle edge cases and multiple possible pronunciations

### 4. Mispronunciation Analysis Engine
- **Purpose**: Identify commonly mispronounced words for teacher insights
- **Input**: Gameplay records from database
- **Output**: Sorted list of words by error ratio
- **Requirements**:
  - Calculate error ratio: (number of incorrect attempts) / (total attempts)
  - Sort by error ratio (descending)
  - Filter by teacher's students (if teacher is viewing)
  - Support filtering by deck (optional)

## Database Schema Requirements

### Users Table
- `id` (UUID, primary key)
- `username` (string, unique)
- `password_hash` (string, hashed)
- `role` (enum: student, teacher, admin)
- `created_at` (timestamp)

### Decks Table
- `id` (UUID, primary key)
- `name` (string)
- `description` (string, nullable)
- `created_at` (timestamp)

### Words Table
- `id` (UUID, primary key)
- `text` (string, Chinese characters)
- `jyutping` (string)
- `deck_id` (UUID, foreign key to decks)
- `created_at` (timestamp)

### Game Sessions Table
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key to users)
- `deck_id` (UUID, foreign key to decks)
- `score` (integer, nullable, calculated on end)
- `started_at` (timestamp)
- `ended_at` (timestamp, nullable)

### Game Attempts Table
- `id` (UUID, primary key)
- `session_id` (UUID, foreign key to game_sessions)
- `word_id` (UUID, foreign key to words)
- `is_correct` (boolean)
- `response_time` (integer, milliseconds)
- `attempted_at` (timestamp)

### Student-Teacher Associations Table
- `id` (UUID, primary key)
- `student_id` (UUID, foreign key to users)
- `teacher_id` (UUID, foreign key to users)
- `created_at` (timestamp)

### User Streaks Table (or computed from game_sessions)
- Track daily game completion for streak calculation
- `user_id` (UUID, foreign key to users)
- `date` (date)
- `games_completed` (integer)

## Business Logic Requirements

### Authentication & Authorization
- Default admin account: username "admin", password "cantonese"
- JWT tokens should expire (recommend 24 hours)
- Role-based access control:
  - Students: Can only view their own data
  - Teachers: Can view their associated students' data
  - Admins: Can view and modify all data

### Game Session Logic
- When starting a game:
  - Randomly shuffle words from selected deck
  - Ensure no duplicates
  - Create session record
  - Return session with word list
- When submitting pronunciation:
  - Record attempt with response time
  - Use speech recognition to evaluate correctness
  - Update session state
- When ending game:
  - Calculate score: `(correct_words * 100) - (average_response_time / 100)` or similar formula
  - Update user statistics
  - Check and update streak if game completed today

### Streak Calculation
- Track consecutive days where user completed at least one game
- Reset to 0 if user misses a day
- Update `currentStreak` and `longestStreak` in user statistics

### Statistics Calculation
- `totalGames`: Count of completed game sessions
- `averageScore`: Mean of all game scores
- `bestScore`: Maximum game score
- `scoresByDate`: Group scores by date for charting
- `topWrongWords`: Top 20 words with highest error ratios

### Word Error Ratio Calculation
- For each word: `errorRatio = incorrect_attempts / total_attempts`
- Sort by error ratio (descending)
- Filter by teacher's students if applicable
- Return top words for display

## Error Handling

- Return appropriate HTTP status codes:
  - `200 OK`: Successful GET requests
  - `201 Created`: Successful POST requests creating resources
  - `204 No Content`: Successful DELETE requests
  - `400 Bad Request`: Invalid request data
  - `401 Unauthorized`: Missing or invalid token
  - `403 Forbidden`: Insufficient permissions
  - `404 Not Found`: Resource not found
  - `500 Internal Server Error`: Server errors

- Error response format:
```json
{
  "error": "Error message",
  "message": "Detailed error description"
}
```

## Performance Requirements

- API response time: < 500ms for most endpoints
- Speech recognition: < 2 seconds for pronunciation evaluation
- Support concurrent game sessions
- Database queries should be optimized with proper indexing

## Security Requirements

- Hash passwords using bcrypt or similar (never store plaintext)
- Validate and sanitize all input
- Use parameterized queries to prevent SQL injection
- CORS configuration for frontend origin
- Rate limiting for authentication endpoints
