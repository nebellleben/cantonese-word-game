#!/usr/bin/env bash

# Start both backend (FastAPI) and frontend (Vite) for the Cantonese Word Game.
# This is a thin wrapper around the existing npm scripts.
#
# Usage:
#   ./start-services.sh
#
# Requirements:
#   - Node/npm installed
#   - In the first run, from the project root:
#       npm install
#       cd backend && uv sync && cd ..
#
# The script will run:
#   npm run dev:all
# which starts:
#   - Backend API on http://localhost:8000
#   - Frontend on http://localhost:5173

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "🚀 Starting frontend and backend via npm run dev:all ..."
echo "   - Backend: http://localhost:8000"
echo "   - Frontend: http://localhost:5173"
echo

npm run dev:all


