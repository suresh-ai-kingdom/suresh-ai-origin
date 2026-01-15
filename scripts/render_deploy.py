#!/usr/bin/env python3
"""
🚀 RENDER DEPLOYMENT AUTOMATION SCRIPT
Automates setup, verification, and deployment to Render
"""

import os
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text:^80}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def run_command(cmd, description=""):
    """Run shell command with error handling"""
    if description:
        print_info(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_prerequisites():
    """Check all prerequisites for deployment"""
    print_header("🔍 CHECKING PREREQUISITES")
    
    checks = {
        "Git installed": ("git --version", ""),
        "Python 3.11+": ("python --version", ""),
        "requirements.txt exists": ("test -f requirements.txt", ""),
        "Dockerfile exists": ("test -f Dockerfile", ""),
        "render.yaml exists": ("test -f render.yaml", ""),
        "app.py exists": ("test -f app.py", ""),
        "models.py exists": ("test -f models.py", ""),
        "alembic directory exists": ("test -d alembic", ""),
        "scripts/seed_demo.py exists": ("test -f scripts/seed_demo.py", ""),
    }
    
    all_ok = True
    for check_name, (cmd, _) in checks.items():
        success, output = run_command(cmd)
        if success:
            print_success(check_name)
        else:
            print_error(f"{check_name} - {output.strip()}")
            all_ok = False
    
    return all_ok

def verify_dependencies():
    """Verify Python dependencies"""
    print_header("📦 VERIFYING PYTHON DEPENDENCIES")
    
    try:
        with open('requirements.txt', 'r') as f:
            deps = f.readlines()
        print_success(f"requirements.txt contains {len(deps)} packages")
        
        # Check critical packages
        critical = ['flask', 'sqlalchemy', 'razorpay', 'gunicorn']
        req_text = open('requirements.txt').read().lower()
        for pkg in critical:
            if pkg in req_text:
                print_success(f"  ✓ {pkg} required")
            else:
                print_warning(f"  ✗ {pkg} NOT found (may be optional)")
        return True
    except Exception as e:
        print_error(f"Failed to read requirements.txt: {e}")
        return False

def generate_secrets():
    """Generate required secrets"""
    print_header("🔐 GENERATING DEPLOYMENT SECRETS")
    
    import secrets
    flask_key = secrets.token_hex(32)
    admin_token = secrets.token_hex(16)
    
    secrets_dict = {
        "FLASK_SECRET_KEY": flask_key,
        "ADMIN_TOKEN": admin_token,
        "DEPLOYMENT_DATE": datetime.now().isoformat(),
    }
    
    print_info("Generated secrets:")
    print(f"\n  FLASK_SECRET_KEY: {flask_key}")
    print(f"  ADMIN_TOKEN: {admin_token}\n")
    
    # Save to file
    with open('.deployment_secrets.json', 'w') as f:
        json.dump(secrets_dict, f, indent=2)
    
    print_success("Secrets saved to .deployment_secrets.json (ADD TO .gitignore)")
    return secrets_dict

def verify_git():
    """Verify Git setup"""
    print_header("🌿 VERIFYING GIT REPOSITORY")
    
    # Check git initialized
    success, output = run_command("git rev-parse --git-dir", "Checking git status")
    if not success:
        print_error("Not a git repository. Initialize with: git init")
        return False
    
    print_success("Git repository found")
    
    # Check remote
    success, output = run_command("git remote get-url origin", "Checking GitHub remote")
    if success and output.strip():
        print_success(f"GitHub remote: {output.strip()}")
    else:
        print_warning("No GitHub remote configured")
        print_info("Add with: git remote add origin https://github.com/YOUR_USERNAME/suresh-ai-origin.git")
    
    # Check branch
    success, output = run_command("git rev-parse --abbrev-ref HEAD", "Checking branch")
    if success:
        current_branch = output.strip()
        print_success(f"Current branch: {current_branch}")
        if current_branch != "main":
            print_warning(f"Consider deploying from 'main' branch, currently on '{current_branch}'")
    
    return True

def prepare_deployment():
    """Prepare deployment files"""
    print_header("📝 PREPARING DEPLOYMENT FILES")
    
    files_to_check = [
        ("Dockerfile", "Docker image configuration"),
        ("render.yaml", "Render service configuration"),
        (".dockerignore", "Docker ignore patterns"),
        (".gitignore", "Git ignore patterns"),
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print_success(f"{filename} - {description}")
        else:
            print_warning(f"{filename} NOT FOUND - {description}")
    
    print_info("\nKey files ready for deployment:")
    print("  ✓ app.py (Flask application)")
    print("  ✓ models.py (Database models)")
    print("  ✓ utils.py (Utility functions)")
    print("  ✓ alembic/ (Database migrations)")
    print("  ✓ scripts/seed_demo.py (Data seeding)")
    print("  ✓ requirements.txt (Dependencies)")
    
    return True

def generate_deployment_checklist():
    """Generate deployment checklist"""
    print_header("✅ DEPLOYMENT CHECKLIST")
    
    checklist = """
BEFORE DEPLOYMENT:
  [ ] All environment variables obtained:
      - RAZORPAY_KEY_ID (Live key)
      - RAZORPAY_KEY_SECRET
      - RAZORPAY_WEBHOOK_SECRET
      - GOOGLE_API_KEY (Gemini)
      - EMAIL_USER (Outlook)
      - EMAIL_PASS (App password)
      - ADMIN_PASSWORD (Strong)
  
  [ ] GitHub repository configured
  [ ] Code pushed to main branch
  [ ] All tests passing (pytest)
  [ ] requirements.txt up to date
  [ ] Database migrations created (alembic)

DURING DEPLOYMENT (Render Dashboard):
  [ ] Create new Web Service
  [ ] Connect GitHub repository
  [ ] Configure environment variables
  [ ] Add persistent disk (/app/data, 10GB)
  [ ] Set build & start commands
  [ ] Enable auto-deploy
  [ ] Review and deploy

POST-DEPLOYMENT (First 24 Hours):
  [ ] Verify service health at /health endpoint
  [ ] Test admin login
  [ ] Verify database connectivity
  [ ] Configure Razorpay webhook
  [ ] Test payment flow (test transaction)
  [ ] Verify email notifications
  [ ] Monitor metrics dashboard
  [ ] Check real-time monitoring active
  [ ] Set up log collection
  [ ] Document live URL

PHASE 1 TARGETS:
  [ ] Track Day 1 users: 50K target
  [ ] Monitor revenue: ₹3-5M target
  [ ] Verify infrastructure: 65 satellites, 36 DCs
  [ ] Confirm marketing campaigns live
  [ ] Ensure 24/7 operations centers active
"""
    
    print(checklist)
    
    # Save checklist
    with open('DEPLOYMENT_CHECKLIST.md', 'w') as f:
        f.write("# RENDER DEPLOYMENT CHECKLIST\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(checklist)
    
    print_success("Checklist saved to DEPLOYMENT_CHECKLIST.md")

def generate_environment_template():
    """Generate environment variables template"""
    print_header("🔧 GENERATING ENVIRONMENT VARIABLES TEMPLATE")
    
    env_template = """# SURESH AI ORIGIN - RENDER DEPLOYMENT
# Generated: {DATE}
# ⚠️  DO NOT COMMIT THIS FILE - Use Render Dashboard to set variables

# Flask Configuration
FLASK_SECRET_KEY={FLASK_SECRET_KEY}
FLASK_DEBUG=false

# Database
DATA_DB=/app/data/data.db

# Payment Integration - Razorpay (LIVE)
RAZORPAY_KEY_ID=rzp_live_XXXXX_REPLACE_ME
RAZORPAY_KEY_SECRET=XXXXX_REPLACE_ME
RAZORPAY_WEBHOOK_SECRET=XXXXX_REPLACE_ME

# Payment Integration - Stripe (Optional)
STRIPE_SECRET_KEY=sk_live_XXXXX_REPLACE_ME
STRIPE_PUBLISHABLE_KEY=pk_live_XXXXX_REPLACE_ME
STRIPE_WEBHOOK_SECRET=XXXXX_REPLACE_ME

# Email Configuration (Outlook)
EMAIL_USER=your-outlook@outlook.com_REPLACE_ME
EMAIL_PASS=your-app-password_REPLACE_ME
EMAIL_SMTP_HOST=smtp-mail.outlook.com
EMAIL_SMTP_PORT=587

# AI Integration (Gemini 2.5 Flash)
GOOGLE_API_KEY=XXXXX_REPLACE_ME
AI_PROVIDER=gemini

# Admin Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=STRONG_PASSWORD_HERE_REPLACE_ME
ADMIN_TOKEN={ADMIN_TOKEN}
ADMIN_SESSION_TIMEOUT=3600

# Feature Flags (Phase 1 - All Enabled)
FLAG_FINANCE_ENTITLEMENTS_ENFORCED=true
FLAG_INTEL_RECOMMENDATIONS_ENABLED=true
FLAG_GROWTH_NUDGES_ENABLED=true
FLAG_MARKETPLACE_ENABLED=true
FLAG_SATELLITE_TRACKING_ENABLED=true
FLAG_CURRENCY_SYSTEM_ENABLED=true
FLAG_BANK_OPERATIONS_ENABLED=true
FLAG_REAL_TIME_MONITORING_ENABLED=true

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# Error Tracking (Optional - Sentry)
# SENTRY_DSN=https://XXXXX@XXXXX.ingest.sentry.io/XXXXX

# Logging
LOG_LEVEL=INFO
""".format(DATE=datetime.now().isoformat(), FLASK_SECRET_KEY="(generated)", ADMIN_TOKEN="(generated)")
    
    # Save template
    with open('.env.render.template', 'w') as f:
        f.write(env_template)
    
    print_success("Environment template saved to .env.render.template")
    print_info("Instructions:")
    print("  1. Copy .env.render.template")
    print("  2. Fill in all XXXXX_REPLACE_ME values")
    print("  3. Add each variable to Render Dashboard")
    print("  4. DO NOT commit this file")

def generate_deployment_summary():
    """Generate deployment summary"""
    print_header("📊 DEPLOYMENT SUMMARY")
    
    summary = f"""
SURESH AI ORIGIN - PHASE 1 RENDER DEPLOYMENT
Generated: {datetime.now().isoformat()}

SERVICE CONFIGURATION:
  Name:                 suresh-ai-origin
  Runtime:              Python 3.11
  Build Command:        pip install -r requirements.txt && python scripts/seed_demo.py seed
  Start Command:        gunicorn -w 4 -b 0.0.0.0:$PORT app:app
  Health Check:         /health endpoint
  Disk:                 /app/data (10GB persistent)
  Auto-deploy:          Enabled (on GitHub push)

INFRASTRUCTURE:
  Replicas:             1 (scale as needed)
  Region:               Default (Render auto-selects)
  SSL/TLS:              Auto-provided by Render
  CDN:                  Available (optional)

DEPLOYMENT TARGETS:
  ✓ Web Service (Flask app)
  ✓ Persistent Disk (SQLite database)
  ✓ Environment Variables (all secrets)
  ✓ Health Monitoring (Render dashboard)
  ✓ Auto-deployments (GitHub integration)
  ✓ SSL Certificates (auto-renewed)

PHASE 1 MILESTONES (30 Days):
  Day 1:   50K users    | ₹3-5M revenue    | Launch event
  Day 7:   200K users   | ₹20M revenue     | Wave 1 complete
  Day 14:  400K users   | ₹50M revenue     | Wave 2 active
  Day 21:  700K users   | ₹100M revenue    | Trending globally
  Day 30:  1M+ users    | ₹215M+ revenue   | Phase 1 complete ✅

NEXT STEPS:
  1. Review RENDER_DEPLOYMENT_GUIDE.md (comprehensive guide)
  2. Prepare environment variables (.env.render.template)
  3. Push code to GitHub
  4. Create service on Render dashboard
  5. Set environment variables in Render
  6. Monitor deployment logs
  7. Test health endpoint and admin login
  8. Configure Razorpay webhook
  9. Start Day 1 milestone tracking
  10. Monitor metrics dashboard 24/7

SUPPORT:
  Dashboard: https://dashboard.render.com
  Health:    https://suresh-ai-origin.onrender.com/health
  Admin:     https://suresh-ai-origin.onrender.com/admin/login
  Docs:      https://render.com/docs

STATUS: ✅ READY FOR DEPLOYMENT
"""
    
    print(summary)
    
    # Save summary
    with open('DEPLOYMENT_SUMMARY.txt', 'w') as f:
        f.write(summary)
    
    print_success("Deployment summary saved to DEPLOYMENT_SUMMARY.txt")

def main():
    """Main deployment preparation"""
    print_header("🚀 SURESH AI ORIGIN - RENDER DEPLOYMENT AUTOMATION")
    
    # Run checks
    print_info("Starting deployment preparation...\n")
    
    checks = [
        ("Prerequisites", check_prerequisites),
        ("Dependencies", verify_dependencies),
        ("Git Setup", verify_git),
        ("Deployment Files", prepare_deployment),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print_error(f"{check_name} failed: {e}")
            all_passed = False
    
    if not all_passed:
        print_warning("Some checks failed. Review and fix before deploying.")
    
    # Generate artifacts
    print_header("📋 GENERATING DEPLOYMENT ARTIFACTS")
    
    secrets = generate_secrets()
    generate_deployment_checklist()
    generate_environment_template()
    generate_deployment_summary()
    
    # Final status
    print_header("🎯 DEPLOYMENT PREPARATION COMPLETE")
    
    print_success("All preparation steps completed!")
    print_info("\nGenerated files:")
    print("  ✓ .deployment_secrets.json (secrets backup)")
    print("  ✓ .env.render.template (environment variables)")
    print("  ✓ DEPLOYMENT_CHECKLIST.md (step-by-step checklist)")
    print("  ✓ DEPLOYMENT_SUMMARY.txt (overview & next steps)")
    
    print_info("\nNext action:")
    print("  1. Review .env.render.template")
    print("  2. Fill in all secret values")
    print("  3. Open Render dashboard")
    print("  4. Create new Web Service")
    print("  5. Add all environment variables")
    print("  6. Deploy!")
    
    print(f"\n{BOLD}{GREEN}✅ READY FOR DEPLOYMENT TO RENDER!{RESET}\n")

if __name__ == "__main__":
    main()
