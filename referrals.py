"""Referral and affiliate program for viral growth."""
import time
import secrets
from datetime import datetime
from models import get_session
from sqlalchemy import and_, func, or_
from enum import Enum


class ReferralStatus(Enum):
    """Referral status states."""
    PENDING = "PENDING"  # Referred customer not yet purchased
    CONVERTED = "CONVERTED"  # Referred customer made purchase
    PAID = "PAID"  # Commission paid to referrer
    CANCELLED = "CANCELLED"  # Referral invalidated


# Commission structure
REFERRAL_COMMISSION = {
    'default_percent': 20,  # 20% commission on referral
    'tier_bonus': {
        'STARTER': 0,  # No extra bonus
        'PRO': 5,  # +5% for Pro referrals
        'PREMIUM': 10  # +10% for Premium referrals
    },
    'minimum_payout_paise': 100000,  # ₹1000 minimum for payout
    'cookie_duration_days': 30  # Referral link valid for 30 days
}


def generate_referral_code(receipt):
    """Generate unique referral code for customer.
    
    Args:
        receipt: Customer receipt ID
        
    Returns:
        str: Unique referral code
    """
    # Create readable code from receipt + random suffix
    suffix = secrets.token_hex(4).upper()[:4]
    code = f"{receipt[:8].upper()}{suffix}"
    return code


def create_referral_program(receipt, name=None):
    """Create referral program for customer.
    
    Args:
        receipt: Customer receipt ID
        name: Optional referrer name
        
    Returns:
        dict with referral program data
    """
    session = get_session()
    try:
        from models import ReferralProgram
        
        # Check if already exists
        existing = session.query(ReferralProgram).filter(
            ReferralProgram.referrer_receipt == receipt
        ).first()
        
        if existing:
            return {
                'referral_code': existing.referral_code,
                'referrer_receipt': existing.referrer_receipt,
                'referrer_name': existing.referrer_name,
                'commission_percent': existing.commission_percent,
                'status': 'EXISTING'
            }
        
        # Create new
        code = generate_referral_code(receipt)
        
        program = ReferralProgram(
            referral_code=code,
            referrer_receipt=receipt,
            referrer_name=name,
            commission_percent=REFERRAL_COMMISSION['default_percent'],
            total_referrals=0,
            successful_referrals=0,
            total_commission_paise=0,
            total_paid_paise=0,
            created_at=time.time()
        )
        
        session.add(program)
        session.commit()
        
        return {
            'referral_code': code,
            'referrer_receipt': receipt,
            'referrer_name': name,
            'commission_percent': REFERRAL_COMMISSION['default_percent'],
            'status': 'CREATED'
        }
    finally:
        session.close()


def record_referral(referral_code, referred_receipt, order_id, amount_paise, product=None):
    """Record a new referral when customer uses referral code.
    
    Args:
        referral_code: Referral code used
        referred_receipt: New customer's receipt
        order_id: Order ID from purchase
        amount_paise: Order amount in paise
        product: Optional product name
        
    Returns:
        dict with referral data
    """
    session = get_session()
    try:
        from models import ReferralProgram, Referral
        
        # Find referral program
        program = session.query(ReferralProgram).filter(
            ReferralProgram.referral_code == referral_code
        ).first()
        
        if not program:
            return {'error': 'Invalid referral code'}
        
        # Calculate commission
        base_commission = REFERRAL_COMMISSION['default_percent']
        
        # Add tier bonus if applicable
        tier_bonus = 0
        if product:
            for tier, bonus in REFERRAL_COMMISSION['tier_bonus'].items():
                if tier.lower() in product.lower():
                    tier_bonus = bonus
                    break
        
        total_commission_percent = base_commission + tier_bonus
        commission_amount = int((amount_paise * total_commission_percent) / 100)
        
        # Create referral record
        referral = Referral(
            id=f'REF_{int(time.time())}_{secrets.token_hex(4)}',
            referral_code=referral_code,
            referrer_receipt=program.referrer_receipt,
            referred_receipt=referred_receipt,
            order_id=order_id,
            order_amount_paise=amount_paise,
            commission_percent=total_commission_percent,
            commission_amount_paise=commission_amount,
            status='PENDING',
            created_at=time.time()
        )
        
        session.add(referral)
        
        # Update program stats
        program.total_referrals += 1
        
        session.commit()
        
        return {
            'referral_id': referral.id,
            'commission_amount_paise': commission_amount,
            'commission_amount_rupees': commission_amount / 100,
            'commission_percent': total_commission_percent,
            'status': 'PENDING'
        }
    finally:
        session.close()


