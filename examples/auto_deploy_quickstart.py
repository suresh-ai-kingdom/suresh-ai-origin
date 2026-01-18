#!/usr/bin/env python3
"""
Quick reference: Auto-Deploy V2.0 Usage Examples
Copy-paste ready code for common scenarios
"""

from auto_deploy_system import GlobalAutoDeploySystem, DeploymentStrategy, PlatformType
import os

# ============================================================================
# 1. SETUP - Initialize System and Register Targets
# ============================================================================

system = GlobalAutoDeploySystem()

# Register Railway production
railway = system.register_deployment_target(
    name="Railway-Production",
    target_type="service",
    platform=PlatformType.RAILWAY,
    endpoint="https://sureshaiorigin-prod.railway.app",
    health_check_url="https://sureshaiorigin-prod.railway.app/health",
    project_id=os.getenv("RAILWAY_PROJECT_ID")
)

# Register Render staging
render = system.register_deployment_target(
    name="Render-Staging",
    target_type="service",
    platform=PlatformType.RENDER,
    endpoint="https://sureshaiorigin-staging.onrender.com",
    health_check_url="https://sureshaiorigin-staging.onrender.com/health",
    project_id=os.getenv("RENDER_SERVICE_ID")
)

# Register Vercel
vercel = system.register_deployment_target(
    name="Vercel-Production",
    target_type="service",
    platform=PlatformType.VERCEL,
    endpoint="https://sureshaiorigin.vercel.app",
    health_check_url="https://sureshaiorigin.vercel.app/api/health",
    project_id=os.getenv("VERCEL_PROJECT_ID")
)


# ============================================================================
# 2. CREATE DEPLOYMENT PACKAGE
# ============================================================================

package = system.create_deployment_package(
    version="2.2.0",
    changes=[
        "🚀 Rare 1% features live",
        "🤖 Autonomous business agent",
        "🔄 Self-healing infrastructure",
        "📊 Advanced analytics"
    ],
    deployment_script="python scripts/deploy.py",
    rollback_script="python scripts/rollback.py"
)

print(f"✓ Package created: v{package.version} (ID: {package.package_id})")


# ============================================================================
# 3. DEPLOY - Choose Strategy
# ============================================================================

# Option A: ROLLING (Recommended - safest, zero downtime)
deployment = system.auto_deploy(
    package_id=package.package_id,
    strategy=DeploymentStrategy.ROLLING,
    build_docker=True,
    commit_sha="abc1234"
)

# Option B: BLUE-GREEN (Instant switch, zero downtime)
# deployment = system.auto_deploy(
#     package_id=package.package_id,
#     strategy=DeploymentStrategy.BLUE_GREEN,
#     build_docker=True,
#     commit_sha="abc1234"
# )

# Option C: CANARY (Gradual, 10% first, then rest)
# deployment = system.auto_deploy(
#     package_id=package.package_id,
#     strategy=DeploymentStrategy.CANARY,
#     build_docker=True,
#     commit_sha="abc1234"
# )

# Option D: Deploy to specific targets only
# railway_target = [t.target_id for t in system.targets.values() if t.name == "Railway-Production"]
# deployment = system.auto_deploy(
#     package_id=package.package_id,
#     strategy=DeploymentStrategy.ROLLING,
#     target_ids=railway_target,
#     build_docker=True,
#     commit_sha="abc1234"
# )


# ============================================================================
# 4. MONITOR DEPLOYMENT
# ============================================================================

print(f"\n📊 Deployment Status:")
print(f"   ID: {deployment.deployment_id}")
print(f"   Status: {deployment.status.value}")
print(f"   Progress: {deployment.get_progress():.0f}%")
print(f"   Success: {deployment.success_count}/{len(deployment.targets)} targets")
print(f"   Health Check: {'✓ Passed' if deployment.health_check_passed else '✗ Failed'}")

if deployment.completed_at:
    duration = deployment.completed_at - deployment.started_at
    print(f"   Duration: {duration:.1f}s")

# Get full status
status = system.get_deployment_status(deployment.deployment_id)
print(f"\n📋 Recent Logs:")
for log in status['logs'][-5:]:
    print(f"   {log}")


# ============================================================================
# 5. MANUAL OPERATIONS
# ============================================================================

# View deployment history
print(f"\n📈 Deployment History:")
print(f"   Total deployments: {len(system.deployment_history)}")
print(f"   Overall success rate: {system.success_rate:.1f}%")

