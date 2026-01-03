# Running the Service

## Build Status

✅ **Frontend**: Built successfully to `dist/` directory
✅ **Backend**: Dependencies installed and ready

## Starting the Services

### Option 1: Development Mode (Recommended for Development)

Start both frontend and backend in development mode:

```bash
npm run dev:all
```

This will start:
- Backend API: http://localhost:8000
- Frontend Dev Server: http://localhost:5173

### Option 2: Production Mode

#### Start Backend Only

```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

#### Serve Built Frontend

After building (`npm run build`), serve the production build:

**Option A: Using Vite Preview**
```bash
npm run preview
```
Frontend will be available at: http://localhost:4173

**Option B: Using a Static Server**
```bash
# Using Python
cd dist
python3 -m http.server 8080

# Or using Node.js http-server
npx http-server dist -p 8080
```

**Option C: Using nginx or Apache**
Point your web server to the `dist/` directory.

### Option 3: Run Both Separately

**Terminal 1 - Backend:**
```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend (Development):**
```bash
npm run dev
```

**Terminal 2 - Frontend (Production):**
```bash
npm run preview
```

## Verify Services

### Check Backend
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"healthy"}`

### Check Frontend
Open http://localhost:5173 (dev) or http://localhost:4173 (preview) in your browser.

## Default Login Credentials

- **Username**: `admin`
- **Password**: `cantonese`

## Environment Variables

If you need to change the API URL, create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Production Deployment

For production deployment:

1. **Backend**: Use a production ASGI server like:
   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Frontend**: The built files in `dist/` can be served by any static file server or CDN.

3. **Database**: Configure a real database (PostgreSQL/SQLite) instead of the mock database.

## Troubleshooting

### Backend not starting?
- Check if port 8000 is in use: `lsof -ti:8000`
- Ensure dependencies are installed: `cd backend && uv sync`
- Check backend logs for errors

### Frontend can't connect to backend?
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in backend
- Verify `VITE_API_BASE_URL` environment variable

### Build errors?
- Run `npm install` to ensure dependencies are installed
- Check TypeScript errors: `npm run build`

