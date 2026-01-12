"""Tests for customer intelligence and segmentation."""
import pytest
import time
import uuid
from customer_intelligence import (
    get_customer_ltv, get_customer_segment, get_all_customers_segmented,
    get_segment_summary, identify_marketing_opportunities, get_customer_churn_risk,
    CustomerSegment
)
from models import get_session, Order


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up test data before and after each test."""
    # Clean before
    session = get_session()
    try:
        session.query(Order).filter(Order.receipt.like('TEST_%')).delete()
        session.commit()
    finally:
        session.close()
    
    yield
    
    # Clean after
    session = get_session()
    try:
        session.query(Order).filter(Order.receipt.like('TEST_%')).delete()
        session.commit()
    finally:
        session.close()


def unique_order_id():
    return f"TEST_{uuid.uuid4().hex[:12]}"


def test_ltv_single_order():
    """Test LTV calculation with single order."""
    now = time.time()
    receipt = f"TEST_{uuid.uuid4().hex[:8]}"
    
    session = get_session()
    try:
        order = Order(
            id=unique_order_id(), amount=100000, currency='INR',
            receipt=receipt, product='starter_pack', status='paid', created_at=now
        )
        session.add(order)
        session.commit()
    finally:
        session.close()
    
    ltv = get_customer_ltv(receipt)
    assert ltv is not None
    assert ltv['ltv_paise'] == 100000
    assert ltv['order_count'] == 1


def test_ltv_multiple_orders():
    """Test LTV with multiple orders."""
    now = time.time()
    receipt = f"TEST_{uuid.uuid4().hex[:8]}"
    
    session = get_session()
    try:
        for i, amount in enumerate([100000, 150000, 200000]):
            order = Order(
                id=unique_order_id(), amount=amount, currency='INR',
                receipt=receipt, product='pro_pack', status='paid',
                created_at=now - (i * 86400)
            )
            session.add(order)
        session.commit()
    finally:
        session.close()
    
    ltv = get_customer_ltv(receipt)
    assert ltv['ltv_paise'] == 450000
    assert ltv['order_count'] == 3
    assert ltv['avg_order_value_paise'] == 150000


def test_segment_new_customer():
    """Test NEW segment for recently acquired customers."""
    now = time.time()
    receipt = f"TEST_{uuid.uuid4().hex[:8]}"
    
    session = get_session()
    try:
        order = Order(
            id=unique_order_id(), amount=50000, currency='INR',
            receipt=receipt, product='starter_pack', status='paid', created_at=now
        )
        session.add(order)
        session.commit()
    finally:
        session.close()
    
    segment = get_customer_segment(receipt)
    assert segment['segment'] == 'NEW'


def test_segment_loyal_customer():
    """Test LOYAL segment for repeat customers."""
    now = time.time()
    receipt = f"TEST_{uuid.uuid4().hex[:8]}"
    
    session = get_session()
    try:
        for i in range(3):
            order = Order(
                id=unique_order_id(), amount=100000, currency='INR',
                receipt=receipt, product='pro_pack', status='paid',
                created_at=now - (i * 30 * 86400)  # Recent purchases
            )
            session.add(order)
        session.commit()
    finally:
        session.close()
    
    segment = get_customer_segment(receipt)
    assert segment['segment'] in ['LOYAL', 'GROWING']


def test_segment_at_risk():
    """Test AT_RISK segment for inactive customers."""
    now = time.time()
    receipt = f"TEST_{uuid.uuid4().hex[:8]}"
    
    session = get_session()
    try:
        # Created 200 days ago, haven't purchased since
        old_time = now - (200 * 86400)
        for i in range(2):
            order = Order(
                id=unique_order_id(), amount=100000, currency='INR',
                receipt=receipt, product='pro_pack', status='paid',
                created_at=old_time - (i * 30 * 86400)
            )
            session.add(order)
        session.commit()
    finally:
        session.close()
    
    segment = get_customer_segment(receipt)
    assert segment['segment'] == 'AT_RISK'


def test_segment_vip():
    """Test VIP segment for high-value active customers."""
    now = time.time()
    receipt = f"TEST_{uuid.uuid4().hex[:8]}"
    
    session = get_session()
    try:
        # High value recent purchases
        for i in range(3):
            order = Order(
                id=unique_order_id(), amount=2000000, currency='INR',
                receipt=receipt, product='premium_pack', status='paid',
                created_at=now - (i * 20 * 86400)  # Recent
            )
            session.add(order)
        session.commit()
    finally:
        session.close()
    
    segment = get_customer_segment(receipt)
    assert segment['segment'] == 'VIP'


def test_segment_one_time():
    """Test ONE_TIME segment."""
    now = time.time()
    receipt = f"TEST_{uuid.uuid4().hex[:8]}"
    
    session = get_session()
    try:
        # Single old purchase
        old_time = now - (60 * 86400)
        order = Order(
            id=unique_order_id(), amount=50000, currency='INR',
            receipt=receipt, product='starter_pack', status='paid',
            created_at=old_time
        )
        session.add(order)
        session.commit()
    finally:
        session.close()
    
    segment = get_customer_segment(receipt)
    assert segment['segment'] == 'ONE_TIME'


def test_get_all_customers_segmented():
    """Test batch customer segmentation."""
    now = time.time()
    
    # Create diverse customers
    receipts = []
    for i in range(3):
        receipt = f"TEST_{uuid.uuid4().hex[:8]}"
        receipts.append(receipt)
        
        session = get_session()
        try:
            order = Order(
                id=unique_order_id(), amount=50000 * (i + 1), currency='INR',
                receipt=receipt, product='starter_pack', status='paid', created_at=now
            )
            session.add(order)
            session.commit()
        finally:
            session.close()
    
    customers = get_all_customers_segmented(days_back=30)
    assert len(customers) >= 3
    
    # Check structure
    for cust in customers[:1]:
        assert 'receipt' in cust
        assert 'segment' in cust
        assert 'ltv_paise' in cust
        assert 'order_count' in cust


def test_segment_summary():
    """Test segment summary statistics."""
    now = time.time()
    
    # Create test customers
    for i in range(2):
        receipt = f"TEST_{uuid.uuid4().hex[:8]}"
        session = get_session()
        try:
            order = Order(
                id=unique_order_id(), amount=100000, currency='INR',
                receipt=receipt, product='pro_pack', status='paid',
                created_at=now - (i * 20 * 86400)
            )
            session.add(order)
            session.commit()
        finally:
            session.close()
    
    summary = get_segment_summary()
    assert isinstance(summary, dict)
    assert any(segment['customer_count'] > 0 for segment in summary.values())


def test_marketing_opportunities():
    """Test marketing opportunity identification."""
    now = time.time()
    
    # Create test customer
    receipt = f"TEST_{uuid.uuid4().hex[:8]}"
    session = get_session()
    try:
        order = Order(
            id=unique_order_id(), amount=100000, currency='INR',
            receipt=receipt, product='pro_pack', status='paid', created_at=now
        )
        session.add(order)
        session.commit()
    finally:
        session.close()
    
    opportunities = identify_marketing_opportunities()
    assert isinstance(opportunities, dict)
    # Should have opportunities for various segments
    assert len(opportunities) > 0


def test_churn_risk_identification():
    """Test churn risk detection."""
    now = time.time()
    
    # Create at-risk customer
    receipt = f"TEST_{uuid.uuid4().hex[:8]}"
    old_time = now - (200 * 86400)
    
    session = get_session()
    try:
        order = Order(
            id=unique_order_id(), amount=500000, currency='INR',
            receipt=receipt, product='pro_pack', status='paid', created_at=old_time
        )
        session.add(order)
        session.commit()
    finally:
        session.close()
    
    churn_risk = get_customer_churn_risk()
    assert isinstance(churn_risk, list)
    # Should have identified this as at-risk
    assert any(c['receipt'] == receipt for c in churn_risk)


def test_ltv_ignores_unpaid_orders():
    """Test that LTV only counts paid orders."""
    now = time.time()
    receipt = f"TEST_{uuid.uuid4().hex[:8]}"
    
    session = get_session()
    try:
        # Add paid order
        session.add(Order(
            id=unique_order_id(), amount=100000, currency='INR',
            receipt=receipt, product='pro_pack', status='paid', created_at=now
        ))
        # Add unpaid order
        session.add(Order(
            id=unique_order_id(), amount=200000, currency='INR',
            receipt=receipt, product='premium_pack', status='created', created_at=now
        ))
        session.commit()
    finally:
        session.close()
    
    ltv = get_customer_ltv(receipt)
    # Should only count paid order
    assert ltv['ltv_paise'] == 100000
    assert ltv['order_count'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
