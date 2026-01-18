# Auto-Deploy System V2.0 - Complete Guide

**SURESH AI ORIGIN** auto-deployment system with GitHub webhooks, Docker, Railway/Vercel/Render APIs, health checks, and Slack/Email notifications.

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Required environment variables
export GITHUB_WEBHOOK_SECRET="your-secret-key"
export RAILWAY_API_TOKEN="your-railway-token"
export VERCEL_TOKEN="your-vercel-token"
export RENDER_API_KEY="your-render-api-key"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
export ADMIN_EMAIL="admin@sureshaiorigin.com"
export DOCKER_REGISTRY="ghcr.io"  # GitHub Container Registry
export DOCKER_IMAGE_NAME="suresh-ai-origin"
```

### 2. Register Deployment Targets

```python
from auto_deploy_system import GlobalAutoDeploySystem, PlatformType

system = GlobalAutoDeploySystem()

# Register Railway production
railway_prod = system.register_deployment_target(
    name="Railway-Production",
    target_type="service",
    platform=PlatformType.RAILWAY,
    endpoint="https://sureshaiorigin-prod.railway.app",
    health_check_url="https://sureshaiorigin-prod.railway.app/health",
    project_id="your-railway-project-id"
)

# Register Render staging
render_staging = system.register_deployment_target(
    name="Render-Staging",
    target_type="service",
    platform=PlatformType.RENDER,
    endpoint="https://sureshaiorigin-staging.onrender.com",
    health_check_url="https://sureshaiorigin-staging.onrender.com/health",
    project_id="your-render-service-id"
)

# Register Vercel
vercel_prod = system.register_deployment_target(
    name="Vercel-Production",
    target_type="service",
    platform=PlatformType.VERCEL,
    endpoint="https://sureshaiorigin.vercel.app",
    health_check_url="https://sureshaiorigin.vercel.app/api/health",
    project_id="your-vercel-project-id"
)
```

### 3. Create Deployment Package

```python
package = system.create_deployment_package(
    version="2.2.0",
    changes=[
        "Fix critical bug in rare features",
        "Add autonomous agent monitoring",
        "Optimize database queries"
    ],
    deployment_script="python scripts/deploy.py",
    rollback_script="python scripts/rollback.py"
)
```

### 4. Trigger Deployment

```python
from auto_deploy_system import DeploymentStrategy

# Auto-deploy with Docker build and rolling strategy
deployment = system.auto_deploy(
    package_id=package.package_id,
    strategy=DeploymentStrategy.ROLLING,
    build_docker=True,
    commit_sha="abc1234"
)

print(f"Deployment ID: {deployment.deployment_id}")
print(f"Status: {deployment.status.value}")
```

---

## 🔗 GitHub Webhook Integration

### Setup in GitHub

1. Go to **GitHub Repository Settings** → **Webhooks**
2. Click **Add webhook**
3. Configure:
   - **Payload URL**: `https://your-deploy-server.com/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: Use `GITHUB_WEBHOOK_SECRET` env var
   - **Events**: Choose "Push events" or "Just the push event"
   - **Active**: ✓ Checked

### How It Works

**GitHub Push to Main Branch** → **Webhook Trigger** → **Auto-Deploy System**

```
git push origin main
    ↓
GitHub sends POST /webhook/github
    ↓
System verifies HMAC-SHA256 signature
    ↓
Creates deployment package with commit SHA
    ↓
Builds Docker image (tag: commit-sha)
    ↓
Pushes to Docker registry
    ↓
Deploys to Railway/Vercel/Render
    ↓
Runs health checks with 3 retries
    ↓
Auto-rolls back on failure
    ↓
Sends Slack/Email notifications
```

---

## 🐳 Docker Build & Registry

### Dockerfile Requirements

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run
EXPOSE 5000
CMD ["python", "app.py"]
```

### Build & Push Manually

```bash
# Build
docker build -t ghcr.io/suresh-ai-origin:v2.2.0 .

# Push
docker push ghcr.io/suresh-ai-origin:v2.2.0

# Also push as latest
docker tag ghcr.io/suresh-ai-origin:v2.2.0 ghcr.io/suresh-ai-origin:latest
docker push ghcr.io/suresh-ai-origin:latest
```

---

## 🚂 Railway Deployment

### API Integration

```python
def _deploy_to_railway(self, target, docker_image, deployment):
    """Deploy to Railway via GraphQL API"""
    
    query = """
    mutation DeployImage($projectId: String!, $image: String!) {
      deploymentCreate(input: {
        projectId: $projectId
        environmentId: "production"
        image: $image
      }) {
        id
        status
      }
    }
    """
    
    # Makes GraphQL call to https://backboard.railway.app/graphql/v2
    # with Bearer token authentication
```

### Setup

1. Get Railway API token: Dashboard → Account → API Tokens
2. Get project ID: Project → Settings → General
3. Set env vars:
   ```bash
   export RAILWAY_API_TOKEN="your-token"
   export RAILWAY_PROJECT_ID="your-project-id"
   ```

---

## ▲ Vercel Deployment

### API Integration

Vercel automatically deploys on GitHub push (via GitHub App integration).

Optionally trigger via API:
```python
def _deploy_to_vercel(self, target, deployment):
    """Trigger re-deployment via Vercel API"""
    
    # POST https://api.vercel.com/v13/deployments
    # with gitSource pointing to main branch
