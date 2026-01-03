# Frontend Requirements and Implementation Status

## Technical Requirements

### ✅ Implemented
- **Framework**: React with TypeScript
- **Routing**: React Router for navigation and protected routes
- **Language Switching**: LanguageSwitcher component available on every page
  - Supports English (en) and Traditional Chinese (zh-TW)
  - Language preference persisted in localStorage
  - Full translation coverage for all UI elements

### Architecture
- **State Management**: React Context API for authentication and language
- **API Client**: Axios-based API client with token authentication
- **Styling**: CSS modules for component-specific styles
- **Charts**: Recharts library for statistics visualization

## User Classes and Authentication

### ✅ Implemented
- **Three user roles**: Student, Teacher, and Admin
- **Registration Page**: Users can register as student or teacher
  - Username, password, email (optional), and role selection
  - Password validation (minimum 3 characters)
- **Login Page**: 
  - Username/password authentication
  - Admin default password hint displayed ("cantonese")
  - Error handling and loading states
- **Protected Routes**: Role-based route protection
  - Automatic redirection based on user role
  - Unauthorized access prevention

## Student User Features

### ✅ Implemented

#### Student Dashboard (`/student`)
- Deck selection dropdown showing available decks
- Deck descriptions displayed
- "Start Game" button to begin practice
- "View Statistics" button to access statistics page
- User welcome message and logout functionality

#### Game Page (`/student/game`)
- **Deck Selection**: Game starts with selected deck from dashboard
- **Swipe Card Interface**: 
  - SwipeCard component with touch and mouse support
  - Swipe left/right to skip words
  - Keyboard support (Arrow keys to swipe, Space/Enter to record)
  - Visual feedback during swipe (rotation and opacity)
- **Word Display**: Words appear one at a time without duplication
- **Recording Functionality**:
  - Microphone access with MediaRecorder API
  - Record button to start/stop recording
  - 5-second auto-stop recording
  - Response time tracking from word display to submission
- **Real-time Feedback**:
  - **Volume Bar**: Visual indicator showing audio level during recording (RMS-based calculation)
  - **Real-time Speech Recognition**: Web Speech API integration showing recognized text as user speaks
  - **Immediate Feedback**: Shows correct/incorrect status after pronunciation
  - **Speech Recognition Display**: Shows what the system recognized (from Web Speech API or backend)
- **Progress Tracking**: 
  - Progress bar showing game completion
  - Word counter (e.g., "Word 3 of 10")
  - Exit game option
- **Game Completion**:
  - Final score display
  - Correct/incorrect word counts
  - Total words count
  - Return to dashboard button

#### Statistics Page (`/student/statistics`)
- **Overview Section**:
  - Total games played
  - Average score
  - Best score
  - Current streak
  - Longest streak
- **Score History Chart**:
  - Bar chart visualization using Recharts
  - Filterable by deck (dropdown menu)
  - "All Decks" option to show all scores
  - Date-based score tracking
- **Top 20 Wrong Words**:
  - List of most frequently mispronounced words
  - Shows wrong count and error rate percentage
  - Sorted by wrong count (descending)

## Teacher User Features

### ✅ Implemented

#### Teacher Dashboard (`/teacher`)
- **Tab-based Interface**: Two tabs for different views
- **Student Statistics Tab**:
  - Dropdown to select from assigned students
  - Student statistics display:
    - Total games
    - Average score
    - Best score
    - Current streak
  - Score history bar chart for selected student
  - Empty state when no students assigned
- **Word Error Ratios Tab**:
  - List of all words sorted by error ratio (descending)
  - Visual ratio bar showing error percentage
  - Displays wrong count and total attempts
  - Ratio percentage calculation

## Admin User Features

### ✅ Implemented

#### Admin Dashboard (`/admin`)
- **Tab-based Interface**: Four main tabs for different functions

#### 1. Word Management Tab
- **Create New Deck**:
  - Deck name input
  - Optional description field
  - Create button
- **Manage Decks**:
  - Deck selection dropdown
  - Delete deck functionality (with confirmation)
  - Word count display per deck
- **Word Management**:
  - Add new words to selected deck
  - Word text input with Enter key support
  - List of all words in selected deck
  - Delete word functionality (with confirmation)
  - Empty state when deck has no words

#### 2. Student-Teacher Association Tab
- Student selection dropdown
- Teacher selection dropdown
- Associate button to link students with teachers
- Success/error message feedback

#### 3. Statistics Tab
- **Individual Student Statistics**:
  - Student selection dropdown
  - Statistics display (total games, average score, best score, current streak)
- **Collective Statistics**:
  - Overall statistics for all students
  - Total games, average score, best score

#### 4. Password Management Tab
- User selection dropdown (students and teachers)
- New password input field
- Password reset functionality
- Minimum password length validation (3 characters)
- Success/error message feedback

## Interactive Features

### ✅ Implemented

1. **Volume Bar During Recording**:
   - Real-time audio level visualization
   - Uses AudioContext and AnalyserNode for accurate volume measurement
   - RMS (Root Mean Square) calculation for accurate amplitude
   - Visual feedback that speech is being detected
   - Appears only when recording is active

2. **Real-time Speech Recognition**:
   - Web Speech API integration (SpeechRecognition/webkitSpeechRecognition)
   - Continuous recognition with interim results
   - Language set to 'zh-HK' (Cantonese) with fallback to 'zh-CN'
   - Displays recognized text in real-time on the swipe card
   - Shows both interim and final recognition results

3. **Immediate Feedback**:
   - Correct/incorrect status displayed immediately after pronunciation
   - Visual feedback with checkmark (✓) or cross (✗) icon
   - Shows recognized text from speech recognition
   - 2-second display before automatically moving to next word
   - Color-coded feedback (green for correct, red for incorrect)

## Additional Implementation Details

### Components
- **SwipeCard**: Reusable card component with swipe gestures
- **LanguageSwitcher**: Language toggle component
- **ProtectedRoute**: Route wrapper for authentication and authorization

### Contexts
- **AuthContext**: Manages user authentication state and token
- **LanguageContext**: Manages language preference and translations

### Services
- **API Client**: Centralized API service with:
  - Token-based authentication
  - Error handling
  - Request/response interceptors
  - FormData support for audio uploads

### Responsive Design
- Mobile-friendly swipe card interface
- Touch and mouse event support
- Responsive charts and layouts
- Keyboard navigation support

## Notes

- All pages include the LanguageSwitcher component for consistent language switching
- Error handling implemented throughout with user-friendly error messages
- Loading states displayed during API calls
- Empty states shown when no data is available
- Confirmation dialogs for destructive actions (delete deck/word)