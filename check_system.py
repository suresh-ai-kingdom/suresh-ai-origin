#!/usr/bin/env python3
"""
System Status Checker - SURESH AI ORIGIN
Verifies all systems are configured and working properly
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_icon(status):
    return "✅" if status else "❌"

def check_payment_setup():
    """Check if payment gateway is configured."""
    print("\n💳 PAYMENT GATEWAY STATUS")
    print("=" * 50)
    
    razorpay_key_id = os.getenv('RAZORPAY_KEY_ID')
    razorpay_secret = os.getenv('RAZORPAY_KEY_SECRET')
    webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
    
    key_ok = bool(razorpay_key_id and len(razorpay_key_id) > 10)
    secret_ok = bool(razorpay_secret and len(razorpay_secret) > 10)
    webhook_ok = bool(webhook_secret)
    
    print(f"{check_icon(key_ok)} Razorpay Key ID: {'Configured' if key_ok else '⚠️  NOT SET'}")
    print(f"{check_icon(secret_ok)} Razorpay Secret: {'Configured' if secret_ok else '⚠️  NOT SET'}")
    print(f"{check_icon(webhook_ok)} Webhook Secret: {'Configured' if webhook_ok else '⚠️  NOT SET'}")
    
    if not (key_ok and secret_ok):
        print("\n⚠️  PAYMENT GATEWAY NOT CONFIGURED!")
        print("   → No real payments can be processed")
        print("   → See SETUP_PAYMENTS_GUIDE.md for instructions")
        return False
    
    # Check if test or live mode
    if razorpay_key_id.startswith('rzp_test_'):
        print("\n🧪 Mode: TEST (use test cards)")
    elif razorpay_key_id.startswith('rzp_live_'):
        print("\n💰 Mode: LIVE (real money!)")
    
    return True

def check_email_setup():
    """Check if email notifications are configured."""
    print("\n📧 EMAIL NOTIFICATIONS STATUS")
    print("=" * 50)
    
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    
    user_ok = bool(email_user and '@' in email_user)
    pass_ok = bool(email_pass and len(email_pass) > 10)
    
    print(f"{check_icon(user_ok)} Email User: {email_user if user_ok else '⚠️  NOT SET'}")
    print(f"{check_icon(pass_ok)} Email Password: {'Configured' if pass_ok else '⚠️  NOT SET'}")
    
    if not (user_ok and pass_ok):
        print("\n⚠️  EMAIL NOT CONFIGURED!")
        print("   → Order confirmations won't be sent")
        print("   → Recovery emails won't work")
        return False
    
    return True

def check_admin_auth():
    """Check if admin authentication is configured."""
    print("\n🔐 ADMIN AUTHENTICATION STATUS")
    print("=" * 50)
    
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_password = os.getenv('ADMIN_PASSWORD')
    admin_token = os.getenv('ADMIN_TOKEN')
    
    session_auth = bool(admin_username and admin_password)
    token_auth = bool(admin_token)
    
    print(f"{check_icon(session_auth)} Session Auth (Username/Password): {'Configured' if session_auth else 'Not Set'}")
    print(f"{check_icon(token_auth)} Token Auth (Bearer): {'Configured' if token_auth else 'Not Set'}")
    
    if not (session_auth or token_auth):
        print("\n⚠️  ADMIN AUTH NOT CONFIGURED!")
        print("   → Anyone can access /admin")
        print("   → Set ADMIN_USERNAME and ADMIN_PASSWORD")
        return False
    
    return True

def check_database():
    """Check if database exists and is accessible."""
    print("\n🗄️  DATABASE STATUS")
    print("=" * 50)
    
    try:
        from models import get_engine, get_session
        from utils import _get_db_url
        from sqlalchemy import text
        
        db_url = _get_db_url()
        db_file = db_url.replace('sqlite:///', '')
        
        if os.path.exists(db_file):
            file_size = os.path.getsize(db_file) / 1024  # KB
            print(f"✅ Database File: {db_file}")
            print(f"✅ Size: {file_size:.2f} KB")
            
            # Test connection
            engine = get_engine(db_url)
            session = get_session(engine)
            result = session.execute(text("SELECT COUNT(*) FROM orders")).scalar()
            print(f"✅ Orders in DB: {result}")
            session.close()
            
            return True
        else:
            print(f"❌ Database not found: {db_file}")
            print("   → Run: python -c 'from utils import init_db; init_db()'")
            return False
            
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return False

def check_automations():
    """Check if automation workflows can execute."""
    print("\n🤖 AUTOMATION WORKFLOWS STATUS")
    print("=" * 50)
    
    try:
        from automation_workflows import (
            churn_retention_workflow,
            payment_retry_workflow,
            segment_campaign_workflow
        )
        
        workflows = [
            'churn_retention_workflow',
            'payment_retry_workflow', 
            'segment_campaign_workflow'
        ]
        
        for wf in workflows:
            print(f"✅ {wf}: Available")
        
        print("\n💡 To test: Visit /admin/automations and click 'Trigger Now'")
        return True
        
    except Exception as e:
        print(f"❌ Automation Error: {e}")
        return False

def check_ai_service():
    """Check if real AI is configured."""
    print("\n🤖 AI SERVICE STATUS")
    print("=" * 50)
    
    try:
        from real_ai_service import get_ai_status, is_ai_real
        
        status = get_ai_status()
        provider = status['provider']
        model = status['model']
        is_real = is_ai_real()
        
        if is_real:
            print(f"✅ Provider: {provider.upper()}")
            print(f"✅ Model: {model}")
            print(f"✅ Status: REAL AI ACTIVE")
            
            # Test generation
            try:
                from real_ai_service import generate_ai_content
                test_response = generate_ai_content("Say hello in 5 words", max_tokens=50)
                if len(test_response) > 0 and "DEMO" not in test_response:
                    print(f"✅ Test Call: SUCCESS")
                else:
                    print(f"⚠️  Test Call: Returns demo response")
            except Exception as e:
                print(f"⚠️  Test Call: {e}")
            
            return True
        else:
            print(f"⚠️  Provider: {provider} (DEMO MODE)")
            print(f"   → No real AI configured")
            print(f"   → Get FREE Gemini API key: https://aistudio.google.com/")
            print(f"   → Read: AI_INTEGRATION_GUIDE.md")
            return False
            
    except Exception as e:
        print(f"❌ AI Service Error: {e}")
        print(f"   → Install: pip install openai anthropic google-generativeai groq")
        return False

def check_crypto_wallets():
    """Check if crypto wallet addresses are configured."""
    print("\n₿ CRYPTO PAYMENT STATUS")
    print("=" * 50)
    
    # Read crypto-effects.js to check wallet addresses
    try:
        with open('static/crypto-effects.js', 'r', encoding='utf-8') as f:
            content = f.read()
            
        demo_wallets = [
            'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',  # Demo BTC
            '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',   # Demo ETH
        ]
        
        using_demo = any(wallet in content for wallet in demo_wallets)
        
        if using_demo:
            print("⚠️  Using DEMO wallet addresses")
            print("   → Update walletAddresses in static/crypto-effects.js")
            print("   → Add your real BTC, ETH, USDT, SOL addresses")
            return False
        else:
            print("✅ Custom wallet addresses configured")
            return True
            
    except Exception as e:
        print(f"❌ Error checking crypto wallets: {e}")
        return False

def generate_summary(results):
    """Generate overall system status summary."""
    print("\n" + "=" * 50)
    print("📊 OVERALL SYSTEM STATUS")
    print("=" * 50)
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    percentage = (passed / total) * 100
    
    print(f"\nSystems Checked: {total}")
    print(f"✅ Working: {passed}")
    print(f"❌ Issues: {failed}")
    print(f"📈 Health: {percentage:.0f}%")
    
    if percentage == 100:
        print("\n🎉 ALL SYSTEMS GO! Ready to accept payments!")
    elif percentage >= 70:
        print("\n⚠️  MOSTLY READY - Fix remaining issues to go live")
    else:
        print("\n🚨 CRITICAL ISSUES - System not ready for production")
        print("   → Follow SETUP_PAYMENTS_GUIDE.md")
    
    print("\n" + "=" * 50)
    
    if failed > 0:
        print("\n🔧 QUICK FIX:")
        if not results.get('payments'):
            print("   1. Get Razorpay API keys from https://razorpay.com")
            print("   2. Add to Render environment: RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET")
        if not results.get('email'):
            print("   3. Set EMAIL_USER and EMAIL_PASS (Gmail app password)")
        if not results.get('crypto'):
            print("   4. Update crypto wallet addresses in crypto-effects.js")
        if not results.get('admin'):
            print("   5. Set ADMIN_USERNAME and ADMIN_PASSWORD for security")

if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════╗
║   SURESH AI ORIGIN - SYSTEM STATUS CHECKER               ║
║   Verifying all components before going live             ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    results = {
        'payments': check_payment_setup(),
        'email': check_email_setup(),
        'admin': check_admin_auth(),
        'database': check_database(),
        'automations': check_automations(),
        'ai_service': check_ai_service(),
        'crypto': check_crypto_wallets(),
    }
    
    generate_summary(results)
    
    # Exit code based on critical systems
    critical_ok = results['payments'] and results['database']
    sys.exit(0 if critical_ok else 1)
