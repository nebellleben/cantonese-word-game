# Cantonese Word Game - Frontend

This is the frontend application for the Cantonese Word Game, built with React and TypeScript.

## Features

### User Roles

- **Student**: Play games, view statistics, track progress
- **Teacher**: View student statistics and word error ratios
- **Admin**: Manage words database, associate students with teachers, view statistics, manage passwords

### Student Features

- Choose from available decks to practice
- Swipe card style game interface (works on desktop and mobile)
- Record pronunciation for each word
- View statistics with charts
- Track streaks and scores
- See top 20 wrongly pronounced words

### Teacher Features

- View list of students under management
- Review individual student statistics
- View word error ratios sorted by frequency

### Admin Features

- Create and manage word decks
- Add/remove words from decks
- Associate students with teachers
- View individual and collective statistics
- Reset user passwords

## Technology Stack

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **React Router**: Navigation
- **Recharts**: Data visualization
- **Axios**: HTTP client (for future backend integration)
- **Vitest**: Testing framework

## Project Structure

```
src/
├── components/       # Reusable components
│   ├── SwipeCard.tsx
│   └── __tests__/
├── contexts/         # React contexts
│   └── AuthContext.tsx
├── pages/            # Page components
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── StudentDashboard.tsx
│   ├── GamePage.tsx
│   ├── StatisticsPage.tsx
│   ├── TeacherDashboard.tsx
│   └── AdminDashboard.tsx
├── services/         # API client and services
│   ├── api.ts        # Centralized API client (mocked)
│   └── __tests__/
├── types/            # TypeScript type definitions
│   └── index.ts
└── test/             # Test setup
    └── setup.ts
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Testing

### Run Tests

```bash
npm test
```

### Run Tests with UI

```bash
npm run test:ui
```

## API Client

All backend API calls are centralized in `src/services/api.ts`. Currently, all methods are mocked for development. When the backend is ready, you can:

1. Set the `VITE_API_BASE_URL` environment variable
2. Replace mock implementations with actual API calls
3. The API client already includes:
   - Authentication token handling
   - Request/response interceptors
   - Error handling structure

## Mock Data

The application uses in-memory mock data for development:

- **Default Admin**: username: `admin`, password: `cantonese`
- **Sample Students**: `student1` (any password)
- **Sample Teachers**: `teacher1` (any password)

## Environment Variables

Create a `.env` file for local development:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Responsive Design

The application is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile devices

The swipe card game interface supports:
- Mouse drag
- Touch gestures
- Keyboard navigation (arrow keys, space/enter)

## Future Integration

When the backend is ready:

1. Update `src/services/api.ts` to use actual API endpoints
2. Remove mock data implementations
3. Update environment variables for API base URL
4. Test all API endpoints match the OpenAPI specification

