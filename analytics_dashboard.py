"""Advanced analytics data API for dashboard visualizations."""
import time
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import func, and_
from models import get_engine, get_session, Order, Subscription, Customer, Payment
from utils import _get_db_url


def get_revenue_trend(days: int = 30, interval: str = 'daily') -> List[Dict]:
    """Get revenue trend data for charts.
    
    Args:
        days: Number of days to look back
        interval: 'daily', 'weekly', or 'monthly'
    
    Returns:
        List of {date, revenue, orders} dicts
    """
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    cutoff = time.time() - (days * 86400)
    
    # Get all paid orders
    orders = session.query(Order).filter(
        Order.status == 'paid',
        Order.created_at >= cutoff
    ).all()
    
    session.close()
    
    # Group by interval
    data = {}
    for order in orders:
        order_date = datetime.fromtimestamp(order.created_at)
        
        if interval == 'daily':
            key = order_date.strftime('%Y-%m-%d')
        elif interval == 'weekly':
            # Week starting Monday
            week_start = order_date - timedelta(days=order_date.weekday())
            key = week_start.strftime('%Y-%m-%d')
        else:  # monthly
            key = order_date.strftime('%Y-%m')
        
        if key not in data:
            data[key] = {'date': key, 'revenue': 0, 'orders': 0}
        
        data[key]['revenue'] += order.amount / 100  # Convert paise to rupees
        data[key]['orders'] += 1
    
    # Fill in missing dates with zeros
    result = []
    if interval == 'daily':
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            result.append(data.get(date, {'date': date, 'revenue': 0, 'orders': 0}))
    else:
        result = list(data.values())
    
    return sorted(result, key=lambda x: x['date'])


def get_customer_growth(days: int = 30) -> List[Dict]:
    """Get customer growth data over time."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    cutoff = time.time() - (days * 86400)
    
    # Get all orders to track first-time vs returning
    orders = session.query(Order).filter(
        Order.created_at >= cutoff
    ).order_by(Order.created_at).all()
    
    session.close()
    
    # Track customers seen
    customers_seen = set()
    data = {}
    
    for order in orders:
        order_date = datetime.fromtimestamp(order.created_at).strftime('%Y-%m-%d')
        
        if order_date not in data:
            data[order_date] = {'date': order_date, 'new': 0, 'returning': 0, 'total': 0}
        
        if order.receipt not in customers_seen:
            data[order_date]['new'] += 1
            customers_seen.add(order.receipt)
        else:
            data[order_date]['returning'] += 1
        
        data[order_date]['total'] = len(customers_seen)
    
    return sorted(data.values(), key=lambda x: x['date'])


def get_subscription_metrics() -> Dict:
    """Get current subscription metrics and trends."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    # Active subscriptions by tier
    subs_by_tier = session.query(
        Subscription.plan_id,
        func.count(Subscription.id).label('count'),
        func.sum(Subscription.amount_paise).label('revenue')
    ).filter(
        Subscription.status == 'ACTIVE'
    ).group_by(Subscription.plan_id).all()
    
    # MRR calculation
    mrr = session.query(func.sum(Subscription.amount_paise)).filter(
        Subscription.status == 'ACTIVE',
        Subscription.billing_cycle == 'monthly',
        Subscription.current_period_end > time.time()
    ).scalar() or 0
    
    # ARR calculation
    arr = session.query(func.sum(Subscription.amount_paise)).filter(
        Subscription.status == 'ACTIVE',
        Subscription.billing_cycle == 'yearly',
        Subscription.current_period_end > time.time()
    ).scalar() or 0
    
    # Churn rate (last 30 days)
    thirty_days_ago = time.time() - (30 * 86400)
    churned = session.query(func.count(Subscription.id)).filter(
        Subscription.status == 'CANCELLED',
        Subscription.cancelled_at >= thirty_days_ago
    ).scalar() or 0
    
    total_active = session.query(func.count(Subscription.id)).filter(
        Subscription.status == 'ACTIVE'
    ).scalar() or 0
    
    session.close()
    
    return {
        'mrr': mrr / 100,
        'arr': (arr / 100) + (mrr * 12 / 100),  # ARR + annualized MRR
        'active_subscriptions': total_active,
        'churn_rate': (churned / (total_active + churned) * 100) if (total_active + churned) > 0 else 0,
        'by_tier': [
            {
                'tier': tier,
                'count': count,
                'revenue': revenue / 100
            }
            for tier, count, revenue in subs_by_tier
        ]
    }


