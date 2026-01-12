"""Coupon and discount code utilities."""
import time
from models import Coupon, get_session


def create_coupon(code, discount_percent, description=None, expiry_date=None, max_uses=None):
    """Create a new coupon code.
    
    Args:
        code: Coupon code (e.g., "SAVE20")
        discount_percent: Discount percentage (0-100)
        description: Optional description
        expiry_date: Unix timestamp when coupon expires, or None for no expiry
        max_uses: Maximum number of times coupon can be used, or None for unlimited
        
    Returns:
        dict with coupon details if created, None if code already exists
    """
    session = get_session()
    try:
        # Check if code already exists
        existing = session.query(Coupon).filter_by(code=code.upper()).first()
        if existing:
            return None
        
        coupon = Coupon(
            code=code.upper(),
            discount_percent=max(0, min(100, discount_percent)),
            description=description,
            expiry_date=expiry_date,
            max_uses=max_uses,
            current_uses=0,
            created_at=time.time(),
            is_active=1
        )
        session.add(coupon)
        session.commit()
        session.refresh(coupon)
        # Return as dict to avoid detached instance issues
        return {
            'code': coupon.code,
            'discount_percent': coupon.discount_percent,
            'description': coupon.description,
            'expiry_date': coupon.expiry_date,
            'max_uses': coupon.max_uses,
            'current_uses': coupon.current_uses,
            'created_at': coupon.created_at,
            'is_active': coupon.is_active
        }
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def validate_coupon(code):
    """Validate a coupon code and return discount percentage if valid.
    
    Args:
        code: Coupon code to validate
        
    Returns:
        dict with 'valid': bool, 'discount_percent': int, 'message': str
    """
    session = get_session()
    try:
        coupon = session.query(Coupon).filter_by(code=code.upper()).first()
        
        if not coupon:
            return {
                'valid': False,
                'discount_percent': 0,
                'message': 'Coupon code not found'
            }
        
        if coupon.is_active == 0:
            return {
                'valid': False,
                'discount_percent': 0,
                'message': 'Coupon code is inactive'
            }
        
        # Check expiry
        if coupon.expiry_date and coupon.expiry_date < time.time():
            return {
                'valid': False,
                'discount_percent': 0,
                'message': 'Coupon code has expired'
            }
        
        # Check max uses
        if coupon.max_uses and coupon.current_uses >= coupon.max_uses:
            return {
                'valid': False,
                'discount_percent': 0,
                'message': 'Coupon code has reached maximum uses'
            }
        
        return {
            'valid': True,
            'discount_percent': coupon.discount_percent,
            'message': f'{coupon.discount_percent}% discount applied'
        }
    except Exception as e:
        return {
            'valid': False,
            'discount_percent': 0,
            'message': f'Error validating coupon: {str(e)}'
        }
    finally:
        session.close()


def apply_coupon(code):
    """Apply a coupon by incrementing its usage counter.
    
    Args:
        code: Coupon code to apply
        
    Returns:
        bool: True if successfully applied, False otherwise
    """
    session = get_session()
    try:
        coupon = session.query(Coupon).filter_by(code=code.upper()).first()
        if coupon:
            coupon.current_uses += 1
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def calculate_discounted_amount(amount_paise, discount_percent):
    """Calculate final amount after discount.
    
    Args:
        amount_paise: Original amount in paise
        discount_percent: Discount percentage (0-100)
        
    Returns:
        tuple: (discounted_amount, discount_amount) in paise
    """
    discount_amount = int(amount_paise * discount_percent / 100)
    final_amount = amount_paise - discount_amount
    return final_amount, discount_amount


def get_all_coupons():
    """Get all coupons with their stats.
    
    Returns:
        list of coupon dicts with code, discount_percent, is_active, current_uses, etc.
    """
    session = get_session()
    try:
        coupons = session.query(Coupon).all()
        result = []
        for coupon in coupons:
            is_expired = coupon.expiry_date is not None and time.time() > coupon.expiry_date
            is_maxed = coupon.max_uses is not None and coupon.current_uses >= coupon.max_uses
            
            result.append({
                'code': coupon.code,
                'discount_percent': coupon.discount_percent,
                'description': coupon.description,
                'is_active': bool(coupon.is_active),
                'is_expired': is_expired,
                'is_maxed_out': is_maxed,
                'current_uses': coupon.current_uses,
                'max_uses': coupon.max_uses,
                'expiry_date': coupon.expiry_date,
                'created_at': coupon.created_at
            })
        return result
    finally:
        session.close()


def deactivate_coupon(code):
    """Deactivate a coupon.
    
    Args:
        code: Coupon code to deactivate
        
    Returns:
        bool: True if deactivated, False if not found
    """
    session = get_session()
    try:
        coupon = session.query(Coupon).filter_by(code=code.upper()).first()
        if coupon:
            coupon.is_active = 0
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
