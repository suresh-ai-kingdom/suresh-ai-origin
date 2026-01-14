#!/usr/bin/env python3
"""Background monitoring service - runs health checks continuously."""

import os
import sys
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from monitor_production import ProductionMonitor

CHECK_INTERVAL = int(os.getenv('MONITOR_INTERVAL', '300'))  # 5 minutes
ALERT_ON_STARTUP = os.getenv('MONITOR_ALERT_ON_STARTUP', 'false').lower() == 'true'


def main():
    """Run monitoring service continuously."""
    monitor = ProductionMonitor()
    
    print(f"{'='*60}")
    print(f"🔍 Production Monitor Service Starting")
    print(f"{'='*60}")
    print(f"   Interval: {CHECK_INTERVAL}s ({CHECK_INTERVAL/60:.1f} minutes)")
    print(f"   URL: {os.getenv('PROD_URL', 'https://suresh-ai-origin.onrender.com')}")
    print(f"   Alerts: {'webhook' if os.getenv('ALERT_WEBHOOK') else 'none'} + {'email' if os.getenv('EMAIL_PASS') else 'none'}")
    print(f"   Started: {datetime.now()}")
    print(f"\nPress Ctrl+C to stop\n")
    
    if ALERT_ON_STARTUP:
        monitor.send_alert("Monitor service started", f"Health monitoring active at {datetime.now()}")
    
    consecutive_errors = 0
    max_errors = 10
    
    try:
        while True:
            try:
                monitor.run_checks()
                consecutive_errors = 0
            except Exception as exc:
                consecutive_errors += 1
                print(f"❌ Check failed: {exc}")
                
                if consecutive_errors >= max_errors:
                    monitor.send_alert(
                        "Monitor service failing",
                        f"Health checks failed {consecutive_errors} consecutive times: {exc}"
                    )
                    print(f"⚠️  Too many consecutive errors ({consecutive_errors}), stopping service")
                    return 1
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n👋 Monitor service stopped")
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
