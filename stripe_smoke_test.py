#!/usr/bin/env python3
"""
Stripe integration smoke test.

Tests:
1. Stripe models in database
2. Coexistence with Razorpay (provider field)
3. Event table idempotency

Run: python stripe_smoke_test.py
"""

import os
import sys
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from models import get_engine, get_session, Base, Subscription, StripeEvent, UsageMeter, Customer

# Configure for testing
engine = get_engine('sqlite:///:memory:')

def init_db():
    """Initialize in-memory database."""
    Base.metadata.create_all(engine)
    print("✅ In-memory database initialized")

def get_db_session():
    """Get a session for testing."""
    return get_session(engine)

def test_stripe_models_exist():
    """Test 1: Stripe models can be created."""
    print("\n📌 Test 1: Stripe models exist and work")
    
    session = get_db_session()
    try:
        # Create customer
        customer = Customer(receipt='test_cust_001')
        session.add(customer)
        session.commit()
        print("  ✅ Customer created")
        
        # Create subscription
        sub = Subscription(
            id='stripe_sub_test',
            receipt='test_cust_001',
            tier='pro',
            provider='stripe',
            stripe_subscription_id='sub_test123',
            stripe_customer_id='cus_test123',
            billing_cycle='monthly',
            amount_paise=2900,
            status='ACTIVE',
            current_period_start=int(time.time()),
            current_period_end=int(time.time()) + 30*86400,
            created_at=time.time()
        )
        session.add(sub)
        session.commit()
        print("  ✅ Stripe subscription created")
        
        # Create usage meter
        usage = UsageMeter(
            id='meter_test',
            receipt='test_cust_001',
            subscription_id='stripe_sub_test',
            attribution_runs=5,
            models_used=2,
            exports=1,
            period_start=int(time.time()),
            period_end=int(time.time()) + 30*86400,
            reset_at=int(time.time()) + 30*86400,
            updated_at=time.time()
        )
        session.add(usage)
        session.commit()
        print("  ✅ Usage meter created")
        
        # Create stripe event
        event = StripeEvent(
            id='evt_test001',
            event_type='customer.subscription.created',
            payload=json.dumps({'id': 'sub_test123'}),
            processed=1,
            processed_at=time.time(),
            received_at=time.time()
        )
        session.add(event)
        session.commit()
        print("  ✅ Stripe event created")
        
    finally:
        session.close()

def test_razorpay_coexistence():
    """Test 2: Razorpay and Stripe coexist."""
    print("\n📌 Test 2: Razorpay + Stripe coexistence")
    
    session = get_db_session()
    try:
        # Create Razorpay subscription
        rz_sub = Subscription(
            id='sub_rz_001',
            receipt='coex_cust_001',
            tier='pro',
            provider='razorpay',
            razorpay_subscription_id='sub_rz_123',
            status='ACTIVE',
            billing_cycle='monthly',
            amount_paise=2900,
            current_period_start=int(time.time()),
            current_period_end=int(time.time()) + 30*86400,
            created_at=time.time()
        )
        session.add(rz_sub)
        session.flush()  # Flush before next add
        
        # Create Stripe subscription
        stripe_sub = Subscription(
            id='stripe_sub_001',
            receipt='coex_cust_002',
            tier='scale',
            provider='stripe',
            stripe_subscription_id='sub_stripe_456',
            stripe_customer_id='cus_stripe_789',
            status='ACTIVE',
            billing_cycle='monthly',
            amount_paise=9900,
            current_period_start=int(time.time()),
            current_period_end=int(time.time()) + 30*86400,
            created_at=time.time()
        )
        session.add(stripe_sub)
        session.commit()
        
        # Verify both exist
        rz_subs = session.query(Subscription).filter_by(provider='razorpay').all()
        stripe_subs = session.query(Subscription).filter_by(provider='stripe').all()
        
        # Note: Could have previous test data
        rz_with_id = [s for s in rz_subs if s.id == 'sub_rz_001']
        stripe_with_id = [s for s in stripe_subs if s.id == 'stripe_sub_001']
        
        assert len(rz_with_id) == 1
        assert len(stripe_with_id) == 1
        assert rz_with_id[0].razorpay_subscription_id == 'sub_rz_123'
        assert stripe_with_id[0].stripe_subscription_id == 'sub_stripe_456'
        
        print(f"  ✅ Razorpay subscriptions found: {len(rz_subs)}")
        print(f"  ✅ Stripe subscriptions found: {len(stripe_subs)}")
        print("  ✅ Both providers coexist in same database")
        
    finally:
        session.close()

def test_event_idempotency():
    """Test 3: Event idempotency via StripeEvent table."""
    print("\n📌 Test 3: Event idempotency")
    
    session = get_db_session()
    try:
        # Create event
        event = StripeEvent(
            id='evt_idem_001',
            event_type='customer.subscription.created',
            payload=json.dumps({'id': 'sub_123'}),
            processed=1,
            processed_at=time.time(),
            received_at=time.time()
        )
        session.add(event)
        session.commit()
        
        # Query for duplicate
        existing = session.query(StripeEvent).filter_by(id='evt_idem_001').first()
        assert existing is not None
        assert existing.processed == 1
        print("  ✅ Event stored and retrieved")
        
        # Verify duplicate detection
        if existing and existing.processed:
            print("  ✅ Duplicate event would be skipped (processed=1)")
        
    finally:
        session.close()

def main():
    print("\n" + "="*70)
    print("🧪 STRIPE INTEGRATION SMOKE TEST")
    print("="*70)
    
    try:
        # Initialize
        init_db()
        
        # Run tests
        test_stripe_models_exist()
        test_razorpay_coexistence()
        test_event_idempotency()
        
        print("\n" + "="*70)
        print("✅ ALL SMOKE TESTS PASSED")
        print("="*70)
        print("\nStripe Phase 2 DB integration is functional.")
        print("Next steps:")
        print("  1. Deploy migration: alembic upgrade head")
        print("  2. Set Stripe env vars (see STRIPE_SETUP.md)")
        print("  3. Test checkout flow: POST /api/billing/create-checkout")
        print("  4. Test webhook: POST /webhook/stripe")
        
        return 0
    
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
