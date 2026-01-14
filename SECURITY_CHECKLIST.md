# Security Hardening Checklist - SURESH AI ORIGIN

## 🔒 Security Audit (January 2026)

**Status:** Production Live | Phase 2 Week 3

---

## 1. Dependency Updates ✅

### Current Dependencies (Check for vulnerabilities)
```bash
# Check for outdated packages
pip list --outdated

# Security audit
pip-audit

# Update all packages
pip install -U -r requirements.txt
```

**Critical Packages to Monitor:**
- `Flask` - Web framework (security patches)
- `razorpay` - Payment gateway (API changes)
- `sqlalchemy` - Database ORM (SQL injection fixes)
- `requests` - HTTP library (SSL/TLS updates)
- `sentry-sdk` - Error tracking (privacy fixes)

**Automated Updates:** Set up Dependabot in GitHub
- `.github/dependabot.yml` → Auto-PRs for security updates

---

## 2. API Key Rotation 🔑

### Rotation Schedule
| Key Type | Current | Last Rotated | Next Rotation | Frequency |
|----------|---------|--------------|---------------|-----------|
| `ADMIN_TOKEN` | ✅ Active | Jan 14, 2026 | Apr 14, 2026 | 90 days |
| `RAZORPAY_KEY_ID` | ✅ LIVE | Jan 13, 2026 | Apr 13, 2026 | 90 days |
| `RAZORPAY_KEY_SECRET` | ✅ LIVE | Jan 13, 2026 | Apr 13, 2026 | 90 days |
| `GROQ_API_KEY` | ✅ Active | - | - | As needed |
| `FLASK_SECRET_KEY` | ✅ Active | - | - | Yearly |
| `SENTRY_DSN` (optional) | ⚠️ Not set | - | - | Never (project-based) |

### Rotation Procedure
```bash
# 1. Generate new key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Add NEW key to Render (keep old active)
ADMIN_TOKEN_NEW=<new_value>

# 3. Update GitHub secrets
ADMIN_TOKEN=<new_value>

# 4. Test with new key
curl -H "Authorization: Bearer <new_key>" https://suresh-ai-origin.onrender.com/api/admin/slow-queries

# 5. Remove old key after 24 hours (grace period)
```

**Automation Script:** `scripts/rotate_keys.py` (see below)

---

## 3. Sentry Alert Tuning 🚨

### Current Configuration
```python
# app.py
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.2,  # 20% of transactions
    )
```

### Recommended Alert Rules

**1. Error Rate Spike**
- Trigger: Error rate > 5% for 5 minutes
- Action: Email + webhook alert
- Severity: High

**2. Payment Failures**
- Trigger: 3+ payment errors in 10 minutes
- Action: Immediate email to admin
- Severity: Critical

**3. Database Errors**
- Trigger: Any database connection failure
- Action: Email + webhook
- Severity: Critical

**4. AI API Quota**
- Trigger: 429 (rate limit) responses from Groq
- Action: Email notification
- Severity: Medium

### Sentry Setup (Optional but Recommended)
1. Sign up: https://sentry.io (free tier: 5K errors/month)
2. Create project: "suresh-ai-origin"
3. Copy DSN: `https://xxx@sentry.io/xxx`
4. Add to Render: `SENTRY_DSN=<value>`
5. Configure alerts in Sentry dashboard

**Filtering Noise:**
```python
# In sentry_sdk.init()
ignore_errors=[
    KeyboardInterrupt,  # Local development interrupts
    'BrokenPipeError',  # Client disconnects
],
before_send=lambda event, hint: None if 'health' in event.get('request', {}).get('url', '') else event
```

---

## 4. Access Control Audit 🔐

### Admin Routes (Protected)
| Route | Protection | Auth Method |
|-------|-----------|-------------|
| `/admin/*` | ✅ Session + Token | `@admin_required` |
| `/api/admin/*` | ✅ Bearer Token | `ADMIN_TOKEN` |

### Session Security
```python
# app.py - Current settings
SESSION_COOKIE_HTTPONLY = True       # ✅ Prevents XSS
SESSION_COOKIE_SECURE = True         # ✅ HTTPS only
SESSION_COOKIE_SAMESITE = 'Lax'      # ✅ CSRF protection
ADMIN_SESSION_TIMEOUT = 3600         # ✅ 1-hour timeout
```

### CSRF Protection
```python
# app.py
@app.before_request
def attach_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)

@csrf_protect  # Decorator for POST routes
def admin_action():
    # Validates X-CSRF-Token header or form field
```

**Status:** ✅ Implemented

---

## 5. Database Security 🗄️

### SQLite (Current)
- ✅ File permissions: 600 (owner read/write only)
- ✅ No network exposure
- ✅ Backups encrypted at rest (Render disk encryption)

### PostgreSQL (Post-Migration)
- ✅ Connection over SSL/TLS
- ✅ Strong password (32+ chars, auto-generated)
- ✅ Internal-only network (Render private network)
- ✅ Daily backups (7-day retention)
- ⚠️ Enable `pg_stat_statements` for query monitoring

