# 🚀 RENDER DEPLOYMENT GUIDE - SURESH AI ORIGIN
## Production Deployment to Render Hosting

---

## 📋 PREREQUISITES

### Before You Start
1. **Render Account**: Create at https://render.com (free tier available)
2. **GitHub Repository**: Push code to GitHub (Render deploys from GitHub)
3. **Environment Secrets**: Have all API keys ready:
   - Razorpay (LIVE keys)
   - Stripe (if using)
   - Google API (Gemini)
   - Outlook email credentials
   - Admin passwords

### Required Credentials
```
✅ RAZORPAY_KEY_ID          (Live key)
✅ RAZORPAY_KEY_SECRET      (Live key)
✅ RAZORPAY_WEBHOOK_SECRET  (Webhook secret)
✅ GOOGLE_API_KEY           (Gemini API)
✅ EMAIL_USER               (Outlook email)
✅ EMAIL_PASS               (Outlook app password)
✅ ADMIN_PASSWORD           (Strong password)
✅ FLASK_SECRET_KEY         (Generate: python -c "import secrets; print(secrets.token_hex(32))")
```

---

## 🔧 STEP 1: PREPARE GITHUB REPOSITORY

### 1.1 Push to GitHub
```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "SURESH AI ORIGIN - Phase 1 Deployment Ready"

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/suresh-ai-origin.git

# Push to main branch
git branch -M main
git push -u origin main
```

### 1.2 Required Files in Repo
- ✅ `requirements.txt` - Python dependencies
- ✅ `Dockerfile` - Container configuration (included)
- ✅ `render.yaml` - Render deployment config (updated)
- ✅ `app.py` - Flask application
- ✅ `models.py` - Database models
- ✅ `alembic/` - Database migrations
- ✅ `scripts/seed_demo.py` - Data seeding

---

## 🌐 STEP 2: CREATE RENDER SERVICE

### 2.1 Option A: Using Render Dashboard (Recommended for First Time)

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Create New Web Service**:
   - Click "New +"
   - Select "Web Service"
   - Connect GitHub repo
   - Select `suresh-ai-origin` repository
   - Authorization: Grant access to your GitHub

3. **Configure Service**:
   - **Name**: `suresh-ai-origin`
   - **Environment**: Python 3.11
   - **Build Command**: 
     ```
     pip install --upgrade pip && pip install -r requirements.txt && python scripts/seed_demo.py seed
     ```
   - **Start Command**: 
     ```
     gunicorn -w 4 -b 0.0.0.0:$PORT app:app
     ```
   - **Branch**: main
   - **Auto-deploy**: ON (when you push to GitHub)

4. **Disk (Persistent Storage)**:
   - Click "Add Disk"
   - **Name**: `suresh-data`
   - **Mount Path**: `/app/data`
   - **Size**: 10 GB

5. **Environment Variables**:
   - Set ALL required environment variables (see list below)

### 2.2 Option B: Using render.yaml (Recommended for Production)

The `render.yaml` file is already configured. Just:

1. Go to https://dashboard.render.com/deploy-github
2. Click "Connect Repository"
3. Select `suresh-ai-origin`
4. Render auto-detects `render.yaml`
5. Click "Create Service"

---

## 🔐 STEP 3: SET ENVIRONMENT VARIABLES

### In Render Dashboard: Settings → Environment

Add all variables:

```env
# Flask
FLASK_SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
FLASK_DEBUG=false

# Database
DATA_DB=/app/data/data.db

# Payment - Razorpay (LIVE)
RAZORPAY_KEY_ID=rzp_live_XXXXX
RAZORPAY_KEY_SECRET=XXXXX
RAZORPAY_WEBHOOK_SECRET=XXXXX

# Payment - Stripe (Optional)
STRIPE_SECRET_KEY=sk_live_XXXXX
STRIPE_PUBLISHABLE_KEY=pk_live_XXXXX
STRIPE_WEBHOOK_SECRET=XXXXX

# Email
EMAIL_USER=your-outlook@outlook.com
EMAIL_PASS=your-app-password
EMAIL_SMTP_HOST=smtp-mail.outlook.com
EMAIL_SMTP_PORT=587

# AI (Gemini 2.5 Flash)
GOOGLE_API_KEY=XXXXX
AI_PROVIDER=gemini

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password>
ADMIN_TOKEN=<generate-random>
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

# Logging
LOG_LEVEL=INFO
```

---

## ✅ STEP 4: DATABASE SETUP

