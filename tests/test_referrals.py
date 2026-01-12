"""Test referral program functionality."""
import pytest
import time
from models import get_session, ReferralProgram, Referral
from referrals import (
    generate_referral_code, create_referral_program, record_referral,
    convert_referral, get_referral_stats, get_all_referrers, get_top_referrers,
    get_pending_payouts, process_payout, get_referral_leaderboard,
    get_referral_analytics, REFERRAL_COMMISSION
)


@pytest.fixture
def cleanup_refs():
    """Clean up test referral data before and after tests."""
    from utils import init_db
    init_db()
    
    session = get_session()
    try:
        # Clean up before test
        session.query(Referral).filter(
            Referral.referrer_receipt.like('TEST_%')
        ).delete(synchronize_session=False)
        session.query(ReferralProgram).filter(
            ReferralProgram.referrer_receipt.like('TEST_%')
        ).delete(synchronize_session=False)
        session.commit()
        
        yield
        
        # Clean up after test
        session.query(Referral).filter(
            Referral.referrer_receipt.like('TEST_%')
        ).delete(synchronize_session=False)
        session.query(ReferralProgram).filter(
            ReferralProgram.referrer_receipt.like('TEST_%')
        ).delete(synchronize_session=False)
        session.commit()
    finally:
        session.close()


def test_generate_referral_code():
    """Test referral code generation."""
    receipt = "TEST_CUSTOMER_123"
    code = generate_referral_code(receipt)
    
    assert len(code) == 12  # 8 from receipt + 4 random
    assert code.startswith("TEST_CUS")
    assert code.isupper()


def test_create_referral_program(cleanup_refs):
    """Test creating a referral program."""
    receipt = "TEST_REF_001"
    name = "Test Referrer"
    
    result = create_referral_program(receipt, name)
    
    assert result['status'] == 'CREATED'
    assert result['referrer_receipt'] == receipt
    assert result['referrer_name'] == name
    assert result['commission_percent'] == REFERRAL_COMMISSION['default_percent']
    assert len(result['referral_code']) == 12


def test_create_referral_program_duplicate(cleanup_refs):
    """Test creating duplicate referral program returns existing."""
    receipt = "TEST_REF_002"
    
    # Create first time
    result1 = create_referral_program(receipt, "First")
    code1 = result1['referral_code']
    
    # Create again
    result2 = create_referral_program(receipt, "Second")
    
    assert result2['status'] == 'EXISTING'
    assert result2['referral_code'] == code1


def test_record_referral(cleanup_refs):
    """Test recording a referral."""
    # Create program first
    referrer_receipt = "TEST_REF_003"
    program = create_referral_program(referrer_receipt, "Referrer")
    code = program['referral_code']
    
    # Record referral
    referred_receipt = "TEST_CUSTOMER_001"
    order_id = "ORDER_TEST_001"
    amount_paise = 49900  # Pro pack
    
    result = record_referral(code, referred_receipt, order_id, amount_paise, "pro_pack")
    
    assert 'referral_id' in result
    assert result['status'] == 'PENDING'
    assert result['commission_percent'] == 25  # 20% base + 5% Pro bonus
    assert result['commission_amount_paise'] == 12475  # 25% of 49900


def test_record_referral_invalid_code(cleanup_refs):
    """Test recording referral with invalid code."""
    result = record_referral("INVALID_CODE", "TEST_CUST", "ORDER_1", 10000)
    
    assert 'error' in result
    assert result['error'] == 'Invalid referral code'


def test_record_referral_tier_bonus(cleanup_refs):
    """Test tier bonuses in referral commission."""
    referrer_receipt = "TEST_REF_004"
    program = create_referral_program(referrer_receipt, "Referrer")
    code = program['referral_code']
    
    # Test PREMIUM bonus (10%)
    result = record_referral(code, "TEST_CUST_002", "ORDER_002", 99900, "premium_pack")
    
    assert result['commission_percent'] == 30  # 20% + 10% Premium
    assert result['commission_amount_paise'] == 29970  # 30% of 99900


