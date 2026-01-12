"""Abandoned order recovery and cart reminder system."""
import time
from datetime import datetime, timedelta
from models import get_session, Order
from sqlalchemy import and_, func
from enum import Enum


class ReminderStatus(Enum):
    """Status of abandoned order reminder."""
    PENDING = "PENDING"  # Not yet sent
    SENT = "SENT"  # Email sent
    OPENED = "OPENED"  # Email opened (if tracking enabled)
    CLICKED = "CLICKED"  # Link clicked
    CONVERTED = "CONVERTED"  # Order paid
    BOUNCED = "BOUNCED"  # Email bounced
    UNSUBSCRIBED = "UNSUBSCRIBED"  # Opted out


REMINDER_SCHEDULE = [
    {'delay_hours': 1, 'name': 'Urgent Reminder', 'subject': 'Complete your purchase ({{product}} waiting!)'},
    {'delay_hours': 24, 'name': '1-Day Follow-up', 'subject': 'Your {{product}} is still waiting for you'},
    {'delay_hours': 72, 'name': '3-Day Last Chance', 'subject': 'Last chance: {{product}} available for 24 more hours'},
]


def get_abandoned_orders(hours_since=None, limit=None):
    """Find abandoned orders (created but not paid).
    
    Args:
        hours_since: Only include orders older than N hours
        limit: Maximum number to return
        
    Returns:
        list of dicts with order details
    """
    session = get_session()
    try:
        query = session.query(Order).filter(
            and_(
                Order.status == 'created',
                Order.receipt.isnot(None),
                Order.receipt != 'TEST'
            )
        )
        
        if hours_since:
            cutoff = time.time() - (hours_since * 3600)
            query = query.filter(Order.created_at <= cutoff)
        
        orders = query.all()
        if limit:
            orders = orders[:limit]
        
        result = []
        for order in orders:
            hours_abandoned = (time.time() - order.created_at) / 3600
            result.append({
                'order_id': order.id,
                'receipt': order.receipt,
                'amount_paise': order.amount,
                'product': order.product,
                'created_at': order.created_at,
                'hours_abandoned': round(hours_abandoned, 1),
                'abandoned_at': datetime.fromtimestamp(order.created_at).strftime('%Y-%m-%d %H:%M'),
                'amount_rupees': order.amount / 100
            })
        
        return result
    finally:
        session.close()


def should_send_reminder(order_id, reminder_sequence):
    """Check if a reminder should be sent for an order.
    
    Args:
        order_id: Order ID
        reminder_sequence: Which reminder (0=first, 1=second, etc)
        
    Returns:
        True if reminder should be sent, False otherwise
    """
    session = get_session()
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        
        if not order or order.status != 'created':
            return False
        
        if reminder_sequence >= len(REMINDER_SCHEDULE):
            return False
        
        # Check if enough time has passed
        reminder_config = REMINDER_SCHEDULE[reminder_sequence]
        delay_seconds = reminder_config['delay_hours'] * 3600
        
        if order.created_at + delay_seconds > time.time():
            return False
        
        return True
    finally:
        session.close()


def get_recovery_metrics():
    """Get metrics on abandoned order recovery.
    
    Returns:
        dict with recovery stats
    """
    session = get_session()
    try:
        # Total abandoned orders
        total_abandoned = session.query(func.count(Order.id)).filter(
            and_(
                Order.status == 'created',
                Order.receipt.isnot(None),
                Order.receipt != 'TEST'
            )
        ).scalar() or 0
        
        # Abandoned amount in paise
        total_abandoned_value = session.query(func.sum(Order.amount)).filter(
            and_(
                Order.status == 'created',
                Order.receipt.isnot(None),
                Order.receipt != 'TEST'
            )
        ).scalar() or 0
        
        # Orders created in last 24 hours
        cutoff_24h = time.time() - 86400
        abandoned_24h = session.query(func.count(Order.id)).filter(
            and_(
                Order.status == 'created',
                Order.receipt.isnot(None),
                Order.receipt != 'TEST',
                Order.created_at >= cutoff_24h
            )
        ).scalar() or 0
        
        # Orders abandoned 24+ hours (more likely to need reminder)
        old_abandoned = session.query(func.count(Order.id)).filter(
            and_(
                Order.status == 'created',
                Order.receipt.isnot(None),
                Order.receipt != 'TEST',
                Order.created_at < cutoff_24h
            )
        ).scalar() or 0
        
        # Get sample of orders by hours abandoned
        distribution = {}
        for hours_threshold in [1, 24, 72, 168, 720]:  # 1h, 1d, 3d, 1w, 30d
            count = session.query(func.count(Order.id)).filter(
                and_(
                    Order.status == 'created',
                    Order.receipt.isnot(None),
                    Order.receipt != 'TEST',
                    Order.created_at <= time.time() - (hours_threshold * 3600)
                )
            ).scalar() or 0
            distribution[f'{hours_threshold}h'] = count
        
        return {
            'total_abandoned_orders': total_abandoned,
            'total_abandoned_value_paise': total_abandoned_value,
            'total_abandoned_value_rupees': round(total_abandoned_value / 100, 2),
            'abandoned_24h': abandoned_24h,
            'abandoned_24h_plus': old_abandoned,
            'recovery_target_paise': total_abandoned_value,  # Potential revenue if all recovered
            'distribution': distribution
        }
    finally:
        session.close()


