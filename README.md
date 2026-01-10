# Cantonese Word Game for Dyslexic Students

A web-based educational game designed for primary school students in Hong Kong, especially those diagnosed with Dyslexia, whose first language is Cantonese. This game aims to improve word recognition and create motivation for students to practice recognizing Chinese words through interactive pronunciation exercises.

## 🎉 Live Production Demo

**The application is deployed and accessible on AWS!**

- **Frontend:** http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com
- **API Docs:** http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com:8000/docs
- **Backend API:** http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com:8000/api

**Status:** ✅ All services running and healthy (Region: us-east-1)

**Test Credentials:**
- Admin: `admin@example.com` / `admin123`
- Teacher: `teacher@example.com` / `teacher123`
- Student: `student@example.com` / `student123`

For detailed access information, see [`PRODUCTION_ACCESS.md`](PRODUCTION_ACCESS.md).

---

## Problem Statement

Dyslexia affects a significant number of students in Hong Kong, making it challenging for them to recognize and pronounce Chinese characters. Traditional learning methods may not be engaging enough for these students. This application provides:

- **Interactive Learning**: A gamified approach to word recognition and pronunciation practice
- **Immediate Feedback**: Real-time pronunciation evaluation using speech recognition technology
- **Progress Tracking**: Comprehensive statistics and progress monitoring for students, teachers, and administrators
- **Accessibility**: Bilingual interface (English and Traditional Chinese) to support diverse learning needs

## Features and Functionality

### User Roles

The application supports three distinct user roles, each with tailored functionality:

#### 👨‍🎓 Student Features
- **Deck Selection**: Choose from available word decks for practice
- **Interactive Game Interface**: Swipe card-style game with touch and mouse support
- **Pronunciation Practice**: Record and submit pronunciation attempts for each word
- **Real-time Feedback**: 
  - Volume visualization during recording
  - Real-time speech recognition display
  - Immediate correct/incorrect feedback after pronunciation
- **Progress Tracking**: 
  - View statistics with charts
  - Track streaks and scores
  - See top 20 wrongly pronounced words
- **Statistics Dashboard**: Comprehensive view of game history, scores, and improvement trends

#### 👨‍🏫 Teacher Features
- **Student Management**: View list of students under their supervision
- **Individual Student Statistics**: Review detailed statistics for each student
- **Word Error Analysis**: View word error ratios sorted by frequency to identify common challenges
- **Score History**: Visualize student progress over time with interactive charts

#### 👨‍💼 Admin Features
- **Deck Management**: Create and delete word decks
- **Word Management**: Add/remove words from decks with automatic Jyutping generation
- **Student-Teacher Association**: Link students with their teachers
- **User Management**: Reset passwords for any user
- **Comprehensive Statistics**: View individual and collective statistics across all users

### Core Functionality

1. **Authentication System**
   - JWT-based authentication
   - User registration (student/teacher roles)
   - Role-based access control
   - Default admin account: `admin` / `cantonese`

2. **Game Engine**
   - Randomized word selection from decks (no duplicates)
   - Response time tracking
   - Score calculation based on correctness and speed
   - Streak tracking for consecutive days of practice

3. **Speech Recognition**
   - Real-time pronunciation evaluation
   - Web Speech API integration for client-side recognition
   - Backend ASR (Automatic Speech Recognition) engine for Cantonese
   - Audio recording and processing

4. **Statistics and Analytics**
   - Total games played
   - Average and best scores
   - Current and longest streaks
   - Score history visualization
   - Word error ratio analysis

5. **Language Support**
   - Bilingual interface (English and Traditional Chinese)
   - Language preference persistence
   - Full translation coverage for all UI elements

## Technology Stack

### Frontend
- **React 18**: Modern UI framework with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and development server
- **React Router**: Client-side routing and navigation
- **Recharts**: Data visualization and charting
- **Axios**: HTTP client for API communication
- **Vitest**: Testing framework
- **CSS Modules**: Component-scoped styling

### Backend
- **Python 3.11+**: Programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and settings management
- **JWT (python-jose)**: Authentication tokens
- **bcrypt**: Password hashing
- **pycantonese**: Jyutping conversion library
- **faster-whisper**: Cantonese speech recognition
- **uv**: Modern Python package manager

### Database
- **SQLite**: Development database (default)
- **PostgreSQL**: Production database support
- **Alembic Migrations**: Version-controlled schema changes

### Development Tools
- **Concurrently**: Run frontend and backend simultaneously
- **pytest**: Backend testing framework
- **ESLint**: Code linting for TypeScript/React

## Documentation Map

