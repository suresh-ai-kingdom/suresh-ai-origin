"""
SIMPLE TEST RARE FEATURES - No dependencies needed!
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_destiny_blueprint():
    print("\n" + "="*60)
    print("TEST 1: DESTINY BLUEPRINT")
    print("="*60)
    
    data = {
        "business_name": "SURESH AI ORIGIN",
        "current_revenue": 0,
        "target_revenue": 10000000,
        "industry": "AI/ML SaaS",
        "current_situation": "Just launched platform with 48 AI systems"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/rare/destiny-blueprint", json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ SUCCESS!")
            print("\nResponse preview:")
            print(json.dumps(result, indent=2)[:500])
            return True
        else:
            print(f"✗ FAILED: {response.text}")
            return False
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

def test_consciousness():
    print("\n" + "="*60)
    print("TEST 2: BUSINESS CONSCIOUSNESS")
    print("="*60)
    
    data = {
        "business_type": "AI SaaS Platform",
        "current_position": "New entrant with comprehensive suite",
        "main_challenge": "Customer acquisition",
        "industry": "AI/ML"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/rare/consciousness", json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ SUCCESS!")
            print("\nResponse preview:")
            print(json.dumps(result, indent=2)[:500])
            return True
        else:
            print(f"✗ FAILED: {response.text}")
            return False
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

def test_timing():
    print("\n" + "="*60)
    print("TEST 3: PERFECT TIMING")
    print("="*60)
    
    data = {
        "decisions": [{
            "decision": "Launch on Product Hunt",
            "context": "Platform ready, pricing live"
        }]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/rare/perfect-timing", json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ SUCCESS!")
            print("\nResponse preview:")
            print(json.dumps(result, indent=2)[:500])
            return True
        else:
            print(f"✗ FAILED: {response.text}")
            return False
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

def test_market():
    print("\n" + "="*60)
    print("TEST 4: MARKET CONSCIOUSNESS")
    print("="*60)
    
    data = {
        "market": "AI Business Automation",
        "competitors": "Zapier, Make.com",
        "position": "All-in-one platform",
        "timeframe": "6 months"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/rare/market-consciousness", json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ SUCCESS!")
            print("\nResponse preview:")
            print(json.dumps(result, indent=2)[:500])
            return True
        else:
            print(f"✗ FAILED: {response.text}")
            return False
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

def test_soul():
    print("\n" + "="*60)
    print("TEST 5: CUSTOMER SOUL MAPPING")
    print("="*60)
    
    data = {
        "product": "AI Business Automation Platform",
        "behavior": "Searching for automation solutions",
        "pain_points": "Too many tools, high costs"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/rare/customer-soul", json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ SUCCESS!")
            print("\nResponse preview:")
            print(json.dumps(result, indent=2)[:500])
            return True
        else:
            print(f"✗ FAILED: {response.text}")
            return False
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

def test_complete():
    print("\n" + "="*60)
    print("TEST 6: COMPLETE BLUEPRINT (ALL 5 COMBINED)")
    print("="*60)
    
    data = {
        "business_name": "SURESH AI ORIGIN",
        "current_situation": "AI platform with 48 systems, monetization live",
        "questions": "What's the path to ₹1 crore? How to position? Perfect timing?"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/rare/complete-blueprint", json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ SUCCESS!")
            print("\nResponse preview:")
            print(json.dumps(result, indent=2)[:500])
            return True
        else:
            print(f"✗ FAILED: {response.text}")
            return False
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("RARE 1% FEATURES - COMPREHENSIVE TEST")
    print("="*60)
    
    results = []
    
    results.append(("Destiny Blueprint", test_destiny_blueprint()))
    results.append(("Business Consciousness", test_consciousness()))
    results.append(("Perfect Timing", test_timing()))
    results.append(("Market Consciousness", test_market()))
    results.append(("Customer Soul Mapping", test_soul()))
    results.append(("Complete Blueprint", test_complete()))
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name.ljust(30)} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL RARE FEATURES WORKING PERFECTLY! 🎉")
        print("READY TO LAUNCH! 🚀\n")
    else:
        print("\n⚠️  SOME FEATURES FAILED - CHECK ERRORS ABOVE\n")
