"""API Marketplace - Developer portal, SDK showcase, API keys, usage analytics."""
import uuid
import time
from typing import Dict, List
import json

class DeveloperPortal:
    """Developer self-service portal."""
    
    def __init__(self):
        self.developers = {}  # dev_id -> developer_config
        self.api_keys = {}    # api_key -> key_config
        self.applications = {} # app_id -> application_config
    
    def create_developer_account(self, email: str, name: str) -> Dict:
        """Create developer account."""
        dev_id = f'dev_{uuid.uuid4().hex[:8]}'
        
        developer = {
            'id': dev_id,
            'email': email,
            'name': name,
            'created_at': time.time(),
            'tier': 'free',  # free, pro, enterprise
            'api_keys': [],
            'applications': [],
            'verified': False,
        }
        
        self.developers[dev_id] = developer
        
        print(f"👨‍💻 Developer account created: {dev_id}")
        
        return developer
    
    def create_application(self, dev_id: str, app_name: str, app_type: str = 'web') -> Dict:
        """Create application (for API key management)."""
        if dev_id not in self.developers:
            return {'error': 'Developer not found'}
        
        app_id = f'app_{uuid.uuid4().hex[:8]}'
        
        application = {
            'id': app_id,
            'dev_id': dev_id,
            'name': app_name,
            'type': app_type,  # web, mobile, backend, cli
            'created_at': time.time(),
            'status': 'active',
            'api_keys': [],
            'webhook_url': None,
        }
        
        self.applications[app_id] = application
        self.developers[dev_id]['applications'].append(app_id)
        
        return application
    
    def create_api_key(self, app_id: str, key_name: str = 'default') -> Dict:
        """Create API key for application."""
        if app_id not in self.applications:
            return {'error': 'Application not found'}
        
        app = self.applications[app_id]
        
        # Generate key (format: sk_live_<random>)
        api_key = f'sk_live_{uuid.uuid4().hex[:32]}'
        
        key_config = {
            'id': f'key_{uuid.uuid4().hex[:8]}',
            'key': api_key,  # Only shown once
            'masked': f'sk_live_****{api_key[-8:]}',
            'name': key_name,
            'app_id': app_id,
            'created_at': time.time(),
            'last_used': None,
            'status': 'active',
            'scopes': ['content.generate', 'content.list', 'analytics.read'],
            'rate_limit': 1000,  # requests per minute
        }
        
        self.api_keys[api_key] = key_config
        app['api_keys'].append(key_config['id'])
        
        return key_config  # Return unmasked only on creation
    
    def rotate_api_key(self, key_id: str) -> Dict:
        """Rotate API key (create new, deprecate old)."""
        for api_key, config in self.api_keys.items():
            if config['id'] == key_id:
                config['status'] = 'deprecated'
                config['deprecated_at'] = time.time()
                
                # Create replacement key
                new_key = f'sk_live_{uuid.uuid4().hex[:32]}'
                new_config = config.copy()
                new_config['key'] = new_key
                new_config['id'] = f'key_{uuid.uuid4().hex[:8]}'
                new_config['created_at'] = time.time()
                
                self.api_keys[new_key] = new_config
                
                return new_config
        
        return {'error': 'Key not found'}
    
    def get_developer_dashboard(self, dev_id: str) -> Dict:
        """Get developer dashboard data."""
        if dev_id not in self.developers:
            return {'error': 'Developer not found'}
        
        developer = self.developers[dev_id]
        
        apps = []
        for app_id in developer['applications']:
            app = self.applications[app_id]
            apps.append({
                'id': app_id,
                'name': app['name'],
                'type': app['type'],
                'created_at': app['created_at'],
                'api_keys': len(app['api_keys']),
                'requests_today': 2543,  # TODO: track real stats
            })
        
        return {
            'developer': {
                'id': developer['id'],
                'name': developer['name'],
                'email': developer['email'],
                'tier': developer['tier'],
            },
            'applications': apps,
            'quota': {
                'requests_limit': 100000,
                'requests_used': 45230,
                'requests_remaining': 54770,
            },
        }