### 4.1 Auto-Migration on Deploy

The `preDeployCommand` in `render.yaml` runs:
```bash
PYTHONPATH=. alembic upgrade head
```

This automatically:
- Creates database tables
- Applies all migrations
- Seeds demo data (via buildCommand)

### 4.2 Manual Database Commands (If Needed)

Once deployed, SSH into Render container:

```bash
# SSH into running container
# From Render Dashboard: Web Service → Shell

# Create tables
python
>>> from utils import init_db
>>> init_db()

# Seed demo data
python scripts/seed_demo.py seed

# View database
sqlite3 /app/data/data.db

# Backup database
python scripts/backup_db.py create
```

---

## 🚀 STEP 5: DEPLOY & VERIFY

### 5.1 Deploy Service

1. **Option A - GitHub Push** (Auto):
   ```bash
   git push origin main
   # Render auto-deploys within 2 minutes
   ```

2. **Option B - Manual Trigger**:
   - Render Dashboard → Web Service → "Deploy latest"

### 5.2 Monitor Deployment

In Render Dashboard:
- **Events Tab**: Watch build & deploy logs
- **Logs Tab**: Real-time application logs
- **Metrics Tab**: CPU, Memory, Network usage

### 5.3 Verify Application

```bash
# Check service is live
curl https://suresh-ai-origin.onrender.com/health

# Expected response:
# {"status":"healthy","timestamp":"2026-01-15T03:49:33Z"}

# Access admin
https://suresh-ai-origin.onrender.com/admin/login
# Username: admin
# Password: <your ADMIN_PASSWORD>
```

---

## 🔗 STEP 6: CONFIGURE WEBHOOKS

### 6.1 Razorpay Webhook Setup

1. **Get Render URL**:
   - From Render Dashboard
   - URL: `https://suresh-ai-origin.onrender.com`

2. **In Razorpay Dashboard**:
   - Go to Settings → Webhooks
   - Add Webhook URL: `https://suresh-ai-origin.onrender.com/webhook`
   - Events: Select `payment.captured`
   - Get Webhook Secret: Copy and set `RAZORPAY_WEBHOOK_SECRET`

3. **Test Webhook**:
   ```bash
   curl -X POST https://suresh-ai-origin.onrender.com/webhook \
     -H "Content-Type: application/json" \
     -H "X-Razorpay-Signature: test" \
     -d '{"event":"payment.captured"}'
   ```

### 6.2 Stripe Webhook Setup (Optional)

1. **In Stripe Dashboard**:
   - Go to Developers → Webhooks
   - Add endpoint: `https://suresh-ai-origin.onrender.com/stripe-webhook`
   - Events: `charge.succeeded`, `charge.failed`
   - Copy Signing Secret: Set `STRIPE_WEBHOOK_SECRET`

---

## 📊 STEP 7: MONITORING & OPERATIONS

### 7.1 Real-Time Monitoring

Access monitoring dashboards:
```
Dashboard: https://suresh-ai-origin.onrender.com/admin
Metrics: https://suresh-ai-origin.onrender.com/admin/metrics
Webhooks: https://suresh-ai-origin.onrender.com/admin/webhooks
```

### 7.2 Database Backups

```bash
# Automatic daily backups (set up in Render)
# Or manually via SSH:
python scripts/backup_db.py create

# List backups
ls backups/

# Restore backup
python scripts/backup_db.py restore <backup-name>
```

### 7.3 Logs & Debugging

- **Real-time logs**: Render Dashboard → Logs tab
- **Download logs**: Render Dashboard → Logs → Download
- **Error tracking**: Sentry (optional, set SENTRY_DSN)

### 7.4 Performance Tuning

**If experiencing slow performance**:

1. **Increase Workers**:
   - Start Command: `gunicorn -w 8 -b 0.0.0.0:$PORT app:app`

2. **Add Redis Cache**:
   - Already in render.yaml (Redis service)
   - Set: `REDIS_URL=redis://suresh-redis:6379/0`

3. **Scale Service**:
   - Render Dashboard → Settings → Increase Num Instances

4. **Monitor Memory**:
   - If >80%: Increase Instance Plan

---

## 🔄 STEP 8: CONTINUOUS DEPLOYMENT

### 8.1 Auto-Deploy on Push

Already enabled in `render.yaml`:
```yaml
autoDeploy: true
```

When you push to GitHub:
```bash
git push origin main
# Render automatically:
# 1. Detects new push
# 2. Pulls latest code
# 3. Installs dependencies
# 4. Runs build command
# 5. Starts new service
# (Previous version keeps running during deploy - zero downtime)
```

