"""
TEST RARE FEATURES ON PRODUCTION
Tests https://sureshaiorigin.com
"""

import requests
import json

BASE_URL = "https://sureshaiorigin.com"

print("\n" + "="*70)
print("RARE 1% FEATURES - PRODUCTION TEST")
print("Testing: " + BASE_URL)
print("="*70)

# Test 1: Check if rare features dashboard loads
print("\n[1/7] Testing Rare Features Dashboard...")
try:
    response = requests.get(f"{BASE_URL}/rare-features", timeout=10)
    if response.status_code == 200:
        print("✓ Dashboard loads successfully!")
    else:
        print(f"✗ Dashboard failed: {response.status_code}")
except Exception as e:
    print(f"✗ Dashboard error: {str(e)}")

# Test 2: Check stats endpoint
print("\n[2/7] Testing Stats Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/rare/stats", timeout=10)
    if response.status_code == 200:
        print("✓ Stats endpoint works!")
        print(f"    Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"✗ Stats failed: {response.status_code}")
except Exception as e:
    print(f"✗ Stats error: {str(e)}")

# Test 3: Test Destiny Blueprint
print("\n[3/7] Testing Destiny Blueprint...")
try:
    data = {
        "business_name": "Test Business",
        "current_revenue": 1000000,
        "target_revenue": 10000000,
        "industry": "SaaS"
    }
    response = requests.post(f"{BASE_URL}/api/rare/destiny-blueprint", json=data, timeout=30)
    if response.status_code == 200:
        result = response.json()
        print("✓ Destiny Blueprint works!")
        print(f"    Generated {len(str(result))} chars of output")
        if 'milestones' in str(result) or 'months' in str(result).lower():
            print("    ✓ Contains milestones/timeline data")
    else:
        print(f"✗ Failed: {response.status_code} - {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {str(e)}")

# Test 4: Test Consciousness
print("\n[4/7] Testing Business Consciousness...")
try:
    data = {
        "business_type": "AI Platform",
        "current_position": "Startup",
        "main_challenge": "Growth"
    }
    response = requests.post(f"{BASE_URL}/api/rare/consciousness", json=data, timeout=30)
    if response.status_code == 200:
        result = response.json()
        print("✓ Business Consciousness works!")
        print(f"    Generated {len(str(result))} chars of analysis")
    else:
        print(f"✗ Failed: {response.status_code} - {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {str(e)}")

# Test 5: Test Perfect Timing
print("\n[5/7] Testing Perfect Timing...")
try:
    data = {
        "decisions": [{
            "decision": "Launch product",
            "context": "Q1 2026"
        }]
    }
    response = requests.post(f"{BASE_URL}/api/rare/perfect-timing", json=data, timeout=30)
    if response.status_code == 200:
        result = response.json()
        print("✓ Perfect Timing works!")
        print(f"    Generated {len(str(result))} chars of timing analysis")
    else:
        print(f"✗ Failed: {response.status_code} - {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {str(e)}")

# Test 6: Test Market Consciousness
print("\n[6/7] Testing Market Consciousness...")
try:
    data = {
        "market": "AI Tools",
        "competitors": "OpenAI, Claude",
        "position": "New entrant"
    }
    response = requests.post(f"{BASE_URL}/api/rare/market-consciousness", json=data, timeout=30)
    if response.status_code == 200:
        result = response.json()
        print("✓ Market Consciousness works!")
        print(f"    Generated {len(str(result))} chars of market analysis")
    else:
        print(f"✗ Failed: {response.status_code} - {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {str(e)}")

# Test 7: Test Customer Soul
print("\n[7/7] Testing Customer Soul Mapping...")
try:
    data = {
        "product": "AI Platform",
        "behavior": "Enterprise buyers",
        "pain_points": "Complex workflows"
    }
    response = requests.post(f"{BASE_URL}/api/rare/customer-soul", json=data, timeout=30)
    if response.status_code == 200:
        result = response.json()
        print("✓ Customer Soul Mapping works!")
        print(f"    Generated {len(str(result))} chars of customer analysis")
    else:
        print(f"✗ Failed: {response.status_code} - {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {str(e)}")

print("\n" + "="*70)
print("PRODUCTION TEST COMPLETE!")
print("="*70)
print("\n✓ If all tests passed, rare features are LIVE and ready!")
print("✓ Dashboard: https://sureshaiorigin.com/rare-features")
print("✓ Ready to launch and show to world! 🚀\n")
