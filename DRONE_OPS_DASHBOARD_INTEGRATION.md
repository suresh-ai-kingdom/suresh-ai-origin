# 🚁 Drone Operations Dashboard - Integration & Usage Guide

**Version**: 1.0  
**Last Updated**: January 19, 2026

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Python API Usage](#python-api-usage)
3. [Flask Integration](#flask-integration)
4. [Data Integration Patterns](#data-integration-patterns)
5. [Advanced Customization](#advanced-customization)
6. [Monitoring & Alerts](#monitoring--alerts)

---

## 🚀 Quick Start

### Installation

```bash
# Install all dependencies
pip install flask folium scikit-learn numpy

# Create data directory
mkdir -p data logs

# Run dashboard
python drone_ops_dashboard.py
```

### Access Dashboard

```
Web UI:        http://localhost:5000
API Endpoints: http://localhost:5000/api/*
Health Check:  http://localhost:5000/health
```

---

## 🐍 Python API Usage

### Basic Usage

```python
from drone_ops_dashboard import DroneOpsDashboard

# Initialize dashboard
dashboard = DroneOpsDashboard(data_dir="data", logs_dir="logs")

# Get KPIs
kpis = dashboard.get_kpis()
print(f"Success Rate: {kpis['success_rate']:.1f}%")
print(f"Total Revenue: ₹{kpis['total_revenue_rupees']:.0f}")

# Get AI insights
insights = dashboard.generate_ai_insights()
for insight in insights:
    print(f"[{insight.severity.upper()}] {insight.message}")
    print(f"  → {insight.recommendation}\n")

# Get regional stats
regional_stats = dashboard.get_regional_stats()
for region, stats in regional_stats.items():
    print(f"{region}: {stats['success_rate']}% success rate")
```

### Access Delivery Records

```python
from drone_ops_dashboard import DroneOpsDashboard

dashboard = DroneOpsDashboard()

# Get all deliveries
all_deliveries = dashboard.deliveries

# Filter by status
completed = [d for d in dashboard.deliveries if d.status == "completed"]
failed = [d for d in dashboard.deliveries if d.status == "failed"]

# Filter by region
us_west = [d for d in dashboard.deliveries if d.destination_region == "us_west"]

# Filter by elite tier
elite = [d for d in dashboard.deliveries if d.elite_tier == "ELITE"]

# Get statistics
total_elite = len(elite)
total_revenue = sum(d.revenue_paise for d in elite if d.status == "completed")
elite_success_rate = len([d for d in elite if d.status == "completed"]) / len(elite) * 100

print(f"Elite Packages: {total_elite}")
print(f"Elite Revenue: ₹{total_revenue / 100:.0f}")
print(f"Elite Success Rate: {elite_success_rate:.1f}%")
```

### Generate Insights Programmatically

```python
from drone_ops_dashboard import DroneOpsDashboard

dashboard = DroneOpsDashboard()
insights = dashboard.generate_ai_insights()

# Get critical insights only
critical_insights = [i for i in insights if i.severity == "critical"]

# Process each insight
for insight in critical_insights:
    print(f"ALERT: {insight.message}")
    print(f"Action: {insight.recommendation}")
    
    # Send to monitoring system
    send_to_monitoring(
        severity=insight.severity,
        region=insight.region,
        message=insight.message,
    )
```

### Access Chart Data

```python
from drone_ops_dashboard import DroneOpsDashboard

dashboard = DroneOpsDashboard()
chart_data = dashboard.get_delivery_data_for_charts()

# Revenue by region
print("Revenue by Region:")
for region, revenue in chart_data["revenue_by_region"].items():
    print(f"  {region}: ₹{revenue:,.0f}")

# Rarity distribution
print("\nRarity Distribution:")
for bucket, count in chart_data["rarity_distribution"].items():
    print(f"  {bucket}: {count} packages")

# Delivery time statistics
print("\nDelivery Time Stats (minutes):")
stats = chart_data["delivery_time_stats"]
print(f"  Mean: {stats['mean']:.1f}")
print(f"  Median: {stats['median']:.1f}")
print(f"  StDev: {stats['stdev']:.1f}")
```

---

## 🔌 Flask Integration

### Embed Dashboard in Existing Flask App

```python
from flask import Flask
from drone_ops_dashboard import DroneOpsDashboard, create_app

# Create main app
main_app = Flask(__name__)

# Create dashboard
dashboard = DroneOpsDashboard()
dashboard_app = create_app(dashboard)

# Serve main routes
@main_app.route("/")
def index():
    return "Welcome to Drone System"

# Embed dashboard routes
for rule in dashboard_app.url_map.iter_rules():
    if rule.endpoint != 'static':
        main_app.add_url_rule(
            rule.rule,
            rule.endpoint,
            dashboard_app.view_functions[rule.endpoint]
        )

if __name__ == "__main__":
    main_app.run(port=5000, debug=True)
```

### Create Standalone Dashboard Service

```python
from flask import Flask
from drone_ops_dashboard import DroneOpsDashboard, create_app

# Initialize
dashboard = DroneOpsDashboard(data_dir="data", logs_dir="logs")
app = create_app(dashboard)

# Add custom routes
@app.before_request
def log_request():
    print(f"[{request.remote_addr}] {request.method} {request.path}")

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", False),
    )
```

### Scheduled Updates

```python
from flask_apscheduler import APScheduler
from drone_ops_dashboard import DroneOpsDashboard
from flask import Flask

app = Flask(__name__)
dashboard = DroneOpsDashboard()
scheduler = APScheduler()

@scheduler.task('interval', id='refresh_data', seconds=300)
def refresh_dashboard_data():
    """Refresh data every 5 minutes."""
    dashboard._load_production_status()
    dashboard._load_delivery_logs()
    dashboard._calculate_metrics()
    print("Dashboard data refreshed")

scheduler.init_app(app)
scheduler.start()

if __name__ == "__main__":
    app.run()
```

---

## 📊 Data Integration Patterns

### Pattern 1: Load from Database

```python
from drone_ops_dashboard import DroneOpsDashboard, DeliveryRecord
from models import Delivery, session

class DatabaseDashboard(DroneOpsDashboard):
    def _load_delivery_logs(self):
        """Load deliveries from SQLAlchemy models."""
        query = session.query(Delivery).filter(
            Delivery.created_at > datetime.now() - timedelta(days=30)
        )
        
        self.deliveries = [
            DeliveryRecord(
                delivery_id=d.delivery_id,
                opportunity_id=d.opportunity_id,
                origin_lat=float(d.origin_lat),
                origin_lon=float(d.origin_lon),
                destination_lat=float(d.destination_lat),
                destination_lon=float(d.destination_lon),
                origin_region=d.origin_region,
                destination_region=d.destination_region,
                rarity_score=d.rarity_score,
                elite_tier=d.elite_tier,
                revenue_paise=d.revenue_paise,
                delivery_time_minutes=d.delivery_time_minutes,
                status=d.status,
                is_cross_border=d.is_cross_border,
                drone_id=d.drone_id,
                timestamp=int(d.timestamp.timestamp()),
            )
            for d in query
        ]

# Use custom dashboard
dashboard = DatabaseDashboard()
kpis = dashboard.get_kpis()
```

### Pattern 2: Stream Real-Time Data

```python
from drone_ops_dashboard import DroneOpsDashboard, DeliveryRecord
import websocket
import json

class RealtimeDashboard(DroneOpsDashboard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = websocket.WebSocketApp(
            "ws://localhost:8000/deliveries",
            on_message=self.on_delivery_update,
        )
        self.ws.run_forever()
    
    def on_delivery_update(self, ws, message):
        """Process real-time delivery update."""
        data = json.loads(message)
        delivery = DeliveryRecord(**data)
        self.deliveries.append(delivery)
        self._calculate_metrics()
        print(f"New delivery: {delivery.delivery_id}")

# Use real-time dashboard
dashboard = RealtimeDashboard()
```

### Pattern 3: Federated Data Sources

```python
from drone_ops_dashboard import DroneOpsDashboard, DeliveryRecord
import requests

class FederatedDashboard(DroneOpsDashboard):
    def __init__(self, api_urls, *args, **kwargs):
        self.api_urls = api_urls
        super().__init__(*args, **kwargs)
    
    def _load_delivery_logs(self):
        """Load from multiple API endpoints."""
        self.deliveries = []
        
        for api_url in self.api_urls:
            try:
                response = requests.get(f"{api_url}/api/deliveries?limit=500")
                data = response.json()
                
                for item in data:
                    delivery = DeliveryRecord(**item)
                    self.deliveries.append(delivery)
                    
            except Exception as e:
                print(f"Error fetching from {api_url}: {e}")

# Use federated dashboard
dashboard = FederatedDashboard(api_urls=[
    "http://fleet1.internal",
    "http://fleet2.internal",
    "http://fleet3.internal",
])
kpis = dashboard.get_kpis()
```

### Pattern 4: Export Data for External Systems

```python
from drone_ops_dashboard import DroneOpsDashboard
import csv
import json

dashboard = DroneOpsDashboard()

# Export to CSV
with open("deliveries.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "delivery_id", "status", "rarity_score", 
        "elite_tier", "revenue_paise", "delivery_time_minutes"
    ])
    writer.writeheader()
    for d in dashboard.deliveries:
        writer.writerow({
            "delivery_id": d.delivery_id,
            "status": d.status,
            "rarity_score": d.rarity_score,
            "elite_tier": d.elite_tier,
            "revenue_paise": d.revenue_paise,
            "delivery_time_minutes": d.delivery_time_minutes,
        })

# Export to JSON
with open("dashboard_export.json", "w") as f:
    json.dump({
        "kpis": dashboard.get_kpis(),
        "insights": [
            {
                "type": i.insight_type,
                "severity": i.severity,
                "message": i.message,
                "recommendation": i.recommendation,
            }
            for i in dashboard.generate_ai_insights()
        ],
        "regional_stats": dashboard.get_regional_stats(),
    }, f, indent=2)

# Export to database
for d in dashboard.deliveries:
    delivery = Delivery(
        delivery_id=d.delivery_id,
        opportunity_id=d.opportunity_id,
        status=d.status,
        rarity_score=d.rarity_score,
        elite_tier=d.elite_tier,
        revenue_paise=d.revenue_paise,
        delivery_time_minutes=d.delivery_time_minutes,
    )
    session.add(delivery)
session.commit()
```

---

## 🎨 Advanced Customization

### Custom Insights

```python
from drone_ops_dashboard import DroneOpsDashboard, AIInsight

class CustomInsightsDashboard(DroneOpsDashboard):
    def generate_ai_insights(self):
        """Add custom insights."""
        insights = super().generate_ai_insights()
        
        # Add profitability analysis
        if len(self.deliveries) > 50:
            margin_data = [
                d.revenue_paise / 1000  # Normalize
                for d in self.deliveries if d.status == "completed"
            ]
            
            if margin_data:
                import statistics
                avg_margin = statistics.mean(margin_data)
                
                if avg_margin < 300:  # Low margin threshold
                    insights.append(AIInsight(
                        insight_type="opportunity",
                        severity="warning",
                        region="global",
                        message=f"Average order margin is ₹{avg_margin:.0f} (low)",
                        recommendation="Focus on high-rarity elite packages for better margins",
                        confidence=0.8,
                    ))
        
        return insights

dashboard = CustomInsightsDashboard()
```

### Custom Metrics

```python
from drone_ops_dashboard import DroneOpsDashboard
from datetime import datetime, timedelta

class AnalyticsDashboard(DroneOpsDashboard):
    def get_cohort_metrics(self):
        """Analyze deliveries by creation date cohort."""
        cohorts = {}
        
        for d in self.deliveries:
            date = datetime.fromtimestamp(d.timestamp).date()
            
            if date not in cohorts:
                cohorts[date] = {
                    "total": 0,
                    "completed": 0,
                    "revenue": 0,
                }
            
            cohorts[date]["total"] += 1
            if d.status == "completed":
                cohorts[date]["completed"] += 1
                cohorts[date]["revenue"] += d.revenue_paise
        
        return {
            date: {
                "retention": (c["completed"] / c["total"] * 100) if c["total"] > 0 else 0,
                "revenue": c["revenue"] / 100,
                "orders": c["total"],
            }
            for date, c in sorted(cohorts.items())
        }

dashboard = AnalyticsDashboard()
cohorts = dashboard.get_cohort_metrics()
```

### Real-Time Monitoring

```python
from drone_ops_dashboard import DroneOpsDashboard
import time

class MonitoringDashboard(DroneOpsDashboard):
    def monitor_continuous(self, interval=60):
        """Continuously monitor and alert on issues."""
        while True:
            insights = self.generate_ai_insights()
            
            # Check for critical issues
            critical = [i for i in insights if i.severity == "critical"]
            
            if critical:
                print(f"\n🚨 CRITICAL ALERTS ({len(critical)})")
                for c in critical:
                    print(f"  • {c.region}: {c.message}")
                    self.send_alert(c)
            
            # Reload data
            self._load_delivery_logs()
            self._calculate_metrics()
            
            # Wait before next check
            time.sleep(interval)
    
    def send_alert(self, insight):
        """Send alert to notification system."""
        # Implement your alerting logic here
        # e.g., Slack, PagerDuty, Email, etc.
        pass

dashboard = MonitoringDashboard()
dashboard.monitor_continuous(interval=300)  # Check every 5 minutes
```

---

## 📢 Monitoring & Alerts

### Slack Alerts

```python
from drone_ops_dashboard import DroneOpsDashboard
from slack_sdk import WebClient
import os

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

dashboard = DroneOpsDashboard()
insights = dashboard.generate_ai_insights()

for insight in insights:
    if insight.severity in ["critical", "warning"]:
        client.chat_postMessage(
            channel="#drone-alerts",
            text=f":warning: {insight.region.upper()}: {insight.message}",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{insight.insight_type.upper()}* - {insight.region}\n{insight.message}",
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"📋 *Recommendation:* {insight.recommendation}",
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🎯 Confidence: {insight.confidence * 100:.0f}%",
                    }
                }
            ]
        )
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Gauge, start_http_server
from drone_ops_dashboard import DroneOpsDashboard

# Define metrics
delivery_total = Counter('drone_deliveries_total', 'Total deliveries', ['status'])
revenue_gauge = Gauge('drone_revenue_rupees', 'Total revenue')
success_rate_gauge = Gauge('drone_success_rate', 'Success rate percentage')

# Start Prometheus server
start_http_server(8000)

dashboard = DroneOpsDashboard()
kpis = dashboard.get_kpis()

# Update metrics
for d in dashboard.deliveries:
    delivery_total.labels(status=d.status).inc()

revenue_gauge.set(kpis['total_revenue_rupees'])
success_rate_gauge.set(kpis['success_rate'])

# Metrics available at http://localhost:8000/metrics
```

### Email Alerts

```python
from drone_ops_dashboard import DroneOpsDashboard
import smtplib
from email.mime.text import MIMEText

dashboard = DroneOpsDashboard()
insights = dashboard.generate_ai_insights()

critical_insights = [i for i in insights if i.severity == "critical"]

if critical_insights:
    message = MIMEText(
        "\n".join([
            f"• {i.message}\n  → {i.recommendation}"
            for i in critical_insights
        ])
    )
    message['Subject'] = f"🚨 Drone System Alert: {len(critical_insights)} Critical Issues"
    message['From'] = "alerts@drone-system.local"
    message['To'] = "ops-team@company.com"
    
    with smtplib.SMTP("localhost") as server:
        server.send_message(message)
```

---

## 🎯 Common Use Cases

### 1. Dashboard for Operations Team

```python
from drone_ops_dashboard import create_app, DroneOpsDashboard

dashboard = DroneOpsDashboard()
app = create_app(dashboard)

# Ops team opens http://localhost:5000
# Sees real-time KPIs, regional performance, AI insights
```

### 2. Analytics Pipeline

```python
from drone_ops_dashboard import DroneOpsDashboard

dashboard = DroneOpsDashboard()

# Export to data warehouse
export_to_snowflake({
    "kpis": dashboard.get_kpis(),
    "regional": dashboard.get_regional_stats(),
    "deliveries": [d.to_dict() for d in dashboard.deliveries],
})
```

### 3. Automated Alerts

```python
from drone_ops_dashboard import DroneOpsDashboard
import schedule

dashboard = DroneOpsDashboard()

@schedule.scheduled_job('interval', minutes=5)
def check_alerts():
    insights = dashboard.generate_ai_insights()
    for i in insights:
        if i.severity == "critical":
            send_sms(i.message)
```

### 4. Executive Dashboard

```python
# Embed in executive portal
# Shows: Revenue, success rate, elite package conversion
# Simple KPI cards, no technical details
```

---

## 📚 Full Example: Complete Integration

```python
#!/usr/bin/env python3
"""
Complete drone operations system with dashboard.
"""

from flask import Flask
from drone_ops_dashboard import DroneOpsDashboard, create_app
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize dashboard
logger.info("Initializing drone operations dashboard...")
dashboard = DroneOpsDashboard(data_dir="data", logs_dir="logs")

# Create Flask app
app = create_app(dashboard)
CORS(app)

# Add custom middleware
@app.before_request
def log_request_info():
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.after_request
def add_response_headers(response):
    response.headers['X-Powered-By'] = 'Drone Operations Dashboard v1.0'
    return response

# Add custom routes
@app.route("/api/status/summary")
def status_summary():
    kpis = dashboard.get_kpis()
    insights = dashboard.generate_ai_insights()
    
    return jsonify({
        "status": "healthy" if kpis['success_rate'] > 80 else "warning",
        "deliveries": kpis['total_deliveries'],
        "success_rate": kpis['success_rate'],
        "critical_alerts": len([i for i in insights if i.severity == "critical"]),
        "revenue": kpis['total_revenue_rupees'],
    })

# Main
if __name__ == "__main__":
    logger.info(f"Starting dashboard on http://0.0.0.0:5000")
    logger.info(f"Loaded {len(dashboard.deliveries)} deliveries")
    logger.info(f"Active regions: {len(dashboard.regional_metrics)}")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,
    )
```

---

**Version**: 1.0  
**Last Updated**: January 19, 2026  
**Status**: ✅ Production Ready
