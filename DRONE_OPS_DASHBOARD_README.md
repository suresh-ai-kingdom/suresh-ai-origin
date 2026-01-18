# 🚁 Drone Operations Dashboard - Requirements & Setup

## Overview

The **Drone Operations Dashboard** is a Flask-based real-time monitoring system for autonomous drone deliveries. It visualizes global operations with interactive maps, KPIs, AI-powered insights, and predictive analytics.

**Status**: Production Ready ✅  
**Version**: 1.0  
**Date**: January 19, 2026

---

## Features

### 📊 Core Visualizations

1. **Real-Time KPIs**
   - Total deliveries, success rate, revenue
   - Elite packages, cross-border ops
   - Fleet utilization, avg delivery time

2. **Interactive World Map** (Folium)
   - Delivery markers with status coloring (green=complete, red=failed)
   - Clustered markers for geographic density
   - Heatmap layer showing completion hotspots
   - Click markers for delivery details

3. **Performance Charts** (Chart.js)
   - Revenue by region (bar chart)
   - Rarity score distribution (doughnut chart)
   - Success rate trends (line chart)

4. **Regional Dashboard**
   - Table with all region metrics
   - Success rates with color coding
   - Revenue, delivery times, elite percentages

### 🤖 AI-Powered Insights

**Bottleneck Detection**
- Identifies regions with <70% success rates
- Flags high delivery times (>50 min)
- Recommends infrastructure improvements

**Anomaly Detection** (Isolation Forest)
- Detects unusual delivery patterns
- Flags fraud candidates
- 5% contamination threshold

**Revenue Opportunities**
- Highlights elite package concentration
- Tracks high-margin order patterns
- Recommends marketing strategies

**Load Forecasting**
- Predicts tomorrow's delivery volume
- 7-day rolling average
- Crew allocation recommendations

---

## Installation

### Prerequisites

```bash
Python 3.9+
pip package manager
```

### Step 1: Install Dependencies

```bash
pip install flask folium scikit-learn numpy
```

### Step 2: Set Up Data Directory

```bash
mkdir -p data logs
```

### Step 3: Create production_status_report.json (Optional)

```bash
# Place in data/ directory
{
  "service_status": "healthy",
  "uptime_percent": 99.8,
  "total_drones": 72,
  "active_drones": 68,
  "api_calls_per_minute": 3456,
  "error_rate": 0.2,
  "avg_response_time_ms": 145,
  "regions_active": ["us_west", "us_east", "eu_central", "in_south"],
  "last_updated": "2026-01-19T12:00:00"
}
```

---

## Running the Dashboard

### Basic Startup

```bash
python drone_ops_dashboard.py
```