def test_convert_referral(cleanup_refs):
    """Test converting a referral when payment completes."""
    # Setup
    referrer_receipt = "TEST_REF_005"
    program = create_referral_program(referrer_receipt, "Referrer")
    code = program['referral_code']
    
    order_id = "ORDER_TEST_003"
    record_referral(code, "TEST_CUST_003", order_id, 9900)
    
    # Convert
    success = convert_referral(order_id)
    
    assert success is True
    
    # Verify stats updated
    stats = get_referral_stats(referrer_receipt)
    assert stats['successful_referrals'] == 1
    assert stats['pending_commission_paise'] == 1980  # 20% of 9900


def test_convert_referral_invalid_order(cleanup_refs):
    """Test converting nonexistent referral."""
    success = convert_referral("INVALID_ORDER")
    assert success is False


def test_get_referral_stats(cleanup_refs):
    """Test getting referral statistics."""
    # Setup
    referrer_receipt = "TEST_REF_006"
    program = create_referral_program(referrer_receipt, "Test Referrer")
    code = program['referral_code']
    
    # Add some referrals
    record_referral(code, "TEST_CUST_004", "ORDER_004", 9900)
    convert_referral("ORDER_004")
    
    record_referral(code, "TEST_CUST_005", "ORDER_005", 49900)
    # Don't convert this one
    
    # Get stats
    stats = get_referral_stats(referrer_receipt)
    
    assert stats['referral_code'] == code
    assert stats['total_referrals'] == 2
    assert stats['successful_referrals'] == 1
    assert stats['conversion_rate'] == 50.0
    assert stats['pending_commission_paise'] == 1980
    assert stats['can_withdraw'] is False  # Below minimum


def test_get_referral_stats_nonexistent(cleanup_refs):
    """Test getting stats for nonexistent program."""
    stats = get_referral_stats("NONEXISTENT")
    assert stats is None


def test_get_all_referrers(cleanup_refs):
    """Test getting all referrers."""
    # Create multiple programs
    create_referral_program("TEST_REF_007", "Referrer 1")
    create_referral_program("TEST_REF_008", "Referrer 2")
    
    referrers = get_all_referrers()
    
    assert len(referrers) >= 2
    # Verify sorted by earnings
    for i in range(len(referrers) - 1):
        assert referrers[i]['total_earned_paise'] >= referrers[i+1]['total_earned_paise']


def test_get_top_referrers(cleanup_refs):
    """Test getting top referrers."""
    # Create programs with earnings
    for i in range(15):
        receipt = f"TEST_REF_TOP_{i}"
        program = create_referral_program(receipt, f"Referrer {i}")
        code = program['referral_code']
        
        # Add referral with amount proportional to index
        order_id = f"ORDER_TOP_{i}"
        record_referral(code, f"TEST_CUST_TOP_{i}", order_id, (i+1) * 10000)
        convert_referral(order_id)
    
    top = get_top_referrers(limit=10)
    
    assert len(top) == 10
    # Should be sorted by earnings descending
    assert top[0]['total_earned_paise'] > top[-1]['total_earned_paise']


def test_get_pending_payouts(cleanup_refs):
    """Test getting pending payouts."""
    # Create program with earnings above minimum
    referrer_receipt = "TEST_REF_PAYOUT_001"
    program = create_referral_program(referrer_receipt, "Big Referrer")
    code = program['referral_code']
    
    # Add referrals totaling > ₹1000 minimum
    for i in range(11):
        order_id = f"ORDER_PAYOUT_{i}"
        record_referral(code, f"TEST_CUST_PAYOUT_{i}", order_id, 49900)
        convert_referral(order_id)
    
    # Total: 11 * 9980 = 109,780 paise (₹1097.80)
    
    payouts = get_pending_payouts()
    
    assert len(payouts) >= 1
    
    # Find our payout
    our_payout = next((p for p in payouts if p['referrer_receipt'] == referrer_receipt), None)
    assert our_payout is not None
    assert our_payout['pending_paise'] == 109780
    assert our_payout['referral_count'] == 11


