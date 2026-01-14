#!/usr/bin/env python3
"""
Deployment Automation - SURESH AI ORIGIN
Automated post-deployment validation and rollback
"""

import requests
import subprocess
import json
import logging
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROD_URL = os.getenv('PROD_URL', 'https://suresh-ai-origin.onrender.com')

class DeploymentValidator:
    """Validates deployments and triggers rollback if needed."""
    
    def __init__(self):
        self.deployment_log = 'deployments.log'
        self.rollback_enabled = True
        self.grace_period = 300  # 5 minutes before rollback
    
    def log_deployment(self, event, status, details=""):
        """Log deployment event."""
        timestamp = datetime.now().isoformat()
        entry = {
            'timestamp': timestamp,
            'event': event,
            'status': status,
            'details': details
        }
        
        with open(self.deployment_log, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        logger.info(f"{event}: {status} - {details}")
    
    def wait_for_deployment(self, timeout=600):
        """Wait for Render deployment to complete."""
        logger.info(f"⏳ Waiting for deployment (timeout: {timeout}s)")
        
        start = time.time()
        while time.time() - start < timeout:
            try:
                r = requests.get(f'{PROD_URL}/health', timeout=10)
                if r.status_code == 200:
                    logger.info("✅ Deployment detected as live")
                    return True
            except:
                pass
            
            time.sleep(5)
        
        logger.error("❌ Deployment timeout")
        return False
    
    def validate_health(self):
        """Validate system health after deployment."""
        checks = {
            'site': self.check_site,
            'health': self.check_health_endpoint,
            'ai': self.check_ai,
            'database': self.check_database
        }
        
        results = {}
        for name, check in checks.items():
            try:
                results[name] = check()
                logger.info(f"{'✅' if results[name] else '❌'} {name.upper()}: {'PASS' if results[name] else 'FAIL'}")
            except Exception as e:
                results[name] = False
                logger.error(f"❌ {name.upper()}: ERROR - {e}")
        
        return results
    
    def check_site(self):
        """Check if site is responding."""
        r = requests.get(PROD_URL, timeout=10)
        return r.status_code == 200 and 'SURESH' in r.text
    
    def check_health_endpoint(self):
        """Check health endpoint."""
        r = requests.get(f'{PROD_URL}/health', timeout=10)
        return r.status_code == 200 and r.json().get('status') == 'healthy'
    
    def check_ai(self):
        """Check AI functionality."""
        r = requests.post(
            f'{PROD_URL}/api/ai/chat',
            json={'message': 'test'},
            timeout=30
        )
        return r.status_code == 200 and r.json().get('success')
    
    def check_database(self):
        """Check database connectivity."""
        r = requests.get(f'{PROD_URL}/api/analytics/daily-revenue', timeout=10)
        return r.status_code == 200
    
    def trigger_rollback(self):
        """Trigger automatic rollback."""
        if not self.rollback_enabled:
            logger.warning("Rollback is disabled")
            return False
        
        try:
            logger.critical("🔄 TRIGGERING AUTOMATIC ROLLBACK")
            
            # Get previous commit
            result = subprocess.run(
                ['git', 'log', '--oneline', '-n', '2'],
                capture_output=True,
                text=True
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                logger.error("Cannot find previous commit for rollback")
                return False
            
            previous_commit = lines[1].split()[0]
            logger.info(f"Rolling back to: {previous_commit}")
            
            # Rollback
            subprocess.run(['git', 'reset', '--hard', previous_commit], check=True)
            subprocess.run(['git', 'push', '--force', 'origin', 'main'], check=True)
            
            logger.info("✅ Rollback triggered successfully")
            self.log_deployment("ROLLBACK", "SUCCESS", f"Rolled back to {previous_commit}")
            
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            self.log_deployment("ROLLBACK", "FAILED", str(e))
            return False
    
    def validate_deployment(self):
        """Full deployment validation with automatic rollback."""
        print("\n" + "="*70)
        print("DEPLOYMENT VALIDATION")
        print("="*70)
        print(f"URL: {PROD_URL}")
        print(f"Time: {datetime.now()}")
        print()
        
        # Wait for deployment
        logger.info("📦 Waiting for deployment...")
        if not self.wait_for_deployment():
            logger.error("Deployment failed to come online")
            self.log_deployment("DEPLOYMENT", "FAILED", "Timeout waiting for site")
            return False
        
        # Grace period
        logger.info(f"⏰ Grace period: {self.grace_period}s")
        time.sleep(self.grace_period)
        
        # Validate health
        logger.info("🔍 Validating system health...")
        results = self.validate_health()
        
        # Check results
        passed = sum(results.values())
        total = len(results)
        
        print(f"\n📊 Validation Results: {passed}/{total} checks passed")
        
        if passed >= 3:  # At least 3 checks must pass
            logger.info("✅ DEPLOYMENT VALIDATION PASSED")
            self.log_deployment("DEPLOYMENT", "SUCCESS", f"{passed}/{total} checks passed")
            print("✅ Deployment validated successfully")
            return True
        else:
            logger.error("❌ DEPLOYMENT VALIDATION FAILED - Triggering rollback")
            self.log_deployment("DEPLOYMENT", "FAILED", f"Only {passed}/{total} checks passed")
            
            if self.trigger_rollback():
                print("✅ Automatic rollback triggered")
                return False
            else:
                print("❌ Rollback failed - manual intervention required")
                return False

def main():
    import sys
    
    validator = DeploymentValidator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'no-rollback':
            validator.rollback_enabled = False
            logger.info("Rollback disabled")
    
    success = validator.validate_deployment()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