- **Implementation & Technical Details**: see `IMPLEMENTATION.md`
- **Docker, CI/CD & Cloud Deployment**: see `DEPLOYMENT.md`
- **Quick Start & Operational Guide**: see `QUICK_START.md`
- **Project Requirements**: see `project_requirements.md`

## System Architecture

### Architecture Overview

```
┌─────────────────┐
│   React Frontend │
│   (Port 5173)    │
└────────┬─────────┘
         │ HTTP/REST API
         │ (JWT Auth)
         ▼
┌─────────────────┐
│  FastAPI Backend │
│   (Port 8000)    │
└────────┬─────────┘
         │
         ├───► SQLAlchemy ORM
         │
         ▼
┌─────────────────┐
│   Database      │
│ SQLite/PostgreSQL│
└─────────────────┘
```

### Component Structure

**Frontend Structure:**
```
src/
├── components/      # Reusable UI components
│   ├── SwipeCard.tsx
│   └── LanguageSwitcher.tsx
├── contexts/        # React Context providers
│   ├── AuthContext.tsx
│   └── LanguageContext.tsx
├── pages/           # Page components
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── StudentDashboard.tsx
│   ├── GamePage.tsx
│   ├── StatisticsPage.tsx
│   ├── TeacherDashboard.tsx
│   └── AdminDashboard.tsx
├── services/        # API client and services
│   └── api.ts       # Centralized API client
└── types/           # TypeScript definitions
```

**Backend Structure:**
```
backend/
├── app/
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── decks.py
│   │   │   ├── games.py
│   │   │   ├── statistics.py
│   │   │   └── admin.py
│   │   └── models/
│   │       └── schemas.py   # Pydantic models
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   ├── security.py      # JWT & password hashing
│   │   └── dependencies.py # FastAPI dependencies
│   ├── db/
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── database_service.py # Database service layer
│   │   └── base.py          # Database connection
│   ├── engines/
│   │   ├── jyutping_engine.py
│   │   └── speech_recognition_engine.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── game_service.py
│   │   └── statistics_service.py
│   └── main.py              # FastAPI application
├── alembic/                 # Database migrations
├── tests/                   # Unit tests
├── tests_integration/       # Integration tests
└── openapi/
    └── openapi.yaml         # API specification
```

### Data Flow

1. **User Authentication**: User logs in → Backend validates credentials → Returns JWT token
2. **Game Session**: User selects deck → Backend creates session with randomized words → Frontend displays words
3. **Pronunciation Submission**: User records audio → Frontend sends to backend → ASR engine evaluates → Returns correctness
4. **Statistics**: User requests stats → Backend queries database → Returns aggregated data → Frontend visualizes

## User Stories / Use Cases

### Student Use Cases

1. **As a student, I want to register an account** so that I can track my progress
   - Registration page with username, password, and role selection
   - Automatic login after successful registration

2. **As a student, I want to select a word deck** so that I can practice specific vocabulary
   - Dashboard with deck selection dropdown
   - Deck descriptions to help choose appropriate content

3. **As a student, I want to practice pronunciation** so that I can improve my Cantonese
   - Interactive swipe card interface
   - Recording functionality with visual feedback
   - Real-time speech recognition display

4. **As a student, I want to see my progress** so that I can track improvement
   - Statistics page with charts and metrics
   - Streak tracking for motivation
   - Top wrong words list for focused practice

### Teacher Use Cases

1. **As a teacher, I want to view my students' statistics** so that I can monitor their progress
   - Student selection dropdown
   - Individual student statistics view
   - Score history charts

2. **As a teacher, I want to identify common mistakes** so that I can adjust my teaching
   - Word error ratios sorted by frequency
   - Visual ratio bars showing error percentages

### Admin Use Cases

1. **As an admin, I want to manage word decks** so that I can organize content
   - Create and delete decks
   - Add/remove words with automatic Jyutping generation

2. **As an admin, I want to associate students with teachers** so that teachers can monitor their students
   - Student-teacher association interface

3. **As an admin, I want to manage user accounts** so that I can support users
   - Password reset functionality
   - User management capabilities

## Setup and Installation

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **uv** (Python package manager) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **PostgreSQL** (optional, for production) or SQLite (default, included)

### Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies using uv
uv sync

# Initialize database (first time only)
uv run python init_db.py

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`
- API Documentation (Swagger): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Running Both Services

```bash
# From project root, run both frontend and backend
npm run dev:all
```

This uses `concurrently` to run both services simultaneously.

### Environment Configuration

Create a `.env` file in the project root (optional):

```env
# Frontend
VITE_API_BASE_URL=http://localhost:8000/api

