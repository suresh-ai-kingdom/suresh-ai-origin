# GitHub Actions Setup for Automation

This repository uses GitHub Actions to run daily automations on production.

## Scheduled Tasks

- **Nightly Backup** (2 AM UTC): Creates database backup with integrity check
- **Daily Automations** (3 AM UTC): Runs all 5 workflow automations
- **Health Check** (Every 6 hours): Monitors production health

## Setup Instructions

### 1. Add Repository Secrets

Go to: **Repository Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

```
PROD_URL=https://suresh-ai-origin.onrender.com
ADMIN_TOKEN=your_admin_token_here
```

To get your `ADMIN_TOKEN`:
- Set `ADMIN_TOKEN` in Render environment variables
- Or generate one: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Add same token to both Render and GitHub secrets

### 2. Enable GitHub Actions

- Go to **Actions** tab
- If disabled, click "I understand my workflows, go ahead and enable them"
- Verify workflow appears: "Daily Automations"

### 3. Test Manually

- Go to **Actions** → **Daily Automations** → **Run workflow**
- Select task: `health`, `backup`, `automations`, or `all`
- Click **Run workflow**
- Check logs for success/failure

### 4. Monitor Runs

- **Actions** tab shows all runs
- Click any run to see detailed logs
- Failed runs appear in red and can trigger notifications
- Configure notifications: **Settings** → **Notifications** → **Actions**

## Workflow Details

### Nightly Backup
- Endpoint: `POST /api/admin/trigger-backup`
- Auth: Bearer token (ADMIN_TOKEN)
- Creates timestamped backup
- Runs SQLite integrity check
- Sends webhook/email alerts on failure

### Daily Automations
- Endpoint: `POST /api/admin/trigger-automations`
- Auth: Bearer token (ADMIN_TOKEN)
- Executes 5 workflows:
  1. Churn retention: Offers for at-risk customers
  2. Payment retry: Email reminders for unpaid orders
  3. Segment campaigns: Auto-campaigns for VIP/LOYAL
  4. Voice support: Escalate negative feedback
  5. Social content: Schedule posts for trending products

### Health Check
- Endpoint: `GET /health`
- Public endpoint (no auth)
- Checks database connectivity
- Reports slow query stats
- Fails workflow if unhealthy

## Troubleshooting

### "Repository secret not found"
- Verify `PROD_URL` and `ADMIN_TOKEN` are added in repository secrets
- Secret names are case-sensitive

### "401 Unauthorized"
- Check `ADMIN_TOKEN` matches between GitHub secrets and Render environment
- Test manually: `curl -X POST $PROD_URL/api/admin/trigger-backup -H "Authorization: Bearer $TOKEN"`

### "Connection refused" or "504 Gateway Timeout"
- Render free tier spins down after 15 minutes of inactivity
- First request may take 30-60 seconds to wake up
- Consider upgrading to paid tier or use external uptime monitor

### Workflow not running on schedule
- Check workflow is enabled: **Actions** → **Daily Automations** → **Enable workflow**
- GitHub Actions may have a few minutes delay (typically < 5 minutes)
- Manual trigger works but scheduled doesn't: Check repository is not archived

## Cost

GitHub Actions is **FREE** for public repositories (unlimited minutes).

For private repositories:
- Free: 2,000 minutes/month
- Each workflow run takes < 1 minute
- Daily automations use ~90 minutes/month (well within free tier)

---

**Need help?** Check workflow logs in Actions tab or review [OPERATIONS_GUIDE.md](../OPERATIONS_GUIDE.md)
