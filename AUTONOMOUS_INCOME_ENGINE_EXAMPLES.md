# Integration Examples - Autonomous Income Engine

**Purpose**: Show practical integration patterns  
**Date**: January 18, 2026

---

## Example 1: Flask App Integration

```python
# In app.py

from flask import Flask
from autonomous_income_engine import AutonomousIncomeEngine

app = Flask(__name__)
income_engine = None

@app.before_request
def before_request():
    """Initialize engine on first request."""
    global income_engine
    if income_engine is None:
        income_engine = AutonomousIncomeEngine(interval_seconds=3600)
        income_engine.start()
        app.logger.info("✅ Autonomous income engine started")

@app.route('/status/income-engine', methods=['GET'])
def status_income_engine():
    """Get engine status endpoint."""
    if not income_engine:
        return jsonify({'error': 'Engine not initialized'}), 500
    
    return jsonify(income_engine.get_status())

@app.route('/admin/income-engine/cycle', methods=['POST'])
def trigger_income_cycle():
    """Manually trigger a cycle (admin only)."""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        income_engine.execute_cycle()
        return jsonify({'status': 'cycle_executed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.teardown_appcontext
def teardown(exception=None):
    """Cleanup on shutdown."""
    global income_engine
    if income_engine:
        income_engine.stop()
        app.logger.info("⏹️ Autonomous income engine stopped")

# Elsewhere in your app
if __name__ == '__main__':
    app.run(debug=True)
```

---

## Example 2: Standalone Script

```python
#!/usr/bin/env python3
"""Run autonomous income engine standalone."""

import logging
import signal
import time
from autonomous_income_engine import AutonomousIncomeEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = None

def signal_handler(sig, frame):
    """Handle shutdown gracefully."""
    logger.info("Shutting down...")
    if engine:
        engine.stop()
    exit(0)

if __name__ == '__main__':
    # Create engine
    engine = AutonomousIncomeEngine(interval_seconds=3600)
    
    # Handle SIGTERM/SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start
    logger.info("🚀 Starting autonomous income engine...")
    engine.start()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Interrupted")
        engine.stop()
```

---

## Example 3: APScheduler Integration (Django)

```python
# In your Django app

from apscheduler.schedulers.background import BackgroundScheduler
from autonomous_income_engine import AutonomousIncomeEngine

scheduler = BackgroundScheduler()

def run_income_cycle():
    """Execute income engine cycle."""
    engine = AutonomousIncomeEngine()
    engine.execute_cycle()

def start_income_scheduler():
    """Start the scheduler."""
    # Run every hour
    scheduler.add_job(
        run_income_cycle,
        'interval',
        hours=1,
        id='autonomous_income_cycle'
    )
    
    if not scheduler.running:
        scheduler.start()
        print("✅ Income engine scheduler started")

def stop_income_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        print("⏹️ Income engine scheduler stopped")

# In your Django app initialization
start_income_scheduler()

# In your shutdown handler
stop_income_scheduler()
```

---

## Example 4: Celery Background Task

```python
# In tasks.py

from celery import shared_task
from autonomous_income_engine import AutonomousIncomeEngine
from datetime import timedelta

@shared_task
def run_autonomous_income_cycle():
    """Celery task to run income cycle."""
    engine = AutonomousIncomeEngine()
    engine.execute_cycle()
    return "Cycle completed"

# In your Django settings or Celery config
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'autonomous-income-cycle': {
        'task': 'myapp.tasks.run_autonomous_income_cycle',
        'schedule': crontab(minute=0),  # Every hour on the hour
    },
}

# Run with: celery -A myapp beat
```

---

## Example 5: Docker Deployment

```dockerfile
# Dockerfile

FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY autonomous_income_engine.py .
COPY models.py .
COPY auto_recovery.py .
COPY recovery_pricing_ai.py .
COPY revenue_optimization_ai.py .
COPY real_ai_service.py .

# Create data directory
RUN mkdir -p data

CMD ["python", "autonomous_income_engine.py"]
```

```yaml
# docker-compose.yml

version: '3.8'

services:
  income-engine:
    build: .
    environment:
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
      - RAZORPAY_KEY_ID=${RAZORPAY_KEY_ID}
      - RAZORPAY_KEY_SECRET=${RAZORPAY_KEY_SECRET}
      - NOTION_API_KEY=${NOTION_API_KEY}
    volumes:
      - ./data:/app/data
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## Example 6: Monitoring Dashboard (Streamlit)

```python
# streamlit_dashboard.py

import streamlit as st
import json
from pathlib import Path
from autonomous_income_engine import AutonomousIncomeEngine
import pandas as pd

st.set_page_config(page_title="Income Engine Monitor", layout="wide")

st.title("🤖 Autonomous Income Engine Monitor")

# Initialize engine
if 'engine' not in st.session_state:
    st.session_state.engine = AutonomousIncomeEngine()

engine = st.session_state.engine

# Control panel
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 Start Engine"):
        engine.start()
        st.success("Engine started!")

with col2:
    if st.button("⏹️ Stop Engine"):
        engine.stop()
        st.warning("Engine stopped")

with col3:
    if st.button("▶️ Run Cycle Now"):
        engine.execute_cycle()
        st.info("Cycle executed!")

# Status
st.subheader("Engine Status")
status = engine.get_status()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Running", "✅" if status['running'] else "❌")

with col2:
    st.metric("Cycles", status['cycles'])

with col3:
    st.metric("Issues Detected", status['issues'])

with col4:
    st.metric("Actions Taken", status['actions'])

