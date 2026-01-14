#!/usr/bin/env python3
"""
Incident Response Guide - SURESH AI ORIGIN
Procedures for common incidents and emergency recovery
"""

import json
import os
from datetime import datetime

class IncidentResponse:
    """Incident response procedures and logging."""
    
    @staticmethod
    def log_incident(incident_type, severity, description, actions_taken=None):
        """Log an incident."""
        incident = {
            'timestamp': datetime.now().isoformat(),
            'type': incident_type,
            'severity': severity,
            'description': description,
            'actions_taken': actions_taken or []
        }
        
        with open('incidents.json', 'a') as f:
            f.write(json.dumps(incident) + '\n')
        
        return incident
    
    @staticmethod
    def get_playbook(incident_type):
        """Get response playbook for incident type."""
        
        playbooks = {
            'DATABASE_DOWN': {
                'description': 'Database is unresponsive',
                'severity': 'CRITICAL',
                'response_time': '2 minutes',
                'actions': [
                    '1. Check database status in Render dashboard',
                    '2. Verify network connectivity',
                    '3. Check database logs: Render → Logs',
                    '4. If locked: python auto_recovery.py unlock-db',
                    '5. If corrupted: python auto_recovery.py repair-db',
                    '6. If failed: python backup_manager.py restore [backup]',
                    '7. Restart service: python automation_engine.py diagnose',
                    '8. Verify health: python comprehensive_health_check.py'
                ]
            },
            'SITE_DOWN': {
                'description': 'Production site returning 5xx errors',
                'severity': 'CRITICAL',
                'response_time': '5 minutes',
                'actions': [
                    '1. Check site: curl https://suresh-ai-origin.onrender.com',
                    '2. Check Render logs: Dashboard → Logs',
                    '3. Look for recent deployments or errors',
                    '4. If recent deploy: Trigger rollback in Render',
                    '5. If not deploy-related: Check database',
                    '6. Restart service: Render Dashboard → Restart',
                    '7. Monitor recovery: python monitor_production.py',
                    '8. Verify health: python comprehensive_health_check.py'
                ]
            },
            'AI_NOT_RESPONDING': {
                'description': 'Groq AI endpoint timing out',
                'severity': 'HIGH',
                'response_time': '5 minutes',
                'actions': [
                    '1. Test AI endpoint: curl -X POST .../api/ai/chat',
                    '2. Check Groq status: https://status.groq.com',
                    '3. Verify API key in Render environment',
                    '4. Check quota usage: Monitor response times',
                    '5. Check rate limiting logs',
                    '6. If quota exceeded: Wait 1 hour or upgrade',
                    '7. If key expired: Update in Render env vars',
                    '8. Monitor: python monitor_production.py'
                ]
            },
            'PAYMENT_FAILURE': {
                'description': 'Payment gateway errors',
                'severity': 'HIGH',
                'response_time': '10 minutes',
                'actions': [
                    '1. Check Razorpay dashboard: https://dashboard.razorpay.com',
                    '2. Check webhook events: /admin/webhooks',
                    '3. Verify payment keys in Render environment',
                    '4. Check webhook signature verification',
                    '5. Review recent payment failures in database',
                    '6. Contact Razorpay support if needed',
                    '7. Enable manual payment processing if needed',
                    '8. Notify affected customers'
                ]
            },
            'HIGH_ERROR_RATE': {
                'description': 'Error rate exceeds 1%',
                'severity': 'HIGH',
                'response_time': '10 minutes',
                'actions': [
                    '1. Get error stats: python error_tracking.py stats',
                    '2. Identify error patterns',
                    '3. Check logs: tail -100 errors.log',
                    '4. Identify root cause (deployment, database, API)',
                    '5. If deployment: Rollback',
                    '6. If database: Run auto_recovery.py diagnose',
                    '7. If API: Check third-party status',
                    '8. Monitor recovery: tail -f errors.log'
                ]
            },
            'LOW_DISK_SPACE': {
                'description': 'Disk usage above 90%',
                'severity': 'MEDIUM',
                'response_time': '30 minutes',
                'actions': [
                    '1. Check disk usage: du -sh /',
                    '2. Identify large files/directories',
                    '3. Clean up old logs: python error_tracking.py',
                    '4. Archive old backups: keep only 30 days',
                    '5. Remove old database WAL files',
                    '6. Consider migration to PostgreSQL (larger storage)',
                    '7. Monitor: python monitor_production.py'
                ]
            },
            'BACKUP_FAILED': {
                'description': 'Automated backup did not complete',
                'severity': 'HIGH',
                'response_time': '30 minutes',
                'actions': [
                    '1. Check backup logs: grep ERROR automation.log',
                    '2. Try manual backup: python backup_manager.py create manual',
                    '3. Verify database is accessible',
                    '4. Check disk space',
                    '5. Check file permissions in backups/ directory',
                    '6. If persistent: Restart database',
                    '7. Consider alternative backup location',
                    '8. Notify admin of issue'
                ]
            },
            'PERFORMANCE_DEGRADATION': {
                'description': 'Response times > 2 seconds',
                'severity': 'MEDIUM',
                'response_time': '15 minutes',
                'actions': [
                    '1. Check current load: python monitor_production.py',
                    '2. Identify slow endpoints from logs',
                    '3. Profile database queries',
                    '4. Check if recent deployment',
                    '5. Run performance optimization: python performance.py optimize',
                    '6. Check cache hit rates',
                    '7. Consider enabling Redis caching',
                    '8. Monitor: tail -f automation.log'
                ]
            }
        }
        
        return playbooks.get(incident_type, {
            'description': 'Unknown incident',
            'severity': 'UNKNOWN',
            'response_time': 'Unknown',
            'actions': ['Contact development team for guidance']
        })

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Incident Response Playbooks")
        print("="*60)
        print("\nAvailable playbooks:")
        for incident_type in IncidentResponse.get_playbook('UNKNOWN').keys():
            print(f"  • {incident_type}")
        print("\nUsage: python incident_response.py [incident_type]")
        sys.exit(1)
    
    incident_type = sys.argv[1].upper()
    playbook = IncidentResponse.get_playbook(incident_type)
    
    print("\n" + "="*60)
    print(f"INCIDENT RESPONSE: {incident_type}")
    print("="*60)
    print(f"\nDescription: {playbook.get('description')}")
    print(f"Severity: {playbook.get('severity')}")
    print(f"Target Response Time: {playbook.get('response_time')}")
    print("\nActions:")
    for action in playbook.get('actions', []):
        print(f"  {action}")
    print("\n" + "="*60)
    
    # Log incident if requested
    if len(sys.argv) > 2 and sys.argv[2] == '--log':
        incident = IncidentResponse.log_incident(
            incident_type,
            playbook.get('severity'),
            playbook.get('description')
        )
        print(f"\n✅ Incident logged: {incident['timestamp']}")

if __name__ == '__main__':
    main()