# Backend (optional, defaults shown)
DATABASE_URL=sqlite:///./cantonese_game.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/cantonese_game
```

## Testing

### Frontend Tests

```bash
# Run tests
npm test

# Run tests with UI
npm run test:ui
```

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_auth.py
```

### Integration Tests

```bash
# Run integration test script
./test_integration.sh

# Or manually run integration tests
cd backend
uv run pytest tests_integration/ -v
```

## Default Login Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `cantonese`

### Student/Teacher Accounts
- Register new accounts through the registration page
- Minimum password length: 3 characters

## API Documentation

The backend API follows OpenAPI 3.0 specification. When the backend is running:

- **Swagger UI**: `http://localhost:8000/docs` - Interactive API documentation
- **ReDoc**: `http://localhost:8000/redoc` - Alternative API documentation
- **OpenAPI Spec**: `backend/openapi/openapi.yaml` - Machine-readable API specification

### Key API Endpoints

- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration
- `GET /api/decks` - Get all decks
- `POST /api/games/start` - Start a game session
- `POST /api/games/pronunciation` - Submit pronunciation attempt
- `POST /api/games/{sessionId}/end` - End game session
- `GET /api/statistics` - Get user statistics
- `GET /api/words/error-ratios` - Get word error ratios

See `backend/openapi/openapi.yaml` for complete API documentation.

## Database

### Database Support

The application supports both SQLite (development) and PostgreSQL (production):

- **SQLite**: Default for development, stored in `backend/cantonese_game.db`
- **PostgreSQL**: Configure via `DATABASE_URL` environment variable

### Database Schema

Key tables:
- `users` - User accounts (students, teachers, admins)
- `decks` - Word decks for practice
- `words` - Individual words with Jyutping
- `game_sessions` - Game session records
- `game_attempts` - Individual pronunciation attempts
- `student_teacher_associations` - Student-teacher relationships
- `user_streaks` - Daily streak tracking

### Migrations

Database migrations are managed with Alembic:

```bash
cd backend

# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## Implementation Status

### ✅ Completed Features

- [x] Frontend with React + TypeScript
- [x] Backend API with FastAPI
- [x] JWT authentication system
- [x] User registration and login
- [x] Role-based access control (Student, Teacher, Admin)
- [x] Deck management
- [x] Word management with automatic Jyutping generation
- [x] Game session management
- [x] Pronunciation recording and submission
- [x] Speech recognition integration (Web Speech API + Backend ASR)
- [x] Statistics and analytics
- [x] Student-teacher associations
- [x] Database integration (SQLite/PostgreSQL)
- [x] Database migrations with Alembic
- [x] OpenAPI specification
- [x] Frontend tests
- [x] Backend tests
- [x] Integration tests
- [x] Bilingual interface (English/Traditional Chinese)
- [x] Real-time feedback and visualization

### 🔄 In Progress / Future Enhancements

- [x] Docker containerization
- [x] CI/CD pipeline (GitHub Actions)
- [x] Cloud deployment (AWS ECS Fargate)
- [ ] Enhanced ASR accuracy improvements
- [ ] Additional statistics visualizations
- [ ] Mobile app version

## Project Structure

```
cantonese-word-game/
├── src/                    # Frontend source code
│   ├── components/         # React components
│   ├── contexts/           # React contexts
│   ├── pages/              # Page components
│   ├── services/           # API services
│   └── types/              # TypeScript types
├── backend/                # Backend source code
│   ├── app/                # Application code
│   ├── alembic/            # Database migrations
│   ├── tests/              # Unit tests
│   ├── tests_integration/  # Integration tests
│   └── openapi/            # API specification
├── dist/                   # Frontend build output
├── package.json            # Frontend dependencies
└── README.md               # This file
```

## Troubleshooting

### Common Issues

1. **Backend not connecting**: Ensure backend is running on port 8000
2. **Database errors**: Run migrations with `uv run alembic upgrade head`
3. **CORS errors**: Check that backend CORS is configured for frontend origin
4. **Speech recognition not working**: Ensure browser supports Web Speech API and microphone permissions are granted

See `TROUBLESHOOTING.md` for more detailed troubleshooting information.

## Docker Deployment

### Local Development with Docker Compose

The project includes Docker Compose configuration for local development:

```bash
# Start all services (frontend, backend, PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

Services will be available at:
- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432

### Building Docker Images

```bash
# Build frontend image
docker build -t cantonese-word-game-frontend .

# Build backend image
docker build -t cantonese-word-game-backend -f backend/Dockerfile backend/
```

## AWS Deployment

The application is configured for deployment to AWS using ECS Fargate, RDS PostgreSQL, and Application Load Balancer.

### Architecture