class SDKShowcase:
    """Showcase SDKs and code examples."""
    
    SDKS = {
        'ios': {
            'name': 'iOS SDK (Swift)',
            'repo': 'https://github.com/suresh-ai-kingdom/suresh-ios-sdk',
            'docs': 'https://docs.suresh-ai.com/ios',
            'example': 'https://github.com/suresh-ai-kingdom/suresh-ios-example',
            'downloads': 12453,
            'stars': 342,
        },
        'android': {
            'name': 'Android SDK (Kotlin)',
            'repo': 'https://github.com/suresh-ai-kingdom/suresh-android-sdk',
            'docs': 'https://docs.suresh-ai.com/android',
            'example': 'https://github.com/suresh-ai-kingdom/suresh-android-example',
            'downloads': 8932,
            'stars': 256,
        },
        'web': {
            'name': 'Web SDK (TypeScript)',
            'repo': 'https://github.com/suresh-ai-kingdom/suresh-js-sdk',
            'docs': 'https://docs.suresh-ai.com/web',
            'example': 'https://github.com/suresh-ai-kingdom/suresh-js-example',
            'downloads': 24567,
            'stars': 891,
        },
        'python': {
            'name': 'Python SDK',
            'repo': 'https://github.com/suresh-ai-kingdom/suresh-python-sdk',
            'docs': 'https://docs.suresh-ai.com/python',
            'example': 'https://github.com/suresh-ai-kingdom/suresh-python-example',
            'downloads': 5632,
            'stars': 178,
        },
        'go': {
            'name': 'Go SDK',
            'repo': 'https://github.com/suresh-ai-kingdom/suresh-go-sdk',
            'docs': 'https://docs.suresh-ai.com/go',
            'example': 'https://github.com/suresh-ai-kingdom/suresh-go-example',
            'downloads': 3421,
            'stars': 142,
        },
    }
    
    @staticmethod
    def get_sdk_list() -> List[Dict]:
        """Get list of available SDKs."""
        return list(SDKShowcase.SDKS.values())
    
    @staticmethod
    def get_code_example(sdk: str, example_type: str = 'basic') -> Dict:
        """Get code example for SDK."""
        examples = {
            'basic': {
                'title': 'Basic Authentication',
                'code': '''// Login and authenticate
const client = new SureshAI.Client({
    apiKey: 'sk_live_...'
});

const session = await client.auth.login({
    email: 'user@example.com',
    password: 'password'
});

console.log('Authenticated:', session.token);
'''
            },
            'generate': {
                'title': 'Generate Content',
                'code': '''// Generate AI content
const content = await client.content.generate({
    prompt: 'Write a marketing email',
    tone: 'professional'
});

console.log('Generated:', content.text);
'''
            },
            'offline': {
                'title': 'Offline Sync',
                'code': '''// Work offline with auto-sync
const syncQueue = client.sync.queue();

// Add action while offline
syncQueue.add({
    action: 'create',
    resource: 'content',
    data: { title: 'My Content' }
});

// Auto-syncs when online
await syncQueue.sync();
'''
            }
        }
        
        return examples.get(example_type, examples['basic'])


class APIAnalytics:
    """Track API usage and analytics for developers."""
    
    def __init__(self):
        self.usage_events = {}  # app_id -> [events]
    
    def track_request(self, app_id: str, endpoint: str, status_code: int, latency_ms: int) -> Dict:
        """Track API request."""
        if app_id not in self.usage_events:
            self.usage_events[app_id] = []
        
        event = {
            'timestamp': time.time(),
            'endpoint': endpoint,
            'status_code': status_code,
            'latency_ms': latency_ms,
            'success': 200 <= status_code < 300,
        }
        
        self.usage_events[app_id].append(event)
        
        return event
    
    def get_usage_analytics(self, app_id: str, days: int = 7) -> Dict:
        """Get usage analytics for application."""
        if app_id not in self.usage_events:
            return {'error': 'No data'}
        
        cutoff_time = time.time() - (days * 86400)
        events = [e for e in self.usage_events[app_id] if e['timestamp'] >= cutoff_time]
        
        total_requests = len(events)
        successful = sum(1 for e in events if e['success'])
        avg_latency = sum(e['latency_ms'] for e in events) / total_requests if total_requests > 0 else 0
        
        return {
            'app_id': app_id,
            'period_days': days,
            'total_requests': total_requests,
            'successful_requests': successful,
            'error_rate': ((total_requests - successful) / total_requests * 100) if total_requests > 0 else 0,
            'avg_latency_ms': avg_latency,
        }


class Webhook:
    """Webhook management for developers."""
    
    def __init__(self):
        self.webhooks = {}  # webhook_id -> webhook_config
    
    def create_webhook(self, app_id: str, url: str, events: List[str]) -> Dict:
        """Create webhook subscription."""
        webhook_id = f'wh_{uuid.uuid4().hex[:8]}'
        
        webhook = {
            'id': webhook_id,
            'app_id': app_id,
            'url': url,
            'events': events,  # e.g., ['content.generated', 'error.occurred']
            'created_at': time.time(),
            'active': True,
            'secret': f'whsec_{uuid.uuid4().hex[:32]}',
        }
        
        self.webhooks[webhook_id] = webhook
        
        return webhook
    
    def test_webhook(self, webhook_id: str) -> Dict:
        """Send test webhook."""
        webhook = self.webhooks.get(webhook_id)
        if not webhook:
            return {'error': 'Webhook not found'}
        
        # In production: send real webhook
        print(f"📨 Test webhook sent to {webhook['url']}")
        
        return {
            'webhook_id': webhook_id,
            'status': 'sent',
            'response_code': 200,
        }
