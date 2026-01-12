"""Customer segmentation and lifetime value (LTV) calculations."""
import time
from datetime import datetime, timedelta
from models import get_session, Order, Customer
from sqlalchemy import func, and_
from enum import Enum


class CustomerSegment(Enum):
    """Customer segment classifications."""
    VIP = "VIP"  # High-value repeat customers
    LOYAL = "LOYAL"  # Regular repeat customers
    GROWING = "GROWING"  # Increasing purchase frequency
    AT_RISK = "AT_RISK"  # Used to buy, but haven't recently
    DORMANT = "DORMANT"  # Purchased once long ago
    NEW = "NEW"  # Recent first-time buyers
    ONE_TIME = "ONE_TIME"  # Single purchase, no repeat
    CHURNED = "CHURNED"  # Purchased but now gone for 6+ months


def get_customer_ltv(receipt):
    """Calculate lifetime value for a single customer.
    
    Args:
        receipt: Customer receipt/identifier
        
    Returns:
        dict with ltv_paise, order_count, first_purchase, last_purchase, avg_order_value
    """
    session = get_session()
    try:
        orders = session.query(Order).filter(
            and_(
                Order.receipt == receipt,
                Order.status == 'paid'
            )
        ).all()
        
        if not orders:
            return None
        
        ltv = sum(o.amount for o in orders)
        first_purchase = min(o.created_at for o in orders)
        last_purchase = max(o.created_at for o in orders)
        
        return {
            'receipt': receipt,
            'ltv_paise': ltv,
            'order_count': len(orders),
            'first_purchase': first_purchase,
            'last_purchase': last_purchase,
            'avg_order_value_paise': int(ltv / len(orders)),
            'customer_age_days': int((time.time() - first_purchase) / 86400),
            'days_since_purchase': int((time.time() - last_purchase) / 86400)
        }
    finally:
        session.close()


def get_customer_segment(receipt):
    """Classify customer into segment based on behavior.
    
    Args:
        receipt: Customer receipt/identifier
        
    Returns:
        dict with segment, reason, ltv_data
    """
    ltv_data = get_customer_ltv(receipt)
    
    if not ltv_data:
        return {
            'receipt': receipt,
            'segment': CustomerSegment.NEW.value,
            'reason': 'No paid orders found',
            'ltv_data': None
        }
    
    order_count = ltv_data['order_count']
    days_since = ltv_data['days_since_purchase']
    customer_age = ltv_data['customer_age_days']
    ltv = ltv_data['ltv_paise']
    
    # VIP: High LTV (₹50k+) AND multiple purchases (3+) AND recent activity
    if ltv >= 5000000 and order_count >= 3 and days_since <= 60:
        segment = CustomerSegment.VIP
        reason = f"High LTV (₹{ltv/100:.0f}), {order_count} orders, active"
    
    # LOYAL: Multiple purchases (2+), recent activity, consistent value
    elif order_count >= 2 and days_since <= 90:
        segment = CustomerSegment.LOYAL
        reason = f"Regular buyer: {order_count} orders in {customer_age} days"
    
    # GROWING: Increasing purchase frequency (multiple purchases, accelerating)
    elif order_count >= 2 and days_since <= 30:
        segment = CustomerSegment.GROWING
        reason = f"Accelerating: {order_count} orders, last {days_since} days ago"
    
    # AT_RISK: Used to be active but hasn't purchased recently (180-365 days)
    elif order_count >= 1 and 180 <= days_since <= 365:
        segment = CustomerSegment.AT_RISK
        reason = f"Inactive {days_since} days, was {order_count} purchases"
    
    # DORMANT: Purchased long ago (6+ months) with no repeat
    elif order_count == 1 and days_since > 180:
        segment = CustomerSegment.DORMANT
        reason = f"Single purchase {days_since} days ago"
    
    # NEW: First purchase within 30 days
    elif order_count == 1 and customer_age <= 30:
        segment = CustomerSegment.NEW
        reason = f"New customer, purchased {days_since} days ago"
    
    # CHURNED: Purchased but completely inactive (6+ months)
    elif days_since > 180:
        segment = CustomerSegment.CHURNED
        reason = f"No activity for {days_since} days"
    
    # ONE_TIME: Single purchase more than 30 days ago
    else:
        segment = CustomerSegment.ONE_TIME
        reason = f"Single purchase {days_since} days ago"
    
    return {
        'receipt': receipt,
        'segment': segment.value,
        'reason': reason,
        'ltv_data': ltv_data
    }


