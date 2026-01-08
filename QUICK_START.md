# Quick Start Guide

Get the Cantonese Word Game up and running quickly. For detailed documentation, see [README.md](README.md), [IMPLEMENTATION.md](IMPLEMENTATION.md), and [DEPLOYMENT.md](DEPLOYMENT.md).

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+ and `uv` (for backend)
- **Docker** and Docker Compose (for containerized development)
- **PostgreSQL** 15+ (or use Docker Compose)

## Local Development

### Option 1: Native Development

1. **Install dependencies:**
   ```bash
   npm install
   cd backend && uv sync && cd ..
   ```

2. **Start services:**
   ```bash
   ./start-services.sh
   ```
   Or manually:
   ```bash
   npm run dev:all
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Docker Development

1. **Start all services with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Frontend: http://localhost:80
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Testing

```bash
# Frontend tests
npm test

# Frontend tests with UI
npm run test:ui

# Backend tests
cd backend && uv run pytest
```

## Build

```bash
# Frontend production build
npm run build

# Preview production build
npm run preview
```

## Default Login Credentials

- **Admin**: `admin` / `cantonese`
- **Student**: `student1` / `any password` (min 3 chars)
- **Teacher**: `teacher1` / `any password` (min 3 chars)

## Deployment

### Quick Deploy to AWS

1. **Ensure infrastructure is deployed:**
   ```bash
   cd infrastructure/cdk
   pip install -r requirements.txt
   cdk bootstrap  # First time only
   cdk deploy
   ```

2. **Deploy application:**
   ```bash
   ./DEPLOY_NOW.sh
   ```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Next Steps

- Read [IMPLEMENTATION.md](IMPLEMENTATION.md) for technical specifications
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for Docker, CI/CD, and AWS deployment
- Check [README.md](README.md) for project overview and architecture

