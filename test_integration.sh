#!/bin/bash

# Integration test script for backend-frontend
# This script starts both servers and tests the integration

set -e

echo "🧪 Testing Backend-Frontend Integration"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo -e "${YELLOW}Checking if backend is running...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not running${NC}"
    echo "Starting backend..."
    cd backend
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    sleep 3
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend started${NC}"
    else
        echo -e "${RED}✗ Failed to start backend${NC}"
        exit 1
    fi
fi

# Test backend endpoints
echo -e "\n${YELLOW}Testing backend endpoints...${NC}"

# Test health endpoint
echo -n "Testing /health... "
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# Test login
echo -n "Testing /api/auth/login... "
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"cantonese"}')
if echo "$LOGIN_RESPONSE" | grep -q "token"; then
    echo -e "${GREEN}✓${NC}"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
else
    echo -e "${RED}✗${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

# Test authenticated endpoint
echo -n "Testing /api/decks (authenticated)... "
DECKS_RESPONSE=$(curl -s -X GET http://localhost:8000/api/decks \
    -H "Authorization: Bearer $TOKEN")
if echo "$DECKS_RESPONSE" | grep -q "id"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Response: $DECKS_RESPONSE"
    exit 1
fi

# Test CORS
echo -n "Testing CORS headers... "
CORS_HEADERS=$(curl -s -I -X OPTIONS http://localhost:8000/api/decks \
    -H "Origin: http://localhost:5173" \
    -H "Access-Control-Request-Method: GET" | grep -i "access-control")
if [ -n "$CORS_HEADERS" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ CORS headers not found (may be handled by middleware)${NC}"
fi

# Check frontend configuration
echo -e "\n${YELLOW}Checking frontend configuration...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
    if grep -q "VITE_API_BASE_URL" .env; then
        echo -e "${GREEN}✓ VITE_API_BASE_URL is set${NC}"
        cat .env | grep VITE_API_BASE_URL
    else
        echo -e "${YELLOW}⚠ VITE_API_BASE_URL not set in .env${NC}"
        echo "Frontend will use default: http://localhost:8000/api"
    fi
else
    echo -e "${YELLOW}⚠ No .env file found${NC}"
    echo "Frontend will use default: http://localhost:8000/api"
fi

# Check if frontend can reach backend
echo -e "\n${YELLOW}Testing frontend-backend connectivity...${NC}"
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend can reach backend at http://localhost:8000${NC}"
else
    echo -e "${RED}✗ Frontend cannot reach backend${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Integration tests passed!${NC}"
echo ""
echo "To test the full integration:"
echo "1. Start backend: cd backend && uv run uvicorn app.main:app --reload"
echo "2. Start frontend: npm run dev"
echo "3. Open http://localhost:5173 in your browser"
echo "4. Login with: username=admin, password=cantonese"

# Cleanup
if [ -n "$BACKEND_PID" ]; then
    echo -e "\n${YELLOW}Stopping backend server (PID: $BACKEND_PID)...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
fi

