# 🚀 DEPLOYMENT GUIDE - SURESH AI ORIGIN V2.0

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Production Deployment](#kubernetes-production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Migrations](#database-migrations)
7. [Monitoring & Health Checks](#monitoring--health-checks)
8. [Scaling & Performance](#scaling--performance)
9. [Security Hardening](#security-hardening)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows 10+
- **Python**: 3.11 or higher
- **Memory**: 2GB RAM (4GB+ recommended)
- **Storage**: 10GB free space
- **Network**: Internet connection for package installation

### Optional (For Production)
- **Docker**: 20.10+ with Docker Compose
- **Kubernetes**: 1.24+ (for production scaling)
- **Redis**: 7.0+ (for caching)
- **PostgreSQL**: 14+ (optional, SQLite used by default)

---

## Local Development Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/suresh-ai-origin.git
cd suresh-ai-origin
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit with your credentials
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Required variables in .env:**
```bash
FLASK_SECRET_KEY=your-secret-key-here-use-strong-random-string
RAZORPAY_KEY_ID=rzp_test_your_key
RAZORPAY_KEY_SECRET=your_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-gmail-app-password
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
```

### Step 5: Initialize Database
```bash
# Windows PowerShell
$env:PYTHONPATH = "."
alembic upgrade head

# Linux/Mac
PYTHONPATH=. alembic upgrade head
```

### Step 6: Run Development Server
```bash
python app.py
```

Visit: **http://localhost:5000**

---

## Docker Deployment

### Single Container (Quick Start)
```bash
# Build image
docker build -t suresh-ai-origin:latest .

# Run container
docker run -d \
  -p 5000:5000 \
  -e FLASK_SECRET_KEY="your-secret" \
  -e RAZORPAY_KEY_ID="your-key" \
  -e RAZORPAY_KEY_SECRET="your-secret" \
  -e EMAIL_USER="your-email@gmail.com" \
  -e EMAIL_PASS="your-password" \
  -v $(pwd)/data:/app/data \
  --name suresh-ai \
  suresh-ai-origin:latest

# Check logs
docker logs -f suresh-ai

# Health check
curl http://localhost:5000/health
```

### Docker Compose (Recommended)
```bash
# Start all services (app + redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Scale application
docker-compose up -d --scale app=3

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View running containers
docker-compose ps
```

### Docker Compose Commands
```bash
# Build images
docker-compose build

# Pull latest images
docker-compose pull

# Remove all containers and volumes
docker-compose down -v

# Execute command in container
docker-compose exec app python scripts/seed_demo.py seed

# View resource usage
docker stats
```

---

## Kubernetes Production Deployment

### Prerequisites
- Kubernetes cluster (1.24+)
- kubectl configured
- Helm (optional, recommended)

### Step 1: Create Namespace
```bash
kubectl create namespace suresh-ai-origin
```

### Step 2: Configure Secrets
Edit `kubernetes.yaml` and replace placeholders:
```yaml
stringData:
  FLASK_SECRET_KEY: "your-actual-secret-key"
  RAZORPAY_KEY_ID: "rzp_live_your_key"
  RAZORPAY_KEY_SECRET: "your_actual_secret"
  # ... other secrets
```

**⚠️ Security Warning**: Never commit secrets to Git!

### Step 3: Apply Configurations
```bash
# Apply all manifests
kubectl apply -f kubernetes.yaml

# Check deployment status
kubectl get all -n suresh-ai-origin

# Wait for rollout
kubectl rollout status deployment/suresh-app -n suresh-ai-origin
```

### Step 4: Get External IP
```bash
# Get service external IP
kubectl get service suresh-app-service -n suresh-ai-origin

# Watch for IP assignment
kubectl get service suresh-app-service -n suresh-ai-origin --watch
```

### Step 5: Configure DNS
Point your domain to the external IP:
```
A     your-domain.com     →  EXTERNAL-IP
```

### Kubernetes Management Commands

#### View Resources
```bash
# All resources in namespace
kubectl get all -n suresh-ai-origin

# Pods with details
kubectl get pods -n suresh-ai-origin -o wide

# Services
kubectl get services -n suresh-ai-origin

# Deployments
kubectl get deployments -n suresh-ai-origin

# ConfigMaps and Secrets
kubectl get configmaps,secrets -n suresh-ai-origin
```

#### Logs & Debugging
```bash
# View logs
kubectl logs -f deployment/suresh-app -n suresh-ai-origin

# Logs from specific pod
kubectl logs -f <pod-name> -n suresh-ai-origin

# Describe pod (for troubleshooting)
kubectl describe pod <pod-name> -n suresh-ai-origin

# Execute command in pod
kubectl exec -it <pod-name> -n suresh-ai-origin -- /bin/bash
```

#### Scaling
```bash
# Manual scaling
kubectl scale deployment suresh-app --replicas=5 -n suresh-ai-origin

# Check HPA status (auto-scaling)
kubectl get hpa -n suresh-ai-origin

# Describe HPA
kubectl describe hpa suresh-app-hpa -n suresh-ai-origin
```

#### Updates & Rollbacks
```bash
# Update image
kubectl set image deployment/suresh-app app=suresh-ai-origin:v2.1 -n suresh-ai-origin

# Check rollout status
kubectl rollout status deployment/suresh-app -n suresh-ai-origin

# View rollout history
kubectl rollout history deployment/suresh-app -n suresh-ai-origin

# Rollback to previous version
kubectl rollout undo deployment/suresh-app -n suresh-ai-origin

# Rollback to specific revision
kubectl rollout undo deployment/suresh-app --to-revision=2 -n suresh-ai-origin
```

#### Resource Monitoring
```bash
# Pod resource usage
kubectl top pods -n suresh-ai-origin

# Node resource usage
kubectl top nodes

# Continuous monitoring
watch kubectl top pods -n suresh-ai-origin
```

#### Cleanup
```bash
# Delete specific resources
kubectl delete deployment suresh-app -n suresh-ai-origin
kubectl delete service suresh-app-service -n suresh-ai-origin

# Delete entire namespace (⚠️ CAUTION)
kubectl delete namespace suresh-ai-origin
```

---

## Environment Configuration

### Production Environment Variables

#### Essential
```bash
# Flask
FLASK_SECRET_KEY=<strong-random-64-char-string>
FLASK_DEBUG=false

# Database
DATA_DB=/app/data/data.db

# Payment Gateways
RAZORPAY_KEY_ID=rzp_live_your_key
RAZORPAY_KEY_SECRET=your_live_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
STRIPE_SECRET_KEY=sk_live_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email
EMAIL_USER=noreply@your-domain.com
EMAIL_PASS=your-app-password

# Redis (Caching)
REDIS_URL=redis://redis:6379/0
```

#### Security
```bash
# Admin Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password-min-12-chars>
ADMIN_SESSION_TIMEOUT=3600

# Session Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

#### Feature Flags
```bash
FLAG_FINANCE_ENTITLEMENTS_ENFORCED=true
FLAG_INTEL_RECOMMENDATIONS_ENABLED=true
FLAG_GROWTH_NUDGES_ENABLED=true
```

### Generating Secure Secrets

#### Flask Secret Key (Python)
```python
import secrets
print(secrets.token_urlsafe(64))
```

#### Flask Secret Key (PowerShell)
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

#### Flask Secret Key (Bash)
```bash
openssl rand -hex 32
```

---

## Database Migrations

### Creating Migrations
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new feature table"

# Create empty migration
alembic revision -m "Custom migration"
```

### Applying Migrations
```bash
# Apply all pending migrations
PYTHONPATH=. alembic upgrade head

# Apply specific migration
PYTHONPATH=. alembic upgrade <revision_id>

# View current version
PYTHONPATH=. alembic current

# View migration history
PYTHONPATH=. alembic history
```

### Rollback Migrations
```bash
# Rollback one migration
PYTHONPATH=. alembic downgrade -1

# Rollback to specific version
PYTHONPATH=. alembic downgrade <revision_id>

# Rollback all (⚠️ CAUTION)
PYTHONPATH=. alembic downgrade base
```

---

## Monitoring & Health Checks

### Health Check Endpoint
```bash
# Check system health
curl http://localhost:5000/health

# Expected response (healthy)
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": 1705055555.123
}
```

### System Metrics
```bash
# Get real-time system metrics
curl http://localhost:5000/api/health/metrics

# Get system health summary
curl http://localhost:5000/api/health/system

# Get anomaly detection report
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:5000/api/health/anomalies

# Get predictive alerts
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:5000/api/health/predictive-alerts
```

### Monitoring with External Tools

#### Prometheus (Metrics Collection)
Add to your prometheus.yml:
```yaml
scrape_configs:
  - job_name: 'suresh-ai-origin'
    static_configs:
      - targets: ['suresh-app-service:5000']
    metrics_path: '/api/health/metrics'
```

#### Grafana (Dashboards)
Import dashboard for visualizing metrics

#### Sentry (Error Tracking)
```python
# Add to app.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## Scaling & Performance

### Horizontal Scaling

#### Docker Compose
```bash
# Scale to 5 instances
docker-compose up -d --scale app=5

# Scale down to 2
docker-compose up -d --scale app=2
```

#### Kubernetes
```bash
# Manual scaling
kubectl scale deployment suresh-app --replicas=10 -n suresh-ai-origin

# Auto-scaling is configured via HPA:
# - Min replicas: 3
# - Max replicas: 10
# - CPU target: 70%
# - Memory target: 80%
```

### Performance Optimization

#### Enable Redis Caching
```bash
# Set Redis URL
export REDIS_URL=redis://localhost:6379/0

# Warm cache
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:5000/api/cache/warm
```

#### Database Optimization
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_orders_receipt ON orders(receipt);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_customers_segment ON customers(segment);
```

#### Gunicorn Configuration
Edit Dockerfile or docker-compose.yml:
```yaml
command: gunicorn --bind 0.0.0.0:5000 \
  --workers 4 \
  --threads 2 \
  --worker-class gthread \
  --timeout 120 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  app:app
```

---

## Security Hardening

### 1. HTTPS/TLS Setup

#### Using Let's Encrypt (Nginx)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 2. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 3. Rate Limiting (Nginx)
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api burst=20 nodelay;
    }
}
```

### 4. Security Headers (Already in app)
- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security

### 5. Database Security
```bash
# Backup encryption
gpg --encrypt --recipient admin@your-domain.com data.db

# Restrict file permissions
chmod 600 data.db
chmod 700 data/
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Windows: Find and kill process
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Linux/Mac
lsof -i :5000
kill -9 <process_id>
```

#### 2. Database Locked
```bash
# Close all connections
# Restart application
# If persistent, delete lock file
rm data.db-journal
```

#### 3. Redis Connection Failed
```bash
# Check Redis is running
redis-cli ping

# Start Redis
redis-server

# Check connection
telnet localhost 6379
```

#### 4. Module Import Errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=.

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

#### 5. Permission Denied
```bash
# Fix file permissions
chmod +x scripts/*.py
chmod 755 app.py

# Docker permission issues
sudo usermod -aG docker $USER
```

### Debug Mode

#### Enable Flask Debug Mode
```bash
export FLASK_DEBUG=true
python app.py
```

#### Enable Verbose Logging
```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help
- 📧 Email: support@suresh-ai-origin.com
- 💬 Discord: [Join community](https://discord.gg/suresh-ai)
- 📖 Docs: [Full documentation](https://docs.suresh-ai-origin.com)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/suresh-ai-origin/issues)

---

## Next Steps

After successful deployment:

1. ✅ Configure domain and SSL
2. ✅ Set up monitoring (Prometheus/Grafana)
3. ✅ Configure backup strategy
4. ✅ Set up CI/CD pipeline
5. ✅ Enable auto-scaling
6. ✅ Performance tuning
7. ✅ Security audit

---

**Deployment Complete! 🎉**

Your SURESH AI ORIGIN platform is now live and ready to serve customers at scale.

For production best practices and advanced configurations, see [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)
