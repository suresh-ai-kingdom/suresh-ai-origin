# Production Operations Guide - SURESH AI ORIGIN

## 🚀 Quick Start Commands

### Deployment
```bash
# Deploy to production (Render auto-deploys from main branch)
git add .
git commit -m "Description"
git push origin main

# Manual deploy trigger in Render dashboard
# Dashboard → suresh-ai-origin → Manual Deploy → Deploy latest commit
```

### Monitoring
```bash
# Run health check once
python monitor_production.py

# Continuous monitoring (5-minute intervals)
python monitor_production.py  # Press Ctrl+C to stop

# Check specific endpoint
curl https://suresh-ai-origin.onrender.com/health
```

### Database Backups
```bash
# Create manual backup
python backup_manager.py create manual

# Create automatic backup (with cleanup)
python backup_manager.py auto

# List all backups
python backup_manager.py list

# Restore from backup
python backup_manager.py restore backups/backup_manual_20260114_001418.db

# Clean up old backups (30+ days)
python backup_manager.py cleanup
```

### Performance
```bash
# Optimize database (create indexes)
python performance.py optimize

# Check system health
python comprehensive_health_check.py
```

---

## 📊 Production URLs

| Service | URL |
|---------|-----|
| **Production Site** | https://suresh-ai-origin.onrender.com |
| **Health Check** | https://suresh-ai-origin.onrender.com/health |
| **Admin Dashboard** | https://suresh-ai-origin.onrender.com/admin |
| **AI Chat** | https://suresh-ai-origin.onrender.com/api/ai/chat |
| **Render Dashboard** | https://dashboard.render.com |

---

## 🔐 Environment Variables

### Critical (Must Be Set in Render)
- `GROQ_API_KEY` - Groq AI authentication
- `AI_PROVIDER=groq` - AI provider selection
- `AI_MODEL=llama-3.3-70b-versatile` - Model configuration
- `RAZORPAY_KEY_ID` - Payment gateway (LIVE keys)
- `RAZORPAY_KEY_SECRET` - Payment secret
- `RAZORPAY_WEBHOOK_SECRET` - Webhook verification
- `ADMIN_PASSWORD_HASH` - Admin authentication (takes precedence)
- `FLASK_SECRET_KEY` - Session encryption

### Optional
- `ADMIN_USERNAME=admin` - Admin username
- `ADMIN_PASSWORD` - Fallback plain password
- `EMAIL_USER` - Email notifications
- `EMAIL_PASS` - Email app password
- `MONITOR_INTERVAL=300` - Health check interval (seconds)
- `ALERT_EMAIL` - Alert destination email

---

## 🔧 Common Operations

### Add New Feature
1. Develop and test locally: `FLASK_DEBUG=1 python app.py`
2. Add tests: `pytest tests/test_new_feature.py -v`
3. Update documentation in `.github/copilot-instructions.md`
4. Commit and push: `git push origin main`
5. Verify deployment: `python comprehensive_health_check.py`

### Update AI Provider
1. Change env vars in Render: `AI_PROVIDER`, `AI_MODEL`, `[PROVIDER]_API_KEY`
2. Trigger manual deploy
3. Test AI endpoint: `curl -X POST .../api/ai/chat -d '{"message":"test"}'`
4. Monitor for errors: `python monitor_production.py`

### Database Migration
```bash
# Create migration
PYTHONPATH=. alembic revision -m "Description"

# Apply migration locally
PYTHONPATH=. alembic upgrade head

# Deploy (Render runs migrations automatically via render.yaml)
git push origin main
```

### Emergency Rollback
```bash
# In Render dashboard:
# 1. Go to Events → Find previous successful deploy
# 2. Click "Redeploy" on that event
# OR restore database:
python backup_manager.py list
python backup_manager.py restore backups/[backup_file].db
```

---

## 🚨 Incident Response

### Site Down (500 errors)
1. Check Render logs: Dashboard → Logs → Last 100 lines
2. Check health endpoint: `curl .../health`
3. Check database: `python backup_manager.py verify`
4. If database corrupt: Restore from backup
5. If code issue: Rollback deployment in Render

### AI Not Responding
1. Check Groq API status: https://status.groq.com
2. Test endpoint: `curl -X POST .../api/ai/chat -d '{"message":"test"}'`
3. Check API key in Render environment
4. Check quota: Monitor response times
5. Fallback: Switch to OpenAI (update `AI_PROVIDER`)

### Payment Issues
1. Check Razorpay dashboard: https://dashboard.razorpay.com
2. Verify webhook events: `/admin/webhooks`
3. Check keys haven't expired: Render environment
4. Test webhook signature verification
5. Check order status: `/admin/orders`

