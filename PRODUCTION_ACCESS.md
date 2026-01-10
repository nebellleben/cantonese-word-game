# Production Access Information

**Last Updated:** January 10, 2026

## 🌐 Live Application URLs

### Frontend Application
```
http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com
```
- Main web interface for students, teachers, and administrators
- Bilingual interface (English/Traditional Chinese)
- Interactive word pronunciation game

### Backend API
```
http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com:8000/api
```
- RESTful API endpoints
- JWT authentication
- Real-time game session management

### API Documentation (Swagger UI)
```
http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com:8000/docs
```
- Interactive API documentation
- Test endpoints directly from the browser
- View request/response schemas

---

## 📊 Deployment Status

| Component | Status | Tasks | Health |
|-----------|--------|-------|--------|
| CloudFormation Stack | ✅ CREATE_COMPLETE | - | Active |
| Frontend Service | ✅ ACTIVE | 1/1 | Healthy |
| Backend Service | ✅ ACTIVE | 1/1 | Healthy |
| RDS PostgreSQL | ✅ RUNNING | - | Available |
| Application Load Balancer | ✅ ACTIVE | - | Active |

**Region:** us-east-1 (US East N. Virginia)

**Stack Name:** CantoneseWordGameStack

---

## 🔍 Health Check Endpoints

### Frontend Health
```bash
curl http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com/health
# Expected: HTTP 200 "healthy"
```

### Backend Health
```bash
curl http://cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com:8000/health
# Expected: HTTP 200 {"status":"healthy"}
```

---

## 📈 Monitoring & Logs

### CloudWatch Log Groups
- **Frontend Logs:** `/ecs/cantonese-word-game-frontend`
- **Backend Logs:** `/ecs/cantonese-word-game-backend`

### CloudWatch Dashboard
```
CantoneseWordGame-Dashboard
```

### View Logs (AWS CLI)
```bash
# Backend logs (last 5 minutes)
aws logs tail /ecs/cantonese-word-game-backend --region us-east-1 --since 5m --follow

# Frontend logs (last 5 minutes)
aws logs tail /ecs/cantonese-word-game-frontend --region us-east-1 --since 5m --follow
```

---

## 🔧 Infrastructure Details

### ECS Cluster
- **Name:** cantonese-word-game-cluster
- **Type:** Fargate
- **Services:** 2 (frontend + backend)

### Services Configuration
**Backend:**
- Image: `808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-backend:latest`
- Size: 529MB (optimized, ML dependencies optional)
- Platform: linux/amd64
- CPU: 512 (0.5 vCPU)
- Memory: 1024MB
- Ephemeral Storage: 30GB

**Frontend:**
- Image: `808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-frontend:latest`
- Platform: linux/amd64
- CPU: 256 (0.25 vCPU)
- Memory: 512MB

### Database
- **Engine:** PostgreSQL 15
- **Instance:** db.t3.micro
- **Storage:** 20GB (auto-scaling up to 100GB)
- **Backup Retention:** 1 day
- **Multi-AZ:** No (for cost optimization)

### Load Balancer
- **Type:** Application Load Balancer
- **Scheme:** internet-facing
- **DNS:** cantonese-word-game-alb-1303843855.us-east-1.elb.amazonaws.com
- **Listeners:**
  - Port 80 → Frontend Target Group
  - Port 8000 → Backend Target Group

---

## 🚀 Deployment Commands

### Check Service Status
```bash
aws ecs describe-services \
  --cluster cantonese-word-game-cluster \
  --services cantonese-word-game-backend-service cantonese-word-game-frontend-service \
  --region us-east-1 \
  --query 'services[*].{Name:serviceName,Running:runningCount,Desired:desiredCount}'
```

### Force New Deployment
```bash
# Backend
aws ecs update-service \
  --cluster cantonese-word-game-cluster \
  --service cantonese-word-game-backend-service \
  --force-new-deployment \
  --region us-east-1

# Frontend
aws ecs update-service \
  --cluster cantonese-word-game-cluster \
  --service cantonese-word-game-frontend-service \
  --force-new-deployment \
  --region us-east-1
```

### View Stack Outputs
```bash
aws cloudformation describe-stacks \
  --stack-name CantoneseWordGameStack \
  --region us-east-1 \
  --query 'Stacks[0].Outputs'
```

---

## 🔐 Secrets Management

### Secrets Manager Secrets
1. **Application Secrets:** `cantonese-word-game-secrets`
   - Contains: SECRET_KEY for JWT tokens

2. **RDS Database Credentials:** `CantoneseWordGameStackPostg-ho5tqD7nznHr`
   - Contains: username, password, host, port, dbname, **uri**
   - **Important:** The "uri" key must be present for backend to connect

### Update Database Secret
```bash
# Get current secret
aws secretsmanager get-secret-value \
  --secret-id CantoneseWordGameStackPostg-ho5tqD7nznHr \
  --region us-east-1 \
  --query 'SecretString' --output text > secret.json

# Add uri key using Python
python3 -c "
import json
s = json.load(open('secret.json'))
s['uri'] = f\"postgresql://{s['username']}:{s['password']}@{s['host']}:{s['port']}/{s['dbname']}\"
json.dump(s, open('secret_updated.json', 'w'))
"

# Update secret
aws secretsmanager put-secret-value \
  --secret-id CantoneseWordGameStackPostg-ho5tqD7nznHr \
  --secret-string file://secret_updated.json \
  --region us-east-1
```

---

## 🎯 Default Credentials

**Admin Account:**
- Email: `admin@example.com`
- Password: `admin123` (change after first login)

**Test Teacher:**
- Email: `teacher@example.com`
- Password: `teacher123`

**Test Student:**
- Email: `student@example.com`
- Password: `student123`

---

## 📝 Notes

### Speech Recognition
- Production deployment uses **mock mode** for speech recognition
- ML dependencies (torch, transformers, librosa) are optional
- This reduces backend image size from 8.6GB to 529MB
- For production ASR, add ML dependencies to `backend/pyproject.toml` and rebuild

### Platform Architecture
- Backend MUST be built with `--platform linux/amd64` for Fargate
- Building on Apple Silicon (ARM64) requires explicit platform flag:
  ```bash
  docker build --platform linux/amd64 -t backend -f backend/Dockerfile backend/
  ```

### Cost Optimization
- Single task per service (can scale up as needed)
- db.t3.micro instance (AWS Free Tier eligible)
- No Multi-AZ deployment
- 1-day backup retention

---

## 📞 Support

For issues or questions:
1. Check CloudWatch Logs for error messages
2. Review `DEPLOYMENT.md` for troubleshooting guide
3. Verify all services are healthy using health check endpoints
4. Check GitHub Actions workflow for CI/CD pipeline status

---

**Generated:** 2026-01-10  
**Deployment Method:** AWS CDK (Infrastructure as Code)  
**Deployment Script:** `DEPLOY_NOW.sh` or `infrastructure/cdk/`
