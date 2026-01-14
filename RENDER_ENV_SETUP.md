# Render Environment Variables Setup

## 🚀 Quick Setup Guide

Go to: **Render Dashboard** → **suresh-ai-origin** → **Environment**

---

## 🆕 New Variables for Week 2 Automations

Add these to enable monitoring, backups, and daily automations:

### Monitoring & Alerts
```bash
# Webhook alerts (Slack/Discord)
ALERT_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email alerts
ALERT_EMAIL=suresh.ai.origin@outlook.com

# Monitoring intervals
MONITOR_INTERVAL=300
MONITOR_ALERT_ON_STARTUP=false

# Error tracking (optional)
SENTRY_DSN=https://YOUR_SENTRY_DSN@sentry.io/PROJECT_ID
```

### Backup Automation
```bash
# Backup configuration
BACKUP_KEEP=7
BACKUP_NOTIFY_SUCCESS=false
PROJECT_NAME=SURESH AI ORIGIN
```

### Daily Automations
```bash
# Workflow automation
AUTOMATION_DAYS_BACK=30
AUTOMATION_NOTIFY_SUCCESS=false

# Slow query tracking
SLOW_QUERY_THRESHOLD=1.0
```

---

## ✅ Existing Variables (Keep These)

### Critical
```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
AI_PROVIDER=groq
AI_MODEL=llama-3.3-70b-versatile
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxxxxxxxxxx
ADMIN_PASSWORD_HASH=scrypt:xxxxxxxxxxxxx
FLASK_SECRET_KEY=xxxxxxxxxxxxx
```

### Optional
```bash
ADMIN_USERNAME=admin
EMAIL_USER=suresh.ai.origin@outlook.com
EMAIL_PASS=your_outlook_app_password
```

---

## 📋 Setup Checklist

### Step 1: Add New Variables
- [ ] `ALERT_WEBHOOK` - Get from Slack/Discord webhook settings
- [ ] `ALERT_EMAIL` - Your alert destination email
- [ ] `SENTRY_DSN` - Optional, from sentry.io (free tier available)
- [ ] `BACKUP_KEEP=7` - Number of backups to retain
- [ ] `AUTOMATION_DAYS_BACK=30` - Lookback window for automations
- [ ] `SLOW_QUERY_THRESHOLD=1.0` - Log queries slower than this (seconds)

### Step 2: Verify Render Deployment
After adding variables, Render auto-deploys. Check:
- [ ] Render logs show successful startup
- [ ] Sentry initialization logged (if DSN set)
- [ ] Health endpoint includes slow_queries metrics: `curl https://suresh-ai-origin.onrender.com/health`

### Step 3: Test Automations
```bash
# Test nightly backup (runs in production)
curl -X POST https://suresh-ai-origin.onrender.com/api/admin/run-backup

# Check health with slow query stats
curl https://suresh-ai-origin.onrender.com/health | jq '.slow_queries'

# Monitor production (local)
python scripts/monitor_service.py
```

### Step 4: Schedule on Render (Paid Tier) or External
Since Render free tier doesn't support cron:

**Option A: GitHub Actions (Free)**
Create `.github/workflows/daily-automations.yml`:
```yaml
name: Daily Automations
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily (nightly backup)
    - cron: '0 3 * * *'  # 3 AM UTC daily (workflows)
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Nightly Backup
        run: |
          curl -X POST https://suresh-ai-origin.onrender.com/api/admin/trigger-backup \
            -H "Authorization: Bearer ${{ secrets.ADMIN_TOKEN }}"
  
  automations:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Daily Automations
        run: |
          curl -X POST https://suresh-ai-origin.onrender.com/api/admin/trigger-automations \
            -H "Authorization: Bearer ${{ secrets.ADMIN_TOKEN }}"
```

**Option B: cron-job.org (Free)**
1. Sign up at https://cron-job.org (free)
2. Create cron jobs:
   - **Nightly Backup**: Daily 2 AM UTC → `POST https://suresh-ai-origin.onrender.com/api/admin/trigger-backup`
   - **Daily Automations**: Daily 3 AM UTC → `POST https://suresh-ai-origin.onrender.com/api/admin/trigger-automations`
   - **Health Check**: Every 5 min → `GET https://suresh-ai-origin.onrender.com/health`

**Option C: Render Cron Jobs (Paid)**
Upgrade to $7/month plan → Add cron jobs in dashboard

---

## 🔧 How to Get Webhook URLs

### Slack
1. Go to https://api.slack.com/apps
2. Create New App → From scratch
3. Incoming Webhooks → Activate
4. Add New Webhook to Workspace
5. Copy webhook URL → Use as `ALERT_WEBHOOK`

### Discord
1. Server Settings → Integrations → Webhooks
2. New Webhook → Choose channel
3. Copy Webhook URL → Use as `ALERT_WEBHOOK`

### Microsoft Teams
1. Channel → More options (⋯) → Connectors
2. Incoming Webhook → Configure
3. Copy URL → Use as `ALERT_WEBHOOK`

---

## 🧪 Testing Locally

Before deploying, test locally:

```powershell
# Set env vars in .env
echo "ALERT_WEBHOOK=https://hooks.slack.com/..." >> .env
echo "BACKUP_KEEP=7" >> .env

# Test backup
python scripts/nightly_backup.py

# Test automations
python scripts/run_daily_automations.py

# Test monitor (Ctrl+C to stop)
python scripts/monitor_service.py
```

---

## 📊 Monitoring Dashboard

After setup, monitor via:
- **Health**: https://suresh-ai-origin.onrender.com/health
- **Admin Dashboard**: https://suresh-ai-origin.onrender.com/admin
- **Render Logs**: https://dashboard.render.com → Logs tab
- **Sentry**: https://sentry.io/organizations/YOUR_ORG/projects/ (if configured)

---

*Setup complete? Mark tasks above and verify alerts are working!*