def test_process_payout(cleanup_refs):
    """Test processing a payout."""
    # Setup with earnings above minimum
    referrer_receipt = "TEST_REF_PAYOUT_002"
    program = create_referral_program(referrer_receipt, "Payout Test")
    code = program['referral_code']
    
    # Add referrals
    for i in range(11):
        order_id = f"ORDER_PAYOUT_PROC_{i}"
        record_referral(code, f"TEST_CUST_PAYOUT_PROC_{i}", order_id, 49900)
        convert_referral(order_id)
    
    # Process payout
    result = process_payout(referrer_receipt)
    
    assert result['success'] is True
    assert result['payout_amount_paise'] == 109780
    assert result['referral_count'] == 11
    
    # Verify stats updated
    stats = get_referral_stats(referrer_receipt)
    assert stats['pending_commission_paise'] == 0
    assert stats['paid_commission_paise'] == 109780


def test_process_payout_below_minimum(cleanup_refs):
    """Test payout fails when below minimum."""
    referrer_receipt = "TEST_REF_PAYOUT_003"
    program = create_referral_program(referrer_receipt, "Small Earner")
    code = program['referral_code']
    
    # Add small referral
    record_referral(code, "TEST_CUST_SMALL", "ORDER_SMALL", 9900)
    convert_referral("ORDER_SMALL")
    
    # Try to process (only ₹198 earned, minimum is ₹1000)
    result = process_payout(referrer_receipt)
    
    assert 'error' in result


def test_process_payout_no_pending(cleanup_refs):
    """Test payout with no pending commission."""
    referrer_receipt = "TEST_REF_PAYOUT_004"
    create_referral_program(referrer_receipt, "No Earnings")
    
    result = process_payout(referrer_receipt)
    
    assert 'error' in result


def test_get_referral_leaderboard(cleanup_refs):
    """Test getting referral leaderboard."""
    # Create multiple referrers with different earnings
    for i in range(5):
        receipt = f"TEST_REF_LEADER_{i}"
        program = create_referral_program(receipt, f"Leader {i}")
        code = program['referral_code']
        
        # Give each progressively more referrals
        for j in range((i + 1) * 3):
            order_id = f"ORDER_LEADER_{i}_{j}"
            record_referral(code, f"TEST_CUST_LEADER_{i}_{j}", order_id, 9900)
            convert_referral(order_id)
    
    leaderboard = get_referral_leaderboard(limit=5)
    
    assert len(leaderboard) == 5
    
    # Verify ranking
    for i, entry in enumerate(leaderboard, 1):
        assert entry['rank'] == i
    
    # Verify sorted by earnings
    for i in range(len(leaderboard) - 1):
        assert leaderboard[i]['total_earned_rupees'] >= leaderboard[i+1]['total_earned_rupees']


def test_get_referral_analytics(cleanup_refs):
    """Test overall referral analytics."""
    # Create programs and referrals
    for i in range(3):
        receipt = f"TEST_REF_ANALYTICS_{i}"
        program = create_referral_program(receipt, f"Analyst {i}")
        code = program['referral_code']
        
        # Add 2 referrals, convert 1
        for j in range(2):
            order_id = f"ORDER_ANALYTICS_{i}_{j}"
            record_referral(code, f"TEST_CUST_ANALYTICS_{i}_{j}", order_id, 9900)
            if j == 0:  # Convert first one only
                convert_referral(order_id)
    
    analytics = get_referral_analytics()
    
    assert analytics['total_referrers'] >= 3
    assert analytics['total_referrals'] >= 6
    assert analytics['successful_referrals'] >= 3
    assert analytics['conversion_rate_percent'] == 50.0  # 3 of 6
    assert analytics['total_commission_paise'] >= 5940  # 3 * 1980
    assert analytics['pending_commission_paise'] == analytics['total_commission_paise']  # None paid yet


def test_referral_commission_structure():
    """Test commission configuration."""
    assert REFERRAL_COMMISSION['default_percent'] == 20
    assert REFERRAL_COMMISSION['tier_bonus']['STARTER'] == 0
    assert REFERRAL_COMMISSION['tier_bonus']['PRO'] == 5
    assert REFERRAL_COMMISSION['tier_bonus']['PREMIUM'] == 10
    assert REFERRAL_COMMISSION['minimum_payout_paise'] == 100000  # ₹1000