def convert_referral(order_id):
    """Mark referral as converted when payment completes.
    
    Args:
        order_id: Order ID that was paid
        
    Returns:
        bool indicating success
    """
    session = get_session()
    try:
        from models import Referral, ReferralProgram
        
        referral = session.query(Referral).filter(
            Referral.order_id == order_id
        ).first()
        
        if not referral or referral.status != 'PENDING':
            return False
        
        # Mark as converted
        referral.status = 'CONVERTED'
        referral.converted_at = time.time()
        
        # Update program stats
        program = session.query(ReferralProgram).filter(
            ReferralProgram.referral_code == referral.referral_code
        ).first()
        
        if program:
            program.successful_referrals += 1
            program.total_commission_paise += referral.commission_amount_paise
        
        session.commit()
        return True
    finally:
        session.close()


def get_referral_stats(receipt):
    """Get referral statistics for a customer.
    
    Args:
        receipt: Referrer's receipt ID
        
    Returns:
        dict with referral stats
    """
    session = get_session()
    try:
        from models import ReferralProgram, Referral
        
        program = session.query(ReferralProgram).filter(
            ReferralProgram.referrer_receipt == receipt
        ).first()
        
        if not program:
            return None
        
        # Get referrals
        referrals = session.query(Referral).filter(
            Referral.referrer_receipt == receipt
        ).all()
        
        pending_commission = sum(
            r.commission_amount_paise for r in referrals 
            if r.status == 'CONVERTED'
        )
        
        paid_commission = sum(
            r.commission_amount_paise for r in referrals 
            if r.status == 'PAID'
        )
        
        return {
            'referral_code': program.referral_code,
            'referrer_name': program.referrer_name,
            'total_referrals': program.total_referrals,
            'successful_referrals': program.successful_referrals,
            'conversion_rate': (program.successful_referrals / program.total_referrals * 100) 
                              if program.total_referrals > 0 else 0,
            'pending_commission_paise': pending_commission,
            'pending_commission_rupees': pending_commission / 100,
            'paid_commission_paise': paid_commission,
            'paid_commission_rupees': paid_commission / 100,
            'total_earned_paise': pending_commission + paid_commission,
            'total_earned_rupees': (pending_commission + paid_commission) / 100,
            'can_withdraw': pending_commission >= REFERRAL_COMMISSION['minimum_payout_paise']
        }
    finally:
        session.close()


def get_all_referrers():
    """Get all active referrers with stats.
    
    Returns:
        list of referrer dicts
    """
    session = get_session()
    try:
        from models import ReferralProgram
        
        programs = session.query(ReferralProgram).all()
        
        result = []
        for program in programs:
            stats = get_referral_stats(program.referrer_receipt)
            if stats:
                result.append(stats)
        
        # Sort by total earned
        result.sort(key=lambda x: x['total_earned_paise'], reverse=True)
        
        return result
    finally:
        session.close()


def get_top_referrers(limit=10):
    """Get top referrers by earnings.
    
    Args:
        limit: Number of top referrers to return
        
    Returns:
        list of top referrer dicts
    """
    all_referrers = get_all_referrers()
    return all_referrers[:limit]


def get_pending_payouts():
    """Get referrers with pending commission ready for payout.
    
    Returns:
        list of payout dicts
    """
    session = get_session()
    try:
        from models import ReferralProgram, Referral
        
        # Get all programs
        programs = session.query(ReferralProgram).all()
        
        payouts = []
        
        for program in programs:
            # Calculate pending commission
            pending = session.query(func.sum(Referral.commission_amount_paise)).filter(
                and_(
                    Referral.referrer_receipt == program.referrer_receipt,
                    Referral.status == 'CONVERTED'
                )
            ).scalar() or 0
            
            # Check if meets minimum
            if pending >= REFERRAL_COMMISSION['minimum_payout_paise']:
                # Count referrals to pay out
                count = session.query(func.count(Referral.id)).filter(
                    and_(
                        Referral.referrer_receipt == program.referrer_receipt,
                        Referral.status == 'CONVERTED'
                    )
                ).scalar() or 0
                
                payouts.append({
                    'referrer_receipt': program.referrer_receipt,
                    'referrer_name': program.referrer_name,
                    'referral_code': program.referral_code,
                    'pending_paise': pending,
                    'pending_rupees': pending / 100,
                    'referral_count': count
                })
        
        # Sort by amount descending
        payouts.sort(key=lambda x: x['pending_paise'], reverse=True)
        
        return payouts
    finally:
        session.close()


