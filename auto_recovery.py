#!/usr/bin/env python3
"""
Automated Recovery System - SURESH AI ORIGIN
Auto-detects and recovers from common failures
"""

import requests
import logging
import time
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROD_URL = os.getenv('PROD_URL', 'https://suresh-ai-origin.onrender.com')
DB_PATH = 'data.db'

class AutoRecovery:
    """Automatic failure detection and recovery."""
    
    def __init__(self):
        self.recovery_log = 'recovery_log.txt'
        self.failure_count = {}
        self.recovery_attempts = {}
    
    def log_recovery(self, action, status, message=""):
        """Log recovery action."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {action} - {status}: {message}\n"
        
        with open(self.recovery_log, 'a') as f:
            f.write(log_entry)
        
        logger.info(f"{action}: {status} - {message}")
    
    def check_site_health(self):
        """Check if site is responding."""
        try:
            r = requests.get(f'{PROD_URL}/health', timeout=10)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def check_database_corruption(self):
        """Check if database is corrupted."""
        try:
            if not os.path.exists(DB_PATH):
                return False, "Database not found"
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            
            if result == 'ok':
                return True, "Database healthy"
            else:
                return False, f"Corruption detected: {result}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_database_locked(self):
        """Check if database is locked."""
        try:
            conn = sqlite3.connect(DB_PATH, timeout=2)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM orders LIMIT 1")
            conn.close()
            return False, "Database accessible"
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                return True, "Database locked"
            return False, str(e)
    
    def recover_locked_database(self):
        """Recover from locked database."""
        try:
            # Remove lock files
            lock_files = ['data.db-shm', 'data.db-wal']
            for lf in lock_files:
                if os.path.exists(lf):
                    os.remove(lf)
                    logger.info(f"Removed lock file: {lf}")
            
            # Verify recovery
            time.sleep(1)
            is_locked, msg = self.check_database_locked()
            
            if not is_locked:
                self.log_recovery("DATABASE_LOCK_RECOVERY", "SUCCESS", msg)
                return True
            else:
                self.log_recovery("DATABASE_LOCK_RECOVERY", "FAILED", msg)
                return False
        except Exception as e:
            self.log_recovery("DATABASE_LOCK_RECOVERY", "ERROR", str(e))
            return False
    
    def recover_corrupted_database(self):
        """Recover from corrupted database."""
        try:
            logger.warning("Attempting database recovery...")
            
            # Run PRAGMA integrity_check with repair
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            cursor.execute("VACUUM")
            conn.commit()
            conn.close()
            
            # Verify
            is_healthy, msg = self.check_database_corruption()
            
            if is_healthy:
                self.log_recovery("DATABASE_CORRUPTION_RECOVERY", "SUCCESS", msg)
                return True
            else:
                self.log_recovery("DATABASE_CORRUPTION_RECOVERY", "NEEDS_RESTORE", "Manual restore required")
                return False
        except Exception as e:
            self.log_recovery("DATABASE_CORRUPTION_RECOVERY", "ERROR", str(e))
            return False
    
    def check_ai_health(self):
        """Check if AI is responding."""
        try:
            r = requests.post(
                f'{PROD_URL}/api/ai/chat',
                json={'message': 'test'},
                timeout=15
            )
            if r.status_code == 200 and r.json().get('success'):
                return True, "AI responding"
            else:
                return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)
    
    def check_payment_system(self):
        """Check if payment system is healthy."""
        try:
            # Check if Razorpay webhooks are being received
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Count recent webhook events
            cursor.execute(
                "SELECT COUNT(*) FROM webhooks WHERE received_at > datetime('now', '-1 hour')"
            )
            recent_webhooks = cursor.fetchone()[0]
            conn.close()
            
            if recent_webhooks > 0:
                return True, f"Recent webhooks: {recent_webhooks}"
            else:
                return True, "No recent webhooks (may be normal)"
        except Exception as e:
            return False, str(e)
    
    def run_diagnostics(self):
        """Run full system diagnostics."""
        print("\n" + "="*70)
        print("AUTO-RECOVERY SYSTEM DIAGNOSTICS")
        print("="*70)
        print(f"Time: {datetime.now()}")
        print(f"URL: {PROD_URL}")
        print()
        
        diagnostics = {
            'Site Health': lambda: self.check_site_health(),
            'Database Locked': lambda: self.check_database_locked(),
            'Database Corruption': lambda: self.check_database_corruption(),
            'AI System': self.check_ai_health,
            'Payment System': self.check_payment_system
        }
        
        results = {}
        for name, check in diagnostics.items():
            try:
                if callable(check) and not isinstance(check, type):
                    result = check()
                    if isinstance(result, tuple):
                        success, message = result
                        results[name] = success
                        icon = '✅' if success else '❌'
                        print(f"{icon} {name}: {message}")
                    else:
                        results[name] = result
                        icon = '✅' if result else '❌'
                        print(f"{icon} {name}: {'Healthy' if result else 'Failed'}")
            except Exception as e:
                results[name] = False
                print(f"❌ {name}: ERROR - {str(e)[:50]}")
        
        # Auto-recovery actions
        print("\n" + "-"*70)
        print("AUTO-RECOVERY ACTIONS")
        print("-"*70)
        
        if not results.get('Database Locked'):
            is_locked, msg = self.check_database_locked()
            if is_locked:
                print("🔧 Attempting to recover locked database...")
                if self.recover_locked_database():
                    print("✅ Database lock recovered!")
                else:
                    print("❌ Failed to recover database lock")
        
        if not results.get('Database Corruption'):
            is_healthy, msg = self.check_database_corruption()
            if not is_healthy:
                print("🔧 Attempting to recover corrupted database...")
                if self.recover_corrupted_database():
                    print("✅ Database corruption recovered!")
                else:
                    print("❌ Manual restore required")
        
        # Summary
        print("\n" + "="*70)
        total = len(results)
        passed = sum(results.values())
        health = passed / total * 100 if total > 0 else 0
        icon = "✅" if health >= 80 else "⚠️"
        print(f"{icon} System Health: {passed}/{total} ({health:.0f}%)")
        print("="*70)
        
        return health >= 80

def main():
    import sys
    
    recovery = AutoRecovery()
    
    if len(sys.argv) < 2:
        # Run diagnostics by default
        success = recovery.run_diagnostics()
        sys.exit(0 if success else 1)
    
    command = sys.argv[1]
    
    if command == 'diagnose':
        success = recovery.run_diagnostics()
        sys.exit(0 if success else 1)
    
    elif command == 'unlock-db':
        print("🔧 Unlocking database...")
        if recovery.recover_locked_database():
            print("✅ Database unlocked")
            sys.exit(0)
        else:
            print("❌ Failed to unlock database")
            sys.exit(1)
    
    elif command == 'repair-db':
        print("🔧 Repairing database...")
        if recovery.recover_corrupted_database():
            print("✅ Database repaired")
            sys.exit(0)
        else:
            print("❌ Failed to repair database")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
