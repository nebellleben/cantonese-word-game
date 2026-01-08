# ⚠️ URGENT: Disk Space Issue

## Problem
Your disk is **100% full** (only 101MB free out of 460GB). This is preventing Docker builds from completing.

## Immediate Actions Required

### 1. Free Up Disk Space

**Quick wins:**
```bash
# Check what's using space
du -sh ~/Library/Caches/* 2>/dev/null | sort -hr | head -10
du -sh ~/Downloads/* 2>/dev/null | sort -hr | head -10

# Clean common caches
rm -rf ~/Library/Caches/pip
rm -rf ~/Library/Caches/npm
rm -rf ~/Library/Caches/yarn
rm -rf ~/.cache/pip
rm -rf ~/.npm
rm -rf ~/.yarn

# Clean Docker (if it works)
docker system prune -a --volumes -f

# Clean Xcode derived data (if you have Xcode)
rm -rf ~/Library/Developer/Xcode/DerivedData

# Clean Homebrew cache
brew cleanup --prune=all
```

**Check large files:**
```bash
# Find large files
find ~ -type f -size +1G -exec ls -lh {} \; 2>/dev/null | head -20

# Find large directories
du -h ~ | sort -rh | head -20
```

### 2. After Freeing Space

Once you have at least 10-20GB free:

1. **Build backend image:**
   ```bash
   cd /Users/kelvinchan/dev/test/cantonese-word-game
   docker build -t 808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-backend:302f9b1 \
     -t 808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-backend:latest \
     -f backend/Dockerfile backend/
   ```

2. **Push to ECR:**
   ```bash
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin 808055627316.dkr.ecr.us-east-1.amazonaws.com
   
   docker push 808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-backend:302f9b1
   docker push 808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-backend:latest
   ```

3. **Deploy infrastructure** (if not done):
   ```bash
   cd infrastructure/cdk
   pip install -r requirements.txt
   cdk bootstrap  # First time only
   cdk deploy
   ```

4. **Update ECS services:**
   ```bash
   ./DEPLOY_NOW.sh
   ```

## Current Status

✅ **Completed:**
- Frontend image built and pushed to ECR
- ECR repositories created
- All deployment scripts ready

⏳ **Blocked by disk space:**
- Backend image build
- Infrastructure deployment (if needed)

## Alternative: Build on AWS

If you can't free up space locally, you can use AWS CodeBuild or build directly on an EC2 instance:

1. **Use AWS CodeBuild:**
   - Create a build project in AWS Console
   - Point to your GitHub repo
   - Build and push images automatically

2. **Use EC2 instance:**
   - Launch a t3.medium instance
   - Install Docker
   - Clone repo and build there

## Recommended: Free at least 20GB

The backend build (especially with PyTorch) needs significant space. Aim for at least 20GB free before attempting the build.

