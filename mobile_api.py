"""Mobile API v2 - REST endpoints for mobile apps."""
import os
import jwt
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'change-me-in-production')
JWT_EXPIRY = 86400 * 7  # 7 days


def generate_jwt_token(user_id: str, tier: str = 'free') -> str:
    """Generate JWT token for mobile client."""
    payload = {
        'user_id': user_id,
        'tier': tier,
        'iat': time.time(),
        'exp': time.time() + JWT_EXPIRY,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise ValueError('Token expired')
    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')


def mobile_auth_required(f):
    """Decorator for mobile API endpoints."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization'}), 401
        
        try:
            token = auth.split(' ')[1]
            payload = verify_jwt_token(token)
            request.user_id = payload['user_id']
            request.user_tier = payload['tier']
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 401
    
    return wrapper


def rate_limit_by_tier(f):
    """Rate limiter based on user tier."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        tier = getattr(request, 'user_tier', 'free')
        
        # Limits per minute
        limits = {
            'free': 10,
            'starter': 50,
            'pro': 200,
            'premium': 1000,
        }
        
        limit = limits.get(tier, 10)
        
        # TODO: Implement Redis-based rate limiting
        # For now, just log
        print(f"Rate limit for {tier}: {limit} req/min")
        
        return f(*args, **kwargs)
    
    return wrapper


# Mobile API Routes Template
MOBILE_API_ROUTES = {
    'auth': {
        'POST /api/v2/auth/login': 'Login with email/password',
        'POST /api/v2/auth/signup': 'Create new account',
        'POST /api/v2/auth/refresh': 'Refresh JWT token',
    },
    'content': {
        'GET /api/v2/content/prompts': 'List available prompts',
        'POST /api/v2/content/generate': 'Generate content',
        'GET /api/v2/content/{id}': 'Get generated content',
    },
    'sync': {
        'POST /api/v2/sync/push': 'Push local changes',
        'GET /api/v2/sync/pull': 'Get remote changes',
        'POST /api/v2/sync/status': 'Check sync status',
    },
    'analytics': {
        'GET /api/v2/analytics/usage': 'Get usage stats',
        'GET /api/v2/analytics/credits': 'Get credit balance',
    },
}


# Offline Sync Queue
class SyncQueue:
    """Queue for offline changes to sync when online."""
    
    def __init__(self):
        self.queue = []
    
    def add(self, action: str, resource: str, data: dict):
        """Add action to queue."""
        self.queue.append({
            'id': str(uuid.uuid4()),
            'action': action,  # 'create', 'update', 'delete'
            'resource': resource,  # 'prompt', 'content', etc
            'data': data,
            'timestamp': time.time(),
            'status': 'pending'  # pending, synced, conflict
        })
    
    def get_pending(self) -> list:
        """Get all pending sync items."""
        return [item for item in self.queue if item['status'] == 'pending']
    
    def mark_synced(self, item_id: str):
        """Mark item as successfully synced."""
        for item in self.queue:
            if item['id'] == item_id:
                item['status'] = 'synced'


# Push Notification Service
class PushNotificationService:
    """Send push notifications to mobile clients."""
    
    def __init__(self, fcm_key: str = None):
        self.fcm_key = fcm_key or os.getenv('FCM_SERVER_KEY')
    
    def send_notification(self, device_token: str, title: str, body: str, data: dict = None):
        """Send push notification via Firebase Cloud Messaging."""
        if not self.fcm_key:
            print("⚠️  FCM_SERVER_KEY not configured")
            return False
        
        # TODO: Implement FCM push
        print(f"📲 Push: {title} → {device_token[:20]}...")
        return True
    
    def send_batch(self, device_tokens: list, title: str, body: str):
        """Send push to multiple devices."""
        for token in device_tokens:
            self.send_notification(token, title, body)
