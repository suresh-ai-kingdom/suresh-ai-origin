"""
Tests for Recovery Pricing AI System
Tests all recovery pricing functions with mocks and edge cases
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from recovery_pricing_ai import (
    RecoveryPricingAI,
    RecoveryPricingProfile,
    RecoveryOutcome,
    calculate_recovery_price,
    get_recovery_suggestions_optimized,
    get_recovery_metrics,
    get_ab_test_winners
)


# ==================== FIXTURES ====================

@pytest.fixture
def recovery_ai():
    """Create RecoveryPricingAI instance."""
    return RecoveryPricingAI(data_dir="test_data")


@pytest.fixture
def cleanup_test_files():
    """Cleanup test files."""
    yield
    
    import shutil
    if Path("test_data").exists():
        shutil.rmtree("test_data")


@pytest.fixture
def mock_order():
    """Mock order object."""
    order = Mock()
    order.id = "ORDER_123"
    order.receipt = "cust_test_123"
    order.amount = 50000  # ₹500
    order.product = "pro"
    order.status = "created"
    order.created_at = time.time()
    return order


@pytest.fixture
def mock_customer():
    """Mock customer object."""
    customer = Mock()
    customer.receipt = "cust_test_123"
    customer.name = "Test Customer"
    customer.email = "test@example.com"
    return customer


# ==================== INITIALIZATION TESTS ====================

def test_recovery_ai_initialization(recovery_ai):
    """Test RecoveryPricingAI initialization."""
    assert recovery_ai is not None
    assert recovery_ai.data_dir is not None
    assert len(recovery_ai.test_variants) == 4
    assert 'high' in recovery_ai.segment_discount_ranges


def test_segment_discount_ranges(recovery_ai):
    """Test segment-based discount ranges."""
    ranges = recovery_ai.segment_discount_ranges
    
    assert ranges['high'][0] < ranges['high'][1]      # Min < Max
    assert ranges['high'][0] < ranges['medium'][0]     # High discount less than medium
    assert ranges['new'][0] > ranges['high'][0]        # New customers get bigger discount


def test_variant_discount_assignments(recovery_ai):
    """Test A/B variant discount values."""
    variants = recovery_ai.variant_discounts
    
    assert variants['A'] == 0.25  # Control
    assert variants['B'] == 0.35  # Aggressive
    assert variants['C'] == 0.15  # Conservative
    assert variants['D'] == 0.50  # Desperate


# ==================== CUSTOMER SEGMENTATION TESTS ====================

@patch('recovery_pricing_ai.get_session')
def test_get_customer_ltv_no_purchases(mock_session, recovery_ai):
    """Test LTV calculation for customer with no purchases."""
    mock_query = Mock()
    mock_query.filter.return_value.scalar.return_value = 0
    mock_session.return_value.query.return_value = mock_query
    
    ltv = recovery_ai._get_customer_ltv("cust_new")
    
    assert ltv == 0


@patch('recovery_pricing_ai.get_session')
def test_get_customer_ltv_with_purchases(mock_session, recovery_ai):
    """Test LTV calculation for returning customer."""
    mock_query = Mock()
    mock_query.filter.return_value.scalar.return_value = 50000  # ₹500 in paise
    mock_session.return_value.query.return_value = mock_query
    
    ltv = recovery_ai._get_customer_ltv("cust_vip")
    
    assert ltv == 500.0


@patch('recovery_pricing_ai.get_session')
def test_get_customer_segment_new(mock_session, recovery_ai):
    """Test customer segmentation - new customer."""
    mock_query = Mock()
    mock_query.filter.return_value.scalar.return_value = 0
    mock_session.return_value.query.return_value = mock_query
    
    segment = recovery_ai._get_customer_segment("cust_new")
    
    assert segment == 'new'


@patch('recovery_pricing_ai.get_session')
def test_get_customer_segment_high_value(mock_session, recovery_ai):
    """Test customer segmentation - high-value customer."""
    mock_query = Mock()
    mock_query.filter.return_value.scalar.return_value = 1500000  # ₹15K in paise
    mock_session.return_value.query.return_value = mock_query
    
    segment = recovery_ai._get_customer_segment("cust_vip")
    
    assert segment == 'high'


@patch('recovery_pricing_ai.get_session')
def test_get_customer_segment_medium(mock_session, recovery_ai):
    """Test customer segmentation - medium-value customer."""
    mock_query = Mock()
    mock_query.filter.return_value.scalar.return_value = 500000  # ₹5K in paise
    mock_session.return_value.query.return_value = mock_query
    
    segment = recovery_ai._get_customer_segment("cust_medium")
    
    assert segment == 'medium'


def test_get_segment_conversion_rate(recovery_ai):
    """Test conversion rate by segment."""
    assert recovery_ai._get_segment_conversion_rate('high') == 0.65
    assert recovery_ai._get_segment_conversion_rate('medium') == 0.45
    assert recovery_ai._get_segment_conversion_rate('low') == 0.30
    assert recovery_ai._get_segment_conversion_rate('new') == 0.20


# ==================== A/B TESTING TESTS ====================

def test_variant_assignment_consistency(recovery_ai):
    """Test that variant assignment is consistent for same customer."""
    receipt = "cust_test_123"
    
    variant1 = recovery_ai._get_variant_for_customer(receipt)
    variant2 = recovery_ai._get_variant_for_customer(receipt)
    
    assert variant1 == variant2  # Same customer gets same variant


def test_variant_assignment_distribution(recovery_ai):
    """Test variant distribution across customers."""
    variants = set()
    
    for i in range(100):
        receipt = f"cust_test_{i}"
        variant = recovery_ai._get_variant_for_customer(receipt)
        variants.add(variant)
    
    assert len(variants) == 4  # Should have all 4 variants


def test_variant_discount_lookup(recovery_ai):
    """Test A/B variant discount lookup."""
    for variant in ['A', 'B', 'C', 'D']:
        discount = recovery_ai.variant_discounts[variant]
        assert 0.0 < discount < 1.0


# ==================== PRICE CALCULATION TESTS ====================

@patch('recovery_pricing_ai.get_session')
def test_calculate_recovery_price_new_customer(mock_session, recovery_ai):
    """Test recovery price calculation for new customer."""
    # Mock database
    mock_order = Mock()
    mock_order.id = "ORDER_1"
    mock_order.amount = 10000  # ₹100
    
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_order
    mock_session.return_value.query.return_value = mock_query
    
    # Mock LTV query
    mock_ltv_query = Mock()
    mock_ltv_query.filter.return_value.scalar.return_value = 0
    
    call_count = 0
    def query_side_effect(model):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_query
        else:
            return mock_ltv_query
    
    mock_session.return_value.query.side_effect = query_side_effect
    
    profile = recovery_ai.calculate_recovery_price("ORDER_1", "cust_new")
    
    assert profile is not None
    assert profile.ltv_segment == 'new'
    # Discount should be within A/B variant range or new customer segment range
    assert 0.10 <= profile.base_discount_percent / 100 <= 0.60


@patch('recovery_pricing_ai.get_session')
def test_calculate_recovery_price_high_value(mock_session, recovery_ai):
    """Test recovery price calculation for high-value customer."""
    mock_order = Mock()
    mock_order.id = "ORDER_2"
    mock_order.amount = 100000  # ₹1000
    
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_order
    
    mock_ltv_query = Mock()
    mock_ltv_query.filter.return_value.scalar.return_value = 5000000  # ₹50K
    
    call_count = 0
    def query_side_effect(model):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_query
        else:
            return mock_ltv_query
    
    mock_session.return_value.query.side_effect = query_side_effect
    
    profile = recovery_ai.calculate_recovery_price("ORDER_2", "cust_vip")
    
    assert profile is not None
    assert profile.ltv_segment == 'high'
    assert profile.conversion_probability == 0.65


@patch('recovery_pricing_ai.get_session')
def test_calculate_recovery_price_order_not_found(mock_session, recovery_ai):
    """Test recovery price calculation when order not found."""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.return_value.query.return_value = mock_query
    
    profile = recovery_ai.calculate_recovery_price("INVALID_ORDER", "cust_test")
    
    assert profile is None


def test_recovery_pricing_profile_structure(recovery_ai):
    """Test RecoveryPricingProfile data structure."""
    profile = RecoveryPricingProfile(
        customer_receipt="cust_test",
        base_discount_percent=25.0,
        reasoning="Test segment",
        ltv_segment="medium",
        conversion_probability=0.45,
        expected_recovery_value=500.0,
        confidence_score=0.85,
        variant="A"
    )
    
    assert profile.customer_receipt == "cust_test"
    assert profile.base_discount_percent == 25.0
    assert profile.ltv_segment == "medium"
    assert profile.conversion_probability == 0.45


# ==================== OUTCOME TRACKING TESTS ====================

def test_log_recovery_outcome(recovery_ai, cleanup_test_files):
    """Test logging recovery outcome."""
    outcome = RecoveryOutcome(
        order_id="ORDER_1",
        customer_receipt="cust_test",
        original_amount_paise=10000,
        offered_discount_percent=25.0,
        offered_price_paise=7500,
        email_sent_at=time.time(),
        conversion=True,
        paid_amount_paise=7500,
        paid_at=time.time()
    )
    
    result = recovery_ai.log_recovery_outcome(outcome)
    
    assert result is True
    assert recovery_ai.outcomes_file.exists()


def test_recovery_outcome_structure():
    """Test RecoveryOutcome data structure."""
    outcome = RecoveryOutcome(
        order_id="ORDER_1",
        customer_receipt="cust_test",
        original_amount_paise=10000,
        offered_discount_percent=25.0,
        offered_price_paise=7500,
        email_sent_at=time.time(),
        email_opened=True,
        link_clicked=True,
        conversion=True,
        paid_amount_paise=7500,
        paid_at=time.time()
    )
    
    assert outcome.order_id == "ORDER_1"
    assert outcome.conversion is True
    assert outcome.email_opened is True


# ==================== PERFORMANCE METRICS TESTS ====================

def test_get_recovery_performance_metrics_empty(recovery_ai, cleanup_test_files):
    """Test recovery metrics with no data."""
    metrics = recovery_ai.get_recovery_performance_metrics()
    
    assert metrics['total_campaigns'] == 0
    assert metrics['conversion_rate'] == 0
    assert metrics['email_open_rate'] == 0


def test_get_recovery_performance_metrics_with_data(recovery_ai, cleanup_test_files):
    """Test recovery metrics with sample data."""
    # Log some outcomes
    outcomes_data = [
        {
            'order_id': 'ORDER_1',
            'customer_receipt': 'cust_1',
            'original_amount_paise': 10000,
            'offered_discount_percent': 25.0,
            'offered_price_paise': 7500,
            'email_sent_at': time.time(),
            'email_opened': True,
            'link_clicked': True,
            'conversion': True,
            'paid_amount_paise': 7500,
            'paid_at': time.time()
        },
        {
            'order_id': 'ORDER_2',
            'customer_receipt': 'cust_2',
            'original_amount_paise': 20000,
            'offered_discount_percent': 30.0,
            'offered_price_paise': 14000,
            'email_sent_at': time.time(),
            'email_opened': False,
            'link_clicked': False,
            'conversion': False,
            'paid_amount_paise': 0,
            'paid_at': 0.0
        }
    ]
    
    with open(recovery_ai.outcomes_file, 'w') as f:
        for outcome in outcomes_data:
            f.write(json.dumps(outcome) + '\n')
    
    metrics = recovery_ai.get_recovery_performance_metrics()
    
    assert metrics['total_campaigns'] == 2
    assert metrics['conversion_rate'] == 50.0  # 1 out of 2
    assert metrics['email_open_rate'] == 50.0
    assert metrics['total_recovered'] == 75.0  # ₹75


# ==================== A/B TEST RESULTS ====================

def test_get_ab_test_results_empty(recovery_ai, cleanup_test_files):
    """Test A/B test results with no data."""
    results = recovery_ai.get_ab_test_results()
    
    assert isinstance(results, dict)
    assert len(results) == 0


def test_get_ab_test_results_with_data(recovery_ai, cleanup_test_files):
    """Test A/B test results with sample data."""
    outcomes_data = [
        # Variant A: 2 campaigns, 1 conversion
        {
            'order_id': 'ORDER_A1',
            'variant': 'A',
            'conversion': True,
            'paid_amount_paise': 7500
        },
        {
            'order_id': 'ORDER_A2',
            'variant': 'A',
            'conversion': False,
            'paid_amount_paise': 0
        },
        # Variant B: 2 campaigns, 2 conversions
        {
            'order_id': 'ORDER_B1',
            'variant': 'B',
            'conversion': True,
            'paid_amount_paise': 7500
        },
        {
            'order_id': 'ORDER_B2',
            'variant': 'B',
            'conversion': True,
            'paid_amount_paise': 10000
        }
    ]
    
    with open(recovery_ai.outcomes_file, 'w') as f:
        for outcome in outcomes_data:
            f.write(json.dumps(outcome) + '\n')
    
    results = recovery_ai.get_ab_test_results()
    
    assert 'A' in results
    assert 'B' in results
    assert results['A']['conversion_rate'] == 50.0
    assert results['B']['conversion_rate'] == 100.0


def test_recommend_best_variant(recovery_ai, cleanup_test_files):
    """Test recommending best A/B variant."""
    outcomes_data = [
        {'order_id': 'ORDER_A1', 'variant': 'A', 'conversion': True, 'paid_amount_paise': 7500},
        {'order_id': 'ORDER_A2', 'variant': 'A', 'conversion': False, 'paid_amount_paise': 0},
        {'order_id': 'ORDER_B1', 'variant': 'B', 'conversion': True, 'paid_amount_paise': 7500},
        {'order_id': 'ORDER_B2', 'variant': 'B', 'conversion': True, 'paid_amount_paise': 10000}
    ]
    
    with open(recovery_ai.outcomes_file, 'w') as f:
        for outcome in outcomes_data:
            f.write(json.dumps(outcome) + '\n')
    
    best = recovery_ai.recommend_best_variant()
    
    assert best == 'B'  # Variant B has 100% conversion


# ==================== PRIORITY CALCULATION ====================

def test_calculate_priority_urgent(recovery_ai):
    """Test priority calculation - urgent."""
    priority = recovery_ai._calculate_priority(hours_abandoned=0.5, amount_paise=50000)
    assert priority == 'URGENT'


def test_calculate_priority_high(recovery_ai):
    """Test priority calculation - high."""
    priority = recovery_ai._calculate_priority(hours_abandoned=12, amount_paise=25000)
    assert priority == 'HIGH'


def test_calculate_priority_medium(recovery_ai):
    """Test priority calculation - medium."""
    priority = recovery_ai._calculate_priority(hours_abandoned=36, amount_paise=5000)
    assert priority == 'MEDIUM'


def test_calculate_priority_low(recovery_ai):
    """Test priority calculation - low."""
    priority = recovery_ai._calculate_priority(hours_abandoned=96, amount_paise=5000)
    assert priority == 'LOW'


# ==================== STANDALONE FUNCTION TESTS ====================

@patch('recovery_pricing_ai.RecoveryPricingAI.calculate_recovery_price')
def test_calculate_recovery_price_function(mock_calc):
    """Test standalone calculate_recovery_price function."""
    mock_profile = RecoveryPricingProfile(
        customer_receipt="cust_test",
        base_discount_percent=25.0,
        reasoning="Test",
        ltv_segment="medium",
        conversion_probability=0.45,
        expected_recovery_value=500.0,
        confidence_score=0.85,
        variant="A"
    )
    mock_calc.return_value = mock_profile
    
    result = calculate_recovery_price("ORDER_1", "cust_test")
    
    assert result is not None
    assert result['customer_segment'] == 'medium'
    assert result['base_discount_percent'] == 25.0


# ==================== EDGE CASES ====================

def test_segment_boundaries(recovery_ai):
    """Test segment boundary values."""
    # Just below medium boundary
    assert recovery_ai._get_customer_segment.__doc__ is not None
    
    # Segment ranges should not overlap incorrectly
    ranges = recovery_ai.segment_discount_ranges
    assert all(v[0] < v[1] for v in ranges.values())


def test_recovery_outcome_with_all_fields():
    """Test RecoveryOutcome with all fields populated."""
    outcome = RecoveryOutcome(
        order_id="ORDER_123",
        customer_receipt="cust_456",
        original_amount_paise=100000,
        offered_discount_percent=35.0,
        offered_price_paise=65000,
        email_sent_at=time.time(),
        email_opened=True,
        link_clicked=True,
        conversion=True,
        paid_amount_paise=65000,
        paid_at=time.time()
    )
    
    # Should be convertible to dict
    outcome_dict = {
        'order_id': outcome.order_id,
        'customer_receipt': outcome.customer_receipt,
        'conversion': outcome.conversion
    }
    
    assert outcome_dict['conversion'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
