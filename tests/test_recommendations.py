"""Tests for Smart Recommendations Engine."""
import pytest
import time
import os
import sys

# Add parent directory to path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from recommendations import (
    generate_recommendations,
    get_product_performance,
    get_cross_sell_opportunities,
    calculate_product_affinity,
    get_complementary_products,
    calculate_seasonal_boost,
    get_recommendation_stats,
    PRODUCT_CATALOG,
    calculate_recommendation_impact,
    Recommendation,
    RecommendationResult
)
import models as models_module
from models import Customer, Order, get_session, get_engine, Base
from datetime import datetime, timedelta


@pytest.fixture(scope="function")
def setup_db():
    """Setup clean in-memory database for each test."""
    # Use in-memory SQLite to avoid file locking on Windows
    engine = get_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    
    # Monkeypatch get_engine to return our in-memory engine
    original_get_engine = models_module.get_engine
    models_module.get_engine = lambda db_url=None: engine
    
    yield engine
    
    # Restore original
    models_module.get_engine = original_get_engine


@pytest.fixture
def sample_customer(setup_db):
    """Create a sample customer."""
    session = get_session()
    try:
        customer = Customer(
            receipt='TEST001',
            segment='premium',
            ltv_paise=10000,  # ₹100
            order_count=3
        )
        session.add(customer)
        session.commit()
        return customer.receipt
    finally:
        session.close()


@pytest.fixture
def new_customer(setup_db):
    """Create a new customer (no orders)."""
    session = get_session()
    try:
        customer = Customer(
            receipt='TEST002',
            segment='standard',
            ltv_paise=0,
            order_count=0
        )
        session.add(customer)
        session.commit()
        return customer.receipt
    finally:
        session.close()


def test_product_catalog_exists():
    """Test product catalog is populated."""
    assert len(PRODUCT_CATALOG) == 4
    assert 'starter' in PRODUCT_CATALOG
    assert 'pro' in PRODUCT_CATALOG
    assert 'premium' in PRODUCT_CATALOG
    assert 'platinum' in PRODUCT_CATALOG
    
    # Each product has required fields
    for product_code, product_info in PRODUCT_CATALOG.items():
        assert 'name' in product_info
        assert 'price' in product_info
        assert 'description' in product_info


def test_recommendation_class():
    """Test Recommendation data class."""
    rec = Recommendation('Premium Pack', 85.5, 'Great value for learners', 0.92)
    
    assert rec.product_name == 'Premium Pack'
    assert rec.score == 85.5
    assert rec.reason == 'Great value for learners'
    assert rec.confidence == 0.92
    assert rec.created_at


def test_recommendation_result_to_dict():
    """Test RecommendationResult serialization."""
    recs = [
        Recommendation('Starter', 40, 'Entry point'),
        Recommendation('Pro', 60, 'Great upgrade'),
    ]
    
    result = RecommendationResult('TEST001', recs)
    data = result.to_dict()
    
    assert data['receipt'] == 'TEST001'
    assert data['total_recommendations'] == 2
    assert len(data['recommendations']) == 2
    assert data['recommendations'][0]['product'] == 'Starter'
    assert 'confidence' in data['recommendations'][0]


def test_get_complementary_products():
    """Test complementary product suggestions."""
    # Starter -> pro, premium, platinum
    assert get_complementary_products('starter') == ['pro', 'premium', 'platinum']
    
    # Pro -> premium, platinum
    assert get_complementary_products('pro') == ['premium', 'platinum']
    
    # Premium -> platinum
    assert get_complementary_products('premium') == ['platinum']
    
    # Platinum -> none
    assert get_complementary_products('platinum') == []


def test_calculate_seasonal_boost():
    """Test seasonal boost calculation."""
    # Q4 (Oct, Nov, Dec) - strong season
    oct_date = datetime(2024, 10, 1)
    assert calculate_seasonal_boost(oct_date) == 1.3
    
    # Q1 (Jan, Feb) - New Year resolutions
    jan_date = datetime(2024, 1, 1)
    assert calculate_seasonal_boost(jan_date) == 1.2
    
    # Mid-year (May, June, July)
    may_date = datetime(2024, 5, 15)
    assert calculate_seasonal_boost(may_date) == 1.0


def test_calculate_product_affinity_new_customer(setup_db):
    """Test affinity calculation for new customer."""
    affinity = calculate_product_affinity('NONEXISTENT')
    
    # New customers should get default recommendations
    assert 'starter' in affinity
    assert 'pro' in affinity
    assert 'premium' in affinity
    assert 'platinum' in affinity
    
    # Starter should be most likely
    assert affinity['starter'] > affinity['pro']
    assert affinity['pro'] > affinity['premium']


def test_calculate_product_affinity_existing_customer(setup_db, sample_customer):
    """Test affinity calculation for existing customer."""
    affinity = calculate_product_affinity(sample_customer)
    
    # Should return affinity scores for all products
    assert isinstance(affinity, dict)
    assert all(isinstance(v, (int, float)) for v in affinity.values())


def test_generate_recommendations_new_customer(setup_db, new_customer):
    """Test recommendations for new customer."""
    result = generate_recommendations(new_customer, limit=3)
    
    assert result.customer_receipt == new_customer
    assert len(result.recommendations) <= 3
    
    # All should be Recommendation objects
    for rec in result.recommendations:
        assert isinstance(rec, Recommendation)
        assert 0 <= rec.score <= 100
        assert 0 <= rec.confidence <= 1


