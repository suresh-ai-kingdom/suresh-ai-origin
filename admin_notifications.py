#!/usr/bin/env python3
"""
Admin Notification System - SURESH AI ORIGIN
Real-time notifications for critical events
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AdminNotifications')

class AdminNotifier:
    """Send notifications to admins."""
    
    def __init__(self):
        self.email_user = os.getenv('EMAIL_USER')
        self.email_pass = os.getenv('EMAIL_PASS')
        self.admin_email = os.getenv('ALERT_EMAIL', self.email_user)
        self.notification_types = {
            'CRITICAL': '🚨',
            'WARNING': '⚠️',
            'INFO': 'ℹ️',
            'SUCCESS': '✅'
        }
    
    def send_notification(self, notification_type, title, message, details=None):
        """Send admin notification."""
        if not self.email_user or not self.email_pass:
            logger.warning("Email not configured")
            return False
        
        try:
            icon = self.notification_types.get(notification_type, '📧')
            subject = f"{icon} {title}"
            
            # Build email body
            body = f"""
SURESH AI ORIGIN NOTIFICATION
=====================================

Type: {notification_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Message:
{message}
"""
            
            if details:
                body += f"\n\nDetails:\n{details}"
            
            body += "\n=====================================\nAutomatic notification"
            
            # Send email
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.admin_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp-mail.outlook.com', 587)
            server.starttls()
            server.login(self.email_user, self.email_pass)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Notification sent: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    def notify_deployment_started(self, commit_sha, commit_msg):
        """Notify deployment started."""
        message = f"""
Deployment has started

Commit: {commit_sha}
Message: {commit_msg}

The system will validate the deployment and auto-rollback if issues are detected.
"""
        return self.send_notification('INFO', 'Deployment Started', message)
    
    def notify_deployment_success(self, commit_sha, duration):
        """Notify deployment succeeded."""
        message = f"""
Deployment completed successfully!

Commit: {commit_sha}
Duration: {duration} seconds

All health checks passed. System is healthy.
"""
        return self.send_notification('SUCCESS', 'Deployment Successful', message)
    
    def notify_deployment_failed(self, commit_sha, reason):
        """Notify deployment failed."""
        message = f"""
Deployment failed and rolled back automatically!

Commit: {commit_sha}
Reason: {reason}

The system detected issues and automatically rolled back to the previous version.
Manual investigation may be needed.
"""
        return self.send_notification('CRITICAL', 'Deployment Failed', message)
    
    def notify_system_down(self, error):
        """Notify system is down."""
        message = f"""
CRITICAL: System is down!

Error: {error}

Immediate action required!
"""
        return self.send_notification('CRITICAL', 'System Down Alert', message)
    
    def notify_high_error_rate(self, error_rate, error_type):
        """Notify high error rate."""
        message = f"""
High error rate detected!

Error Type: {error_type}
Error Rate: {error_rate}%
Threshold: 1%

Investigate and take action if necessary.
"""
        return self.send_notification('WARNING', 'High Error Rate', message)
    
    def notify_backup_completed(self, backup_file, size_mb):
        """Notify backup completed."""
        message = f"""
Automated backup completed successfully

File: {backup_file}
Size: {size_mb:.2f} MB

Backup verified and ready for restore if needed.
"""
        return self.send_notification('SUCCESS', 'Backup Completed', message)
    
    def notify_backup_failed(self, reason):
        """Notify backup failed."""
        message = f"""
Automated backup failed!

Reason: {reason}

Manual backup may be needed. Please investigate.
"""
        return self.send_notification('CRITICAL', 'Backup Failed', message)
    
    def notify_disk_space_low(self, percent_used):
        """Notify low disk space."""
        message = f"""
Disk space is running low!

Used: {percent_used}%
Action: Clean up old logs and backups

Archive old data if necessary.
"""
        return self.send_notification('WARNING', 'Low Disk Space', message)
    
    def notify_daily_summary(self, summary_stats):
        """Send daily summary to admin."""
        message = f"""
Daily Summary Report

Uptime: {summary_stats.get('uptime', 'N/A')}
Errors: {summary_stats.get('errors', 0)}
Successful Requests: {summary_stats.get('requests', 0)}
Avg Response Time: {summary_stats.get('response_time', 'N/A')}ms

Status: {summary_stats.get('status', 'OK')}
"""
        return self.send_notification('INFO', 'Daily Summary', message)

# Global notifier instance
admin_notifier = AdminNotifier()

def notify(notification_type, title, message, details=None):
    """Global notification function."""
    return admin_notifier.send_notification(notification_type, title, message, details)

def main():
    import sys
    
    notifier = AdminNotifier()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        print("Sending test notification...")
        if notifier.send_notification('INFO', 'Test Notification', 'This is a test'):
            print("✅ Test notification sent successfully")
        else:
            print("❌ Failed to send test notification")

if __name__ == '__main__':
    main()