Output:
```
╔══════════════════════════════════════════════════════╗
║  🚁 DRONE OPERATIONS DASHBOARD - STARTING           ║
║                                                      ║
║  📊 Loaded 500 deliveries                           ║
║  🌍 Regions: 5                                       ║
║  🤖 AI Insights: Ready                              ║
║                                                      ║
║  🌐 Open: http://localhost:5000                     ║
║  📡 API:  http://localhost:5000/api/kpis            ║
║           http://localhost:5000/api/insights        ║
║           http://localhost:5000/api/regional        ║
║           http://localhost:5000/health              ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

### Access Dashboard

1. **Web UI**: http://localhost:5000
2. **Health Check**: http://localhost:5000/health

---

## API Endpoints

### Get Key Performance Indicators

```bash
GET /api/kpis
```

Response:
```json
{
  "total_deliveries": 500,
  "completed_deliveries": 350,
  "failed_deliveries": 25,
  "in_transit_deliveries": 125,
  "success_rate": 87.5,
  "total_revenue_rupees": 485000,
  "elite_packages": 45,
  "cross_border_deliveries": 120,
  "avg_delivery_time_minutes": 28.5,
  "avg_rarity_score": 62.3
}
```

### Get AI Insights

```bash
GET /api/insights
```

Response:
```json
[
  {
    "type": "bottleneck",
    "severity": "warning",
    "region": "eu_central",
    "message": "Region eu_central has 65.2% success rate (8 failures)",
    "recommendation": "Investigate infrastructure in eu_central. Consider drone maintenance.",
    "confidence": 0.85
  },
  {
    "type": "forecast",
    "severity": "info",
    "region": "global",
    "message": "Predicted tomorrow's load: ~67 deliveries (based on 7-day average)",
    "recommendation": "Ensure 7 drones are ready. Allocate staff accordingly.",
    "confidence": 0.8
  }
]
```

### Get Regional Statistics

```bash
GET /api/regional
```

Response:
```json
{
  "us_west": {
    "total_deliveries": 125,
    "successful": 112,
    "failed": 5,
    "success_rate": 89.6,
    "total_revenue": 185000,
    "avg_delivery_time": 24.3,
    "avg_rarity": 65.2,
    "elite_count": 18
  },
  "eu_central": {
    "total_deliveries": 95,
    "successful": 62,
    "failed": 8,
    "success_rate": 65.2,
    "total_revenue": 120000,
    "avg_delivery_time": 35.8,
    "avg_rarity": 58.1,
    "elite_count": 8
  }
}
```

### Get Chart Data

```bash
GET /api/charts
```

Response:
```json
{
  "revenue_by_region": {
    "us_west": 185000,
    "us_east": 165000,
    "eu_central": 120000,
    "in_south": 105000,
    "ap_se": 85000
  },
  "rarity_distribution": {
    "0-10": 50,
    "10-20": 85,
    "20-30": 120,
    "90-100": 65
  },
  "delivery_time_stats": {
    "mean": 28.5,
    "median": 26.2,
    "stdev": 12.3,
    "min": 5.1,
    "max": 87.4
  }
}
```

### Get All Deliveries (Paginated)

```bash
GET /api/deliveries?region=us_west&status=completed&limit=50
```

Response:
```json
[
  {
    "delivery_id": "DELIVERY_00001",
    "opportunity_id": "OPP_5432",
    "destination_lat": 37.7849,
    "destination_lon": -122.4094,
    "rarity_score": 96.5,
    "elite_tier": "ELITE",
    "revenue_paise": 400000,
    "delivery_time_minutes": 18.5,
    "status": "completed",
    "is_cross_border": false,
    "drone_id": "DRONE_042",
    "timestamp": 1705596000
  }
]
```

### Production Status

```bash
GET /api/status
```

Response:
```json
{
  "service_status": "healthy",
  "uptime_percent": 99.8,
  "total_drones": 72,
  "active_drones": 68,
  "api_calls_per_minute": 3456,
  "error_rate": 0.2,
  "avg_response_time_ms": 145,
  "regions_active": ["us_west", "us_east", "eu_central", "in_south"]
}
```

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-19T12:34:56.123456",
  "deliveries_loaded": 500,
  "regions": 5
}
```

---

## Data Models

### DeliveryRecord

```python
@dataclass
class DeliveryRecord:
    delivery_id: str              # DELIVERY_00001
    opportunity_id: str           # OPP_5432
    origin_lat: float             # 37.7749
    origin_lon: float             # -122.4194
    destination_lat: float        # 34.0522
    destination_lon: float        # -118.2437
    origin_region: str            # us_west
    destination_region: str       # us_west
    rarity_score: float           # 0-100
    elite_tier: str               # ELITE|ENTERPRISE|PRO|BASIC
    revenue_paise: int            # 400000 (₹4000)
    delivery_time_minutes: float  # 18.5
    status: str                   # completed|in_transit|failed|cancelled
    is_cross_border: bool         # True/False
    drone_id: str                 # DRONE_042
    timestamp: int                # Unix timestamp
```

### RegionalMetrics

```python
@dataclass
class RegionalMetrics:
    region: str                   # us_west
    total_deliveries: int         # 125
    successful_deliveries: int    # 112
    failed_deliveries: int        # 5
    total_revenue_paise: int      # 185000000
    avg_delivery_time: float      # 24.3
    avg_rarity_score: float       # 65.2
    elite_count: int              # 18
    success_rate: float           # 89.6%
```

### AIInsight

```python
@dataclass
class AIInsight:
    insight_type: str             # bottleneck|anomaly|forecast|opportunity
    severity: str                 # critical|warning|info
    region: str                   # us_west|global
    message: str                  # "Region X has Y% success rate"
    recommendation: str           # Actionable recommendation
    confidence: float             # 0.0-1.0
```

