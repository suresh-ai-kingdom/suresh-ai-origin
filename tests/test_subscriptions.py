"""Tests for subscription management system."""
import pytest
import time
from models import get_session, Subscription, Base, get_engine
from subscriptions import (
    get_active_subscriptions, calculate_mrr, get_subscription_analytics,
    get_expiring_subscriptions, create_subscription, cancel_subscription,
    renew_subscription, get_tier_upgrade_opportunities,
    get_subscription_revenue_forecast, SUBSCRIPTION_PRICING
)


@pytest.fixture
def cleanup_subs():
    """Clean up test subscriptions before and after each test."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    
    session = get_session()
    try:
        session.query(Subscription).filter(Subscription.receipt.like('TEST_%')).delete()
        session.commit()
    finally:
        session.close()
    
    yield
    
    session = get_session()
    try:
        session.query(Subscription).filter(Subscription.receipt.like('TEST_%')).delete()
        session.commit()
    finally:
        session.close()


def test_create_subscription_starter(cleanup_subs):
    """Test creating a starter subscription."""
    sub = create_subscription('TEST_CUST_1', 'STARTER', 'monthly')
    
    assert sub['receipt'] == 'TEST_CUST_1'
    assert sub['tier'] == 'STARTER'
    assert sub['billing_cycle'] == 'monthly'
    assert sub['amount_rupees'] == 99
    assert sub['status'] == 'ACTIVE'


def test_create_subscription_pro_yearly(cleanup_subs):
    """Test creating a pro yearly subscription."""
    sub = create_subscription('TEST_CUST_2', 'PRO', 'yearly')
    
    assert sub['receipt'] == 'TEST_CUST_2'
    assert sub['tier'] == 'PRO'
    assert sub['billing_cycle'] == 'yearly'
    assert sub['amount_rupees'] == 4990
    assert sub['status'] == 'ACTIVE'


def test_create_subscription_invalid_tier(cleanup_subs):
    """Test creating subscription with invalid tier."""
    with pytest.raises(ValueError):
        create_subscription('TEST_CUST_3', 'INVALID', 'monthly')


def test_get_active_subscriptions_empty(cleanup_subs):
    """Test getting active subscriptions when none exist."""
    subs = get_active_subscriptions()
    assert isinstance(subs, list)
    assert len(subs) == 0


def test_get_active_subscriptions_single(cleanup_subs):
    """Test getting a single active subscription."""
    create_subscription('TEST_CUST_4', 'STARTER', 'monthly')
    
    subs = get_active_subscriptions()
    assert len(subs) == 1
    assert subs[0]['receipt'] == 'TEST_CUST_4'
    assert subs[0]['tier'] == 'STARTER'


def test_get_active_subscriptions_by_receipt(cleanup_subs):
    """Test filtering subscriptions by receipt."""
    create_subscription('TEST_CUST_5', 'PRO', 'monthly')
    create_subscription('TEST_CUST_6', 'STARTER', 'monthly')
    
    subs = get_active_subscriptions(receipt='TEST_CUST_5')
    assert len(subs) == 1
    assert subs[0]['receipt'] == 'TEST_CUST_5'


def test_calculate_mrr_empty(cleanup_subs):
    """Test MRR calculation with no subscriptions."""
    mrr = calculate_mrr()
    
    assert mrr['mrr_paise'] == 0
    assert mrr['mrr_rupees'] == 0
    assert mrr['arr_paise'] == 0
    assert mrr['active_subscribers'] == 0


def test_calculate_mrr_monthly(cleanup_subs):
    """Test MRR calculation with monthly subscriptions."""
    create_subscription('TEST_CUST_7', 'STARTER', 'monthly')
    create_subscription('TEST_CUST_8', 'PRO', 'monthly')
    
    mrr = calculate_mrr()
    
    # 9900 + 49900 = 59800 paise = ₹598
    assert mrr['mrr_paise'] == 59800
    assert mrr['mrr_rupees'] == 598
    assert mrr['active_subscribers'] == 2


def test_calculate_mrr_yearly(cleanup_subs):
    """Test MRR calculation with yearly subscription."""
    create_subscription('TEST_CUST_9', 'PREMIUM', 'yearly')
    
    mrr = calculate_mrr()
    
    # 999000 / 12 = 83250 paise/month
    assert mrr['mrr_paise'] == 83250
    assert mrr['mrr_rupees'] == 832.5
    assert mrr['active_subscribers'] == 1


def test_calculate_mrr_mixed(cleanup_subs):
    """Test MRR with mixed monthly and yearly subscriptions."""
    create_subscription('TEST_CUST_10', 'STARTER', 'monthly')
    create_subscription('TEST_CUST_11', 'PRO', 'yearly')
    
    mrr = calculate_mrr()
    
    # Monthly: 9900
    # Yearly: 499000 / 12 = 41583.33
    # Total: 51483.33 paise
    assert mrr['mrr_paise'] == 51483
    assert mrr['active_subscribers'] == 2


def test_cancel_subscription(cleanup_subs):
    """Test cancelling a subscription."""
    sub = create_subscription('TEST_CUST_12', 'PRO', 'monthly')
    sub_id = sub['id']
    
    success = cancel_subscription(sub_id, reason='Testing')
    assert success is True
    
    # Verify subscription is cancelled
    session = get_session()
    try:
        cancelled = session.query(Subscription).filter(Subscription.id == sub_id).first()
        assert cancelled.status == 'CANCELLED'
        assert cancelled.cancellation_reason == 'Testing'
    finally:
        session.close()


def test_cancel_nonexistent_subscription(cleanup_subs):
    """Test cancelling a subscription that doesn't exist."""
    success = cancel_subscription('FAKE_SUB_ID')
    assert success is False


