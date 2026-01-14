#!/usr/bin/env python3
"""
Production Monitoring - SURESH AI ORIGIN
Real-time health monitoring with email alerts
"""

import requests
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

PROD_URL = os.getenv('PROD_URL', 'https://suresh-ai-origin.onrender.com')
ALERT_EMAIL = os.getenv('ALERT_EMAIL', 'suresh.ai.origin@outlook.com')
EMAIL_USER = os.getenv('EMAIL_USER', 'suresh.ai.origin@outlook.com')
EMAIL_PASS = os.getenv('EMAIL_PASS')
CHECK_INTERVAL = int(os.getenv('MONITOR_INTERVAL', '300'))  # 5 minutes default

class ProductionMonitor:
    def __init__(self):
        self.last_alert_time = {}
        self.alert_cooldown = 900  # 15 minutes between duplicate alerts
        self.consecutive_failures = {}
        
    def send_alert(self, subject, message):
        """Send email alert."""
        try:
            # Check cooldown
            alert_key = subject
            now = time.time()
            if alert_key in self.last_alert_time:
                if now - self.last_alert_time[alert_key] < self.alert_cooldown:
                    print(f"⏳ Skipping alert (cooldown): {subject}")
                    return
            
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = ALERT_EMAIL
            msg['Subject'] = f"🚨 SURESH AI ORIGIN ALERT: {subject}"
            
            body = f"""
PRODUCTION ALERT
================
Time: {datetime.now()}
URL: {PROD_URL}

{message}

---
This is an automated alert from SURESH AI ORIGIN production monitoring.
"""
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp-mail.outlook.com', 587)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
            server.quit()
            
            self.last_alert_time[alert_key] = now
            print(f"📧 Alert sent: {subject}")
            
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")
    
    def check_site_health(self):
        """Check if site is responding."""
        try:
            r = requests.get(f'{PROD_URL}/health', timeout=15)
            if r.status_code == 200:
                data = r.json()
                if data.get('status') == 'healthy':
                    self.consecutive_failures['site'] = 0
                    return True, "Site healthy"
                else:
                    return False, f"Unhealthy: {data}"
            else:
                return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)
    
    def check_ai_working(self):
        """Check if AI is generating responses."""
        try:
            r = requests.post(
                f'{PROD_URL}/api/ai/chat',
                json={'message': 'Test'},
                timeout=30
            )
            if r.status_code == 200:
                data = r.json()
                if data.get('success') and data.get('response'):
                    self.consecutive_failures['ai'] = 0
                    return True, f"AI responding ({len(data['response'])} chars)"
                else:
                    return False, f"No response: {data}"
            else:
                return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)
    
    def check_database(self):
        """Check database connectivity."""
        try:
            r = requests.get(f'{PROD_URL}/api/analytics/daily-revenue', timeout=15)
            if r.status_code == 200:
                self.consecutive_failures['database'] = 0
                return True, "Database queries working"
            else:
                return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)
    
    def check_groq_quota(self):
        """Estimate Groq API usage."""
        try:
            # Make test call and check response time
            start = time.time()
            r = requests.post(
                f'{PROD_URL}/api/ai/chat',
                json={'message': 'Hi'},
                timeout=30
            )
            elapsed = time.time() - start
            
            if r.status_code == 200:
                if elapsed > 10:
                    return False, f"Slow response: {elapsed:.1f}s (possible quota issue)"
                return True, f"Response time: {elapsed:.1f}s"
            else:
                return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)
    
    def run_checks(self):
        """Run all health checks."""
        print(f"\n{'='*60}")
        print(f"Health Check: {datetime.now()}")
        print(f"{'='*60}")
        
        checks = {
            'Site Health': self.check_site_health,
            'AI Generation': self.check_ai_working,
            'Database': self.check_database,
            'Groq Quota': self.check_groq_quota
        }
        
        results = {}
        for name, check_func in checks.items():
            success, message = check_func()
            icon = '✅' if success else '❌'
            print(f"{icon} {name}: {message}")
            results[name] = success
            
            # Track consecutive failures
            if not success:
                self.consecutive_failures[name] = self.consecutive_failures.get(name, 0) + 1
                
                # Alert on 3 consecutive failures
                if self.consecutive_failures[name] >= 3:
                    alert_msg = f"""
{name} has failed {self.consecutive_failures[name]} consecutive times.

Last error: {message}

Immediate action required!
"""
                    self.send_alert(f"{name} CRITICAL", alert_msg)
        
        # Overall health
        total = len(results)
        passed = sum(results.values())
        health_pct = passed/total*100
        
        print(f"\n📊 Overall Health: {passed}/{total} ({health_pct:.0f}%)")
        
        # Alert if overall health drops below 75%
        if health_pct < 75:
            self.send_alert(
                "Low System Health",
                f"System health at {health_pct:.0f}% ({passed}/{total} checks passing)"
            )
        
        return health_pct >= 75
    
    def monitor_continuous(self):
        """Run monitoring loop."""
        print(f"🔍 Starting production monitor...")
        print(f"   URL: {PROD_URL}")
        print(f"   Interval: {CHECK_INTERVAL}s")
        print(f"   Alerts to: {ALERT_EMAIL}")
        print(f"\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_checks()
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")

def main():
    if not EMAIL_PASS:
        print("⚠️  EMAIL_PASS not set - alerts will be disabled")
        print("   Set in .env or environment for email alerts\n")
    
    monitor = ProductionMonitor()
    
    # Run once if not continuous mode
    if os.getenv('MONITOR_ONCE', 'false').lower() == 'true':
        success = monitor.run_checks()
        exit(0 if success else 1)
    else:
        monitor.monitor_continuous()

if __name__ == '__main__':
    main()