def get_all_customers_segmented(days_back=90):
    """Get all customers with their segments and LTV.
    
    Args:
        days_back: Only include customers who purchased in last N days
        
    Returns:
        list of dicts with receipt, segment, ltv, and metrics
    """
    session = get_session()
    try:
        cutoff = time.time() - (days_back * 86400)
        
        # Get unique customers from paid orders in period
        customers = session.query(Order.receipt).filter(
            and_(
                Order.status == 'paid',
                Order.created_at >= cutoff
            )
        ).distinct().all()
        
        result = []
        for (receipt,) in customers:
            if not receipt or receipt == 'TEST':
                continue
            
            segment_data = get_customer_segment(receipt)
            ltv_data = segment_data['ltv_data']
            
            if ltv_data:
                result.append({
                    'receipt': receipt,
                    'segment': segment_data['segment'],
                    'ltv_paise': ltv_data['ltv_paise'],
                    'order_count': ltv_data['order_count'],
                    'avg_order_value_paise': ltv_data['avg_order_value_paise'],
                    'customer_age_days': ltv_data['customer_age_days'],
                    'days_since_purchase': ltv_data['days_since_purchase'],
                    'first_purchase': datetime.fromtimestamp(ltv_data['first_purchase']).strftime('%Y-%m-%d'),
                    'last_purchase': datetime.fromtimestamp(ltv_data['last_purchase']).strftime('%Y-%m-%d')
                })
        
        return result
    finally:
        session.close()


def get_segment_summary():
    """Get summary statistics by customer segment.
    
    Returns:
        dict with segment stats: count, total_ltv, avg_ltv, churn_risk
    """
    session = get_session()
    try:
        # Get all unique receipts with paid orders
        customers = session.query(Order.receipt).filter(
            Order.status == 'paid'
        ).distinct().all()
        
        segments = {}
        
        for (receipt,) in customers:
            if not receipt or receipt == 'TEST':
                continue
            
            segment_data = get_customer_segment(receipt)
            segment_name = segment_data['segment']
            
            if segment_name not in segments:
                segments[segment_name] = {
                    'count': 0,
                    'total_ltv_paise': 0,
                    'receipts': []
                }
            
            segments[segment_name]['count'] += 1
            if segment_data['ltv_data']:
                segments[segment_name]['total_ltv_paise'] += segment_data['ltv_data']['ltv_paise']
                segments[segment_name]['receipts'].append(receipt)
        
        # Calculate stats per segment
        result = {}
        for segment_name, data in segments.items():
            count = data['count']
            total_ltv = data['total_ltv_paise']
            
            result[segment_name] = {
                'customer_count': count,
                'total_ltv_paise': total_ltv,
                'avg_ltv_paise': int(total_ltv / count) if count > 0 else 0,
                'percentage': 0  # Will be calculated below
            }
        
        # Calculate percentages
        total_customers = sum(s['customer_count'] for s in result.values())
        for segment in result.values():
            segment['percentage'] = round(segment['customer_count'] / total_customers * 100, 1) if total_customers > 0 else 0
        
        return result
    finally:
        session.close()