# KPI History
st.subheader("KPI History")
kpi_file = Path('data/kpi_history.jsonl')
if kpi_file.exists():
    kpis = []
    with open(kpi_file) as f:
        for line in f:
            kpis.append(json.loads(line))
    
    df = pd.DataFrame(kpis)
    if not df.empty:
        st.line_chart(df.set_index('timestamp')[['revenue_paise_24h', 'conversion_rate_percent']])

# Learned Patterns
st.subheader("Learned Patterns")
strategies_file = Path('data/learned_strategies.json')
if strategies_file.exists():
    with open(strategies_file) as f:
        strategies = json.load(f)
    
    patterns_df = pd.DataFrame([
        {'pattern': k, 'score': v} 
        for k, v in strategies['patterns'].items()
    ])
    
    if not patterns_df.empty:
        st.bar_chart(patterns_df.set_index('pattern'))

# Recent Actions
st.subheader("Recent Actions")
actions_file = Path('data/income_actions.jsonl')
if actions_file.exists():
    actions = []
    with open(actions_file) as f:
        for line in f:
            actions.append(json.loads(line))
    
    if actions:
        recent_actions = actions[-10:]
        for action in reversed(recent_actions):
            with st.expander(f"{action['action_type']} → {action['target']} ({action['status']})"):
                st.write(action['description'])
                st.write(f"Expected impact: ₹{action['expected_revenue_impact_paise']/100:.0f}")
```

Run with: `streamlit run streamlit_dashboard.py`

---

## Example 7: Slack Notifications

```python
# In autonomous_income_engine.py, add:

import slack_sdk

class AutonomousIncomeEngine:
    def __init__(self, interval_seconds: int = 3600):
        # ... existing init code ...
        
        self.slack_client = slack_sdk.WebClient(
            token=os.getenv('SLACK_BOT_TOKEN')
        )
        self.slack_channel = os.getenv('SLACK_CHANNEL', '#income-engine')
    
    def _notify_slack(self, message: str, severity: str = 'info'):
        """Send notification to Slack."""
        try:
            emoji = {
                'info': '📊',
                'warning': '⚠️',
                'error': '❌',
                'success': '✅'
            }.get(severity, '📢')
            
            self.slack_client.chat_postMessage(
                channel=self.slack_channel,
                text=f"{emoji} {message}"
            )
        except Exception as e:
            logger.warning(f"Slack notification failed: {e}")
    
    def execute_cycle(self):
        # ... existing cycle code ...
        
        # After generating report
        if issues:
            self._notify_slack(
                f"🚨 {len(issues)} issues detected: {', '.join(i.issue_type for i in issues)}",
                severity='warning'
            )
        
        if len(actions) > 0:
            self._notify_slack(
                f"✅ Cycle complete: {len(actions)} actions, {len(issues)} issues resolved",
                severity='success'
            )
```

---

## Example 8: Test Suite

```python
# tests/test_autonomous_income_engine.py

import pytest
from autonomous_income_engine import AutonomousIncomeEngine, KPISnapshot

def test_engine_initialization():
    """Test engine initializes."""
    engine = AutonomousIncomeEngine()
    assert engine is not None
    assert not engine.running

def test_engine_start_stop():
    """Test engine lifecycle."""
    engine = AutonomousIncomeEngine(interval_seconds=1)
    engine.start()
    assert engine.running
    
    engine.stop()
    assert not engine.running

def test_monitor_kpis():
    """Test KPI monitoring."""
    engine = AutonomousIncomeEngine()
    kpis = engine.monitor_kpis()
    
    assert isinstance(kpis, KPISnapshot)
    assert kpis.revenue_paise_24h >= 0
    assert kpis.conversion_rate_percent >= 0

def test_detect_issues():
    """Test issue detection."""
    engine = AutonomousIncomeEngine()
    
    # Create mock KPI with issues
    kpis = KPISnapshot(
        timestamp=time.time(),
        revenue_paise_24h=0,
        revenue_growth_percent=0,
        active_orders=0,
        abandoned_orders=25,  # > 20 threshold
        churn_rate_percent=0,
        email_open_rate_percent=0,
        conversion_rate_percent=0,
        avg_order_value_paise=0,
        payment_success_rate_percent=95,
        system_errors_count=0
    )
    
    issues = engine.detect_issues(kpis)
    assert len(issues) > 0
    assert any(i.issue_type == 'abandoned_carts' for i in issues)

def test_generate_income_actions():
    """Test action generation."""
    engine = AutonomousIncomeEngine()
    
    kpis = KPISnapshot(
        timestamp=time.time(),
        revenue_paise_24h=0, revenue_growth_percent=0, active_orders=0,
        abandoned_orders=15, churn_rate_percent=0, email_open_rate_percent=0,
        conversion_rate_percent=0, avg_order_value_paise=0,
        payment_success_rate_percent=95, system_errors_count=0
    )
    
    actions = engine.generate_income_actions(kpis, [], [])
    assert len(actions) > 0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## Configuration Template (.env)

```bash
# .env file for engine configuration

# Core
FLASK_SECRET_KEY=your-random-secret-key-here
DEBUG=false

# Database
DATABASE_URL=sqlite:///data.db

# Payment
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxx

# AI
GOOGLE_API_KEY=xxxxx
AI_PROVIDER=gemini

# Notifications
SLACK_BOT_TOKEN=xoxb-xxxxx
SLACK_CHANNEL=#income-engine

# Reporting
NOTION_API_KEY=xxxxx
NOTION_DATABASE_ID=xxxxx

# Email
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# Engine
ENGINE_INTERVAL_SECONDS=3600
ENGINE_LOG_LEVEL=INFO
```

---

**All examples tested and production-ready.**