```

### Setup

1. Install Vercel GitHub App: https://github.com/apps/vercel
2. Get token: Vercel Dashboard → Settings → Tokens
3. Set env var:
   ```bash
   export VERCEL_TOKEN="your-token"
   ```

---

## 🎨 Render Deployment

### API Integration

```python
def _deploy_to_render(self, target, deployment):
    """Trigger manual deployment via Render API"""
    
    # POST https://api.render.com/v1/services/{service_id}/deploys
    # triggers immediate re-deployment
```

### Setup

1. Get API key: Render Dashboard → Account → API Keys
2. Get service ID: Service → Settings → Service ID
3. Set env vars:
   ```bash
   export RENDER_API_KEY="your-key"
   export RENDER_SERVICE_ID="your-service-id"
   ```

---

## ✅ Health Checks

### Automatic Health Checks

After deployment, system runs **3 retries with 10s delay**:

```python
def _comprehensive_health_check(self, deployment):
    """Run health checks with retries"""
    
    for attempt in range(3):
        for target in targets:
            resp = requests.get(target.health_check_url, timeout=10)
            if resp.status_code != 200:
                # Retry in 10 seconds
                time.sleep(10)
```

### Endpoint Requirements

Your app must have a `/health` endpoint:

```python
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.2.0"
    }), 200
```

### Auto-Rollback on Failure

If health checks fail after 3 retries:

1. **Previous version preserved** (stored in `target.previous_version`)
2. **Auto-rollback triggered** via platform API
3. **System automatically** restores previous version
4. **Alerts sent** to Slack + Email
5. **Logs saved** with failure reason

---

## 📬 Notifications

### Slack Integration

```python
# Auto-sends notifications for:
# - Deployment started ℹ️
# - Deployment success ✅
# - Deployment failed ❌
# - Rollback triggered 🔄
# - Health check warning ⚠️

# Includes:
# - Color-coded messages (green/red/yellow)
# - Deployment ID
# - Timestamp
# - Target information
```

### Email Integration

Critical alerts (errors, success) sent to `ADMIN_EMAIL`:

```html
Subject: ✅ Deployment Successful - Auto Deploy System

---

<h2>Deployment Successful</h2>
<p>v2.2.0 deployed to 2 targets using rolling strategy</p>

Deployment ID: dpl_42c6299934e0
Timestamp: 2026-01-18T22:40:57.037851

Duration: 26.2 seconds
Success Rate: 100% (2/2 targets)
```

---

## 🔄 Deployment Strategies

### 1. Blue-Green (Zero Downtime)

- Deploy new version ("Blue") alongside current ("Green")
- Test thoroughly
- Switch traffic instantly
- Instant rollback if needed

```python
strategy=DeploymentStrategy.BLUE_GREEN
```

### 2. Canary (Gradual Rollout)

- Deploy to 10% of targets first
- Monitor metrics
- Gradually rollout to remaining 90%
- Rollback if issues detected

```python
strategy=DeploymentStrategy.CANARY
```

### 3. Rolling (Sequential Updates)

- Update one target at a time
- Always maintains uptime
- Slower but safest
- Monitors health between updates

```python
strategy=DeploymentStrategy.ROLLING  # RECOMMENDED
```

### 4. Shadow (Parallel Testing)

- Deploy new version alongside current
- Send same traffic to both
- Compare results
- Switch if new version performs better

```python
strategy=DeploymentStrategy.SHADOW
```

### 5. Instant (All at Once)

- Deploy to all targets immediately
- Fast but risky
- No gradual rollout

```python
strategy=DeploymentStrategy.INSTANT
```

---

## 🛡️ Safety Features

### Automatic Safeguards

✅ **Signature Verification**
- Every GitHub webhook verified with HMAC-SHA256
- Invalid signatures rejected immediately

✅ **Version Tracking**
- Previous version stored before deployment
- Instant rollback available

✅ **Health Check Retries**
- 3 attempts with 10-second delays
- Accounts for slow startups

✅ **Deployment Validation**
- Package checksum verified
- Deployment scripts validated
- Dependencies checked

✅ **Audit Logging**
- Every deployment logged to `deployment_history`
- Success rate tracked
- Logs preserved for debugging

### Manual Overrides

```python
# Get deployment status
status = system.get_deployment_status("dpl_42c6299934e0")

# Manual rollback
system._rollback_deployment(deployment)

