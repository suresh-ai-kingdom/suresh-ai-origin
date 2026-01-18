# Autonomous Business Agent - Complete Guide

## Overview

**AutonomousBusinessAgent** is a self-operating AI for SURESH AI ORIGIN that monitors revenue/leads, auto-generates content, deploys fixes, and makes autonomous business decisions.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 AUTONOMOUS BUSINESS AGENT                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │  DATA SOURCES    │  │  AI DECISION    │  │  ACTIONS   │ │
│  ├──────────────────┤  ├─────────────────┤  ├────────────┤ │
│  │ • Stripe API     │──│ • Analyze       │──│ • Content  │ │
│  │ • Google Sheets  │  │ • Decide        │  │ • Deploy   │ │
│  │ • Analytics API  │  │ • Execute       │  │ • Email    │ │
│  │ • Health Checks  │  │ • Learn         │  │ • Alert    │ │
│  └──────────────────┘  └─────────────────┘  └────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SAFETY GUARDRAILS                                   │   │
│  │  • Budget limits  • Risk thresholds  • Approval     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Core Features

### 1. Revenue & Leads Monitoring
- **Stripe Integration**: Real-time revenue tracking
- **Google Sheets**: Lead capture monitoring
- **Analytics API**: Platform metrics aggregation
- **Health Checks**: System uptime and error rates

### 2. Auto-Content Generation
- Triggers when leads < threshold (default: 10/day)
- Uses Claude API via `generate_ai_content()`
- Generates LinkedIn/Reels viral content
- Sends to admin email for review/posting
- Includes business context and metrics

### 3. GitHub Actions Auto-Deploy
- Triggers when error_rate > threshold (default: 5%)
- Calls GitHub Actions `workflow_dispatch`
- Deploys fixes automatically
- Sends deployment alerts

### 4. Self-Recovery
- Retry logic via `tenacity` (3 attempts, exponential backoff)
- WhatsApp/Email alerts on failures
- JSONL logging (`data/agent_*.jsonl`)
- Automatic error recovery

### 5. Autonomous Decision Making
- Reinforcement learning from outcomes
- Multi-objective optimization (revenue, satisfaction, growth)
- Explainable decisions with reasoning chains
- Confidence-based execution (CRITICAL, HIGH, MEDIUM, LOW)

## Installation

```bash
# Install dependencies
pip install schedule tenacity requests

# Environment variables (add to Render dashboard)
AGENT_LEADS_THRESHOLD=10
AGENT_REVENUE_THRESHOLD=1000.0
AGENT_ERROR_RATE=0.05

# Optional integrations
STRIPE_API_KEY=sk_live_...
GITHUB_TOKEN=ghp_...
GITHUB_REPO=suresh-ai-kingdom/suresh-ai-origin
ADMIN_EMAIL=admin@sureshaiorigin.com
WHATSAPP_API_KEY=...
NOTION_API_KEY=...
```

## Usage

### Run Continuous Monitoring (Production)

```bash
# Every hour monitoring
python autonomous_business_agent.py --interval 3600

# Custom base URL + interval
python autonomous_business_agent.py --base-url https://sureshaiorigin.com --interval 1800

# Run as background daemon
python autonomous_business_agent.py --daemon
```

### One-Time Check (Testing)

```bash
# Run single monitoring cycle and exit
python autonomous_business_agent.py --once

# Test specific decision
python autonomous_business_agent.py --once --base-url http://localhost:5000
```

### API Usage (Programmatic)

```python
from autonomous_business_agent import autonomous_agent, agent_make_decision

# Initialize agent
autonomous_agent.base_url = "https://sureshaiorigin.com"

# Make decision
business_context = {
    'revenue_today': 500.0,
    'leads_today': 5,
    'error_rate': 0.02,
    'mrr': 50000.0,
    'active_subscriptions': 10
}

decision = agent_make_decision(business_context)
print(f"Decision: {decision['action_type']} (confidence: {decision['confidence']})")
print(f"Reasoning: {decision['reasoning']}")
```

## Monitoring Cycle

Every interval (default: 1 hour):

