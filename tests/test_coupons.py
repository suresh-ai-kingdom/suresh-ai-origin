"""Tests for discount coupon system."""
import pytest
import time
from coupon_utils import (
    create_coupon, validate_coupon, apply_coupon, 
    calculate_discounted_amount, get_all_coupons, deactivate_coupon
)


def test_create_coupon():
    """Test creating a new coupon."""
    code = f"TEST{int(time.time())}"
    coupon = create_coupon(code, 20, "Test coupon", None, None)
    
    assert coupon is not None
    assert coupon['code'] == code.upper()
    assert coupon['discount_percent'] == 20
    assert coupon['is_active'] == 1


def test_create_coupon_duplicate():
    """Test that duplicate coupon codes are rejected."""
    code = f"DUP{int(time.time())}"
    create_coupon(code, 15)
    
    # Try to create duplicate
    duplicate = create_coupon(code, 25)
    assert duplicate is None


def test_create_coupon_clamped_discount():
    """Test that discount percent is clamped to 0-100."""
    code1 = f"CLAMP1{int(time.time())}"
    coupon1 = create_coupon(code1, 150)  # Should clamp to 100
    assert coupon1['discount_percent'] == 100
    
    code2 = f"CLAMP2{int(time.time())}"
    coupon2 = create_coupon(code2, -50)  # Should clamp to 0
    assert coupon2['discount_percent'] == 0


def test_validate_coupon_valid():
    """Test validating a valid coupon."""
    code = f"VALID{int(time.time())}"
    create_coupon(code, 25)
    
    result = validate_coupon(code)
    assert result['valid'] is True
    assert result['discount_percent'] == 25
    assert 'discount applied' in result['message'].lower()


def test_validate_coupon_not_found():
    """Test validating a coupon that doesn't exist."""
    result = validate_coupon("NOTEXIST999")
    assert result['valid'] is False
    assert 'not found' in result['message'].lower()


def test_validate_coupon_expired():
    """Test that expired coupons are invalid."""
    code = f"EXP{int(time.time())}"
    expiry = time.time() - 3600  # Expired 1 hour ago
    create_coupon(code, 20, expiry_date=expiry)
    
    result = validate_coupon(code)
    assert result['valid'] is False
    assert 'expired' in result['message'].lower()


def test_validate_coupon_maxed_out():
    """Test that coupons with max uses reached are invalid."""
    code = f"MAX{int(time.time())}"
    create_coupon(code, 30, max_uses=2)
    
    # Use coupon twice
    apply_coupon(code)
    apply_coupon(code)
    
    result = validate_coupon(code)
    assert result['valid'] is False
    assert 'maximum uses' in result['message'].lower()


def test_validate_coupon_inactive():
    """Test that inactive coupons are invalid."""
    code = f"INACTIVE{int(time.time())}"
    create_coupon(code, 15)
    deactivate_coupon(code)
    
    result = validate_coupon(code)
    assert result['valid'] is False
    assert 'inactive' in result['message'].lower()


def test_validate_coupon_case_insensitive():
    """Test that coupon validation is case-insensitive."""
    code = f"CASE{int(time.time())}"
    create_coupon(code, 20)
    
    result = validate_coupon(code.lower())
    assert result['valid'] is True


def test_apply_coupon():
    """Test applying a coupon increments usage counter."""
    code = f"APPLY{int(time.time())}"
    create_coupon(code, 10)
    
    apply_coupon(code)
    coupons = get_all_coupons()
    coupon = next((c for c in coupons if c['code'] == code.upper()), None)
    
    assert coupon is not None
    assert coupon['current_uses'] == 1


def test_apply_coupon_multiple_times():
    """Test applying same coupon multiple times increments counter."""
    code = f"MULTI{int(time.time())}"
    create_coupon(code, 10, max_uses=5)
    
    for _ in range(3):
        apply_coupon(code)
    
    coupons = get_all_coupons()
    coupon = next((c for c in coupons if c['code'] == code.upper()), None)
    assert coupon['current_uses'] == 3


def test_calculate_discounted_amount():
    """Test discount calculation."""
    # ₹100 with 20% discount = ₹80
    final, discount = calculate_discounted_amount(10000, 20)
    assert final == 8000
    assert discount == 2000
    
    # ₹199 with 10% discount = ₹179.10
    final, discount = calculate_discounted_amount(19900, 10)
    assert final == 17910
    assert discount == 1990


def test_calculate_discounted_amount_zero_discount():
    """Test with 0% discount."""
    final, discount = calculate_discounted_amount(10000, 0)
    assert final == 10000
    assert discount == 0


def test_calculate_discounted_amount_full_discount():
    """Test with 100% discount."""
    final, discount = calculate_discounted_amount(10000, 100)
    assert final == 0
    assert discount == 10000


def test_get_all_coupons():
    """Test retrieving all coupons with stats."""
    code = f"GETALL{int(time.time())}"
    create_coupon(code, 25, "Test", None, 10)
    apply_coupon(code)
    
    coupons = get_all_coupons()
    coupon = next((c for c in coupons if c['code'] == code.upper()), None)
    
    assert coupon is not None
    assert coupon['discount_percent'] == 25
    assert coupon['current_uses'] == 1
    assert coupon['max_uses'] == 10
    assert coupon['is_active'] is True
    assert coupon['is_expired'] is False


def test_deactivate_coupon():
    """Test deactivating a coupon."""
    code = f"DEACT{int(time.time())}"
    create_coupon(code, 20)
    
    assert deactivate_coupon(code) is True
    
    result = validate_coupon(code)
    assert result['valid'] is False


def test_coupon_with_expiry():
    """Test coupon with future expiry date is valid."""
    code = f"FUTURE{int(time.time())}"
    future_expiry = time.time() + 86400  # Tomorrow
    create_coupon(code, 20, expiry_date=future_expiry)
    
    result = validate_coupon(code)
    assert result['valid'] is True


def test_coupon_max_uses_exactly_reached():
    """Test that coupon becomes invalid exactly when max uses is reached."""
    code = f"EXACT{int(time.time())}"
    create_coupon(code, 20, max_uses=2)
    
    # First use should be valid
    result1 = validate_coupon(code)
    assert result1['valid'] is True
    apply_coupon(code)
    
    # Second use should still be valid before applying
    result2 = validate_coupon(code)
    assert result2['valid'] is True
    apply_coupon(code)
    
    # Third use should be invalid
    result3 = validate_coupon(code)
    assert result3['valid'] is False


@pytest.fixture(autouse=True)
def cleanup_coupons():
    """Clean up test coupons after each test."""
    yield
    # Cleanup is handled by test isolation
