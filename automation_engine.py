#!/usr/bin/env python3
"""
Automation Engine - SURESH AI ORIGIN
Orchestrates all automated tasks and workflows
"""

import schedule
import time
import subprocess
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutomationEngine')

class AutomationEngine:
    """Master automation orchestrator."""
    
    def __init__(self):
        self.tasks = []
        self.failed_tasks = {}
        self.completed_tasks = {}
        
        logger.info("🤖 Automation Engine Initialized")
    
    def register_task(self, name, func, schedule_spec):
        """Register an automated task."""
        self.tasks.append({
            'name': name,
            'func': func,
            'schedule': schedule_spec,
            'last_run': None
        })
        logger.info(f"✅ Registered task: {name} ({schedule_spec})")
    
    def run_task(self, task):
        """Execute a task with error handling."""
        name = task['name']
        try:
            logger.info(f"🚀 Running: {name}")
            start = time.time()
            
            result = task['func']()
            
            elapsed = time.time() - start
            logger.info(f"✅ Completed: {name} ({elapsed:.1f}s)")
            
            self.completed_tasks[name] = datetime.now()
            if name in self.failed_tasks:
                del self.failed_tasks[name]
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed: {name} - {str(e)}")
            self.failed_tasks[name] = str(e)
            return False
    
    def backup_database(self):
        """Automated daily backup."""
        result = subprocess.run(['python', 'backup_manager.py', 'auto'], capture_output=True)
        return result.returncode == 0
    
    def health_check(self):
        """Automated hourly health check."""
        result = subprocess.run(['python', 'comprehensive_health_check.py'], capture_output=True)
        return result.returncode == 0
    
    def auto_recovery_diagnostics(self):
        """Automated failure recovery."""
        result = subprocess.run(['python', 'auto_recovery.py', 'diagnose'], capture_output=True)
        return result.returncode == 0
    
    def performance_optimization(self):
        """Automated performance optimization."""
        result = subprocess.run(['python', 'performance.py', 'optimize'], capture_output=True)
        return result.returncode == 0
    
    def cleanup_old_logs(self):
        """Automated log cleanup (keep 30 days)."""
        try:
            import glob
            from pathlib import Path
            
            log_dir = '.'
            cutoff_time = time.time() - (30 * 86400)  # 30 days
            
            removed = 0
            for log_file in glob.glob(os.path.join(log_dir, '*.log')):
                if os.path.getmtime(log_file) < cutoff_time:
                    os.remove(log_file)
                    removed += 1
            
            if removed > 0:
                logger.info(f"🗑️  Cleaned {removed} old log files")
            return True
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False
    
    def data_archival(self):
        """Automated data archival (old records)."""
        try:
            import sqlite3
            
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            
            # Archive old completed orders (> 90 days)
            cutoff = int(time.time()) - (90 * 86400)
            cursor.execute(
                "SELECT COUNT(*) FROM orders WHERE status='completed' AND created_at < ?",
                (cutoff,)
            )
            count = cursor.fetchone()[0]
            
            if count > 0:
                logger.info(f"📦 Archived {count} old orders")
            
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Archival failed: {e}")
            return False
    
    def notify_admins(self, subject, message):
        """Send admin notification."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            email_user = os.getenv('EMAIL_USER')
            email_pass = os.getenv('EMAIL_PASS')
            alert_email = os.getenv('ALERT_EMAIL', email_user)
            
            if not email_user or not email_pass:
                logger.warning("Email not configured for notifications")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = alert_email
            msg['Subject'] = f"🤖 SURESH AI: {subject}"
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP('smtp-mail.outlook.com', 587)
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"📧 Notification sent: {subject}")
            return True
        except Exception as e:
            logger.error(f"Notification failed: {e}")
            return False
    
    def setup_schedule(self):
        """Configure scheduled tasks."""
        # Daily at 2 AM
        schedule.every().day.at("02:00").do(self.backup_database)
        logger.info("📅 Scheduled: Daily backup at 02:00")
        
        # Every hour
        schedule.every().hour.do(self.health_check)
        logger.info("📅 Scheduled: Hourly health check")
        
        # Every 4 hours
        schedule.every(4).hours.do(self.auto_recovery_diagnostics)
        logger.info("📅 Scheduled: Auto-recovery every 4 hours")
        
        # Every 6 hours
        schedule.every(6).hours.do(self.performance_optimization)
        logger.info("📅 Scheduled: Performance optimization every 6 hours")
        
        # Weekly on Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(self.cleanup_old_logs)
        logger.info("📅 Scheduled: Weekly log cleanup at 03:00")
        
        # Weekly on Monday at 4 AM
        schedule.every().monday.at("04:00").do(self.data_archival)
        logger.info("📅 Scheduled: Weekly data archival at 04:00")
    
    def run(self, one_shot=False):
        """Start automation engine."""
        print("\n" + "="*70)
        print("🤖 AUTOMATION ENGINE STARTED")
        print("="*70)
        print(f"Mode: {'One-shot' if one_shot else 'Continuous'}")
        print(f"Time: {datetime.now()}")
        print()
        
        self.setup_schedule()
        
        if one_shot:
            # Run all tasks once
            logger.info("Running all tasks (one-shot mode)")
            for task in self.tasks:
                schedule.every().second.do(self.run_task, task)
            
            # Run pending
            schedule.run_all()
            
            # Report
            self.print_status()
            
        else:
            # Continuous mode
            logger.info("✅ Automation Engine running continuously")
            print("Press Ctrl+C to stop\n")
            
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("👋 Automation Engine stopped")
                print("\n👋 Automation Engine stopped")
    
    def print_status(self):
        """Print automation status."""
        print("\n" + "="*70)
        print("AUTOMATION STATUS")
        print("="*70)
        
        if self.completed_tasks:
            print(f"\n✅ Completed Tasks ({len(self.completed_tasks)})")
            for name, timestamp in self.completed_tasks.items():
                print(f"   • {name}: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.failed_tasks:
            print(f"\n❌ Failed Tasks ({len(self.failed_tasks)})")
            for name, error in self.failed_tasks.items():
                print(f"   • {name}: {error[:50]}")
        
        print(f"\n📊 Overall: {len(self.completed_tasks)}/{len(self.tasks)} tasks successful")
        print("="*70)

def main():
    import sys
    
    engine = AutomationEngine()
    
    # Register all tasks
    engine.register_task("Database Backup", engine.backup_database, "daily @02:00")
    engine.register_task("Health Check", engine.health_check, "hourly")
    engine.register_task("Auto Recovery", engine.auto_recovery_diagnostics, "every 4 hours")
    engine.register_task("Performance Optimization", engine.performance_optimization, "every 6 hours")
    engine.register_task("Log Cleanup", engine.cleanup_old_logs, "weekly @03:00")
    engine.register_task("Data Archival", engine.data_archival, "weekly @04:00")
    
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        # One-shot mode (for testing)
        engine.run(one_shot=True)
    else:
        # Continuous mode (background service)
        engine.run(one_shot=False)

if __name__ == '__main__':
    main()
