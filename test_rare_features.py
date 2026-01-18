"""
TEST RARE FEATURES - Verify all 5 god-tier features work perfectly
Run this to make sure everything is ready before launch!
"""

import requests
import json
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:5000"  # Change to production URL when testing live

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{text.center(60)}")
    print(f"{Fore.CYAN}{'='*60}\n")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}")

def print_info(text):
    print(f"{Fore.YELLOW}→ {text}")

def test_feature(name, endpoint, data):
    """Test a single rare feature endpoint."""
    print_info(f"Testing {name}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"{name} works! Status: {response.status_code}")
            
            # Print first few lines of response
            result_str = json.dumps(result, indent=2)
            lines = result_str.split('\n')[:10]
            print(f"{Fore.WHITE}Response preview:")
            for line in lines:
                print(f"{Fore.WHITE}  {line}")
            if len(result_str.split('\n')) > 10:
                print(f"{Fore.WHITE}  ... (truncated)")
            
            return True
        else:
            print_error(f"{name} failed! Status: {response.status_code}")
            print(f"{Fore.RED}  Error: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"{name} error: {str(e)}")
        return False

def main():
    print_header("RARE 1% FEATURES - COMPREHENSIVE TEST")
    print(f"{Fore.WHITE}Testing all 5 god-tier features...\n")
    
    results = {}
    
    # Test 1: Destiny Blueprint
    print_header("TEST 1: DESTINY BLUEPRINT")
    results['destiny'] = test_feature(
        "Destiny Blueprint",
        "/api/rare/destiny-blueprint",
        {
            "business_name": "SURESH AI ORIGIN",
            "current_revenue": 0,
            "target_revenue": 10000000,
            "industry": "AI/ML SaaS",
            "current_situation": "Just launched platform with 48 AI systems"
        }
    )
    
    # Test 2: Universal Business Consciousness
    print_header("TEST 2: UNIVERSAL BUSINESS CONSCIOUSNESS")
    results['consciousness'] = test_feature(
        "Business Consciousness",
        "/api/rare/consciousness",
        {
            "business_type": "AI SaaS Platform",
            "current_position": "New entrant with comprehensive AI automation suite",
            "main_challenge": "Customer acquisition and market differentiation",
            "industry": "AI/ML"
        }
    )
    
    # Test 3: Perfect Timing Engine
    print_header("TEST 3: PERFECT TIMING ENGINE")
    results['timing'] = test_feature(
        "Perfect Timing Engine",
        "/api/rare/perfect-timing",
        {
            "decisions": [
                {
                    "decision": "Launch on Product Hunt",
                    "context": "Platform ready, pricing live, rare features deployed"
                },
                {
                    "decision": "Start paid advertising",
                    "context": "Need to validate product-market fit first"
                }
            ]
        }
    )
    
    # Test 4: Market Consciousness
    print_header("TEST 4: MARKET CONSCIOUSNESS")
    results['market'] = test_feature(
        "Market Consciousness",
        "/api/rare/market-consciousness",
        {
            "market": "AI Business Automation",
            "competitors": "Zapier, Make.com, various AI tools",
            "position": "Comprehensive all-in-one platform vs point solutions",
            "timeframe": "6 months"
        }
    )
    
    # Test 5: Customer Soul Mapping
    print_header("TEST 5: CUSTOMER SOUL MAPPING")
    results['soul'] = test_feature(
        "Customer Soul Mapping",
        "/api/rare/customer-soul",
        {
            "product": "AI Business Automation Platform",
            "behavior": "Business owners searching for automation, overwhelmed by complexity",
            "pain_points": "Too many tools, high costs, technical complexity, time waste"
        }
    )
    
    # Test 6: Complete Blueprint (ALL 5 COMBINED)
    print_header("TEST 6: COMPLETE RARE BLUEPRINT (ALL COMBINED)")
    results['complete'] = test_feature(
        "Complete Rare Blueprint",
        "/api/rare/complete-blueprint",
        {
            "business_name": "SURESH AI ORIGIN",
            "current_situation": "AI platform with 48 systems, just launched monetization + rare features",
            "questions": "What's the exact path to ₹1 crore revenue? How to position? Perfect timing? Market future? Customer understanding?"
        }
    )
    
    # Final Results
    print_header("FINAL RESULTS")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n{Fore.WHITE}Test Summary:")
    print(f"{Fore.WHITE}{'='*60}\n")
    
    for feature, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        color = Fore.GREEN if passed_test else Fore.RED
        print(f"{color}{feature.upper().ljust(20)} {status}")
    
    print(f"\n{Fore.WHITE}{'='*60}")
    print(f"\n{Fore.CYAN}Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{Fore.GREEN}{'🎉 ALL RARE FEATURES WORKING PERFECTLY! 🎉'.center(60)}")
        print(f"{Fore.GREEN}{'READY TO LAUNCH! 🚀'.center(60)}\n")
        return 0
    else:
        print(f"\n{Fore.RED}{'⚠️  SOME FEATURES FAILED - FIX BEFORE LAUNCH'.center(60)}\n")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
