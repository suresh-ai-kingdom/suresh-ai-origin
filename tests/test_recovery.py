"""Tests for abandoned order recovery system."""
import pytest
import time
from models import get_session, Order, AbandonedReminder, Base, get_engine
from recovery import (
    get_abandoned_orders, should_send_reminder, get_recovery_metrics,
    get_product_abandonment_rate, get_recovery_suggestions,
    estimate_recovery_potential, get_abandoned_orders_by_customer_segment,
    REMINDER_SCHEDULE
)


@pytest.fixture
def cleanup_db():
    """Clean up test abandoned orders before and after each test."""
    engine = get_engine()
    # Ensure tables exist
    Base.metadata.create_all(engine)
    
    session = get_session()
    try:
        # Clean ALL orders before (not just TEST_% - they may come from previous test data)
        session.query(Order).delete()
        try:
            session.query(AbandonedReminder).delete()
        except:
            pass  # Table may not exist yet
        session.commit()
    finally:
        session.close()

    yield

    # Clean after
    session = get_session()
    try:
        session.query(Order).filter(Order.receipt.like('TEST_%')).delete()
        try:
            session.query(AbandonedReminder).delete()
        except:
            pass
        session.commit()
    finally:
        session.close()


def test_get_abandoned_orders_empty(cleanup_db):
    """Test getting abandoned orders when none exist."""
    orders = get_abandoned_orders()
    assert isinstance(orders, list)
    assert len(orders) == 0


def test_get_abandoned_orders_single(cleanup_db):
    """Test getting a single abandoned order."""
    session = get_session()
    try:
        # Create abandoned order
        order = Order(
            id='TEST_ORDER_1',
            amount=19900,
            currency='INR',
            receipt='TEST_REC_1',
            product='starter_pack',
            status='created',  # Not paid
            created_at=time.time()
        )
        session.add(order)
        session.commit()
    finally:
        session.close()

    orders = get_abandoned_orders()
    assert len(orders) == 1
    assert orders[0]['receipt'] == 'TEST_REC_1'
    assert orders[0]['product'] == 'starter_pack'
    assert orders[0]['amount_paise'] == 19900
    assert orders[0]['amount_rupees'] == 199


def test_get_abandoned_orders_multiple(cleanup_db):
    """Test getting multiple abandoned orders."""
    session = get_session()
    try:
        for i in range(5):
            order = Order(
                id=f'TEST_ORDER_{i}',
                amount=10000 * (i + 1),
                currency='INR',
                receipt=f'TEST_REC_{i}',
                product='pro_pack',
                status='created',
                created_at=time.time()
            )
            session.add(order)
        session.commit()
    finally:
        session.close()

    orders = get_abandoned_orders()
    assert len(orders) == 5
    # Verify that orders have required fields
    for o in orders:
        assert 'receipt' in o
        assert 'product' in o
        assert 'amount_paise' in o


def test_get_abandoned_orders_excludes_paid(cleanup_db):
    """Test that paid orders are not included in abandoned list."""
    session = get_session()
    try:
        # Create both paid and unpaid orders
        paid = Order(
            id='TEST_PAID',
            amount=10000,
            currency='INR',
            receipt='TEST_PAID_REC',
            product='starter_pack',
            status='paid',
            created_at=time.time()
        )
        abandoned = Order(
            id='TEST_ABANDONED',
            amount=10000,
            currency='INR',
            receipt='TEST_ABANDONED_REC',
            product='starter_pack',
            status='created',
            created_at=time.time()
        )
        session.add(paid)
        session.add(abandoned)
        session.commit()
    finally:
        session.close()

    orders = get_abandoned_orders()
    assert len(orders) == 1
    assert orders[0]['receipt'] == 'TEST_ABANDONED_REC'


def test_get_abandoned_orders_hours_since(cleanup_db):
    """Test filtering abandoned orders by age."""
    session = get_session()
    try:
        now = time.time()
        # Old order (2 days ago)
        old = Order(
            id='TEST_OLD',
            amount=10000,
            currency='INR',
            receipt='TEST_OLD_REC',
            product='starter_pack',
            status='created',
            created_at=now - (48 * 3600)
        )
        # Recent order (30 minutes ago)
        recent = Order(
            id='TEST_RECENT',
            amount=10000,
            currency='INR',
            receipt='TEST_RECENT_REC',
            product='starter_pack',
            status='created',
            created_at=now - 1800
        )
        session.add(old)
        session.add(recent)
        session.commit()
    finally:
        session.close()

    # Get orders older than 24 hours
    old_orders = get_abandoned_orders(hours_since=24)
    assert len(old_orders) == 1
    assert old_orders[0]['receipt'] == 'TEST_OLD_REC'

    # Get all orders (1 hour threshold) - both should be > 1 hour old due to test execution time
    # Actually, recent order is only 30 mins old so it won't be in 1-hour filter
    # Let's just verify we get all orders without hours_since filter
    all_orders = get_abandoned_orders()
    assert len(all_orders) == 2


