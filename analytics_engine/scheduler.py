"""
Scheduler Module - Schedule analytics tasks (cron-compatible)
"""

import logging
import sys
import time
import signal
from typing import Callable
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from analytics_engine.data_collector import DataCollector
from analytics_engine.kpi_calculator import KPICalculator
from analytics_engine.anomaly_detector import AnomalyDetector
from analytics_engine.pdf_generator import PDFGenerator
from analytics_engine.email_notifier import EmailNotifier

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    print("⚠️  APScheduler not installed. Install with: pip install apscheduler")

logger = logging.getLogger("AnalyticsScheduler")


class AnalyticsScheduler:
    """Schedule automated analytics tasks."""
    
    def __init__(self):
        """Initialize scheduler."""
        if not SCHEDULER_AVAILABLE:
            raise ImportError("APScheduler is required. Install with: pip install apscheduler")
        
        self.scheduler = BlockingScheduler()
        self.collector = DataCollector()
        self.calculator = KPICalculator()
        self.detector = AnomalyDetector()
        self.pdf_generator = PDFGenerator()
        self.email_notifier = EmailNotifier()
        
        self.is_running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("AnalyticsScheduler initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum} - shutting down gracefully")
        self.stop()
        sys.exit(0)
    
    def collect_data_job(self):
        """Job: Collect data from all sources."""
        try:
            logger.info("Running scheduled data collection")
            data = self.collector.collect_all_data()
            logger.info(f"✓ Data collected: {len(data)} sources")
            return data
        except Exception as e:
            logger.error(f"Data collection job failed: {e}", exc_info=True)
            return None
    
    def check_anomalies_job(self):
        """Job: Check for anomalies and send alerts."""
        try:
            logger.info("Running scheduled anomaly check")
            
            # Collect data and calculate KPIs
            data = self.collector.collect_all_data()
            kpis = self.calculator.calculate_all_kpis(data)
            
            # Detect anomalies
            anomalies = self.detector.detect_all_anomalies(kpis)
            
            # Send alert if anomalies detected
            if anomalies.get("anomalies_detected"):
                logger.warning(f"⚠️  {anomalies.get('total_anomalies')} anomaly/anomalies detected")
                self.email_notifier.send_anomaly_alert(anomalies)
            else:
                logger.info("✓ No anomalies detected")
            
            return anomalies
        except Exception as e:
            logger.error(f"Anomaly check job failed: {e}", exc_info=True)
            return None
    
    def generate_weekly_report_job(self):
        """Job: Generate weekly PDF report and email."""
        try:
            logger.info("Running scheduled weekly report generation")
            
            # Collect data and calculate KPIs
            data = self.collector.collect_all_data()
            kpis = self.calculator.calculate_all_kpis(data)
            
            # Detect anomalies (for report)
            anomalies = self.detector.detect_all_anomalies(kpis)
            
            # Generate PDF
            pdf_path = self.pdf_generator.generate_weekly_report(kpis, anomalies)
            logger.info(f"✓ PDF generated: {pdf_path}")
            
            # Send email with PDF
            self.email_notifier.send_weekly_report(kpis, anomalies, pdf_path)
            logger.info("✓ Weekly report email sent")
            
            return pdf_path
        except Exception as e:
            logger.error(f"Weekly report job failed: {e}", exc_info=True)
            return None
    
    def add_job(self, job_func: Callable, trigger: str, **kwargs):
        """
        Add a job to the scheduler.
        
        Args:
            job_func: Function to execute
            trigger: 'cron' or 'interval'
            **kwargs: Trigger-specific arguments
        
        Example:
            # Run every day at midnight
            scheduler.add_job(my_func, 'cron', hour=0, minute=0)
            
            # Run every hour
            scheduler.add_job(my_func, 'interval', hours=1)
        """
        try:
            self.scheduler.add_job(job_func, trigger, **kwargs)
            logger.info(f"Job added: {job_func.__name__} ({trigger})")
        except Exception as e:
            logger.error(f"Failed to add job: {e}", exc_info=True)
    
    def setup_default_schedule(self):
        """Setup default analytics schedule."""
        logger.info("Setting up default analytics schedule")
        
        # Daily data collection at midnight
        self.add_job(
            self.collect_data_job,
            'cron',
            hour=0,
            minute=0,
            id='daily_data_collection'
        )
        logger.info("  ✓ Daily data collection: 12:00 AM")
        
        # Hourly anomaly checks
        self.add_job(
            self.check_anomalies_job,
            'interval',
            hours=1,
            id='hourly_anomaly_check'
        )
        logger.info("  ✓ Hourly anomaly checks")
        
        # Weekly report generation (Sunday at 9 AM)
        self.add_job(
            self.generate_weekly_report_job,
            'cron',
            day_of_week='sun',
            hour=9,
            minute=0,
            id='weekly_report'
        )
        logger.info("  ✓ Weekly report: Sunday 9:00 AM")
        
        logger.info("✓ Default schedule configured")
    
    def start(self, daemon: bool = False):
        """
        Start the scheduler.
        
        Args:
            daemon: Run in background (blocks if False)
        """
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        try:
            self.is_running = True
            logger.info("=" * 60)
            logger.info("SURESH AI ORIGIN - Analytics Scheduler Starting")
            logger.info("=" * 60)
            
            # Print scheduled jobs
            jobs = self.scheduler.get_jobs()
            logger.info(f"\nScheduled Jobs ({len(jobs)}):")
            for job in jobs:
                logger.info(f"  • {job.id}: {job.next_run_time}")
            
            logger.info("\nScheduler running - Press Ctrl+C to stop")
            logger.info("=" * 60)
            
            # Start scheduler
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("\nShutting down scheduler...")
            self.stop()
        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)
            self.is_running = False
    
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            return
        
        logger.info("Stopping scheduler...")
        self.scheduler.shutdown(wait=False)
        self.is_running = False
        logger.info("✓ Scheduler stopped")
    
    def run_once(self, job: str = "all"):
        """
        Run a job once (for testing).
        
        Args:
            job: 'collect', 'anomalies', 'report', or 'all'
        """
        logger.info(f"Running job once: {job}")
        
        if job in ["collect", "all"]:
            self.collect_data_job()
        
        if job in ["anomalies", "all"]:
            self.check_anomalies_job()
        
        if job in ["report", "all"]:
            self.generate_weekly_report_job()


def main():
    """Main entry point for scheduler."""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(
        description="SURESH AI ORIGIN Analytics Scheduler"
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run scheduler as background daemon'
    )
    parser.add_argument(
        '--once',
        choices=['collect', 'anomalies', 'report', 'all'],
        help='Run a job once and exit (for testing)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run test jobs and exit'
    )
    
    args = parser.parse_args()
    
    if not SCHEDULER_AVAILABLE:
        print("\n❌ APScheduler is not installed")
        print("Install with: pip install apscheduler")
        print("\nOr use cron directly:")
        print("  0 0 * * * cd /path/to/project && python analytics_engine_main.py --collect")
        print("  0 9 * * 0 cd /path/to/project && python analytics_engine_main.py --report")
        sys.exit(1)
    
    try:
        scheduler = AnalyticsScheduler()
        
        if args.test:
            # Run test email
            print("\n📧 Testing email configuration...")
            scheduler.email_notifier.send_test_email()
            print("✓ Test complete - check your inbox\n")
            sys.exit(0)
        
        if args.once:
            # Run once and exit
            scheduler.run_once(args.once)
            sys.exit(0)
        
        # Setup default schedule and start
        scheduler.setup_default_schedule()
        scheduler.start(daemon=args.daemon)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