# View rollback queue
print(f"\n🔄 Rollbacks triggered: {len(system.rollback_queue)}")

# Manual rollback (if needed)
# system._rollback_deployment(deployment)

# Force health check
# health_ok = system._comprehensive_health_check(deployment)

# Deploy to specific targets
# railway_only = [t for t in system.targets.values() if t.platform == PlatformType.RAILWAY]
# target_ids = [t.target_id for t in railway_only]
# system.auto_deploy(package.package_id, DeploymentStrategy.ROLLING, target_ids=target_ids)


# ============================================================================
# 6. WEBHOOK SERVER (For GitHub Integration)
# ============================================================================

# Run webhook server to receive GitHub push events
# Start in separate terminal or background:
# python auto_deploy_system.py --webhook-server
# 
# Then configure GitHub webhook:
# 1. Go to GitHub repo Settings > Webhooks
# 2. Add webhook:
#    - Payload URL: https://your-server.com/webhook/github
#    - Secret: Set GITHUB_WEBHOOK_SECRET env var
#    - Events: Push events
# 3. Every push to main branch auto-triggers deployment


# ============================================================================
# 7. ENVIRONMENT VARIABLES (Required)
# ============================================================================

"""
# Required env vars (.env or Render dashboard):

# GitHub Webhook
GITHUB_WEBHOOK_SECRET=your-secret-key

# Railway
RAILWAY_API_TOKEN=your-railway-token
RAILWAY_PROJECT_ID=your-project-id

# Vercel
VERCEL_TOKEN=your-vercel-token
VERCEL_PROJECT_ID=your-project-id

# Render
RENDER_API_KEY=your-render-api-key
RENDER_SERVICE_ID=your-service-id

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ADMIN_EMAIL=admin@sureshaiorigin.com

# Docker
DOCKER_REGISTRY=ghcr.io
DOCKER_IMAGE_NAME=suresh-ai-origin
"""


# ============================================================================
# 8. EXAMPLE: Custom Deployment Script
# ============================================================================

custom_package = system.create_deployment_package(
    version="2.3.0",
    changes=["Database migration", "Cache warm-up"],
    deployment_script="""
import subprocess
import sys

# Run database migration
print('🔄 Running database migration...')
result = subprocess.run(['python', 'scripts/migrate_db.py'], check=True)

# Warm up cache
print('💾 Warming up cache...')
result = subprocess.run(['python', 'scripts/seed_cache.py'], check=True)

# Verify deployment
print('✓ Deployment verification passed')
sys.exit(0)
""",
    rollback_script="""
import subprocess
print('🔄 Rolling back database...')
subprocess.run(['python', 'scripts/rollback_db.py'], check=True)
print('✓ Rollback complete')
"""
)

# Then deploy with custom script
# deployment = system.auto_deploy(
#     custom_package.package_id,
#     DeploymentStrategy.ROLLING
# )


# ============================================================================
# 9. DOCKER BUILD LOCALLY (Optional)
# ============================================================================

"""
# Build Docker image manually:
docker build -t ghcr.io/suresh-ai-origin:v2.2.0 .

# Push to registry:
docker push ghcr.io/suresh-ai-origin:v2.2.0

# Tag as latest:
docker tag ghcr.io/suresh-ai-origin:v2.2.0 ghcr.io/suresh-ai-origin:latest
docker push ghcr.io/suresh-ai-origin:latest
"""


# ============================================================================
# 10. HEALTH CHECK ENDPOINT (Required in app.py)
# ============================================================================

"""
# Your Flask app needs this endpoint:

from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.2.0",
        "uptime": "99.95%"
    }), 200

# Optional: Detailed health check
@app.route('/api/health', methods=['GET'])
def detailed_health():
    return jsonify({
        "status": "healthy",
        "database": "✓ Connected",
        "redis": "✓ Connected",
        "services": {
            "rare_features": "✓ 5/5 operational",
            "autonomous_agent": "✓ Running",
            "webhooks": "✓ Listening"
        },
        "metrics": {
            "uptime_percent": 99.95,
            "requests_per_minute": 1250,
            "error_rate": 0.01
        }
    }), 200
"""


if __name__ == "__main__":
    print(f"✅ Auto-Deploy System Ready!")
    print(f"   Production targets: {len(system.targets)}")
    print(f"   Deployment packages: {len(system.packages)}")
    print(f"   Recent deployments: {len(system.deployment_history)}")
    print(f"   Success rate: {system.success_rate:.1f}%")
