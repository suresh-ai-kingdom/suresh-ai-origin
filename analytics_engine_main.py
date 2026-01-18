"""
Analytics Engine Main Orchestrator
Ties all modules together for complete analytics workflow
"""

import logging
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add analytics_engine to path
sys.path.insert(0, str(Path(__file__).parent))

from analytics_engine.data_collector import DataCollector
from analytics_engine.kpi_calculator import KPICalculator
from analytics_engine.anomaly_detector import AnomalyDetector
from analytics_engine.pdf_generator import PDFGenerator
from analytics_engine.email_notifier import EmailNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/analytics_engine.log')
    ]
)

logger = logging.getLogger("AnalyticsEngineMain")


class AnalyticsEngine:
    """Main analytics engine orchestrator."""
    
    def __init__(self):
        """Initialize all components."""
        logger.info("Initializing Analytics Engine")
        
        try:
            self.collector = DataCollector()
            self.calculator = KPICalculator()
            self.detector = AnomalyDetector()
            self.pdf_generator = PDFGenerator()
            self.email_notifier = EmailNotifier()
            
            logger.info("✓ All components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}", exc_info=True)
            raise
    
    def collect_data(self) -> dict:
        """
        Collect data from all sources.
        
        Returns:
            Dictionary with data from GA, Stripe, referrals, prompts
        """
        logger.info("=" * 60)
        logger.info("STEP 1: Collecting Data")
        logger.info("=" * 60)
        
        try:
            data = self.collector.collect_all_data()
            
            logger.info("\nData Collection Summary:")
            logger.info(f"  GA Data: {len(data.get('ga_data', []))} records")
            logger.info(f"  Stripe Data: {data.get('stripe_data', {}).get('active_subscriptions', 0)} active subs")
            logger.info(f"  Referral Sources: {len(data.get('referral_data', []))}")
            logger.info(f"  Prompt Stats: {len(data.get('prompt_stats', []))} features")
            logger.info("✓ Data collection complete\n")
            
            return data
        except Exception as e:
            logger.error(f"Data collection failed: {e}", exc_info=True)
            return {}
    
    def calculate_kpis(self, data: dict) -> dict:
        """
        Calculate all KPIs from collected data.
        
        Args:
            data: Collected data from all sources
        
        Returns:
            Dictionary with all calculated KPIs
        """
        logger.info("=" * 60)
        logger.info("STEP 2: Calculating KPIs")
        logger.info("=" * 60)
        
        try:
            kpis = self.calculator.calculate_all_kpis(data)
            
            revenue = kpis.get("revenue_metrics", {})
            growth = kpis.get("growth_metrics", {})
            prompts = kpis.get("prompt_statistics", {})
            
            logger.info("\nKPI Summary:")
            logger.info(f"  MRR: ₹{revenue.get('mrr', 0):,.2f}")
            logger.info(f"  ARR: ₹{revenue.get('arr', 0):,.2f}")
            logger.info(f"  Churn Rate: {revenue.get('churn_rate', 0):.1f}%")
            logger.info(f"  Active Users: {growth.get('total_active_users', 0):,}")
            logger.info(f"  User Growth (WoW): {growth.get('user_growth_wow', 0):+.1f}%")
            logger.info(f"  Total Prompts: {prompts.get('total_prompts', 0):,}")
            logger.info("✓ KPI calculation complete\n")
            
            return kpis
        except Exception as e:
            logger.error(f"KPI calculation failed: {e}", exc_info=True)
            return {}
    
    def detect_anomalies(self, kpis: dict) -> dict:
        """
        Detect anomalies in KPIs.
        
        Args:
            kpis: Calculated KPIs
        
        Returns:
            Dictionary with anomaly detection results
        """
        logger.info("=" * 60)
        logger.info("STEP 3: Detecting Anomalies")
        logger.info("=" * 60)
        
        try:
            anomalies = self.detector.detect_all_anomalies(kpis)
            
            if anomalies.get("anomalies_detected"):
                logger.warning(f"\n⚠️  {anomalies.get('total_anomalies')} ANOMALY/ANOMALIES DETECTED")
                logger.warning(f"  Critical: {anomalies.get('critical_count', 0)}")
                logger.warning(f"  Warnings: {anomalies.get('warning_count', 0)}")
                
                logger.warning("\nDetected Anomalies:")
                for anom in anomalies.get("all_anomalies", []):
                    logger.warning(f"  [{anom['severity'].upper()}] {anom['message']}")
            else:
                logger.info("\n✓ No anomalies detected - all metrics healthy")
            
            logger.info("")
            return anomalies
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}", exc_info=True)
            return {"anomalies_detected": False}
    
    def generate_report(self, kpis: dict, anomalies: dict) -> str:
        """
        Generate PDF report.
        
        Args:
            kpis: Calculated KPIs
            anomalies: Anomaly detection results
        
        Returns:
            Path to generated PDF file
        """
        logger.info("=" * 60)
        logger.info("STEP 4: Generating PDF Report")
        logger.info("=" * 60)
        
        try:
            pdf_path = self.pdf_generator.generate_weekly_report(kpis, anomalies)
            logger.info(f"\n✓ PDF report generated: {pdf_path}\n")
            return pdf_path
        except Exception as e:
            logger.error(f"PDF generation failed: {e}", exc_info=True)
            return None
    
    def send_alerts(self, kpis: dict, anomalies: dict, pdf_path: str = None, 
                   force_report: bool = False):
        """
        Send email alerts and reports.
        
        Args:
            kpis: Calculated KPIs
            anomalies: Anomaly detection results
            pdf_path: Path to PDF report (optional)
            force_report: Force weekly report email even without anomalies
        """
        logger.info("=" * 60)
        logger.info("STEP 5: Sending Email Notifications")
        logger.info("=" * 60)
        
        try:
            # Send anomaly alert if detected
            if anomalies.get("anomalies_detected"):
                logger.info("\n📧 Sending anomaly alert...")
                success = self.email_notifier.send_anomaly_alert(anomalies)
                if success:
                    logger.info("✓ Anomaly alert sent")
                else:
                    logger.error("✗ Failed to send anomaly alert")
            
            # Send weekly report if PDF exists or forced
            if pdf_path or force_report:
                logger.info("\n📧 Sending weekly report...")
                success = self.email_notifier.send_weekly_report(kpis, anomalies, pdf_path)
                if success:
                    logger.info("✓ Weekly report sent")
                else:
                    logger.error("✗ Failed to send weekly report")
            
            logger.info("")
        except Exception as e:
            logger.error(f"Email sending failed: {e}", exc_info=True)
    
    def run_full_cycle(self, send_report: bool = False, check_anomalies: bool = True):
        """
        Run complete analytics cycle.
        
        Args:
            send_report: Generate and send PDF report
            check_anomalies: Check for anomalies and send alerts
        """
        logger.info("\n" + "=" * 60)
        logger.info("SURESH AI ORIGIN - Analytics Engine")
        logger.info(f"Started: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        logger.info("=" * 60 + "\n")
        
        try:
            # Step 1: Collect data
            data = self.collect_data()
            if not data:
                logger.error("❌ Data collection failed - aborting cycle")
                return
            
            # Step 2: Calculate KPIs
            kpis = self.calculate_kpis(data)
            if not kpis:
                logger.error("❌ KPI calculation failed - aborting cycle")
                return
            
            # Step 3: Detect anomalies
            anomalies = None
            if check_anomalies:
                anomalies = self.detect_anomalies(kpis)
            
            # Step 4: Generate PDF report
            pdf_path = None
            if send_report:
                pdf_path = self.generate_report(kpis, anomalies or {})
            
            # Step 5: Send alerts
            if check_anomalies or send_report:
                self.send_alerts(kpis, anomalies or {}, pdf_path, force_report=send_report)
            
            logger.info("=" * 60)
            logger.info("✓ ANALYTICS CYCLE COMPLETE")
            logger.info(f"Finished: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
            logger.info("=" * 60 + "\n")
        
        except Exception as e:
            logger.error(f"❌ Analytics cycle failed: {e}", exc_info=True)
            logger.info("=" * 60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SURESH AI ORIGIN Analytics Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full cycle (collect + calculate + detect anomalies)
  python analytics_engine_main.py --collect --check-anomalies
  
  # Generate and send weekly report
  python analytics_engine_main.py --collect --report
  
  # Full cycle with report
  python analytics_engine_main.py --collect --check-anomalies --report
  
  # Just collect data (no alerts)
  python analytics_engine_main.py --collect
"""
    )
    
    parser.add_argument(
        '--collect',
        action='store_true',
        help='Collect data from all sources'
    )
    parser.add_argument(
        '--check-anomalies',
        action='store_true',
        help='Check for anomalies and send alerts'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate PDF report and send email'
    )
    parser.add_argument(
        '--test-email',
        action='store_true',
        help='Send test email to verify configuration'
    )
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any([args.collect, args.check_anomalies, args.report, args.test_email]):
        parser.print_help()
        sys.exit(0)
    
    try:
        engine = AnalyticsEngine()
        
        # Test email configuration
        if args.test_email:
            logger.info("Sending test email...")
            success = engine.email_notifier.send_test_email()
            if success:
                print("\n✓ Test email sent - check your inbox!")
            else:
                print("\n✗ Failed to send test email - check credentials")
            sys.exit(0)
        
        # Run analytics cycle
        if args.collect:
            engine.run_full_cycle(
                send_report=args.report,
                check_anomalies=args.check_anomalies
            )
        else:
            logger.warning("No --collect flag - use --collect to run analytics")
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    main()
