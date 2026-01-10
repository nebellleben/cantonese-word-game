## Deployment Guide

This document collects all information related to Docker containerization, CI/CD, and cloud deployment for the Cantonese Word Game.

For project overview, see `README.md`. For implementation details, see `IMPLEMENTATION.md`. For a short local-run guide, see `QUICK_START.md`.

---

## 🎉 Current Production Deployment

**Status:** ✅ **LIVE AND OPERATIONAL**

**Access URLs:**
- **Frontend Application:** http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com
- **Backend API:** http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com:8000/api
- **API Documentation:** http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com:8000/docs

**Deployment Details:**
- **Region:** us-east-1
- **Stack Name:** CantoneseWordGameStack
- **Status:** CREATE_COMPLETE
- **Frontend Tasks:** 1/1 Running
- **Backend Tasks:** 1/1 Running
- **Database:** RDS PostgreSQL (db.t3.micro)
- **Backend Image Size:** 529MB (optimized, ML dependencies optional)

---

## 1. Docker Containerization

### 1.1 Images & Dockerfiles

- **Frontend**
  - `Dockerfile` in the project root.
  - Multi-stage build:
    - Build stage: Node 18, `npm install`, `npm run build`.
    - Runtime stage: `nginx:alpine` serving static assets from `/usr/share/nginx/html`.
  - Health check: `GET /health` endpoint served by nginx.

- **Backend**
  - `backend/Dockerfile`.
  - Multi-stage build using `python:3.11-slim` and `uv`:
    - Builder stage:
      - Copies `pyproject.toml` and `uv.lock`.
      - Installs dependencies via `uv sync` (with lockfile).
    - Runtime stage:
      - Copies `.venv` and app code.
      - Runs Alembic migrations then starts Uvicorn:
        - `uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`.
  - Health check: `GET /health` on the FastAPI app.

### 1.2 Docker Compose (Local)

`docker-compose.yml` orchestrates:

- `postgres` (PostgreSQL 15):
  - User: `cantonese_user`
  - Password: `cantonese_pass`
  - DB: `cantonese_game`
  - Exposed on `5432`.
- `backend`:
  - Built from `backend/Dockerfile`.
  - `DATABASE_URL` points to the `postgres` service.
  - Exposed on `8000`.
  - **Note:** ML dependencies (torch, transformers) are optional. For production deployment, these are excluded to reduce image size from 8.6GB to 529MB. Speech recognition will use mock mode.
- `frontend`:
  - Built from root `Dockerfile`.
  - `VITE_API_BASE_URL` points at `http://backend:8000/api`.
  - Exposed on `80`.

Typical local workflow:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### 1.3 Building Images Manually

```bash
# From project root

# Frontend
docker build -t cantonese-word-game-frontend .

# Backend (for AWS Fargate - must use linux/amd64 platform)
docker build --platform linux/amd64 -t cantonese-word-game-backend -f backend/Dockerfile backend/

# Backend with ML dependencies (local development)
# Note: This creates a much larger image (~8.6GB vs 529MB)
# Edit backend/pyproject.toml to move torch/transformers back to main dependencies
```

**Important Notes:**
- Production backend image excludes ML dependencies to optimize size and deployment speed
- Speech recognition engine gracefully falls back to mock mode when ML libraries are unavailable
- For AWS Fargate deployment, always use `--platform linux/amd64` flag

---

## 2. CI/CD (GitHub Actions)

The CI/CD pipeline is defined in `.github/workflows/deploy.yml` and runs on pushes to `main` and on pull requests.

### 2.1 Stages

1. **Test**
   - Frontend:
     - Install dependencies: `npm ci`.
     - Run tests: `npm test`.
   - Backend:
     - Install with `uv sync` in `backend/`.
     - Run unit tests: `uv run pytest`.
     - Run integration tests: `uv run pytest tests_integration/ -v`.

2. **Build & Push Docker Images** (on `main` only)
   - Logs into Amazon ECR.
   - Builds and tags:
     - `cantonese-word-game-frontend`
     - `cantonese-word-game-backend`
   - Tags:
     - Commit SHA (e.g. `302f9b1`)
     - `latest`
   - Pushes images to ECR.

