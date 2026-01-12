import time
from typing import Dict, List
from models import get_engine, get_session, Order, Customer
from utils import _get_db_url


def _days_since(timestamp: float) -> int:
    """Convert timestamp to days since now."""
    return int((time.time() - timestamp) / 86400.0)


def compute_churn_risk(receipt: str) -> Dict:
    """Compute churn risk score (0-100) for a customer.
    
    Risk factors:
    - Days since last purchase (recency)
    - Purchase frequency
    - Order value trends
    
    Returns dict with risk_score, risk_level, reasons, and recommendations.
    """
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    orders = session.query(Order).filter_by(receipt=receipt).filter_by(status='paid').order_by(Order.paid_at).all()
    session.close()
    
    if not orders:
        return {
            'receipt': receipt,
            'risk_score': 0,
            'risk_level': 'NONE',
            'reasons': ['No purchase history'],
            'recommendations': ['Wait for first purchase'],
            'last_purchase_days': None,
            'order_count': 0,
        }
    
    # Recency score (0-50 points)
    last_purchase = max(o.paid_at for o in orders if o.paid_at)
    days_since = _days_since(last_purchase)
    recency_score = min(50, int(days_since / 2))  # 1 day = 0.5 pts, caps at 50
    
    # Frequency score (0-30 points)
    order_count = len(orders)
    avg_days_between = None
    if order_count > 1:
        first_purchase = min(o.paid_at for o in orders if o.paid_at)
        total_days = _days_since(first_purchase)
        avg_days_between = total_days / max(order_count - 1, 1)
        expected_orders = total_days / avg_days_between if avg_days_between > 0 else order_count
        frequency_gap = max(0, expected_orders - order_count)
        frequency_score = min(30, int(frequency_gap * 10))
    else:
        frequency_score = 20  # Single purchase = moderate frequency risk
    
    # Value trend score (0-20 points)
    if order_count >= 3:
        recent_avg = sum(o.amount for o in orders[-2:]) / 2
        older_avg = sum(o.amount for o in orders[:2]) / 2
        decline_ratio = (older_avg - recent_avg) / older_avg if older_avg > 0 else 0
        value_score = int(max(0, decline_ratio) * 20)
    else:
        value_score = 0
    
    # Total risk score
    risk_score = min(100, recency_score + frequency_score + value_score)
    
    # Risk level classification
    if risk_score >= 70:
        risk_level = 'CRITICAL'
    elif risk_score >= 50:
        risk_level = 'HIGH'
    elif risk_score >= 30:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'
    
    # Generate reasons and recommendations
    reasons = []
    recommendations = []
    
    if days_since > 60:
        reasons.append(f'No purchase in {days_since} days')
        recommendations.append('Send win-back email with exclusive discount')
    elif days_since > 30:
        reasons.append(f'Last purchase {days_since} days ago')
        recommendations.append('Send personalized product recommendations')
    
    if order_count == 1 and days_since > 14:
        reasons.append('Single purchase, no repeat')
        recommendations.append('Offer first repeat customer discount')
    
    if frequency_score > 15:
        reasons.append('Declining purchase frequency')
        recommendations.append('Implement loyalty rewards program')
    
    if value_score > 10:
        reasons.append('Order values declining')
        recommendations.append('Offer bundle deals or upsells')
    
    if not reasons:
        reasons.append('Healthy engagement pattern')
        recommendations.append('Continue current engagement strategy')
    
    return {
        'receipt': receipt,
        'risk_score': risk_score,
        'risk_level': risk_level,
        'reasons': reasons,
        'recommendations': recommendations,
        'last_purchase_days': days_since,
        'order_count': order_count,
        'avg_days_between_orders': round(avg_days_between, 1) if avg_days_between else None,
    }


def get_at_risk_customers(min_risk: int = 50, limit: int = 50) -> List[Dict]:
    """Get customers with risk score >= min_risk, sorted by risk descending."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    # Get all unique customer receipts from orders
    receipts = [r[0] for r in session.query(Order.receipt).distinct().all()]
    session.close()
    
    at_risk = []
    for receipt in receipts:
        risk_data = compute_churn_risk(receipt)
        if risk_data['risk_score'] >= min_risk:
            at_risk.append(risk_data)
    
    # Sort by risk score descending
    at_risk.sort(key=lambda x: x['risk_score'], reverse=True)
    
    return at_risk[:limit]


def churn_stats() -> Dict:
    """Aggregate churn statistics across all customers."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    receipts = [r[0] for r in session.query(Order.receipt).distinct().all()]
    session.close()
    
    if not receipts:
        return {
            'total_customers': 0,
            'critical_risk': 0,
            'high_risk': 0,
            'medium_risk': 0,
            'low_risk': 0,
            'avg_risk_score': 0,
            'customers_needing_attention': 0,
        }
    
    risk_levels = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'NONE': 0}
    total_risk = 0
    
    for receipt in receipts:
        risk_data = compute_churn_risk(receipt)
        risk_levels[risk_data['risk_level']] += 1
        total_risk += risk_data['risk_score']
    
    return {
        'total_customers': len(receipts),
        'critical_risk': risk_levels['CRITICAL'],
        'high_risk': risk_levels['HIGH'],
        'medium_risk': risk_levels['MEDIUM'],
        'low_risk': risk_levels['LOW'],
        'avg_risk_score': round(total_risk / len(receipts), 1) if receipts else 0,
        'customers_needing_attention': risk_levels['CRITICAL'] + risk_levels['HIGH'],
    }


def generate_alerts(min_risk: int = 70) -> List[Dict]:
    """Generate actionable alerts for critical churn risks."""
    at_risk = get_at_risk_customers(min_risk=min_risk, limit=20)
    
    alerts = []
    for customer in at_risk:
        alert = {
            'receipt': customer['receipt'],
            'risk_level': customer['risk_level'],
            'risk_score': customer['risk_score'],
            'priority': 'URGENT' if customer['risk_score'] >= 80 else 'HIGH',
            'action': customer['recommendations'][0] if customer['recommendations'] else 'Review customer',
            'days_inactive': customer['last_purchase_days'],
        }
        alerts.append(alert)
    
    return alerts