**Checklist:**
```bash
# 1. Verify SSL connection
psql $DATABASE_URL -c "SHOW ssl;"  # Should be 'on'

# 2. Check user permissions
psql $DATABASE_URL -c "\du"  # User should NOT be superuser

# 3. Enable query logging (production)
ALTER SYSTEM SET log_min_duration_statement = 1000;  # Log queries > 1s
```

---

## 6. Rate Limiting 🚦

### Current Implementation
```python
# Admin keepalive endpoint only
ADMIN_KEEPALIVE_RATE_LIMIT = 10      # 10 requests
ADMIN_KEEPALIVE_RATE_WINDOW = 60     # per 60 seconds
```

### Recommended Extensions
```python
# Add to app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"],
    storage_uri="memory://",  # Or redis://
)

# Apply to routes
@app.route('/api/ai/chat', methods=['POST'])
@limiter.limit("30 per minute")  # 30 AI requests/min per IP
def ai_chat():
    ...
```

**Install:**
```bash
pip install Flask-Limiter
```

---

## 7. Secrets Management 🔐

### Current (Render Environment Variables)
- ✅ Encrypted at rest
- ✅ Not in code/logs
- ❌ No versioning
- ❌ No audit trail

### Recommended Upgrade (Future)
- **Render Secret Files** (Paid tier) - version-controlled secrets
- **HashiCorp Vault** (Enterprise) - centralized secret management
- **AWS Secrets Manager** (If migrating to AWS)

**Current Best Practices:**
1. ✅ Never commit `.env` to git
2. ✅ Rotate keys quarterly
3. ✅ Use separate keys for test/production
4. ✅ Document key owners and rotation schedule

---

## 8. HTTPS & Headers 🌐

### Render (Auto-Configured)
- ✅ Free SSL certificate (Let's Encrypt)
- ✅ Auto-renewal
- ✅ TLS 1.2+ only
- ✅ HTTP → HTTPS redirect

### Security Headers (Via `security_middleware.py`)
```python
# Already implemented ✅
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

**Verification:**
```bash
curl -I https://suresh-ai-origin.onrender.com | grep -i "x-"
```

---

## 9. Monitoring & Alerts 📊

### Current Monitoring
- ✅ Health checks (every 6 hours via GitHub Actions)
- ✅ Slow query tracking (`SLOW_QUERY_THRESHOLD=1.0`)
- ✅ Webhook alerts (Slack/Discord)
- ✅ Email alerts (Outlook)
- ⚠️ Sentry (optional, not yet configured)

### Recommended Additions
1. **Uptime Monitor** (External)
   - UptimeRobot (free, 5 min intervals)
   - Pingdom (paid, 1 min intervals)

2. **Performance Monitoring**
   - New Relic (free tier: 100 GB/month)
   - DataDog (free trial: 14 days)

3. **Log Aggregation**
   - Papertrail (free: 50 MB/month)
   - Loggly (free: 200 MB/day)

---

## 10. Incident Response Plan 🚨

### Severity Levels
| Level | Response Time | Examples |
|-------|--------------|----------|
| **Critical** | < 15 min | Payment gateway down, data breach |
| **High** | < 1 hour | Database errors, AI service outage |
| **Medium** | < 4 hours | Slow queries, elevated error rate |
| **Low** | < 24 hours | UI bugs, non-critical warnings |

### Emergency Contacts
```
Primary: suresh.ai.origin@outlook.com
Backup: ALERT_WEBHOOK (Slack/Discord)
Escalation: Render Support (if infrastructure)
```

### Runbook
See: `OPERATIONS_GUIDE.md` → Incident Response section

---

## 11. Compliance & Privacy 🛡️

### Data Protection
- ✅ Customer emails hashed in logs
- ✅ Payment details NOT stored (Razorpay handles)
- ✅ Session tokens rotated
- ❌ GDPR data export (not yet implemented)
- ❌ Right to deletion (manual process)

### Recommended Additions
1. **Privacy Policy** (Legal requirement for EU/CA users)
2. **Terms of Service** (Payment/subscription T&Cs)
3. **Data Retention Policy** (How long to keep logs/backups)
4. **GDPR Compliance** (If targeting EU users)

**Template:** See `templates/privacy_policy.html`

---

## Security Audit Schedule

| Task | Frequency | Last Done | Next Due |
|------|-----------|-----------|----------|
| Dependency updates | Monthly | Jan 14, 2026 | Feb 14, 2026 |
| Key rotation | Quarterly | Jan 13, 2026 | Apr 13, 2026 |
| Security headers check | Monthly | Jan 14, 2026 | Feb 14, 2026 |
| Access logs review | Weekly | - | Jan 21, 2026 |
| Penetration test | Yearly | - | Dec 2026 |

---

## Quick Win Checklist (Do This Week)

- [ ] Install `pip-audit` and run security scan
- [ ] Set up Sentry DSN (free tier)
- [ ] Configure Dependabot for auto-updates
- [ ] Add UptimeRobot for external monitoring
- [ ] Document key rotation schedule
- [ ] Review and update `.gitignore` (ensure no secrets)
- [ ] Test backup restoration process

---

*Security is a continuous process, not a one-time task. Review this checklist monthly.*