def identify_marketing_opportunities():
    """Identify specific marketing opportunities by segment.
    
    Returns:
        dict with actionable recommendations for each segment
    """
    segments = get_segment_summary()
    
    opportunities = {}
    
    for segment_name, stats in segments.items():
        count = stats['customer_count']
        
        if segment_name == 'VIP':
            opportunities[segment_name] = {
                'action': 'VIP Retention Program',
                'description': f'Reward {count} VIP customers with exclusive products/early access',
                'potential_impact': 'High - protect highest-value revenue source'
            }
        elif segment_name == 'LOYAL':
            opportunities[segment_name] = {
                'action': 'Loyalty Bonus Program',
                'description': f'Incentivize {count} loyal customers with bundle deals',
                'potential_impact': 'High - increase repeat purchase frequency'
            }
        elif segment_name == 'GROWING':
            opportunities[segment_name] = {
                'action': 'Growth Acceleration',
                'description': f'Upsell to {count} customers showing increasing engagement',
                'potential_impact': 'Very High - convert to VIP segment'
            }
        elif segment_name == 'AT_RISK':
            opportunities[segment_name] = {
                'action': 'Win-back Campaign',
                'description': f'Re-engage {count} at-risk customers with special offers',
                'potential_impact': 'Medium - recover lost revenue'
            }
        elif segment_name == 'NEW':
            opportunities[segment_name] = {
                'action': 'New Customer Nurture',
                'description': f'Convert {count} new customers to repeat buyers with follow-up offers',
                'potential_impact': 'High - establish habit formation'
            }
        elif segment_name == 'ONE_TIME':
            opportunities[segment_name] = {
                'action': 'One-time to Repeat',
                'description': f'Convert {count} one-time buyers with targeted recommendations',
                'potential_impact': 'Medium - double customer value'
            }
        elif segment_name == 'DORMANT':
            opportunities[segment_name] = {
                'action': 'Reactivation Campaign',
                'description': f'Remind {count} dormant customers with nostalgia/new products',
                'potential_impact': 'Low-Medium - expensive but possible wins'
            }
        elif segment_name == 'CHURNED':
            opportunities[segment_name] = {
                'action': 'Last Chance Offer',
                'description': f'Final offer to {count} churned customers before giving up',
                'potential_impact': 'Low - focus on others'
            }
    
    return opportunities


def get_customer_churn_risk():
    """Identify customers at risk of churn.
    
    Returns:
        list of customers likely to churn, sorted by urgency
    """
    session = get_session()
    try:
        # Get all customers with at least 1 purchase
        customers = session.query(Order.receipt).filter(
            Order.status == 'paid'
        ).distinct().all()
        
        at_risk = []
        
        for (receipt,) in customers:
            if not receipt or receipt == 'TEST':
                continue
            
            segment_data = get_customer_segment(receipt)
            ltv_data = segment_data['ltv_data']
            
            # Consider at-risk if: (1) AT_RISK, (2) DORMANT, or (3) had multiple purchases but no activity for 60+ days
            is_at_risk = segment_data['segment'] in ['AT_RISK', 'DORMANT', 'CHURNED']
            
            if is_at_risk and ltv_data:
                days_since = ltv_data['days_since_purchase']
                ltv = ltv_data['ltv_paise']
                
                # Churn risk score: days inactive + potential lost revenue
                # Higher value customers = higher urgency
                risk_score = (days_since / 180) + (ltv / 10000000)  # Normalize LTV
                
                at_risk.append({
                    'receipt': receipt,
                    'segment': segment_data['segment'],
                    'ltv_paise': ltv,
                    'days_inactive': days_since,
                    'order_count': ltv_data['order_count'],
                    'risk_score': round(risk_score, 2),
                    'urgency': 'CRITICAL' if ltv >= 1000000 and days_since > 90 else 'HIGH' if days_since > 120 else 'MEDIUM'
                })
        
        # Sort by risk score descending
        at_risk.sort(key=lambda x: x['risk_score'], reverse=True)
        return at_risk
    finally:
        session.close()