---

## Integration with Backend

### Data Loading Strategy

The dashboard can load data from multiple sources:

1. **In-Memory Generation** (Default)
   - Generates 500 realistic delivery records
   - Useful for demos and testing

2. **From Disk Logs**
   ```python
   # Modify _load_delivery_logs() to read from logs/
   for log_file in os.listdir("logs/"):
       with open(f"logs/{log_file}") as f:
           deliveries.extend(json.load(f))
   ```

3. **From Database**
   ```python
   # Connect to SQLAlchemy models
   from models import Delivery, session
   self.deliveries = session.query(Delivery).all()
   ```

4. **From API**
   ```python
   # Call AI gateway endpoints
   response = requests.get("http://localhost:5000/api/deliveries")
   self.deliveries = [DeliveryRecord(**d) for d in response.json()]
   ```

### Integration with autonomous_income_engine.py v4

The dashboard automatically integrates with v4 data:

```python
# In app.py, add route to dashboard
from drone_ops_dashboard import DroneOpsDashboard, create_app

dashboard = DroneOpsDashboard()
dashboard_app = create_app(dashboard)

# Serve dashboard on port 5001
dashboard_app.run(port=5001)
```

---

## Customization

### Adding New Insights

Edit `generate_ai_insights()` method:

```python
def generate_ai_insights(self) -> List[AIInsight]:
    insights = []
    
    # Add custom insight
    if some_condition:
        insights.append(AIInsight(
            insight_type="custom",
            severity="info",
            region="global",
            message="Your custom message",
            recommendation="Your recommendation",
            confidence=0.85,
        ))
    
    return insights
```

### Changing Chart Styling

Modify CSS in `DASHBOARD_TEMPLATE`:

```css
.kpi-value {
    background: linear-gradient(135deg, #f39c12 0%, #e94560 100%);
    /* Change gradient colors here */
}
```

### Adding New Regions

Update `_generate_sample_deliveries()`:

```python
regions = {
    "us_west": (37.7749, -122.4194),
    "jp_tokyo": (35.6762, 139.6503),  # Add new region
    # ...
}
```

---

## Performance Tuning

### Optimize for Large Datasets

```python
# Limit deliveries loaded in memory
self.deliveries = self.deliveries[:1000]  # Cap at 1000

# Use pagination in API
@app.route("/api/deliveries")
def api_deliveries():
    limit = int(request.args.get("limit", 100))  # Default 100
    offset = int(request.args.get("offset", 0))
    return jsonify([d.to_dict() for d in dashboard.deliveries[offset:offset+limit]])
```

### Cache API Responses

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_kpis_cached():
    return dashboard.get_kpis()
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'folium'"

**Solution**:
```bash
pip install folium
```

### Issue: "No deliveries loaded"

**Solution**: Check that `data/` directory exists and contains `production_status_report.json`

### Issue: "AI insights not generating"

**Solution**: Ensure scikit-learn is installed:
```bash
pip install scikit-learn numpy
```

### Issue: Port 5000 already in use

**Solution**:
```bash
python drone_ops_dashboard.py --port 5001
```

---

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY drone_ops_dashboard.py .
COPY data/ data/

EXPOSE 5000

CMD ["python", "drone_ops_dashboard.py"]
```

Build and run:
```bash
docker build -t drone-ops-dashboard .
docker run -p 5000:5000 drone-ops-dashboard
```

### Production Server (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "drone_ops_dashboard:create_app(dashboard)"
```

---

## Monitoring & Alerts

### Health Check Script

```bash
#!/bin/bash
curl http://localhost:5000/health || echo "Dashboard down!"
```

### Monitor Insights

```bash
watch -n 60 'curl -s http://localhost:5000/api/insights | jq'
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 19, 2026 | Initial release - KPIs, maps, AI insights, charts |

---

## Support & Documentation

- **GitHub**: https://github.com/suresh-ai-origin/drone-ops-dashboard
- **Issues**: Report at GitHub Issues
- **Email**: support@suresh-ai-origin.com

---

**Status**: 🟢 Production Ready  
**Last Updated**: January 19, 2026  
**Maintainer**: Suresh AI Origin Team
