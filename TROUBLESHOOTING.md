# Troubleshooting Guide

## "Backend server is not running" Error

If you see this error even though you think the backend is running, try these steps:

### Step 1: Check if Backend is Actually Running

```bash
# Check if something is listening on port 8000
lsof -ti:8000

# Test if backend responds
curl http://localhost:8000/health
```

Expected output: `{"status":"healthy"}`

### Step 2: Kill Any Stale Processes

Sometimes old backend processes can interfere:

```bash
# Kill all uvicorn processes
pkill -f "uvicorn app.main:app"

# Or kill specific process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Step 3: Start Backend Fresh

**Option A: Using the script**
```bash
./start-backend.sh
```

**Option B: Manual start**
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option C: Using npm (starts both frontend and backend)**
```bash
npm run dev:all
```

### Step 4: Verify Backend is Working

Open a new terminal and test:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test login endpoint
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"cantonese"}'
```

You should get a JSON response with a token.

### Step 5: Check Browser Console

1. Open your browser's Developer Tools (F12)
2. Go to the Console tab
3. Try to login again
4. Look for any CORS errors or network errors

Common errors:
- **CORS error**: Backend CORS not configured properly
- **Network Error**: Backend not running or wrong URL
- **404 Not Found**: Backend running but wrong endpoint

### Step 6: Check Backend Logs

If you started the backend manually, check the terminal output for errors.

If using the script, check:
```bash
tail -f /tmp/backend.log
```

### Step 7: Verify Frontend Configuration

Check that the frontend is trying to connect to the right URL:

1. Open browser DevTools → Network tab
2. Try to login
3. Look for the failed request
4. Check the request URL - it should be `http://localhost:8000/api/auth/login`

### Common Issues

#### Issue: Port 8000 Already in Use

```bash
# Find what's using port 8000
lsof -ti:8000

# Kill it
lsof -ti:8000 | xargs kill -9
```

#### Issue: Backend Starts But Immediately Crashes

Check if dependencies are installed:
```bash
cd backend
uv sync
```

#### Issue: CORS Errors in Browser

The backend should allow `http://localhost:5173`. Check `backend/app/core/config.py`:
```python
cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
```

#### Issue: "Module not found" Errors

Make sure you're in the backend directory and dependencies are synced:
```bash
cd backend
uv sync
```

### Still Not Working?

1. **Restart everything**:
   - Kill all backend processes
   - Kill frontend dev server
   - Start backend first, wait 3 seconds
   - Then start frontend

2. **Check firewall/antivirus**: Some security software blocks localhost connections

3. **Try a different port**: 
   - Backend: Change port in uvicorn command
   - Frontend: Set `VITE_API_BASE_URL=http://localhost:NEW_PORT/api` in `.env`

4. **Clear browser cache**: Sometimes cached errors persist

### Quick Test

Run this to verify everything works:

```bash
# Start backend
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait a moment
sleep 3

# Test
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"cantonese"}'

# Stop backend
pkill -f "uvicorn app.main:app"
```

If both curl commands work, the backend is fine and the issue is with the frontend connection.

