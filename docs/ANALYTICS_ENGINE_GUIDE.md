# Analytics Engine Complete Guide

**SURESH AI ORIGIN - Analytics Engine v1.0**

Comprehensive analytics system with data collection, KPI calculation, anomaly detection (>20% drops), PDF reporting, and email alerts.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Module Reference](#module-reference)
6. [Usage Examples](#usage-examples)
7. [Scheduling](#scheduling)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

---

## Overview

### What is Analytics Engine?

Analytics Engine is a modular Python system that:
- **Collects** data from Google Analytics, Stripe, referrals, and AI prompt logs
- **Calculates** KPIs: MRR, ARR, churn rate, growth metrics, top referrers, prompt statistics
- **Detects** anomalies: flags >20% drops in key metrics with severity levels (critical/warning)
- **Generates** weekly PDF reports with matplotlib visualizations
- **Sends** email alerts for anomalies and weekly summaries

### Key Features

✅ **Modular Design**: 6 independent modules (`data_collector`, `kpi_calculator`, `anomaly_detector`, `pdf_generator`, `email_notifier`, `scheduler`)  
✅ **Retry Logic**: Tenacity-based retries for API calls (3 attempts, exponential backoff 4-10s)  
✅ **Mock Data Fallbacks**: Works without API credentials for testing  
✅ **JSONL Historical Storage**: Tracks KPI history in `data/kpi_history.jsonl`  
✅ **Anomaly Thresholds**: 20% drop = warning, 30% drop = critical  
✅ **Cron-Compatible**: APScheduler for automated scheduling  
✅ **Comprehensive Tests**: 40+ tests with mocks for GA/Stripe/email

---

## Architecture

```
analytics_engine/
├── __init__.py                 # Package exports
├── data_collector.py           # GA/Stripe/referral/prompt data collection
├── kpi_calculator.py           # MRR, churn, growth, referrers, prompt stats
├── anomaly_detector.py         # >20% drop detection with severity levels
├── pdf_generator.py            # Weekly PDF reports with matplotlib
├── email_notifier.py           # Anomaly alerts + weekly reports via SMTP
└── scheduler.py                # APScheduler for cron jobs

analytics_engine_main.py        # Main orchestrator script
tests/test_analytics_engine.py  # 40+ comprehensive tests
data/
├── kpi_history.jsonl           # Historical KPI data
└── api_events.jsonl            # AI prompt logs (parsed by data_collector)
reports/
└── weekly_report_*.pdf         # Generated PDF reports
logs/
└── analytics_engine.log        # Application logs
```

### Data Flow

```
┌─────────────────┐
│  Data Sources   │
│  (GA/Stripe/    │
│   Referrals/    │
│   Prompts)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Collector  │  → Retry logic, mock fallbacks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ KPI Calculator  │  → MRR, churn, growth, referrers, prompts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Anomaly Detect. │  → >20% drop detection, severity levels
└────────┬────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│ PDF Generator   │───▶│ Email Notifier  │
│ (matplotlib)    │    │ (smtplib)       │
└─────────────────┘    └─────────────────┘
         │                      │
         ▼                      ▼
   weekly_report.pdf     admin@example.com
```

---

## Installation

### Prerequisites

- Python 3.9+
- pip package manager
- SMTP email account (Gmail, Outlook, etc.)
- (Optional) Google Analytics API credentials
- (Optional) Stripe API key

### Install Dependencies

```bash
cd "c:\Users\sures\Suresh ai origin"

# Install required packages
pip install pandas matplotlib seaborn requests tenacity apscheduler

# Optional: Google Analytics
pip install google-analytics-data google-auth

# Optional: Stripe
pip install stripe

# For testing
pip install pytest pytest-mock
```

### Verify Installation

```bash
python analytics_engine_main.py --test-email
```

---

## Configuration

### Environment Variables

Create `.env` file or set in Render dashboard:

```bash
# ==================== GOOGLE ANALYTICS ====================
GA_PROPERTY_ID=123456789
GA_API_KEY=your-ga-api-key

# ==================== STRIPE ====================
STRIPE_API_KEY=sk_live_...

# ==================== EMAIL (REQUIRED) ====================
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password        # NOT regular password!
ADMIN_EMAIL=admin@sureshaiorigin.com

# ==================== DATABASE (OPTIONAL) ====================
REFERRAL_DB_URL=sqlite:///data.db
```

### Email Setup (Gmail Example)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password
3. **Set Environment Variables**:
   ```bash
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASS=your-16-char-app-password
   ```

### Directory Structure

Create required directories:

```bash
mkdir -p data reports logs
```

---

## Module Reference

### 1. DataCollector (`data_collector.py`)

**Purpose**: Collect data from GA, Stripe, referrals, prompt logs

**Key Methods**:

```python
from analytics_engine import DataCollector

collector = DataCollector()

# Collect Google Analytics data (last 30 days)
ga_data = collector.get_ga_data(start_date="2024-01-01", end_date="2024-01-31")
# Returns: [{"date": "20240101", "source": "google", "activeUsers": 100, ...}]

# Collect Stripe subscription data
stripe_data = collector.get_stripe_data()
# Returns: {"total_revenue": 150000, "active_subscriptions": 45, ...}

# Collect referral data
referral_data = collector.get_referral_data()
# Returns: [{"referrer_name": "LinkedIn", "referral_count": 25, "revenue": 75000}]

# Collect AI prompt statistics
prompt_stats = collector.get_prompt_stats()
# Returns: [{"feature_name": "ai_generator", "prompt_count": 150, ...}]

# Collect all data sources
all_data = collector.collect_all_data()
# Returns: {"ga_data": [...], "stripe_data": {...}, ...}
```

**Features**:
- **Retry Logic**: `@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=10))`
- **Mock Fallbacks**: Returns demo data if APIs unavailable
- **GA Metrics**: activeUsers, newUsers, pageViews, engagementRate, bounceRate
- **Stripe Metrics**: total_revenue, active_subs, cancelled_subs

---

### 2. KPICalculator (`kpi_calculator.py`)

**Purpose**: Calculate KPIs from collected data

**Key Methods**:

```python
from analytics_engine import KPICalculator

calculator = KPICalculator()

# Calculate Monthly Recurring Revenue
mrr = calculator.calculate_mrr(stripe_data)
# Returns: 134550.00 (sum of active subscription amounts)

# Calculate churn rate
churn = calculator.calculate_churn_rate(stripe_data)
# Returns: 10.0 (% of cancelled subscriptions)

# Get top referrers by revenue
top_referrers = calculator.get_top_referrers(referral_data, limit=10)
# Returns: [{"referrer_name": "Direct", "revenue": 90000, ...}]

# Calculate prompt statistics
prompt_stats = calculator.calculate_prompt_statistics(prompt_stats)
# Returns: {"total_prompts": 350, "avg_tokens": 500, "success_rate": 96.5, ...}

# Calculate all KPIs
kpis = calculator.calculate_all_kpis(all_data)
# Returns: {"revenue_metrics": {...}, "growth_metrics": {...}, ...}
```

**KPI Categories**:

1. **Revenue Metrics**:
   - `mrr`: Monthly Recurring Revenue (₹)
   - `arr`: Annual Recurring Revenue (MRR × 12)
   - `arpu`: Average Revenue Per User
   - `churn_rate`: % of cancelled subscriptions
   - `active_subscriptions`: Count of active subs
   - `total_revenue`: Total revenue from Stripe

2. **Growth Metrics**:
   - `total_active_users`: Active users (30 days)
   - `total_new_users`: New users (30 days)
   - `total_page_views`: Total page views
   - `user_growth_wow`: Week-over-week user growth %
   - `pageview_growth_wow`: Week-over-week pageview growth %
   - `avg_daily_users`: Average daily active users
   - `avg_daily_pageviews`: Average daily page views

3. **Top Referrers**: Top 10 by revenue
4. **Prompt Statistics**:
   - `total_prompts`: Total AI prompts
   - `avg_tokens_per_prompt`: Average tokens used
   - `overall_success_rate`: % successful prompts
   - `most_used_feature`: Feature with most prompts
   - `best_performing_feature`: Feature with highest success rate

---

### 3. AnomalyDetector (`anomaly_detector.py`)

**Purpose**: Detect >20% drops in KPIs

**Key Methods**:

```python
from analytics_engine import AnomalyDetector

detector = AnomalyDetector(threshold=0.20)  # 20% threshold

# Save current KPIs to history
detector.save_kpis(kpis)

# Load historical KPIs (last 7 days)
historical = detector.load_historical_kpis(days=7)

# Detect revenue anomalies (MRR, ARR, churn)
revenue_anomalies = detector.detect_revenue_anomalies(current_kpis, historical)

# Detect growth anomalies (users, pageviews)
growth_anomalies = detector.detect_growth_anomalies(current_kpis, historical)

# Detect all anomalies
anomalies = detector.detect_all_anomalies(current_kpis)
# Returns: {
#   "anomalies_detected": True,
#   "total_anomalies": 2,
#   "critical_count": 1,
#   "all_anomalies": [...]
# }
```

**Anomaly Structure**:

```python
{
    "metric": "MRR",
    "current_value": 70000.00,
    "previous_value": 100000.00,
    "change_percent": -30.0,
    "severity": "critical",  # critical, warning, info
    "message": "MRR has decreased by 30.0% (₹70,000.00 → ₹100,000.00)"
}
```

**Severity Rules**:
- **Critical**: >30% drop in MRR/ARR, >5% churn increase
- **Warning**: >20% drop in any metric
- **Info**: <20% change

**Historical Storage**:
- File: `data/kpi_history.jsonl`
- Format: One JSON object per line with timestamp
- Retention: Last 30 days (auto-cleanup in future versions)

---

### 4. PDFGenerator (`pdf_generator.py`)

**Purpose**: Generate weekly PDF reports with matplotlib

**Key Methods**:

```python
from analytics_engine import PDFGenerator

generator = PDFGenerator(output_dir="reports")

# Generate complete weekly report
pdf_path = generator.generate_weekly_report(kpis, anomalies)
# Returns: "reports/weekly_report_20240113_142530.pdf"

# Create individual charts (for custom reports)
revenue_chart = generator.create_revenue_chart(kpis)
growth_chart = generator.create_growth_chart(kpis)
referrers_chart = generator.create_referrers_chart(kpis)
prompt_chart = generator.create_prompt_stats_chart(kpis)
summary_page = generator.create_summary_page(kpis, anomalies)
```

**Report Structure** (5 pages):

1. **Page 1: Executive Summary**
   - KPI summary table
   - Anomaly alerts section
   - Timestamp and metadata

2. **Page 2: Revenue Metrics**
   - MRR/ARR bar chart
   - Active vs Cancelled subs (pie chart)
   - Churn rate gauge
   - ARPU bar chart

3. **Page 3: Growth Metrics**
   - Total/new users bar chart
   - Week-over-week growth rates (horizontal bars)
   - Daily averages
   - Total page views

4. **Page 4: Top Referrers**
   - Top 10 by referral count (horizontal bar)
   - Top 10 by revenue (horizontal bar)

5. **Page 5: AI Prompt Statistics**
   - Total prompts bar chart
   - Overall success rate gauge
   - Most used feature
   - Best performing feature

**Styling**:
- Seaborn whitegrid theme
- Color-coded severity (green/yellow/red)
- 11×8 inch page size (A4-like)
- Embedded metadata (title, author, keywords)

---

### 5. EmailNotifier (`email_notifier.py`)

**Purpose**: Send anomaly alerts and weekly reports

**Key Methods**:

```python
from analytics_engine import EmailNotifier

notifier = EmailNotifier(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_user="your-email@gmail.com",
    smtp_pass="your-app-password",
    admin_email="admin@example.com"
)

# Send test email (verify configuration)
notifier.send_test_email()

# Send anomaly alert (immediate)
notifier.send_anomaly_alert(anomalies)

# Send weekly report (with PDF attachment)
notifier.send_weekly_report(kpis, anomalies, pdf_path="reports/weekly_report.pdf")
```

**Email Templates**:

1. **Anomaly Alert Email**:
   - Subject: `🚨 [CRITICAL] Analytics Anomalies Detected - 2 Alert(s)`
   - Color-coded severity header
   - Anomaly details table
   - Recommended actions section

2. **Weekly Report Email**:
   - Subject: `📊 Weekly Analytics Report - January 13, 2024`
   - KPI summary cards (MRR, ARR, churn, users)
   - Growth metrics with color-coded trends
   - Top 3 referrers
   - PDF attachment notice
   - Anomaly summary (if any)

**HTML Features**:
- Responsive design (mobile-friendly)
- Color-coded metrics (green=good, red=bad)
- Embedded styles (no external CSS)
- Attachment support (PDF reports)

---

### 6. AnalyticsScheduler (`scheduler.py`)

**Purpose**: Schedule automated analytics tasks

**Key Methods**:

```python
from analytics_engine import AnalyticsScheduler

scheduler = AnalyticsScheduler()

# Setup default schedule
scheduler.setup_default_schedule()
# - Daily data collection: 12:00 AM
# - Hourly anomaly checks
# - Weekly report: Sunday 9:00 AM

# Add custom job
scheduler.add_job(
    job_func=my_custom_function,
    trigger='cron',
    hour=6,
    minute=30
)

# Run once (testing)
scheduler.run_once(job="report")  # Options: collect, anomalies, report, all

# Start scheduler (blocking)
scheduler.start()

# Stop scheduler
scheduler.stop()
```

**Default Schedule**:

| Job | Trigger | Description |
|-----|---------|-------------|
| `daily_data_collection` | Daily 12:00 AM | Collect data from all sources |
| `hourly_anomaly_check` | Every hour | Check for anomalies, send alerts |
| `weekly_report` | Sunday 9:00 AM | Generate PDF, send weekly email |

**CLI Usage**:

```bash
# Run scheduler as daemon (background)
python analytics_engine/scheduler.py --daemon

# Run once for testing
python analytics_engine/scheduler.py --once report

# Send test email
python analytics_engine/scheduler.py --test
```

---

## Usage Examples

### Example 1: Manual Data Collection

```python
from analytics_engine import DataCollector

collector = DataCollector()

# Collect all data
data = collector.collect_all_data()

print(f"GA Records: {len(data['ga_data'])}")
print(f"Active Subs: {data['stripe_data']['active_subscriptions']}")
print(f"Top Referrer: {data['referral_data'][0]['referrer_name']}")
```

### Example 2: Calculate KPIs

```python
from analytics_engine import DataCollector, KPICalculator

collector = DataCollector()
calculator = KPICalculator()

# Collect and calculate
data = collector.collect_all_data()
kpis = calculator.calculate_all_kpis(data)

print(f"MRR: ₹{kpis['revenue_metrics']['mrr']:,.2f}")
print(f"Churn: {kpis['revenue_metrics']['churn_rate']:.1f}%")
print(f"User Growth: {kpis['growth_metrics']['user_growth_wow']:+.1f}%")
```

### Example 3: Detect Anomalies

```python
from analytics_engine import DataCollector, KPICalculator, AnomalyDetector

collector = DataCollector()
calculator = KPICalculator()
detector = AnomalyDetector()

# Full cycle
data = collector.collect_all_data()
kpis = calculator.calculate_all_kpis(data)
anomalies = detector.detect_all_anomalies(kpis)

if anomalies['anomalies_detected']:
    print(f"⚠️  {anomalies['total_anomalies']} anomaly/anomalies detected!")
    for anom in anomalies['all_anomalies']:
        print(f"  [{anom['severity']}] {anom['message']}")
else:
    print("✓ All metrics healthy")
```

### Example 4: Generate PDF Report

```python
from analytics_engine import DataCollector, KPICalculator, AnomalyDetector, PDFGenerator

# Collect, calculate, detect
collector = DataCollector()
calculator = KPICalculator()
detector = AnomalyDetector()
generator = PDFGenerator()

data = collector.collect_all_data()
kpis = calculator.calculate_all_kpis(data)
anomalies = detector.detect_all_anomalies(kpis)

# Generate PDF
pdf_path = generator.generate_weekly_report(kpis, anomalies)
print(f"✓ PDF generated: {pdf_path}")
```

### Example 5: Send Email Alert

```python
from analytics_engine import EmailNotifier

notifier = EmailNotifier()

# Test configuration
notifier.send_test_email()

# Send anomaly alert
if anomalies['anomalies_detected']:
    notifier.send_anomaly_alert(anomalies)

# Send weekly report
notifier.send_weekly_report(kpis, anomalies, pdf_path="reports/weekly_report.pdf")
```

### Example 6: Complete Cycle (Main Script)

```bash
# Collect data + check anomalies + send alerts
python analytics_engine_main.py --collect --check-anomalies

# Generate weekly report with PDF
python analytics_engine_main.py --collect --report

# Full cycle (all features)
python analytics_engine_main.py --collect --check-anomalies --report
```

---

## Scheduling

### Option 1: APScheduler (Recommended)

**Start Scheduler**:

```bash
# Start daemon
python analytics_engine/scheduler.py --daemon

# Verify jobs
ps aux | grep scheduler.py
```

**Default Jobs**:
- Daily data collection: 12:00 AM
- Hourly anomaly checks
- Weekly report: Sunday 9:00 AM

---

### Option 2: System Cron (Linux/Mac)

**Edit Crontab**:

```bash
crontab -e
```

**Add Jobs**:

```bash
# Daily data collection at midnight
0 0 * * * cd /path/to/project && python analytics_engine_main.py --collect >> logs/cron.log 2>&1

# Hourly anomaly checks
0 * * * * cd /path/to/project && python analytics_engine_main.py --collect --check-anomalies >> logs/cron.log 2>&1

# Weekly report (Sunday 9 AM)
0 9 * * 0 cd /path/to/project && python analytics_engine_main.py --collect --report >> logs/cron.log 2>&1
```

---

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. **Trigger**: Daily at 12:00 AM
4. **Action**: Start a program
   - Program: `python`
   - Arguments: `analytics_engine_main.py --collect --check-anomalies`
   - Start in: `C:\Users\sures\Suresh ai origin`

---

### Option 4: Render/Heroku Scheduler

**Render (Dashboard)**:
1. Go to your service → Settings → Cron Jobs
2. Add job:
   ```bash
   python analytics_engine_main.py --collect --check-anomalies
   ```
3. Schedule: `0 0 * * *` (daily midnight)

**Heroku CLI**:

```bash
heroku addons:create scheduler:standard
heroku addons:open scheduler

# Add job (daily 9 AM):
python analytics_engine_main.py --collect --report
```

---

## Troubleshooting

### Issue 1: Email Not Sending

**Symptoms**: `Failed to send email: [Errno 535] Authentication failed`

**Solutions**:

1. **Check App Password** (Gmail):
   ```bash
   # Verify environment variables
   echo $EMAIL_USER
   echo $EMAIL_PASS
   ```
   - Must use App Password, NOT regular password
   - Generate at: https://myaccount.google.com/apppasswords

2. **Check SMTP Settings**:
   ```python
   # Outlook
   EMAIL_HOST=smtp-mail.outlook.com
   EMAIL_PORT=587
   
   # Gmail
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   ```

3. **Test Email**:
   ```bash
   python analytics_engine_main.py --test-email
   ```

---

### Issue 2: Google Analytics 403 Forbidden

**Symptoms**: `403 Forbidden: The caller does not have permission`

**Solutions**:

1. **Enable GA Data API**:
   - Go to: https://console.cloud.google.com/apis/library
   - Search "Google Analytics Data API"
   - Click "Enable"

2. **Check Service Account Permissions**:
   - Go to GA property → Admin → Property Access Management
   - Add service account email with "Viewer" role

3. **Verify Property ID**:
   ```python
   # Should be numeric, not UA-XXXXXXX-X
   GA_PROPERTY_ID=123456789
   ```

4. **Use Mock Data (Testing)**:
   ```python
   # analytics_engine will fall back to mock data if API fails
   collector = DataCollector()
   data = collector.collect_all_data()  # Uses mock data
   ```

---

### Issue 3: Stripe API Key Invalid

**Symptoms**: `stripe.error.AuthenticationError: Invalid API Key`

**Solutions**:

1. **Check Key Format**:
   ```bash
   # Live key starts with sk_live_
   STRIPE_API_KEY=sk_live_...
   
   # Test key starts with sk_test_
   STRIPE_API_KEY=sk_test_...  # For testing only
   ```

2. **Verify Key in Stripe Dashboard**:
   - Go to: https://dashboard.stripe.com/apikeys
   - Copy "Secret key" (not publishable key)

3. **Use Mock Data (Testing)**:
   ```python
   # analytics_engine falls back to mock if stripe not installed
   pip uninstall stripe  # Temporarily remove
   ```

---

### Issue 4: PDF Generation Fails

**Symptoms**: `ImportError: No module named 'matplotlib'`

**Solutions**:

1. **Install Dependencies**:
   ```bash
   pip install matplotlib seaborn
   ```

2. **Check Backend**:
   ```python
   import matplotlib
   matplotlib.use('Agg')  # Non-interactive backend
   ```

3. **Verify Reports Directory**:
   ```bash
   mkdir -p reports
   ```

---

### Issue 5: APScheduler Not Found

**Symptoms**: `ModuleNotFoundError: No module named 'apscheduler'`

**Solutions**:

1. **Install APScheduler**:
   ```bash
   pip install apscheduler
   ```

2. **Use Cron Instead**:
   ```bash
   # See "Option 2: System Cron" in Scheduling section
   crontab -e
   ```

---

### Issue 6: JSONL History Corrupted

**Symptoms**: `JSONDecodeError: Expecting value: line 1 column 1`

**Solutions**:

1. **Reset History**:
   ```bash
   rm data/kpi_history.jsonl
   python analytics_engine_main.py --collect --check-anomalies
   ```

2. **Manually Inspect**:
   ```bash
   cat data/kpi_history.jsonl | jq .
   ```

---

## API Reference

### CLI Commands

#### analytics_engine_main.py

```bash
# Full syntax
python analytics_engine_main.py [--collect] [--check-anomalies] [--report] [--test-email]

# Examples
python analytics_engine_main.py --collect --check-anomalies   # Daily job
python analytics_engine_main.py --collect --report            # Weekly job
python analytics_engine_main.py --test-email                  # Test email
```

**Arguments**:
- `--collect`: Collect data from all sources
- `--check-anomalies`: Detect anomalies and send alerts
- `--report`: Generate PDF report and send email
- `--test-email`: Send test email to verify SMTP configuration

---

#### scheduler.py

```bash
# Full syntax
python analytics_engine/scheduler.py [--daemon] [--once {collect,anomalies,report,all}] [--test]

# Examples
python analytics_engine/scheduler.py --daemon                 # Start background daemon
python analytics_engine/scheduler.py --once report            # Run once, exit
python analytics_engine/scheduler.py --test                   # Test email
```

**Arguments**:
- `--daemon`: Run scheduler as background service
- `--once {job}`: Run job once and exit (testing)
  - `collect`: Data collection
  - `anomalies`: Anomaly check
  - `report`: Weekly report
  - `all`: Full cycle
- `--test`: Send test email

---

### Python API

#### Import Modules

```python
from analytics_engine import (
    DataCollector,
    KPICalculator,
    AnomalyDetector,
    PDFGenerator,
    EmailNotifier,
    AnalyticsScheduler
)
```

#### DataCollector API

```python
collector = DataCollector()

# Methods
ga_data = collector.get_ga_data(start_date="2024-01-01", end_date="2024-01-31")
stripe_data = collector.get_stripe_data()
referral_data = collector.get_referral_data()
prompt_stats = collector.get_prompt_stats()
all_data = collector.collect_all_data()
```

#### KPICalculator API

```python
calculator = KPICalculator()

# Methods
mrr = calculator.calculate_mrr(stripe_data)
churn = calculator.calculate_churn_rate(stripe_data)
top_referrers = calculator.get_top_referrers(referral_data, limit=10)
prompt_stats = calculator.calculate_prompt_statistics(prompt_stats)
revenue_metrics = calculator.calculate_revenue_metrics(stripe_data)
growth_metrics = calculator.calculate_growth_metrics(ga_data)
kpis = calculator.calculate_all_kpis(all_data)
```

#### AnomalyDetector API

```python
detector = AnomalyDetector(threshold=0.20)

# Methods
detector.save_kpis(kpis)
historical = detector.load_historical_kpis(days=7)
revenue_anomalies = detector.detect_revenue_anomalies(current, historical)
growth_anomalies = detector.detect_growth_anomalies(current, historical)
anomalies = detector.detect_all_anomalies(kpis)
```

#### PDFGenerator API

```python
generator = PDFGenerator(output_dir="reports")

# Methods
pdf_path = generator.generate_weekly_report(kpis, anomalies)
fig = generator.create_revenue_chart(kpis)
fig = generator.create_growth_chart(kpis)
fig = generator.create_referrers_chart(kpis)
fig = generator.create_prompt_stats_chart(kpis)
fig = generator.create_summary_page(kpis, anomalies)
```

#### EmailNotifier API

```python
notifier = EmailNotifier(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_user="user@gmail.com",
    smtp_pass="app-password",
    admin_email="admin@example.com"
)

# Methods
success = notifier.send_test_email()
success = notifier.send_anomaly_alert(anomalies)
success = notifier.send_weekly_report(kpis, anomalies, pdf_path)
```

#### AnalyticsScheduler API

```python
scheduler = AnalyticsScheduler()

# Methods
scheduler.setup_default_schedule()
scheduler.add_job(func, trigger='cron', hour=9, minute=0)
scheduler.run_once(job="report")
scheduler.start(daemon=False)
scheduler.stop()
```

---

## Testing

### Run All Tests

```bash
# Run all analytics engine tests
pytest tests/test_analytics_engine.py -v

# Run specific test
pytest tests/test_analytics_engine.py::test_calculate_mrr -v

# With coverage
pytest tests/test_analytics_engine.py --cov=analytics_engine --cov-report=html
```

### Test Coverage

**40+ tests covering**:
- Data collection (GA, Stripe, referrals, prompts)
- KPI calculation (revenue, growth, referrers, prompts)
- Anomaly detection (>20% drops, severity levels)
- PDF generation (charts, summary page, full report)
- Email notifications (alerts, weekly reports)
- Integration tests (full cycle)
- Edge cases (empty data, no history, API failures)

---

## Best Practices

### 1. Security

✅ **DO**:
- Store API keys in environment variables (Render dashboard)
- Use App Passwords for email (not regular passwords)
- Rotate keys after exposure
- Use `.gitignore` to exclude `.env` files

❌ **DON'T**:
- Commit `.env` files with secrets
- Share API keys in code or comments
- Use production keys in development

---

### 2. Data Management

✅ **DO**:
- Backup `data/kpi_history.jsonl` regularly
- Monitor log file size (`logs/analytics_engine.log`)
- Archive old PDF reports (>30 days)

❌ **DON'T**:
- Delete historical KPI data (needed for anomaly detection)
- Ignore disk space warnings
- Store sensitive customer data in logs

---

### 3. Error Handling

✅ **DO**:
- Use mock data fallbacks for testing
- Log errors with `exc_info=True`
- Set up monitoring for email failures

❌ **DON'T**:
- Crash on API failures (retry instead)
- Send sensitive errors in emails
- Ignore anomaly alerts

---

### 4. Performance

✅ **DO**:
- Run hourly anomaly checks (not every minute)
- Generate weekly reports (not daily)
- Use APScheduler for efficient scheduling

❌ **DON'T**:
- Query APIs excessively (respect rate limits)
- Generate PDFs on every check
- Send emails more than necessary

---

## Support

**Documentation**: This guide  
**Tests**: `tests/test_analytics_engine.py`  
**Logs**: `logs/analytics_engine.log`  
**Issues**: Check Troubleshooting section above

---

## Changelog

### v1.0.0 (January 2024)
- ✅ Initial release
- ✅ 6 modular components (data, KPI, anomaly, PDF, email, scheduler)
- ✅ Google Analytics + Stripe + referral + prompt data collection
- ✅ MRR, churn, growth, referrer, prompt KPIs
- ✅ >20% anomaly detection with severity levels
- ✅ Weekly PDF reports with matplotlib (5 pages)
- ✅ Email alerts for anomalies + weekly summaries
- ✅ APScheduler for cron-compatible scheduling
- ✅ 40+ comprehensive tests
- ✅ Complete documentation

---

**Built for SURESH AI ORIGIN by Analytics Engine Team**