def test_renew_subscription(cleanup_subs):
    """Test renewing a subscription."""
    sub = create_subscription('TEST_CUST_13', 'STARTER', 'monthly')
    sub_id = sub['id']
    
    # Get current period end
    session = get_session()
    try:
        original = session.query(Subscription).filter(Subscription.id == sub_id).first()
        original_end = original.current_period_end
    finally:
        session.close()
    
    # Renew
    renewed = renew_subscription(sub_id)
    
    # Verify new period is extended
    assert 'new_period_end' in renewed
    
    # Check database
    session = get_session()
    try:
        updated = session.query(Subscription).filter(Subscription.id == sub_id).first()
        assert updated.current_period_end > original_end
    finally:
        session.close()


def test_get_subscription_analytics_empty(cleanup_subs):
    """Test analytics with no subscriptions."""
    analytics = get_subscription_analytics(days_back=30)
    
    assert analytics['new_subscriptions'] == 0
    assert analytics['cancelled_subscriptions'] == 0
    assert analytics['net_change'] == 0
    assert analytics['churn_rate_percent'] == 0


def test_get_subscription_analytics_with_data(cleanup_subs):
    """Test analytics calculation."""
    # Create subscriptions
    create_subscription('TEST_CUST_14', 'PRO', 'monthly')
    create_subscription('TEST_CUST_15', 'STARTER', 'monthly')
    
    analytics = get_subscription_analytics(days_back=30)
    
    assert analytics['new_subscriptions'] == 2
    assert analytics['cancelled_subscriptions'] == 0
    assert analytics['net_change'] == 2
    assert analytics['active_subscriptions'] == 2


def test_get_expiring_subscriptions_none(cleanup_subs):
    """Test getting expiring subscriptions when none are expiring."""
    # Create subscription that won't expire soon
    create_subscription('TEST_CUST_16', 'PRO', 'monthly')
    
    expiring = get_expiring_subscriptions(days_ahead=7)
    assert len(expiring) == 0


def test_get_expiring_subscriptions_with_data(cleanup_subs):
    """Test getting expiring subscriptions."""
    # Create subscription
    sub = create_subscription('TEST_CUST_17', 'STARTER', 'monthly')
    
    # Manually set expiry to 3 days from now
    session = get_session()
    try:
        subscription = session.query(Subscription).filter(
            Subscription.receipt == 'TEST_CUST_17'
        ).first()
        subscription.current_period_end = time.time() + (3 * 86400)
        session.commit()
    finally:
        session.close()
    
    expiring = get_expiring_subscriptions(days_ahead=7)
    assert len(expiring) == 1
    assert expiring[0]['receipt'] == 'TEST_CUST_17'
    assert expiring[0]['days_left'] <= 3  # Allow for timing variance
    assert expiring[0]['urgency'] == 'CRITICAL'


def test_get_tier_upgrade_opportunities(cleanup_subs):
    """Test identifying upgrade opportunities."""
    # Create starter subscription from 60 days ago
    session = get_session()
    try:
        old_time = time.time() - (60 * 86400)
        sub = Subscription(
            id='TEST_OLD_SUB',
            receipt='TEST_CUST_18',
            tier='STARTER',
            billing_cycle='monthly',
            amount_paise=9900,
            status='ACTIVE',
            current_period_start=old_time,
            current_period_end=old_time + (30 * 86400),
            created_at=old_time
        )
        session.add(sub)
        session.commit()
    finally:
        session.close()
    
    opportunities = get_tier_upgrade_opportunities()
    
    assert len(opportunities) > 0
    assert opportunities[0]['receipt'] == 'TEST_CUST_18'
    assert opportunities[0]['current_tier'] == 'STARTER'
    assert opportunities[0]['suggested_tier'] == 'PRO'
    assert opportunities[0]['days_active'] >= 60


def test_subscription_revenue_forecast(cleanup_subs):
    """Test revenue forecasting."""
    # Create some subscriptions
    create_subscription('TEST_CUST_19', 'PRO', 'monthly')
    create_subscription('TEST_CUST_20', 'PREMIUM', 'monthly')
    
    forecast = get_subscription_revenue_forecast(months_ahead=6)
    
    assert 'current_mrr_rupees' in forecast
    assert 'forecast' in forecast
    assert len(forecast['forecast']) == 6
    assert forecast['forecast'][0]['month'] == 1
    assert forecast['forecast'][0]['projected_mrr_rupees'] > 0


def test_subscription_pricing_structure():
    """Test that pricing is properly configured."""
    assert 'STARTER' in SUBSCRIPTION_PRICING
    assert 'PRO' in SUBSCRIPTION_PRICING
    assert 'PREMIUM' in SUBSCRIPTION_PRICING
    
    # Check each tier has required fields
    for tier in ['STARTER', 'PRO', 'PREMIUM']:
        assert 'monthly' in SUBSCRIPTION_PRICING[tier]
        assert 'yearly' in SUBSCRIPTION_PRICING[tier]
        assert 'name' in SUBSCRIPTION_PRICING[tier]
        assert 'features' in SUBSCRIPTION_PRICING[tier]
        
        # Yearly should be cheaper per month
        monthly = SUBSCRIPTION_PRICING[tier]['monthly']
        yearly = SUBSCRIPTION_PRICING[tier]['yearly']
        assert yearly < (monthly * 12)