def get_top_products(days: int = 30, limit: int = 10) -> List[Dict]:
    """Get top-selling products."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    cutoff = time.time() - (days * 86400)
    
    top_products = session.query(
        Order.product,
        func.count(Order.id).label('orders'),
        func.sum(Order.amount).label('revenue')
    ).filter(
        Order.status == 'paid',
        Order.created_at >= cutoff
    ).group_by(Order.product).order_by(func.sum(Order.amount).desc()).limit(limit).all()
    
    session.close()
    
    return [
        {
            'product': product,
            'orders': orders,
            'revenue': revenue / 100
        }
        for product, orders, revenue in top_products
    ]


def get_conversion_funnel(days: int = 30) -> Dict:
    """Get conversion funnel metrics."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    cutoff = time.time() - (days * 86400)
    
    # Total orders created
    total_orders = session.query(func.count(Order.id)).filter(
        Order.created_at >= cutoff
    ).scalar() or 0
    
    # Paid orders
    paid_orders = session.query(func.count(Order.id)).filter(
        Order.status == 'paid',
        Order.created_at >= cutoff
    ).scalar() or 0
    
    # Failed payments
    failed = session.query(func.count(Payment.id)).filter(
        Payment.status == 'failed',
        Payment.created_at >= cutoff
    ).scalar() or 0
    
    session.close()
    
    conversion_rate = (paid_orders / total_orders * 100) if total_orders > 0 else 0
    
    return {
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        'failed_payments': failed,
        'conversion_rate': conversion_rate,
        'abandonment_rate': 100 - conversion_rate
    }


def get_dashboard_summary(days: int = 30) -> Dict:
    """Get comprehensive dashboard summary."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    cutoff = time.time() - (days * 86400)
    
    # Revenue metrics
    revenue = session.query(func.sum(Order.amount)).filter(
        Order.status == 'paid',
        Order.created_at >= cutoff
    ).scalar() or 0
    
    # Previous period revenue (for comparison)
    prev_cutoff = cutoff - (days * 86400)
    prev_revenue = session.query(func.sum(Order.amount)).filter(
        Order.status == 'paid',
        Order.created_at >= prev_cutoff,
        Order.created_at < cutoff
    ).scalar() or 0
    
    # Customer metrics
    customers = session.query(func.count(func.distinct(Order.receipt))).filter(
        Order.created_at >= cutoff
    ).scalar() or 0
    
    prev_customers = session.query(func.count(func.distinct(Order.receipt))).filter(
        Order.created_at >= prev_cutoff,
        Order.created_at < cutoff
    ).scalar() or 0
    
    # Orders
    orders = session.query(func.count(Order.id)).filter(
        Order.status == 'paid',
        Order.created_at >= cutoff
    ).scalar() or 0
    
    prev_orders = session.query(func.count(Order.id)).filter(
        Order.status == 'paid',
        Order.created_at >= prev_cutoff,
        Order.created_at < cutoff
    ).scalar() or 0
    
    session.close()
    
    # Calculate growth rates
    revenue_growth = ((revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    customer_growth = ((customers - prev_customers) / prev_customers * 100) if prev_customers > 0 else 0
    order_growth = ((orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
    
    return {
        'revenue': {
            'current': revenue / 100,
            'previous': prev_revenue / 100,
            'growth': revenue_growth
        },
        'customers': {
            'current': customers,
            'previous': prev_customers,
            'growth': customer_growth
        },
        'orders': {
            'current': orders,
            'previous': prev_orders,
            'growth': order_growth
        },
        'avg_order_value': (revenue / orders / 100) if orders > 0 else 0
    }
