#!/usr/bin/env python3
"""
Production System Test - SURESH AI ORIGIN
Tests production deployment and AI functionality
"""

import requests
import json
import re
from datetime import datetime

PROD_URL = 'https://suresh-ai-origin.onrender.com'
ADMIN_USER = 'admin'
ADMIN_PASS = 'SureshAI2026!'

def test_site_live():
    """Test if site is live and responding."""
    print("\n🌐 TESTING PRODUCTION SITE")
    print("=" * 60)
    try:
        r = requests.get(PROD_URL, timeout=15)
        is_live = r.status_code == 200 and 'SURESH' in r.text
        print(f"{'✅' if is_live else '❌'} Site Status: {r.status_code}")
        print(f"{'✅' if is_live else '❌'} Content: {'Present' if is_live else 'Missing'}")
        return is_live
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint."""
    print("\n🏥 TESTING HEALTH ENDPOINT")
    print("=" * 60)
    try:
        r = requests.get(f'{PROD_URL}/health', timeout=15)
        data = r.json() if r.status_code == 200 else {}
        is_healthy = data.get('status') == 'healthy'
        print(f"{'✅' if is_healthy else '❌'} Status: {r.status_code}")
        print(f"{'✅' if is_healthy else '❌'} Database: {data.get('database', 'unknown')}")
        return is_healthy
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_admin_ai():
    """Test AI generation with admin authentication."""
    print("\n🤖 TESTING GROQ AI GENERATION")
    print("=" * 60)
    try:
        # Step 1: Get login page to extract CSRF token
        session = requests.Session()
        r1 = session.get(f'{PROD_URL}/admin/login', timeout=15)
        print(f"📄 Login page: {r1.status_code}")
        
        # Extract CSRF token
        csrf_match = re.search(r'csrf_token.*?value=["\']([^"\']+)', r1.text)
        csrf_token = csrf_match.group(1) if csrf_match else ''
        print(f"🔐 CSRF token: {'Found' if csrf_token else 'Not found'}")
        
        # Step 2: Login
        login_data = {
            'username': ADMIN_USER,
            'password': ADMIN_PASS,
            'csrf_token': csrf_token
        }
        r2 = session.post(f'{PROD_URL}/admin/login', data=login_data, timeout=15, allow_redirects=True)
        is_logged_in = r2.status_code == 200 and 'admin' in r2.url
        print(f"{'✅' if is_logged_in else '❌'} Login: {r2.status_code} (redirects: {len(r2.history)})")
        print(f"🍪 Cookies: {dict(session.cookies)}")
        print(f"🔗 Final URL: {r2.url}")
        
        if not is_logged_in:
            print(f"⚠️  Login may have failed, checking session...")
            # Try accessing a protected page to verify
            r_test = session.get(f'{PROD_URL}/admin', timeout=15)
            print(f"   Admin page status: {r_test.status_code}")
        
        # Step 3: Test AI generation
        ai_payload = {
            'type': 'email',
            'variables': {
                'product': 'Premium AI Pack',
                'benefit': 'saves time and increases productivity',
                'customer_name': 'Test User'
            }
        }
        headers = {
            'X-Idempotency-Key': f'test-{datetime.now().timestamp()}',
            'Content-Type': 'application/json'
        }
        r3 = session.post(f'{PROD_URL}/api/ai/generate', json=ai_payload, headers=headers, timeout=30)
        print(f"{'✅' if r3.status_code == 200 else '❌'} AI Status: {r3.status_code}")
        
        if r3.status_code == 200:
            data = r3.json()
            content = data.get('content', '')
            print(f"✅ Content length: {len(content)} chars")
            print(f"📝 Sample: {content[:150]}...")
            return True
        else:
            print(f"❌ Response: {r3.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("SURESH AI ORIGIN - PRODUCTION SYSTEM TEST")
    print("=" * 60)
    print(f"URL: {PROD_URL}")
    print(f"Time: {datetime.now()}")
    
    results = {
        'site_live': test_site_live(),
        'health': test_health_endpoint(),
        'ai_generation': test_admin_ai()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test, result in results.items():
        print(f"{'✅' if result else '❌'} {test.replace('_', ' ').title()}: {'PASS' if result else 'FAIL'}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n📊 Score: {passed}/{total} ({passed/total*100:.0f}%)")
    
    return all(results.values())

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
