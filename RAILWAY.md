# Railway Deployment

This guide covers deploying the Cantonese Word Game to Railway.

## Prerequisites

- [Railway account](https://railway.app/) (free tier includes $5/month credit)
- [Railway CLI](https://docs.railway.app/develop/cli) (optional, for local development)

## Quick Deploy

### Option 1: Deploy via Railway Dashboard

1. Go to [railway.app](https://railway.app/) and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect the `railway.toml` configuration

### Option 2: Deploy via CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize and deploy
railway init
railway up
```

## Required Environment Variables

Set these in Railway dashboard (Project → Variables):

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Auto-provided by Railway Postgres |
| `SECRET_KEY` | JWT secret key | Yes - generate a secure random string |

### Generating SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Adding PostgreSQL Database

1. In Railway dashboard, click "New" → "Database" → "Add PostgreSQL"
2. Railway automatically sets `DATABASE_URL` environment variable
3. The database will be linked to your service

## How It Works

The deployment uses `backend/Dockerfile.unified` which:
1. Builds the React frontend with Vite
2. Sets API base URL to `/api` (same-origin requests)
3. Packages the Python FastAPI backend
4. Copies frontend static files to `./static` for the backend to serve
5. Runs Alembic migrations on startup
6. Serves both API and frontend on a single port

## Architecture

```
┌─────────────────────────────────────┐
│  Railway Service (Single Container) │
├─────────────────────────────────────┤
│  FastAPI Backend (:8000)            │
│  ├── /api/*  → API routes           │
│  └── /*      → React static files   │
├─────────────────────────────────────┤
│  PostgreSQL (Railway Add-on)        │
└─────────────────────────────────────┘
```

## Cost Estimate

- **Starter Plan**: Free with $5/month credit
- **Estimated usage**: ~$2-4/month for small app
- Always-on (no cold starts)

## Monitoring

- View logs: `railway logs` or Railway dashboard
- Health check: `https://your-app.railway.app/health`

## Troubleshooting

### Database connection errors
- Verify `DATABASE_URL` is set
- Check PostgreSQL service is running

### Build failures
- Check build logs in Railway dashboard
- Verify `uv.lock` exists in `backend/` directory

### Frontend not loading
- Check that static files are being served
- Verify `VITE_API_BASE_URL=/api` in Dockerfile