### Database Locked
1. Restart service in Render dashboard
2. If persists: `rm data.db && restore from backup`
3. Consider PostgreSQL migration for high concurrency

### High Error Rate
1. Check monitoring: `python monitor_production.py`
2. Review Render logs for patterns
3. Check rate limiting not blocking legitimate users
4. Scale up service if needed (Render dashboard → Scaling)

---

## 📈 Scaling Checklist

### Current Setup (Free Tier)
- Instance: 512 MB RAM, 0.1 CPU
- Database: SQLite (single file)
- Concurrent users: ~10-20
- Groq AI: 60 requests/minute

### When to Scale

#### Upgrade to Paid Tier (Render)
**Trigger**: Response times > 3s consistently
- [ ] Upgrade to $7/month plan (512 MB → 1 GB RAM)
- [ ] Enable auto-scaling if available

#### Migrate to PostgreSQL
**Trigger**: Database locked errors or > 100 concurrent users
- [ ] Create PostgreSQL instance in Render
- [ ] Update DATABASE_URL in environment
- [ ] Migrate data: `pg_dump` and restore
- [ ] Update `utils.py` to use PostgreSQL connection

#### Add Redis Caching
**Trigger**: Same data queried frequently
- [ ] Add Redis instance
- [ ] Update `performance.py` to use Redis instead of in-memory cache
- [ ] Cache AI responses (5-minute TTL)
- [ ] Cache analytics queries (1-hour TTL)

#### CDN for Static Assets
**Trigger**: Users in multiple regions
- [ ] Set up Cloudflare (free tier)
- [ ] Configure DNS to point through Cloudflare
- [ ] Enable caching rules

---

## 🧪 Testing in Production

### Safe Testing (Non-Destructive)
```bash
# Health check
curl https://suresh-ai-origin.onrender.com/health

# AI generation (public endpoint)
curl -X POST https://suresh-ai-origin.onrender.com/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Analytics (read-only)
curl https://suresh-ai-origin.onrender.com/api/analytics/daily-revenue
```

### Risky Testing (Use Caution)
```bash
# Create test order (uses LIVE Razorpay!)
# DO NOT DO THIS unless you want real charges

# Test webhook (requires valid signature)
# Only test with Razorpay test mode enabled
```

---

## 📝 Logging

### View Logs
- **Render Dashboard**: Logs tab (real-time)
- **Local**: Check terminal output
- **Structured Logging**: All requests have `request_id` for tracing

### Log Levels
- `INFO`: Normal operations
- `WARNING`: Recoverable issues (rate limit, validation failures)
- `ERROR`: Failures (payment errors, API failures)
- `CRITICAL`: System failures (database down, critical service unavailable)

---

## 🔒 Security Best Practices

### API Keys
- [ ] Never commit to git (use `.env` for local, Render for prod)
- [ ] Rotate every 90 days
- [ ] Use different keys for test/live environments
- [ ] Monitor GitHub for accidental leaks

### Admin Access
- [ ] Use strong passwords (20+ chars, mixed case, symbols)
- [ ] Enable 2FA on Render account
- [ ] Regularly review admin logs
- [ ] Limit admin access to specific IPs if possible

### Payment Security
- [ ] Always verify webhook signatures
- [ ] Never log full credit card numbers
- [ ] Use HTTPS only (enforced by Render)
- [ ] Implement idempotency for webhook handlers

---

## 📞 Support Contacts

| Service | Contact |
|---------|---------|
| **Render Support** | https://render.com/support |
| **Groq Support** | https://groq.com/support |
| **Razorpay Support** | support@razorpay.com |
| **GitHub Issues** | Repository Issues tab |

---

## 🎯 Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Response Time | < 500ms | ~300ms | ✅ |
| Uptime | > 99% | TBD | 🔄 |
| AI Response | < 3s | ~1.4s | ✅ |
| Error Rate | < 1% | ~0% | ✅ |
| Health Score | > 90% | 92% | ✅ |

---

## 📅 Maintenance Schedule

### Daily
- [ ] Monitor health check results
- [ ] Review error logs (if any)
- [ ] Check Groq API quota usage

### Weekly
- [ ] Create manual backup
- [ ] Review Razorpay transactions
- [ ] Check disk space usage
- [ ] Review response times

### Monthly
- [ ] Rotate API keys (if policy requires)
- [ ] Review and clean old backups
- [ ] Update dependencies (`pip install -U -r requirements.txt`)
- [ ] Performance audit

### Quarterly
- [ ] Security audit
- [ ] Cost optimization review
- [ ] Capacity planning
- [ ] Disaster recovery test

---

*Last updated: January 14, 2026*
