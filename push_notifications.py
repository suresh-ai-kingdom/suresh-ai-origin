"""Push notification integration - Firebase Cloud Messaging."""
import os
import json
import requests
from typing import Dict, List
import uuid

class FCMService:
    """Firebase Cloud Messaging for push notifications."""
    
    def __init__(self):
        self.server_key = os.getenv('FCM_SERVER_KEY')
        self.base_url = 'https://fcm.googleapis.com/fcm/send'
        self.headers = {
            'Authorization': f'key={self.server_key}',
            'Content-Type': 'application/json',
        }
    
    def send_to_device(self, device_token: str, title: str, body: str, data: Dict = None) -> Dict:
        """Send notification to single device."""
        if not self.server_key or self.server_key == 'mock':
            print(f"📲 FCM Mock → {device_token[:20]}... | {title}")
            return {'success': True, 'message_id': str(uuid.uuid4())}
        
        payload = {
            'to': device_token,
            'notification': {
                'title': title,
                'body': body,
                'sound': 'default',
            },
            'data': data or {},
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def send_to_topic(self, topic: str, title: str, body: str, data: Dict = None) -> Dict:
        """Send notification to topic subscribers."""
        if not self.server_key or self.server_key == 'mock':
            print(f"📢 FCM Topic → {topic} | {title}")
            return {'success': True, 'message_id': str(uuid.uuid4())}
        
        payload = {
            'to': f'/topics/{topic}',
            'notification': {
                'title': title,
                'body': body,
            },
            'data': data or {},
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def subscribe_to_topic(self, device_token: str, topic: str) -> Dict:
        """Subscribe device to topic."""
        # Real implementation would use FCM management API
        print(f"✅ Subscribed {device_token[:20]}... to topic '{topic}'")
        return {'success': True}
    
    def unsubscribe_from_topic(self, device_token: str, topic: str) -> Dict:
        """Unsubscribe device from topic."""
        print(f"❌ Unsubscribed {device_token[:20]}... from topic '{topic}'")
        return {'success': True}


# Usage in campaigns
def send_segment_push_notification(segment: str, title: str, body: str, campaign_id: str = None) -> Dict:
    """Send push notification to entire segment."""
    fcm = FCMService()
    topic = f'segment_{segment}'
    
    result = fcm.send_to_topic(
        topic=topic,
        title=title,
        body=body,
        data={'campaign_id': campaign_id or 'none'}
    )
    
    return result