### 8.2 Branch-Based Deployments

To deploy different branches to different services:

```yaml
# For staging branch
services:
  - type: web
    name: suresh-ai-staging
    branch: staging
    ...
```

---

## 📈 STEP 9: PHASE 1 DEPLOYMENT VERIFICATION

### 9.1 Health Checks (First 24 Hours)

```bash
# Hour 0: Service running
curl https://suresh-ai-origin.onrender.com/health

# Hour 1: Database functional
curl https://suresh-ai-origin.onrender.com/api/health

# Hour 2: Payment gateway live
curl https://suresh-ai-origin.onrender.com/admin/webhooks

# Hour 6: Real-time monitoring active
curl https://suresh-ai-origin.onrender.com/admin/metrics

# Hour 24: All systems operational
curl https://suresh-ai-origin.onrender.com/admin/dashboard
```

### 9.2 Day 1 Targets

From Phase 1 Orchestrator:
- ✅ **Users**: 50K new users acquired
- ✅ **Revenue**: ₹3-5M generated
- ✅ **Infrastructure**: 65 satellites, 36 data centers
- ✅ **Marketing**: All campaigns live (₹425M)
- ✅ **Operations**: 7 command centers active

---

## 🆘 TROUBLESHOOTING

### Problem: Build Fails
```
Solution:
1. Check Python version (should be 3.11)
2. Verify requirements.txt exists
3. Check for syntax errors: python -m py_compile *.py
4. See Render build logs for specific error
```

### Problem: Database Connection Error
```
Solution:
1. Check DATA_DB=/app/data/data.db is set
2. SSH into Render: python scripts/seed_demo.py seed
3. Verify disk is mounted: ls -la /app/data/
4. Restart service from Render dashboard
```

### Problem: Payment Webhook Not Working
```
Solution:
1. Verify RAZORPAY_WEBHOOK_SECRET is set correctly
2. Check webhook URL: https://suresh-ai-origin.onrender.com/webhook
3. Test manually: curl -X POST with signature header
4. Check Render logs for webhook handler errors
5. Verify Razorpay webhook is enabled and pointing to correct URL
```

### Problem: Slow Performance
```
Solution:
1. Check memory usage (Render Dashboard → Metrics)
2. If >80%: Increase plan
3. Check CPU usage (should be <70% normally)
4. If spiking: Increase gunicorn workers
5. Monitor real-time metrics at /admin/metrics
```

### Problem: Cannot Login to Admin
```
Solution:
1. Verify ADMIN_PASSWORD is set (strong password)
2. Clear browser cookies/cache
3. Try incognito window
4. Check logs for authentication errors
5. Reset password in Render environment variables
6. Restart service
```

---

## 📞 SUPPORT

### Quick Reference
- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **Health Check**: GET `/health`
- **Admin Panel**: GET `/admin/login`
- **API Docs**: GET `/api/docs`

### Contact Support
- **Render Support**: https://render.com/support
- **GitHub Issues**: For bugs in code
- **Email**: admin@suresh-ai-origin.com

---

## 🎯 POST-DEPLOYMENT CHECKLIST

After deployment, verify:

- [ ] Service running on Render (green status)
- [ ] Health endpoint responding
- [ ] Admin login working
- [ ] Database migrated successfully
- [ ] Razorpay webhook configured & tested
- [ ] Email notifications working
- [ ] All feature flags enabled
- [ ] Real-time monitoring dashboard accessible
- [ ] Daily monitoring set up
- [ ] Backup scripts scheduled
- [ ] Team notified of live URL
- [ ] SSL certificate active (auto on Render)
- [ ] Logs being collected
- [ ] Performance metrics being tracked

---

## 🚀 PHASE 1 GO-LIVE STATUS

**Deployment Target**: ✅ READY

When you're ready to go live:

1. Set all environment variables in Render
2. Push code to GitHub (triggers deploy)
3. Monitor Render logs during deploy
4. Verify all endpoints responding
5. Test payment webhook
6. Announce live URL to stakeholders
7. Start Day 1 milestone tracking

**Live URL**: `https://suresh-ai-origin.onrender.com`

**Expected Uptime**: 99.95%
**Response Time**: <50ms global average
**Support**: 24/7 via Render dashboard

---

**Generated**: January 15, 2026  
**Phase**: 1 Production Deployment  
**Status**: ✅ READY FOR DEPLOYMENT