def test_get_recovery_metrics_empty(cleanup_db):
    """Test recovery metrics with no abandoned orders."""
    metrics = get_recovery_metrics()
    assert metrics['total_abandoned_orders'] == 0
    assert metrics['total_abandoned_value_paise'] == 0
    assert metrics['abandoned_24h'] == 0
    assert metrics['abandoned_24h_plus'] == 0


def test_get_recovery_metrics_multiple(cleanup_db):
    """Test recovery metrics calculation."""
    session = get_session()
    try:
        now = time.time()
        # Recent abandonment
        order1 = Order(
            id='TEST_M1',
            amount=50000,
            currency='INR',
            receipt='TEST_M_REC_1',
            product='starter_pack',
            status='created',
            created_at=now - 3600  # 1 hour ago
        )
        # Old abandonment
        order2 = Order(
            id='TEST_M2',
            amount=100000,
            currency='INR',
            receipt='TEST_M_REC_2',
            product='pro_pack',
            status='created',
            created_at=now - (100 * 3600)  # 100 hours ago
        )
        session.add(order1)
        session.add(order2)
        session.commit()
    finally:
        session.close()

    metrics = get_recovery_metrics()
    assert metrics['total_abandoned_orders'] == 2
    assert metrics['total_abandoned_value_paise'] == 150000
    assert metrics['abandoned_24h'] == 1
    assert metrics['abandoned_24h_plus'] == 1


def test_get_product_abandonment_rate_empty(cleanup_db):
    """Test product abandonment rates with no orders."""
    rates = get_product_abandonment_rate()
    assert isinstance(rates, dict)
    assert len(rates) == 0


def test_get_product_abandonment_rate(cleanup_db):
    """Test product abandonment rate calculation."""
    session = get_session()
    try:
        # starter_pack: 2 abandoned, 1 paid
        session.add(Order(
            id='TEST_P1',
            amount=10000,
            currency='INR',
            receipt='TEST_P_REC_1',
            product='starter_pack',
            status='created',
            created_at=time.time()
        ))
        session.add(Order(
            id='TEST_P2',
            amount=10000,
            currency='INR',
            receipt='TEST_P_REC_2',
            product='starter_pack',
            status='created',
            created_at=time.time()
        ))
        session.add(Order(
            id='TEST_P3',
            amount=10000,
            currency='INR',
            receipt='TEST_P_REC_3',
            product='starter_pack',
            status='paid',
            created_at=time.time()
        ))
        session.commit()
    finally:
        session.close()

    rates = get_product_abandonment_rate()
    assert 'starter_pack' in rates
    assert rates['starter_pack']['total_initiated'] == 3
    assert rates['starter_pack']['completed_orders'] == 1
    assert rates['starter_pack']['abandoned_orders'] == 2
    assert rates['starter_pack']['abandonment_rate'] == 66.7  # 2/3
    assert rates['starter_pack']['abandoned_value_paise'] == 20000


def test_get_recovery_suggestions_empty(cleanup_db):
    """Test recovery suggestions with no abandoned orders."""
    suggestions = get_recovery_suggestions()
    assert isinstance(suggestions, list)
    # May have some default suggestions


def test_get_recovery_suggestions_high_value(cleanup_db):
    """Test recovery suggestions for high-value abandoned orders."""
    session = get_session()
    try:
        # Create high-value abandoned order
        order = Order(
            id='TEST_S1',
            amount=1100000,  # ₹11k
            currency='INR',
            receipt='TEST_S_REC_1',
            product='premium_pack',
            status='created',
            created_at=time.time()
        )
        session.add(order)
        session.commit()
    finally:
        session.close()

    suggestions = get_recovery_suggestions()
    assert len(suggestions) > 0
    # Should suggest high-value recovery campaign
    priority_levels = [s['priority'] for s in suggestions]
    assert 'CRITICAL' in priority_levels or 'HIGH' in priority_levels