The deployment uses:
- **ECS Fargate**: Serverless container hosting for frontend and backend
- **RDS PostgreSQL**: Managed database service
- **Application Load Balancer**: Traffic distribution and health checks
- **ECR**: Container image registry
- **CloudWatch**: Monitoring and logging
- **Secrets Manager**: Secure secret storage

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured: `aws configure`
3. **AWS CDK CLI** installed: `npm install -g aws-cdk`
4. **Docker** installed and running
5. **Python 3.11+** for CDK infrastructure code

### Initial AWS Setup

1. **Bootstrap CDK** (first time only):
```bash
cd infrastructure/cdk
cdk bootstrap
```

2. **Install CDK dependencies**:
```bash
pip install -r requirements.txt
```

3. **Deploy infrastructure**:
```bash
# Deploy all infrastructure
cdk deploy

# Or use the setup script
cd ../..
./scripts/setup-aws.sh
```

This creates:
- VPC with public and private subnets
- RDS PostgreSQL instance
- ECS Fargate cluster
- ECS services for frontend and backend
- Application Load Balancer
- ECR repositories
- Security groups and IAM roles
- CloudWatch log groups and dashboard
- Secrets Manager secret

### Configure Secrets

After infrastructure deployment, update the Secrets Manager secret with:

```bash
aws secretsmanager put-secret-value \
  --secret-id cantonese-word-game-secrets \
  --secret-string '{
    "SECRET_KEY": "your-generated-secret-key",
    "DATABASE_URL": "postgresql://username:password@rds-endpoint:5432/cantonese_game",
    "CORS_ORIGINS": "[\"https://your-domain.com\"]"
  }'
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Deploy Application

#### Option 1: Manual Deployment

```bash
# Build and push images, then update ECS services
./DEPLOY_NOW.sh
```

#### Option 2: GitHub Actions CI/CD

1. **Configure GitHub Secrets**:
   - `AWS_ACCESS_KEY_ID`: AWS access key
   - `AWS_SECRET_ACCESS_KEY`: AWS secret key
   - `AWS_ACCOUNT_ID`: Your AWS account ID

2. **Push to main branch**:
   - The CI/CD pipeline will automatically:
     - Run tests
     - Build Docker images
     - Push to ECR
     - Deploy to ECS

### Accessing the Application

After deployment, get the Load Balancer DNS:

```bash
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[?LoadBalancerName==`cantonese-word-game-alb`].DNSName' \
  --output text
```

**Current Production URLs:**
- **Frontend:** `http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com`
- **Backend API:** `http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com:8000/api`
- **API Documentation:** `http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com:8000/docs`

### Monitoring

Access the CloudWatch Dashboard:
- Dashboard name: `CantoneseWordGame-Dashboard`
- View in AWS Console: CloudWatch → Dashboards

The dashboard includes:
- ECS service CPU and memory utilization
- RDS CPU and connections
- ALB request count and response time
- Target health status

### Scaling

Update ECS service desired count:

```bash
aws ecs update-service \
  --cluster cantonese-word-game-cluster \
  --service cantonese-word-game-backend-service \
  --desired-count 3
```

Or configure auto-scaling in the CDK stack.

### Cleanup

To destroy all AWS resources:

```bash
cd infrastructure/cdk
cdk destroy
```

**Warning**: This will delete all resources including the database. Ensure you have backups!

## CI/CD Pipeline

The project includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that:

1. **Tests**: Runs frontend and backend tests
2. **Builds**: Creates Docker images (backend optimized at 529MB)
3. **Pushes**: Uploads images to ECR
4. **Deploys**: Updates ECS services

The pipeline triggers on:
- Push to `main` branch (full deployment)
- Pull requests (tests only)

**Required GitHub Secrets:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`  
- `AWS_ACCOUNT_ID`

**Production Optimization:** Backend image excludes ML dependencies (torch, transformers) to reduce size from 8.6GB to 529MB. Speech recognition gracefully falls back to mock mode.

## Contributing

This is a capstone project for the AI Development Tools Zoomcamp. For questions or issues, please refer to the project documentation files:

- `IMPLEMENTATION.md` - Frontend and backend implementation details and technical specifications
- `DEPLOYMENT.md` - Dockerization, CI/CD pipeline, and cloud deployment details
- `project_requirements.md` - Complete project requirements
- `ASR_FIX.md` - Speech recognition fixes and improvements

## License

This project is created for educational purposes as part of the AI Development Tools Zoomcamp Capstone Project.

## Acknowledgments

- Built for primary school students in Hong Kong with Dyslexia
- Designed to support Cantonese language learning
- Uses modern web technologies for accessibility and engagement