3. **Deploy to ECS** (on `main` only)
   - Forces new deployments on:
     - `cantonese-word-game-frontend-service`
     - `cantonese-word-game-backend-service`
   - Waits for services to become stable.

### 2.2 Required GitHub Secrets

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ACCOUNT_ID`

These are used by the workflow to authenticate to AWS and ECR.

---

## 3. AWS Cloud Deployment

Deployment is managed via:

- **ECS Fargate** – frontend and backend services.
- **RDS PostgreSQL** – production database.
- **Application Load Balancer (ALB)** – ingress for frontend and backend.
- **ECR** – container registry.
- **CloudWatch** – logs and dashboards.
- **Secrets Manager** – secure storage for secrets and connection strings.
- **CDK (AWS Cloud Development Kit)** – infrastructure as code under `infrastructure/cdk`.

### 3.1 CDK Stack

Main files:

- `infrastructure/cdk/app.py` – CDK app entrypoint.
- `infrastructure/cdk/cantonese_word_game_stack.py` – defines:
  - VPC, subnets, NAT gateway.
  - RDS PostgreSQL instance (with free-tier-compatible backup retention).
  - ECR repositories (referenced via `from_repository_name`).
  - ECS cluster, task definitions, and services.
  - ALB, target groups, and listeners.
  - Security groups and IAM roles.
  - CloudWatch logs and dashboard.
  - Secrets Manager secret (`cantonese-word-game-secrets`).

### 3.2 Prerequisites

On your machine:

- AWS account and credentials (`aws configure`).
- Docker.
- Node.js (for CDK CLI).
- Python 3.11+ for CDK Python code.

Install CDK CLI:

```bash
npm install -g aws-cdk
```

Set up CDK environment:

```bash
cd infrastructure/cdk
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3.3 Initial Infrastructure Deploy

You can either use the helper script or run CDK commands directly.

**Using the helper script:**

```bash
./scripts/setup-aws.sh
```

This will:

- Bootstrap CDK.
- Deploy the `CantoneseWordGameStack`.
- Print ECR repository URIs, ALB DNS, and RDS endpoint.

**Manual CDK commands (equivalent):**

```bash
cd infrastructure/cdk
cdk bootstrap aws://<ACCOUNT_ID>/us-east-1
cdk deploy
```

---

## 4. Building & Deploying Application Images

### 4.1 Scripted Deployment (Recommended)

Use `DEPLOY_NOW.sh` to build and deploy:

```bash
./DEPLOY_NOW.sh
```

This script:

1. Checks Docker and AWS credentials.
2. Logs into ECR.
3. Builds frontend and backend images.
4. Pushes both tags (commit SHA + `latest`) to ECR.
5. Checks if infrastructure exists (prompts if not).
6. Forces new deployments for the ECS frontend and backend services.
7. Waits for services to stabilize.
8. Prints the ALB DNS and links to CloudWatch resources.

### 4.2 Manual Commands (If Needed)

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build and push frontend
docker build -t <REGISTRY>/cantonese-word-game-frontend:<TAG> -t <REGISTRY>/cantonese-word-game-frontend:latest .
docker push <REGISTRY>/cantonese-word-game-frontend:<TAG>
docker push <REGISTRY>/cantonese-word-game-frontend:latest

# Build and push backend
docker build -t <REGISTRY>/cantonese-word-game-backend:<TAG> -t <REGISTRY>/cantonese-word-game-backend:latest -f backend/Dockerfile backend/
docker push <REGISTRY>/cantonese-word-game-backend:<TAG>
docker push <REGISTRY>/cantonese-word-game-backend:latest

# Force new deployments
aws ecs update-service \
  --cluster cantonese-word-game-cluster \
  --service cantonese-word-game-frontend-service \
  --force-new-deployment --region us-east-1

aws ecs update-service \
  --cluster cantonese-word-game-cluster \
  --service cantonese-word-game-backend-service \
  --force-new-deployment --region us-east-1