def test_estimate_recovery_potential_default(cleanup_db):
    """Test recovery potential with default rate."""
    session = get_session()
    try:
        order = Order(
            id='TEST_REP1',
            amount=100000,
            currency='INR',
            receipt='TEST_REP_REC_1',
            product='starter_pack',
            status='created',
            created_at=time.time()
        )
        session.add(order)
        session.commit()
    finally:
        session.close()

    potential = estimate_recovery_potential()
    assert potential['recovery_rate_percent'] == 30.0
    assert potential['estimated_recoverable_paise'] == 30000  # 30% of 100k
    assert potential['estimated_recoverable_rupees'] == 300.0


def test_estimate_recovery_potential_custom_rate(cleanup_db):
    """Test recovery potential with custom recovery rate."""
    session = get_session()
    try:
        order = Order(
            id='TEST_REP2',
            amount=100000,
            currency='INR',
            receipt='TEST_REP_REC_2',
            product='pro_pack',
            status='created',
            created_at=time.time()
        )
        session.add(order)
        session.commit()
    finally:
        session.close()

    potential = estimate_recovery_potential(recovery_rate=0.5)
    assert potential['recovery_rate_percent'] == 50.0
    assert potential['estimated_recoverable_paise'] == 50000
    assert potential['estimated_recoverable_rupees'] == 500.0


def test_get_abandoned_orders_by_customer_segment(cleanup_db):
    """Test grouping abandoned orders by customer segment."""
    session = get_session()
    try:
        # Create abandoned orders for different products
        session.add(Order(
            id='TEST_SEG1',
            amount=10000,
            currency='INR',
            receipt='TEST_SEG_REC_1',
            product='starter_pack',
            status='created',
            created_at=time.time()
        ))
        session.add(Order(
            id='TEST_SEG2',
            amount=20000,
            currency='INR',
            receipt='TEST_SEG_REC_2',
            product='pro_pack',
            status='created',
            created_at=time.time()
        ))
        session.add(Order(
            id='TEST_SEG3',
            amount=15000,
            currency='INR',
            receipt='TEST_SEG_REC_3',
            product='starter_pack',
            status='created',
            created_at=time.time()
        ))
        session.commit()
    finally:
        session.close()

    segment_data = get_abandoned_orders_by_customer_segment()
    assert 'total_abandoned' in segment_data
    assert 'by_product' in segment_data
    assert segment_data['total_abandoned'] == 3
    assert 'starter_pack' in segment_data['by_product']
    assert 'pro_pack' in segment_data['by_product']
    assert segment_data['by_product']['starter_pack']['count'] == 2
    assert segment_data['by_product']['pro_pack']['count'] == 1


def test_should_send_reminder_not_created(cleanup_db):
    """Test that reminders are not sent for paid orders."""
    session = get_session()
    try:
        order = Order(
            id='TEST_REM1',
            amount=10000,
            currency='INR',
            receipt='TEST_REM_REC_1',
            product='starter_pack',
            status='paid',
            created_at=time.time()
        )
        session.add(order)
        session.commit()
    finally:
        session.close()

    # Should not send reminder for paid order
    result = should_send_reminder('TEST_REM1', 0)
    assert result is False


def test_should_send_reminder_too_early(cleanup_db):
    """Test that first reminder is not sent too early."""
    session = get_session()
    try:
        order = Order(
            id='TEST_REM2',
            amount=10000,
            currency='INR',
            receipt='TEST_REM_REC_2',
            product='starter_pack',
            status='created',
            created_at=time.time()  # Just created
        )
        session.add(order)
        session.commit()
    finally:
        session.close()

    # First reminder is scheduled for 1 hour - shouldn't send immediately
    result = should_send_reminder('TEST_REM2', 0)
    assert result is False


def test_should_send_reminder_ready(cleanup_db):
    """Test that reminder is sent when ready."""
    session = get_session()
    try:
        now = time.time()
        order = Order(
            id='TEST_REM3',
            amount=10000,
            currency='INR',
            receipt='TEST_REM_REC_3',
            product='starter_pack',
            status='created',
            created_at=now - 7200  # 2 hours ago
        )
        session.add(order)
        session.commit()
    finally:
        session.close()

    # First reminder (1 hour) should be ready
    result = should_send_reminder('TEST_REM3', 0)
    assert result is True

    # Second reminder (24 hours) should not be ready
    result = should_send_reminder('TEST_REM3', 1)
    assert result is False


def test_reminder_schedule_config():
    """Test that reminder schedule is properly configured."""
    assert len(REMINDER_SCHEDULE) >= 3
    assert REMINDER_SCHEDULE[0]['delay_hours'] == 1
    assert REMINDER_SCHEDULE[1]['delay_hours'] == 24
    assert REMINDER_SCHEDULE[2]['delay_hours'] == 72
