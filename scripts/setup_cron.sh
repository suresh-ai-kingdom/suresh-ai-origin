# Linux/Render Cron Setup for Automation Services
# Add these lines to your crontab (crontab -e)

# 1. Nightly backup at 2 AM UTC
0 2 * * * cd /opt/render/project/src && /opt/render/project/.venv/bin/python scripts/nightly_backup.py >> /var/log/nightly_backup.log 2>&1

# 2. Daily automations at 3 AM UTC (churn retention, payment retry, campaigns, etc.)
0 3 * * * cd /opt/render/project/src && /opt/render/project/.venv/bin/python scripts/run_daily_automations.py >> /var/log/daily_automations.log 2>&1

# 3. Health check every 5 minutes (alternative to background service)
*/5 * * * * cd /opt/render/project/src && MONITOR_ONCE=true /opt/render/project/.venv/bin/python monitor_production.py >> /var/log/health_check.log 2>&1

# For continuous monitoring (preferred), run as background service:
# nohup python scripts/monitor_service.py >> /var/log/monitor_service.log 2>&1 &

# Note: Render doesn't support cron jobs on free tier
# Use Render's cron jobs feature (paid tier) or external services like:
# - GitHub Actions scheduled workflows (free)
# - cron-job.org (free)
# - EasyCron (free tier available)