def test_generate_recommendations_existing_customer(setup_db, sample_customer):
    """Test recommendations for existing customer."""
    result = generate_recommendations(sample_customer, limit=3)
    
    assert result.customer_receipt == sample_customer
    assert len(result.recommendations) > 0
    
    # Serialize to dict
    data = result.to_dict()
    assert 'recommendations' in data
    assert all('product' in r for r in data['recommendations'])


def test_generate_recommendations_limit(setup_db, sample_customer):
    """Test recommendations respects limit parameter."""
    result = generate_recommendations(sample_customer, limit=1)
    assert len(result.recommendations) <= 1
    
    result = generate_recommendations(sample_customer, limit=5)
    assert len(result.recommendations) <= 5


def test_get_product_performance(setup_db, sample_customer):
    """Test product performance metrics."""
    # Add some orders with unique IDs
    session = get_session()
    try:
        orders = [
            Order(id='ORD001', receipt=sample_customer, product='starter', amount=9900, status='completed', created_at=time.time()),
            Order(id='ORD002', receipt=sample_customer, product='pro', amount=49900, status='completed', created_at=time.time()),
        ]
        session.add_all(orders)
        session.commit()
    finally:
        session.close()
    
    perf = get_product_performance()
    
    assert 'starter' in perf
    assert 'pro' in perf
    assert 'premium' in perf
    assert 'platinum' in perf
    
    # Check metrics
    for product_code, metrics in perf.items():
        assert 'name' in metrics
        assert 'total_orders' in metrics
        assert 'total_revenue' in metrics
        assert 'unique_customers' in metrics
        assert 'avg_order_value' in metrics


def test_get_cross_sell_opportunities(setup_db, sample_customer):
    """Test cross-sell opportunity identification."""
    opportunities = get_cross_sell_opportunities()
    
    assert isinstance(opportunities, list)
    
    if opportunities:
        opp = opportunities[0]
        assert 'receipt' in opp
        assert 'ltv' in opp
        assert 'order_count' in opp
        assert 'recommended_product' in opp
        assert 'confidence' in opp


def test_calculate_recommendation_impact(setup_db, sample_customer):
    """Test recommendation impact calculation."""
    impact = calculate_recommendation_impact()
    
    assert 'total_customers' in impact
    assert 'recommendations_made' in impact
    assert 'total_customer_ltv' in impact
    assert 'average_customer_ltv' in impact
    assert 'estimated_revenue_lift' in impact
    assert 'estimated_lift_percentage' in impact
    
    # Values should be reasonable
    assert impact['total_customers'] >= 0
    assert impact['estimated_revenue_lift'] >= 0
    assert impact['estimated_lift_percentage'] >= 0


def test_get_recommendation_stats(setup_db, sample_customer):
    """Test complete recommendation statistics."""
    stats = get_recommendation_stats()
    
    assert 'product_performance' in stats
    assert 'recommendation_impact' in stats
    assert 'generated_at' in stats
    
    # Product performance should have all 4 products
    assert len(stats['product_performance']) == 4
    
    # Impact should have metrics
    assert 'total_customers' in stats['recommendation_impact']


def test_recommendations_scores_are_valid(setup_db, sample_customer):
    """Test all recommendation scores are in valid range."""
    result = generate_recommendations(sample_customer, limit=5)
    
    for rec in result.recommendations:
        assert 0 <= rec.score <= 100, f"Invalid score: {rec.score}"
        assert 0 <= rec.confidence <= 1, f"Invalid confidence: {rec.confidence}"


def test_recommendation_reasons_generated(setup_db, sample_customer):
    """Test recommendations include reasons."""
    result = generate_recommendations(sample_customer, limit=3)
    
    for rec in result.recommendations:
        assert rec.reason
        assert len(rec.reason) > 0
        assert isinstance(rec.reason, str)


def test_recommendations_deterministic(setup_db, sample_customer):
    """Test recommendations are consistent for same customer."""
    result1 = generate_recommendations(sample_customer, limit=2)
    result2 = generate_recommendations(sample_customer, limit=2)
    
    # Should recommend same products
    rec1_products = [r.product_name for r in result1.recommendations]
    rec2_products = [r.product_name for r in result2.recommendations]
    
    assert rec1_products == rec2_products


def test_product_catalog_complete():
    """Test all products have complete information."""
    for code, product in PRODUCT_CATALOG.items():
        assert product['price'] > 0
        assert 'tags' in product
        assert isinstance(product['tags'], list)


@pytest.fixture
def orders_setup(setup_db, sample_customer):
    """Setup multiple orders for testing."""
    session = get_session()
    try:
        orders = [
            Order(
                id='ORDERS001',
                receipt=sample_customer,
                product='starter',
                amount=9900,
                status='completed',
                created_at=time.time() - 86400 * 90
            ),
            Order(
                id='ORDERS002',
                receipt=sample_customer,
                product='pro',
                amount=49900,
                status='completed',
                created_at=time.time() - 86400 * 30
            ),
        ]
        session.add_all(orders)
        session.commit()
    finally:
        session.close()
    
    return sample_customer


def test_upgrade_path_recommendations(setup_db, orders_setup):
    """Test recommendations follow upgrade path."""
    result = generate_recommendations(orders_setup, limit=2)
    
    # With pro already bought, should recommend premium or platinum
    product_names = [r.product_name for r in result.recommendations]
    
    # At least one should be premium or platinum (upgrade from pro)
    assert any('Premium' in name or 'Platinum' in name for name in product_names)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
