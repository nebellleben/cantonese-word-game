# Setup Guide

## Frontend Setup

The frontend is already set up and running. The dev server should be accessible at http://localhost:5173

## Backend Setup Required

The frontend requires a backend API server to be running. Currently, the frontend is configured to connect to:
- **Backend URL**: `http://localhost:8000/api`

### To Fix the "Network Error" Issue:

1. **Start the Backend Server**
   - The backend should be a Python-based API server
   - It should run on port 8000
   - The API should have the following endpoints:
     - `POST /api/auth/login` - User login
     - `POST /api/auth/register` - User registration
     - `GET /api/decks` - Get word decks
     - And other endpoints as defined in `src/services/api.ts`

2. **Check Backend Status**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/api/health
   # or
   lsof -ti:8000
   ```

3. **If Backend is on Different Port**
   - Create a `.env` file in the project root
   - Add: `VITE_API_BASE_URL=http://localhost:YOUR_PORT/api`
   - Restart the dev server

### Current Error Message

When the backend is not running, you should now see:
> "Backend server is not running. Please start the backend API server on port 8000."

Instead of the generic "Network Error".

## Testing Without Backend

Currently, the frontend requires the backend to function. All API calls will fail if the backend is not running.

