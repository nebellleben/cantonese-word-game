# Quick Start Guide

## Installation

```bash
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Testing

Run tests:

```bash
npm test
```

Run tests with UI:

```bash
npm run test:ui
```

## Build

Build for production:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

## Default Login Credentials

### Admin
- Username: `admin`
- Password: `cantonese`

### Student (Mock)
- Username: `student1`
- Password: `any password` (minimum 3 characters)

### Teacher (Mock)
- Username: `teacher1`
- Password: `any password` (minimum 3 characters)

## Features Overview

### Student
1. Login/Register
2. Select a deck to practice
3. Play game with swipe card interface
4. View statistics with charts
5. See top 20 wrongly pronounced words

### Teacher
1. View list of students
2. Review individual student statistics
3. View word error ratios

### Admin
1. Manage word decks (create, delete)
2. Add/remove words from decks
3. Associate students with teachers
4. View statistics (individual and collective)
5. Reset user passwords

## Project Structure

- `src/pages/` - Page components
- `src/components/` - Reusable components
- `src/services/api.ts` - Centralized API client (currently mocked)
- `src/contexts/` - React contexts (Auth)
- `src/types/` - TypeScript type definitions

## Next Steps

When the backend is ready:
1. Set `VITE_API_BASE_URL` in `.env`
2. Update `src/services/api.ts` to use real API endpoints
3. Remove mock implementations