```

---

## 5. Secrets & Configuration

Secrets are stored in **AWS Secrets Manager** under `cantonese-word-game-secrets`, and consumed by the backend via environment variables (and optionally via the AWS SDK in `config.py`).

Example payload:

```json
{
  "SECRET_KEY": "your-generated-secret-key",
  "DATABASE_URL": "postgresql://username:password@rds-endpoint:5432/cantonese_game",
  "CORS_ORIGINS": "[\"https://your-frontend-domain.com\"]"
}
```

Generate a secure `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 6. Monitoring & Observability

### 6.1 CloudWatch Logs

Log groups:

- `/ecs/cantonese-word-game-frontend`
- `/ecs/cantonese-word-game-backend`

Container logs from ECS tasks are sent here.

### 6.2 CloudWatch Dashboard & Alarms

The CDK stack creates a dashboard (e.g. `CantoneseWordGame-Dashboard`) with:

- ECS CPU and memory utilization (frontend and backend services).
- RDS CPU utilization and connection counts.
- ALB request count and target response time.

Alarms:

- High CPU/memory for ECS services.
- RDS CPU or connection count thresholds.
- ALB target health alarms for frontend and backend target groups.

---

## 7. Accessing the Deployed Application

Get the ALB DNS:

```bash
aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[?LoadBalancerName==`cantonese-word-game-alb`].DNSName' \
  --output text
```

Then:

- **Frontend**: `http://<alb-dns>`
- **Backend API**: `http://<alb-dns>:8000/api`
- **API Docs**: `http://<alb-dns>:8000/docs`

---

## 8. Troubleshooting (Selected Topics)

- **Build failures due to missing `terser`**:
  - Vite is configured to use the default `esbuild` minifier instead of `terser`, so no extra action is needed.
  
- **Disk space errors during Docker builds**:
  - Ensure you have at least ~20GB free, especially for backend builds with PyTorch.
  - Clean Docker artifacts with `docker system prune -a --volumes -f` and clear local caches if needed.
  - For production, ML dependencies are optional - see backend/pyproject.toml
  
- **ECS tasks not starting / staying at 0 running**:
  - Check logs in the CloudWatch log groups: `/ecs/cantonese-word-game-backend` and `/ecs/cantonese-word-game-frontend`
  - Verify that Secrets Manager `DATABASE_URL` is correct and contains the "uri" key
  - Confirm that the RDS secret has been updated with: `python -c "import json; secret = json.load(open('secret.json')); secret['uri'] = f\"postgresql://{secret['username']}:{secret['password']}@{secret['host']}:{secret['port']}/{secret['dbname']}\"; print(json.dumps(secret))"`
  - Ensure the RDS instance is reachable from the ECS tasks' security group
  - Confirm that migrations run successfully on container startup
  - Check if using correct platform: `docker build --platform linux/amd64` for Fargate

- **Platform mismatch errors (ARM64 vs AMD64)**:
  - Fargate requires linux/amd64 images
  - On Apple Silicon Macs, always use: `docker build --platform linux/amd64 ...`
  - Error message: "image Manifest does not contain descriptor matching platform 'linux/amd64'"
  
- **Backend container exits with "ModuleNotFoundError: No module named 'torch'"**:
  - This means the image was built with ML dependencies but they're now optional
  - The speech_recognition_engine.py has been updated to handle missing ML dependencies gracefully
  - Rebuild the image to pick up the updated imports
  
- **RDS secret missing "uri" key**:
  - The CDK-generated RDS secret contains individual fields (host, port, username, password, dbname) but not "uri"
  - After stack deployment, add the uri key:
    ```bash
    aws secretsmanager get-secret-value --secret-id <SECRET_ARN> --query 'SecretString' --output text > secret.json
    python3 -c "import json; s=json.load(open('secret.json')); s['uri']=f\"postgresql://{s['username']}:{s['password']}@{s['host']}:{s['port']}/{s['dbname']}\"; json.dump(s, open('secret_updated.json', 'w'))"
    aws secretsmanager put-secret-value --secret-id <SECRET_ARN> --secret-string file://secret_updated.json
    ```