def process_payout(receipt):
    """Process commission payout for referrer.
    
    Args:
        receipt: Referrer's receipt ID
        
    Returns:
        dict with payout details
    """
    session = get_session()
    try:
        from models import Referral, ReferralProgram
        
        # Get all converted referrals
        referrals = session.query(Referral).filter(
            and_(
                Referral.referrer_receipt == receipt,
                Referral.status == 'CONVERTED'
            )
        ).all()
        
        if not referrals:
            return {'error': 'No pending commission'}
        
        total_payout = sum(r.commission_amount_paise for r in referrals)
        
        if total_payout < REFERRAL_COMMISSION['minimum_payout_paise']:
            return {'error': f'Minimum payout is ₹{REFERRAL_COMMISSION["minimum_payout_paise"]/100}'}
        
        # Mark all as paid
        for referral in referrals:
            referral.status = 'PAID'
            referral.paid_at = time.time()
        
        # Update program
        program = session.query(ReferralProgram).filter(
            ReferralProgram.referrer_receipt == receipt
        ).first()
        
        if program:
            program.total_paid_paise += total_payout
        
        session.commit()
        
        return {
            'success': True,
            'payout_amount_paise': total_payout,
            'payout_amount_rupees': total_payout / 100,
            'referral_count': len(referrals)
        }
    finally:
        session.close()


def get_referral_leaderboard(limit=20):
    """Get referral leaderboard.
    
    Args:
        limit: Number of top referrers
        
    Returns:
        list of leaderboard entries
    """
    referrers = get_all_referrers()
    
    leaderboard = []
    for i, ref in enumerate(referrers[:limit], 1):
        leaderboard.append({
            'rank': i,
            'referrer_name': ref.get('referrer_name', 'Anonymous'),
            'referral_code': ref['referral_code'],
            'successful_referrals': ref['successful_referrals'],
            'total_earned_rupees': ref['total_earned_rupees'],
            'conversion_rate': ref['conversion_rate']
        })
    
    return leaderboard


def get_referral_analytics():
    """Get overall referral program analytics.
    
    Returns:
        dict with program metrics
    """
    session = get_session()
    try:
        from models import ReferralProgram, Referral
        
        # Total programs
        total_programs = session.query(func.count(ReferralProgram.referral_code)).scalar() or 0
        
        # Total referrals
        total_referrals = session.query(func.count(Referral.id)).scalar() or 0
        
        # Converted referrals
        converted = session.query(func.count(Referral.id)).filter(
            Referral.status.in_(['CONVERTED', 'PAID'])
        ).scalar() or 0
        
        # Total commission
        total_commission = session.query(func.sum(Referral.commission_amount_paise)).filter(
            Referral.status.in_(['CONVERTED', 'PAID'])
        ).scalar() or 0
        
        # Paid commission
        paid_commission = session.query(func.sum(Referral.commission_amount_paise)).filter(
            Referral.status == 'PAID'
        ).scalar() or 0
        
        # Pending commission
        pending_commission = total_commission - paid_commission
        
        # Conversion rate
        conversion_rate = (converted / total_referrals * 100) if total_referrals > 0 else 0
        
        return {
            'total_referrers': total_programs,
            'total_referrals': total_referrals,
            'successful_referrals': converted,
            'conversion_rate_percent': round(conversion_rate, 1),
            'total_commission_paise': total_commission,
            'total_commission_rupees': round(total_commission / 100, 2),
            'paid_commission_paise': paid_commission,
            'paid_commission_rupees': round(paid_commission / 100, 2),
            'pending_commission_paise': pending_commission,
            'pending_commission_rupees': round(pending_commission / 100, 2),
            'average_commission_per_referral': round(total_commission / converted / 100, 2) 
                                              if converted > 0 else 0
        }
    finally:
        session.close()