def get_product_abandonment_rate():
    """Get abandonment rate by product.
    
    Returns:
        dict with abandonment metrics per product
    """
    session = get_session()
    try:
        products = session.query(Order.product).distinct().all()
        
        result = {}
        
        for (product,) in products:
            if not product:
                continue
            
            # Total orders for product
            total = session.query(func.count(Order.id)).filter(
                Order.product == product
            ).scalar() or 1
            
            # Abandoned orders
            abandoned = session.query(func.count(Order.id)).filter(
                and_(
                    Order.product == product,
                    Order.status == 'created'
                )
            ).scalar() or 0
            
            # Paid orders
            paid = session.query(func.count(Order.id)).filter(
                and_(
                    Order.product == product,
                    Order.status == 'paid'
                )
            ).scalar() or 0
            
            abandonment_rate = (abandoned / total * 100) if total > 0 else 0
            
            # Total abandoned value
            abandoned_value = session.query(func.sum(Order.amount)).filter(
                and_(
                    Order.product == product,
                    Order.status == 'created'
                )
            ).scalar() or 0
            
            result[product] = {
                'total_initiated': total,
                'completed_orders': paid,
                'abandoned_orders': abandoned,
                'abandonment_rate': round(abandonment_rate, 1),
                'abandoned_value_paise': abandoned_value,
                'abandoned_value_rupees': round(abandoned_value / 100, 2)
            }
        
        return result
    finally:
        session.close()


def get_recovery_suggestions():
    """Get actionable suggestions for recovery.
    
    Returns:
        list of specific recommendations
    """
    metrics = get_recovery_metrics()
    product_rates = get_product_abandonment_rate()
    
    suggestions = []
    
    # High-value abandoned orders
    if metrics['total_abandoned_value_paise'] >= 1000000:  # ₹10k+
        suggestions.append({
            'priority': 'CRITICAL',
            'action': 'High-Value Recovery Campaign',
            'detail': f"₹{metrics['total_abandoned_value_rupees']:.0f} in abandoned orders - send personalized recovery emails",
            'potential_revenue': metrics['total_abandoned_value_paise']
        })
    
    # High abandonment products
    for product, stats in product_rates.items():
        if stats['abandonment_rate'] > 50:
            suggestions.append({
                'priority': 'HIGH',
                'action': f'Optimize {product} Checkout',
                'detail': f"{stats['abandonment_rate']}% abandonment rate for {product} - consider simplifying checkout",
                'potential_revenue': stats['abandoned_value_paise']
            })
    
    # Old abandoned orders
    if metrics['abandoned_24h_plus'] > 5:
        suggestions.append({
            'priority': 'HIGH',
            'action': 'Last-Chance Recovery',
            'detail': f"{metrics['abandoned_24h_plus']} orders abandoned 24h+ ago - send final reminder with discount",
            'potential_revenue': metrics['total_abandoned_value_paise'] * 0.3  # Estimate 30% recovery
        })
    
    # Recent abandonments (can still catch)
    if metrics['abandoned_24h'] > 2:
        suggestions.append({
            'priority': 'URGENT',
            'action': 'Immediate Recovery',
            'detail': f"{metrics['abandoned_24h']} orders abandoned in last 24h - send immediate reminder",
            'potential_revenue': metrics['total_abandoned_value_paise'] * 0.6  # Estimate 60% recovery
        })
    
    return suggestions


def estimate_recovery_potential(recovery_rate=0.3):
    """Estimate potential revenue from recovery campaigns.
    
    Args:
        recovery_rate: Estimated % of abandoned orders that can be recovered (default 30%)
        
    Returns:
        dict with recovery estimates
    """
    metrics = get_recovery_metrics()
    
    potential_paise = int(metrics['total_abandoned_value_paise'] * recovery_rate)
    potential_rupees = potential_paise / 100
    
    return {
        'recovery_rate_percent': recovery_rate * 100,
        'estimated_recoverable_paise': potential_paise,
        'estimated_recoverable_rupees': round(potential_rupees, 2),
        'impact_on_monthly_revenue_percent': 0,  # Can be calculated with actual monthly revenue
        'effort_required': 'Low - automated email campaigns',
        'risk_level': 'None - win-back customers for free'
    }


def get_abandoned_orders_by_customer_segment():
    """Get abandoned orders grouped by customer segment.
    
    Returns:
        dict with abandonment by customer type
    """
    session = get_session()
    try:
        # New customers (no previous paid orders)
        new_customers = session.query(func.count(Order.id)).filter(
            and_(
                Order.status == 'created',
                Order.receipt.isnot(None),
                Order.receipt != 'TEST'
            )
        ).scalar() or 0
        
        # Get abandoned value by product
        by_product = session.query(
            Order.product,
            func.count(Order.id),
            func.sum(Order.amount)
        ).filter(
            and_(
                Order.status == 'created',
                Order.receipt.isnot(None),
                Order.receipt != 'TEST'
            )
        ).group_by(Order.product).all()
        
        result = {
            'total_abandoned': new_customers,
            'by_product': {}
        }
        
        for product, count, value in by_product:
            if product:
                result['by_product'][product] = {
                    'count': count,
                    'value_paise': value or 0,
                    'value_rupees': round((value or 0) / 100, 2)
                }
        
        return result
    finally:
        session.close()
