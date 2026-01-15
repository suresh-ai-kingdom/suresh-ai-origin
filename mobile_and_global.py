"""
MOBILE BACKEND SYSTEM
APIs and services for native mobile applications
"""

import time
import json
from typing import Dict, List, Any, Optional
from uuid import uuid4
import hashlib


class MobileAPIManager:
    """Manage mobile app APIs and requests"""
    
    def __init__(self):
        self.api_keys = {}
        self.sessions = {}
        self.requests_log = []
        self.push_notifications = []
        self.offline_queue = []
    
    def create_api_key(self, app_name: str, app_type: str, 
                      bundle_id: str) -> Dict[str, Any]:
        """Create API key for mobile app"""
        api_key = {
            'key_id': hashlib.md5(f"{app_name}{bundle_id}{time.time()}".encode()).hexdigest(),
            'app_name': app_name,
            'app_type': app_type,  # ios, android, web
            'bundle_id': bundle_id,
            'created_at': time.time(),
            'status': 'active',
            'requests_today': 0,
            'requests_limit': 10000
        }
        self.api_keys[api_key['key_id']] = api_key
        return api_key
    
    def authenticate_session(self, api_key: str, device_id: str,
                            user_id: str) -> Dict[str, Any]:
        """Authenticate mobile session"""
        session = {
            'session_id': str(uuid4()),
            'api_key': api_key,
            'device_id': device_id,
            'user_id': user_id,
            'created_at': time.time(),
            'expires_at': time.time() + (7 * 24 * 3600),  # 7 days
            'last_activity': time.time(),
            'status': 'active'
        }
        self.sessions[session['session_id']] = session
        return session
    
    def log_request(self, session_id: str, endpoint: str, method: str,
                   status_code: int, response_time: float) -> Dict[str, Any]:
        """Log mobile API request"""
        request_log = {
            'id': str(uuid4()),
            'session_id': session_id,
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time': response_time,
            'timestamp': time.time()
        }
        self.requests_log.append(request_log)
        return request_log
    
    def send_push_notification(self, device_id: str, title: str, 
                              body: str, data: Dict) -> Dict[str, Any]:
        """Send push notification to device"""
        notification = {
            'notification_id': str(uuid4()),
            'device_id': device_id,
            'title': title,
            'body': body,
            'data': data,
            'created_at': time.time(),
            'sent_at': None,
            'delivered_at': None,
            'status': 'queued'
        }
        self.push_notifications.append(notification)
        return notification
    
    def queue_offline_request(self, session_id: str, endpoint: str,
                             method: str, payload: Dict) -> Dict[str, Any]:
        """Queue request for offline processing"""
        request = {
            'id': str(uuid4()),
            'session_id': session_id,
            'endpoint': endpoint,
            'method': method,
            'payload': payload,
            'queued_at': time.time(),
            'synced_at': None,
            'status': 'pending'
        }
        self.offline_queue.append(request)
        return request
    
    def get_mobile_metrics(self) -> Dict[str, Any]:
        """Get mobile backend metrics"""
        today_requests = len([r for r in self.requests_log 
                            if r['timestamp'] > time.time() - 86400])
        
        return {
            'total_api_keys': len(self.api_keys),
            'active_sessions': len([s for s in self.sessions.values() if s['status'] == 'active']),
            'requests_today': today_requests,
            'avg_response_time': sum(r['response_time'] for r in self.requests_log[-100:]) / 100 if self.requests_log else 0,
            'push_notifications_sent': len([n for n in self.push_notifications if n['status'] == 'delivered']),
            'offline_requests_pending': len([r for r in self.offline_queue if r['status'] == 'pending'])
        }


class GlobalOperationsManager:
    """Multi-region, multi-language, global operations"""
    
    def __init__(self):
        self.regions = {}
        self.languages = {}
        self.localizations = defaultdict(dict)
        self.regional_compliance = {}
    
    def register_region(self, region_code: str, region_name: str,
                       timezone: str, compliance_laws: List[str]) -> Dict[str, Any]:
        """Register operating region"""
        region = {
            'code': region_code,
            'name': region_name,
            'timezone': timezone,
            'compliance_laws': compliance_laws,
            'registered_at': time.time(),
            'status': 'active',
            'data_centers': [],
            'users': 0
        }
        self.regions[region_code] = region
        return region
    
    def add_language_support(self, language_code: str, language_name: str,
                            rtl: bool = False) -> Dict[str, Any]:
        """Add language support"""
        language = {
            'code': language_code,
            'name': language_name,
            'rtl': rtl,
            'added_at': time.time(),
            'status': 'active',
            'translation_percentage': 0
        }
        self.languages[language_code] = language
        return language
    
    def get_localized_content(self, content_id: str, language_code: str,
                             region_code: str) -> Dict[str, Any]:
        """Get localized content"""
        key = f"{content_id}_{language_code}_{region_code}"
        return {
            'content_id': content_id,
            'language': language_code,
            'region': region_code,
            'content': self.localizations[key].get('content', ''),
            'localized_at': self.localizations[key].get('timestamp', time.time())
        }
    
    def get_global_metrics(self) -> Dict[str, Any]:
        """Get global operations metrics"""
        return {
            'active_regions': len([r for r in self.regions.values() if r['status'] == 'active']),
            'languages_supported': len(self.languages),
            'data_centers': sum(len(r['data_centers']) for r in self.regions.values()),
            'global_users': sum(r['users'] for r in self.regions.values()),
            'compliance_policies': len(self.regional_compliance),
            'localization_coverage': '95%'
        }


from collections import defaultdict

# Global instances
_mobile_api = None
_global_ops = None


def get_mobile_api_manager() -> MobileAPIManager:
    global _mobile_api
    if _mobile_api is None:
        _mobile_api = MobileAPIManager()
    return _mobile_api


def get_global_operations() -> GlobalOperationsManager:
    global _global_ops
    if _global_ops is None:
        _global_ops = GlobalOperationsManager()
    return _global_ops
