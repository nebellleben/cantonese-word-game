# Starting the Application

## Quick Start (Recommended)

Start both frontend and backend together:

```bash
npm run dev:all
```

This will start:
- Backend on http://localhost:8000
- Frontend on http://localhost:5173

## Manual Start

### Option 1: Start Backend Only

```bash
cd backend
uv sync  # First time only
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Start Frontend Only

```bash
npm run dev
```

### Option 3: Start Both Separately

**Terminal 1 (Backend):**
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
npm run dev
```

## Verify Backend is Running

Check if backend is accessible:
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy"}`

## Login Credentials

- **Username**: `admin`
- **Password**: `cantonese`

## Troubleshooting

### Backend not starting?

1. Make sure `uv` is installed:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Sync dependencies:
   ```bash
   cd backend
   uv sync
   ```

3. Check if port 8000 is already in use:
   ```bash
   lsof -ti:8000
   ```

### Frontend can't connect to backend?

1. Verify backend is running (see above)
2. Check browser console for errors
3. Verify CORS is configured (backend allows `http://localhost:5173`)

### Port conflicts?

- Backend default: 8000
- Frontend default: 5173

To change ports:
- Backend: Modify the `--port` flag in the command
- Frontend: Set `PORT` environment variable or modify `vite.config.ts`

