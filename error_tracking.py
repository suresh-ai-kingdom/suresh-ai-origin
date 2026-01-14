#!/usr/bin/env python3
"""
Enhanced Error Tracking - SURESH AI ORIGIN
Integration with Sentry-like error tracking (self-hosted via logging)
"""

import logging
import json
import smtplib
import os
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

class ErrorTracker:
    """Tracks errors and sends alerts."""
    
    def __init__(self):
        self.error_log_file = 'errors.json'
        self.error_counts = defaultdict(int)
        self.error_threshold = 5  # Alert after 5 errors in 1 hour
        self.alert_cooldown = 3600  # 1 hour between duplicate alerts
        self.last_alert_time = {}
        
        # Set up logger
        self.logger = logging.getLogger('ErrorTracker')
        self.logger.setLevel(logging.ERROR)
        
        handler = logging.FileHandler('errors.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_error(self, error_type, error_msg, context=None, severity='ERROR'):
        """Log an error with context."""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_msg,
            'severity': severity,
            'context': context or {}
        }
        
        # Write to JSON log
        try:
            with open(self.error_log_file, 'a') as f:
                f.write(json.dumps(error_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to log error: {e}")
        
        # Track error count
        self.error_counts[error_type] += 1
        
        # Check if we should alert
        if self.error_counts[error_type] >= self.error_threshold:
            self.check_and_send_alert(error_type, error_entry)
    
    def check_and_send_alert(self, error_type, error_entry):
        """Send alert if threshold reached and cooldown passed."""
        now = time.time()
        last_alert = self.last_alert_time.get(error_type, 0)
        
        if now - last_alert > self.alert_cooldown:
            subject = f"⚠️ {error_type} Error Alert"
            message = f"""
Error Type: {error_type}
Severity: {error_entry.get('severity', 'ERROR')}
Count (this hour): {self.error_counts[error_type]}
Last Error: {error_entry['message']}

Context: {json.dumps(error_entry.get('context', {}), indent=2)}

Time: {datetime.now()}
"""
            self.send_alert(subject, message)
            self.last_alert_time[error_type] = now
    
    def send_alert(self, subject, message):
        """Send email alert."""
        try:
            email_user = os.getenv('EMAIL_USER')
            email_pass = os.getenv('EMAIL_PASS')
            alert_email = os.getenv('ALERT_EMAIL', email_user)
            
            if not email_user or not email_pass:
                self.logger.warning("Email not configured for alerts")
                return
            
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = alert_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP('smtp-mail.outlook.com', 587)
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Alert sent: {subject}")
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
    
    def get_error_stats(self, hours=1):
        """Get error statistics for past N hours."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            error_stats = defaultdict(int)
            
            if not os.path.exists(self.error_log_file):
                return error_stats
            
            with open(self.error_log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_time = datetime.fromisoformat(entry['timestamp'])
                        if entry_time > cutoff_time:
                            error_stats[entry['type']] += 1
                    except:
                        pass
            
            return dict(error_stats)
        except Exception as e:
            self.logger.error(f"Failed to get error stats: {e}")
            return {}
    
    def generate_error_report(self):
        """Generate daily error report."""
        try:
            stats_1h = self.get_error_stats(hours=1)
            stats_24h = self.get_error_stats(hours=24)
            
            report = f"""
ERROR REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================

Last Hour:
{json.dumps(stats_1h, indent=2) if stats_1h else 'No errors'}

Last 24 Hours:
{json.dumps(stats_24h, indent=2) if stats_24h else 'No errors'}

Status: {'⚠️ ISSUES DETECTED' if stats_24h else '✅ HEALTHY'}
"""
            return report
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return "Report generation failed"

# Global error tracker instance
error_tracker = ErrorTracker()

def log_error(error_type, error_msg, context=None, severity='ERROR'):
    """Global error logging function."""
    error_tracker.log_error(error_type, error_msg, context, severity)

def main():
    import sys
    
    tracker = ErrorTracker()
    
    if len(sys.argv) < 2:
        # Show recent errors
        print("\n" + "="*60)
        print("ERROR TRACKING SYSTEM")
        print("="*60)
        print(tracker.generate_error_report())
    
    elif sys.argv[1] == 'report':
        print(tracker.generate_error_report())
    
    elif sys.argv[1] == 'stats':
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        stats = tracker.get_error_stats(hours=hours)
        print(f"Errors (last {hours} hours):")
        print(json.dumps(stats, indent=2))
    
    elif sys.argv[1] == 'test':
        print("Testing error tracking...")
        tracker.log_error('TEST_ERROR', 'This is a test error', {'test': True})
        print("✅ Error logged successfully")

if __name__ == '__main__':
    main()