# Force health check
system._comprehensive_health_check(deployment)
```

---

## 🔧 Advanced Usage

### Start Webhook Server

```bash
python auto_deploy_system.py --webhook-server
```

Runs Flask server on `0.0.0.0:5050` listening for GitHub webhooks.

### Custom Deployment Script

```python
package = system.create_deployment_package(
    version="2.3.0",
    changes=["Custom feature"],
    deployment_script="""
import subprocess
subprocess.run(['python', 'scripts/migrate_db.py'], check=True)
subprocess.run(['python', 'scripts/seed_cache.py'], check=True)
print('✓ Custom deployment complete')
""",
    rollback_script="""
import subprocess
subprocess.run(['python', 'scripts/rollback_db.py'], check=True)
print('✓ Rollback complete')
"""
)
```

### Deploy to Specific Targets

```python
# Deploy only to Railway
railway_targets = [t.target_id for t in system.targets.values() if t.platform == PlatformType.RAILWAY]
system.auto_deploy(
    package.package_id,
    DeploymentStrategy.ROLLING,
    target_ids=railway_targets
)
```

---

## 📊 Monitoring Deployments

### Get Deployment Status

```python
status = system.get_deployment_status("dpl_42c6299934e0")

print(f"Status: {status['status']}")
print(f"Progress: {status['progress']}%")
print(f"Success: {status['success_count']}/{status['success_count'] + status['failure_count']}")
print(f"Duration: {status['duration_seconds']}s")
print(f"Recent logs:")
for log in status['logs']:
    print(f"  {log}")
```

### View Deployment History

```python
for deployment_record in system.deployment_history:
    print(f"{deployment_record['timestamp']}: {deployment_record['status']} ({deployment_record['targets']} targets)")

print(f"\nOverall Success Rate: {system.success_rate:.1f}%")
```

### View Rollback Queue

```python
print(f"Rollbacks triggered: {len(system.rollback_queue)}")
for deployment_id in system.rollback_queue:
    print(f"  - {deployment_id}")
```

---

## 🐛 Troubleshooting

### Webhook Not Triggering

✓ Verify GitHub webhook payload URL is correct
✓ Check `GITHUB_WEBHOOK_SECRET` matches GitHub settings
✓ Look at webhook delivery history in GitHub Settings
✓ Verify server is accessible from GitHub

### Docker Build Fails

✓ Ensure Dockerfile is in repo root
✓ Check Docker is installed and running
✓ Verify registry credentials
✓ Check disk space for image

### Platform Deployment Fails

✓ Verify API tokens are valid and not expired
✓ Check project IDs match platform settings
✓ Ensure service is running on target platform
✓ Check firewall rules allow API calls

### Health Checks Failing

✓ Verify `/health` endpoint is implemented
✓ Check endpoint returns 200 status
✓ Verify endpoint is accessible from deployment server
✓ Check logs on deployed service

### Slack/Email Not Sending

✓ Verify `SLACK_WEBHOOK_URL` is correct
✓ Check webhook is still active
✓ Verify `ADMIN_EMAIL` is valid
✓ Check email service credentials

---

## 📈 Performance Metrics

Typical deployment times (assuming all health checks pass):

| Strategy | Avg Time | Downtime | Risk |
|----------|----------|----------|------|
| Blue-Green | 2-3 min | 0s | Low |
| Canary | 3-5 min | 0s | Very Low |
| Rolling | 1-2 min | 0s | Low |
| Shadow | 2-3 min | 0s | Medium |
| Instant | 30-60s | 0s | High |

---

## 🔗 API Endpoints

### Webhook Handler

```
POST /webhook/github
- Receives GitHub push events
- Verifies HMAC signature
- Triggers auto-deployment
- Returns: {"status": "deployment triggered", "commit": "abc1234"}
```

### Deployment Status

```
GET /webhook/status/<deployment_id>
- Returns deployment status
- Shows progress, success/failure counts
- Shows recent logs
```

---

## 📚 Examples

### Full Production Setup

```python
from auto_deploy_system import GlobalAutoDeploySystem, DeploymentStrategy, PlatformType
import os

# Initialize
system = GlobalAutoDeploySystem()

# Register all targets
prod_render = system.register_deployment_target(
    "Render-Production",
    "service",
    PlatformType.RENDER,
    "https://sureshaiorigin.com",
    "https://sureshaiorigin.com/health",
    os.getenv("RENDER_SERVICE_ID")
)

staging_railway = system.register_deployment_target(
    "Railway-Staging",
    "service",
    PlatformType.RAILWAY,
    "https://staging.sureshaiorigin.com",
    "https://staging.sureshaiorigin.com/health",
    os.getenv("RAILWAY_PROJECT_ID")
)

# Create package from git commit
package = system.create_deployment_package(
    version="2.2.0",
    changes=["Rare features launch", "Autonomous agent", "Self-healing infrastructure"],
    deployment_script="docker pull ghcr.io/suresh-ai-origin:2.2.0",
    rollback_script="docker pull ghcr.io/suresh-ai-origin:2.1.0"
)

# Deploy
deployment = system.auto_deploy(
    package.package_id,
    DeploymentStrategy.ROLLING,
    build_docker=True,
    commit_sha="abc1234"
)

print(f"✅ Deployment {deployment.deployment_id} complete!")
print(f"Status: {deployment.status.value}")
```

---

**Status**: ✅ Production-Ready  
**Version**: 2.0  
**Last Updated**: Jan 18, 2026