1. **Collect Metrics** from all sources:
   - Internal analytics API (`/api/analytics/daily-summary`)
   - Stripe charges (today's revenue)
   - Google Sheets leads (if configured)
   - Health check endpoints

2. **Analyze Situation**:
   - Compare metrics to thresholds
   - Calculate risk scores
   - Identify trends and anomalies

3. **Make Decision**:
   - Use reinforcement learning policy
   - Generate confidence score
   - Create reasoning chain

4. **Execute Actions** (if confidence ≥ HIGH):
   - `CONTENT_GENERATION`: Generate LinkedIn/Reels content
   - `DEPLOY_FIX`: Trigger GitHub Actions deployment
   - `EMAIL_CAMPAIGN`: Send alert emails
   - Other autonomous actions per config

5. **Log & Learn**:
   - Write to JSONL files (`data/agent_*.jsonl`)
   - Update learning buffer
   - Adjust policy weights based on outcomes

## Decision Types

| Action Type | Trigger | Confidence Required | Example |
|------------|---------|---------------------|---------|
| `CONTENT_GENERATION` | leads < 10/day | HIGH | Generate viral LinkedIn post |
| `DEPLOY_FIX` | error_rate > 5% | CRITICAL | Auto-deploy fix via GitHub |
| `EMAIL_CAMPAIGN` | revenue < ₹1000/day | MEDIUM | Send alert to admin |
| `PRICING_ADJUSTMENT` | conversion < target | LOW | Suggest price change |
| `FEATURE_TOGGLE` | error in feature | HIGH | Disable problematic feature |

## Safety Guardrails

### Budget Limits
```python
safety_limits = {
    'max_daily_spend': 10000.0,  # ₹10k max/day
    'max_discount': 0.5,          # 50% max discount
    'max_refund': 5000.0          # ₹5k max refund
}
```

### Risk Thresholds
- **Critical**: 0-20 (execute immediately)
- **High**: 21-40 (execute with logging)
- **Medium**: 41-70 (suggest to human)
- **Low**: 71-100 (requires approval)

### Approval Required
- All `PRODUCT_LAUNCH` decisions
- `PRICING_ADJUSTMENT` > ±20%
- `REFUND_APPROVAL` > ₹5,000

## Logs & Analytics

### JSONL Files

```bash
# Metrics log (every cycle)
data/agent_metrics.jsonl
{
  "timestamp": 1705612800.0,
  "revenue_today": 2500.0,
  "leads_today": 15,
  "error_rate": 0.01,
  "active_subscriptions": 20,
  "mrr": 100000.0
}

# Actions log (every action)
data/agent_actions.jsonl
{
  "timestamp": 1705612800.0,
  "action_type": "content_generated",
  "details": {"reason": "low_leads", "content_length": 250},
  "success": true
}

# Alerts log (on failures/warnings)
data/agent_alerts.jsonl
{
  "timestamp": 1705612800.0,
  "title": "Low Revenue Alert",
  "message": "Revenue ₹500 below target ₹1000",
  "metrics": {...}
}
```

### Query Logs

```bash
# View recent metrics
tail -n 10 data/agent_metrics.jsonl | jq .

# Count successful actions today
grep "$(date +%Y-%m-%d)" data/agent_actions.jsonl | jq 'select(.success==true)' | wc -l

# View all alerts
jq . data/agent_alerts.jsonl
```

## Content Generation

### Prompt Template

```
Generate a viral LinkedIn post for Suresh AI Origin.

Context: low_leads
Metrics: 5 leads, ₹500 revenue today

Requirements:
1. Hook in first line (curiosity-driven)
2. Highlight god-tier rare features
3. Social proof (48 AI systems, 99.95% uptime)
4. CTA: https://sureshaiorigin.com
5. Bold, confident tone
6. 150-250 words
```

### Example Generated Content

```
🚀 Here's why 99% of businesses will fail in 2026...

They're still doing manual work while AI is eating the world.

We built SURESH AI ORIGIN - 48 AI systems that run your business on autopilot.

→ Destiny Blueprint: Your exact path to ₹10L/month
→ Business Consciousness: Multi-industry AI brain
→ Perfect Timing: Never make wrong decisions again

99.95% uptime. Zero manual work.

Join the top 1%: https://sureshaiorigin.com

The future doesn't wait.
```

## GitHub Actions Integration

### Workflow Dispatch

```yaml
# .github/workflows/deploy.yml
name: Auto-Deploy
on:
  workflow_dispatch:
    inputs:
      reason:
        required: true
      triggered_by:
        required: true
      error_rate:
        required: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        run: |
          echo "Deploying due to: ${{ github.event.inputs.reason }}"
          # Render auto-deploys on push, or use API
```

### Trigger from Agent

```python
# In autonomous_business_agent.py
resp = requests.post(
    f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/deploy.yml/dispatches",
    headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
    json={
        "ref": "main",
        "inputs": {
            "reason": "high_error_rate",
            "triggered_by": "autonomous_agent",
            "error_rate": "0.10"
        }
    }
)
```

## Testing

```bash
# Run all tests
pytest tests/test_autonomous_agent.py -v

# Test specific functionality
pytest tests/test_autonomous_agent.py::test_generate_content -v
pytest tests/test_autonomous_agent.py::test_deploy_update -v
pytest tests/test_autonomous_agent.py::test_monitor_metrics -v
```

## Production Deployment

### Render.com (Web Service)

```yaml
# render.yaml
services:
  - type: cron
    name: autonomous-agent
    env: python
    schedule: "0 * * * *"  # Every hour
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python autonomous_business_agent.py --once --base-url $RENDER_EXTERNAL_URL"
    envVars:
      - key: AGENT_LEADS_THRESHOLD
        value: 10
      - key: STRIPE_API_KEY
        sync: false
      - key: GITHUB_TOKEN
        sync: false
```

### Systemd (Linux Server)

```ini
# /etc/systemd/system/autonomous-agent.service
[Unit]
Description=Autonomous Business Agent
After=network.target

[Service]
Type=simple
User=suresh
WorkingDirectory=/opt/suresh-ai-origin
ExecStart=/opt/suresh-ai-origin/.venv/bin/python autonomous_business_agent.py --daemon
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl enable autonomous-agent
sudo systemctl start autonomous-agent
sudo systemctl status autonomous-agent

# View logs
sudo journalctl -u autonomous-agent -f
```

## Troubleshooting

### Issue: No metrics collected

**Cause**: API endpoint not reachable or returning errors

**Solution**:
```bash
# Test API endpoint
curl https://sureshaiorigin.com/api/analytics/daily-summary

# Check agent logs
tail -f data/agent_metrics.jsonl
```

### Issue: Content generation fails

**Cause**: `generate_ai_content()` not available or AI provider down

**Solution**:
```python
# Test AI service manually
from real_ai_service import generate_ai_content
result = generate_ai_content("Test prompt")
print(result)
```

### Issue: GitHub Actions not triggering

**Cause**: Invalid GITHUB_TOKEN or workflow name mismatch

**Solution**:
```bash
# Verify token permissions (needs `workflow` scope)
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/suresh-ai-kingdom/suresh-ai-origin/actions/workflows

# Check workflow name matches (deploy.yml)
```

## Advanced Configuration

### Custom Decision Policy

```python
# Override policy weights for specific actions
autonomous_agent.policy_weights = {
    ActionType.CONTENT_GENERATION: 0.8,
    ActionType.DEPLOY_FIX: 0.6,
    ActionType.EMAIL_CAMPAIGN: 0.4,
    # ... other actions
}
```

### Custom Thresholds

```python
# Adjust per environment
if os.getenv('ENVIRONMENT') == 'staging':
    agent.leads_threshold = 5
    agent.revenue_threshold = 500.0
    agent.error_threshold = 0.10
```

### Disable Autonomous Mode

```python
# Require human approval for all decisions
autonomous_agent.config['autonomous_mode'] = False

# Agent will only suggest, not execute
decision = autonomous_agent.make_decision(context)
print(f"Suggestion: {decision.action_type.value}")
print(f"Execute? (y/n): ", end='')
```

## API Reference

### Core Methods

#### `__init__(config, base_url)`
Initialize agent with config and API base URL.

#### `run_loop(interval_seconds)`
Run continuous monitoring loop.

#### `monitor_metrics() -> Dict`
Collect metrics from all sources (Stripe, Sheets, Analytics).

#### `make_decision(context) -> Decision`
Analyze context and make autonomous decision with confidence.

#### `execute_decision(decision_id)`
Execute a decision by ID.

#### `generate_content(reason, metrics)`
Generate LinkedIn/Reels content via Claude.

#### `deploy_update(reason, metrics)`
Trigger GitHub Actions deployment.

### Data Classes

#### `Decision`
```python
@dataclass
class Decision:
    decision_id: str
    action_type: ActionType
    confidence: DecisionConfidence
    reasoning: str
    expected_impact: Dict[str, float]
    risk_score: float
    parameters: Dict[str, Any]
    created_at: float
    executed_at: Optional[float]
    outcome: Optional[Dict]
    success: Optional[bool]
```

#### `LearningExperience`
```python
@dataclass
class LearningExperience:
    state: Dict[str, Any]
    action: ActionType
    reward: float
    next_state: Dict[str, Any]
    timestamp: float
    meta: Dict[str, Any]
```

## Roadmap

- [ ] **Google Sheets Integration**: Automated lead import
- [ ] **WhatsApp Alerts**: Real-time notifications via WhatsApp API
- [ ] **Notion Logging**: Push logs to Notion database
- [ ] **A/B Testing**: Auto-generate and run split tests
- [ ] **Customer Intervention**: Automated support responses
- [ ] **Predictive Scaling**: Auto-adjust resources based on traffic
- [ ] **Voice Alerts**: Call admin on critical issues

## Security Notes

⚠️ **IMPORTANT**:
- Store all API keys in environment variables (Render dashboard)
- Never commit `.env` with real keys to git
- Use read-only Stripe keys where possible
- Set budget limits in `safety_limits`
- Review generated content before posting
- Monitor agent actions daily via JSONL logs
- Set `autonomous_mode=false` for testing

## Support

- **Docs**: [docs/AUTONOMOUS_AGENT_GUIDE.md](./AUTONOMOUS_AGENT_GUIDE.md)
- **Tests**: [tests/test_autonomous_agent.py](../tests/test_autonomous_agent.py)
- **Source**: [autonomous_business_agent.py](../autonomous_business_agent.py)
- **Issues**: GitHub Issues tab

---

**Built for SURESH AI ORIGIN** - Top 1% AI Automation Platform  
Version: 2.5.0 | Last Updated: Jan 18, 2026
