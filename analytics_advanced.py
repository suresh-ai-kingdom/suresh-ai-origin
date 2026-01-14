"""Advanced analytics engine with caching."""
import time
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import func, and_, or_
from models import get_engine, get_session, Order, Subscription, Customer
from utils import _get_db_url
from cache_layer import cache_analytics
from analytics_dashboard import get_revenue_trend, get_subscription_metrics as get_sub_metrics
from analytics_dashboard import get_customer_segmentation, get_revenue_forecast


@cache_analytics(ttl=1800)  # Cache for 30 minutes
def get_revenue_trends(days: int = 30, interval: str = 'daily') -> Dict:
    """Get revenue trends over time."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    cutoff = time.time() - (days * 86400)
    
    orders = session.query(Order).filter(
        Order.status == 'paid',
        Order.created_at >= cutoff
    ).all()
    
    session.close()
    
    # Group by time interval
    trends = {}
    for order in orders:
        if interval == 'daily':
            key = datetime.fromtimestamp(order.created_at).strftime('%Y-%m-%d')
        elif interval == 'weekly':
            dt = datetime.fromtimestamp(order.created_at)
            key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
        else:  # monthly
            key = datetime.fromtimestamp(order.created_at).strftime('%Y-%m')
        
        if key not in trends:
            trends[key] = {'revenue': 0, 'orders': 0, 'customers': set()}
        
        trends[key]['revenue'] += order.amount
        trends[key]['orders'] += 1
        trends[key]['customers'].add(order.receipt)
    
    # Convert to list format for charts
    result = []
    for date, data in sorted(trends.items()):
        result.append({
            'date': date,
            'revenue': data['revenue'] / 100,  # Convert to rupees
            'orders': data['orders'],
            'customers': len(data['customers']),
            'avg_order_value': (data['revenue'] / data['orders'] / 100) if data['orders'] > 0 else 0
        })
    
    return {
        'interval': interval,
        'data': result,
        'total_revenue': sum(r['revenue'] for r in result),
        'total_orders': sum(r['orders'] for r in result),
        'total_customers': len(set(order.receipt for order in orders)),
    }


@cache_analytics(ttl=1800)
def get_subscription_metrics(days: int = 30) -> Dict:
    """Get subscription growth and churn metrics."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    cutoff = time.time() - (days * 86400)
    
    # New subscriptions
    new_subs = session.query(Subscription).filter(
        Subscription.created_at >= cutoff
    ).all()
    
    # Active subscriptions
    active_subs = session.query(Subscription).filter(
        Subscription.status == 'ACTIVE'
    ).all()
    
    # Cancelled subscriptions
    cancelled_subs = session.query(Subscription).filter(
        Subscription.status == 'CANCELLED',
        Subscription.updated_at >= cutoff
    ).all()
    
    session.close()
    
    # Calculate MRR by tier
    mrr_by_tier = {}
    for sub in active_subs:
        tier = sub.plan_id or 'unknown'
        if sub.billing_cycle == 'monthly':
            mrr = sub.amount_paise / 100
        elif sub.billing_cycle == 'yearly':
            mrr = (sub.amount_paise / 12) / 100
        else:
            continue
        
        mrr_by_tier[tier] = mrr_by_tier.get(tier, 0) + mrr
    
    # Calculate churn rate
    churned = len(cancelled_subs)
    active = len(active_subs)
    churn_rate = (churned / (active + churned) * 100) if (active + churned) > 0 else 0
    
    return {
        'new_subscriptions': len(new_subs),
        'active_subscriptions': active,
        'cancelled_subscriptions': churned,
        'churn_rate': round(churn_rate, 2),
        'mrr_total': sum(mrr_by_tier.values()),
        'mrr_by_tier': mrr_by_tier,
        'growth_rate': (len(new_subs) / active * 100) if active > 0 else 0,
    }


@cache_analytics(ttl=1800)
def get_customer_segments() -> Dict:
    """RFM (Recency, Frequency, Monetary) customer segmentation."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    # Get all orders grouped by customer
    orders = session.query(Order).filter(Order.status == 'paid').all()
    session.close()
    
    # Calculate RFM scores
    customers = {}
    now = time.time()
    
    for order in orders:
        if order.receipt not in customers:
            customers[order.receipt] = {
                'receipt': order.receipt,
                'orders': [],
                'total_spent': 0,
            }
        customers[order.receipt]['orders'].append(order)
        customers[order.receipt]['total_spent'] += order.amount
    
    # Calculate RFM metrics
    segments = {
        'champions': [],      # High F, high M, low R
        'loyal': [],          # High F, high M
        'potential': [],      # Low F, low M, low R
        'at_risk': [],        # High F, high M, high R
        'dormant': [],        # Low F, low M, high R
    }
    
    for receipt, data in customers.items():
        last_order = max(data['orders'], key=lambda o: o.created_at)
        recency = (now - last_order.created_at) / 86400  # days since last order
        frequency = len(data['orders'])
        monetary = data['total_spent'] / 100
        
        # Simple segmentation logic
        if frequency >= 3 and monetary >= 5000 and recency <= 30:
            segments['champions'].append(receipt)
        elif frequency >= 2 and monetary >= 2000:
            if recency <= 60:
                segments['loyal'].append(receipt)
            else:
                segments['at_risk'].append(receipt)
        elif recency <= 30:
            segments['potential'].append(receipt)
        else:
            segments['dormant'].append(receipt)
    
    return {
        'segments': {k: len(v) for k, v in segments.items()},
        'segment_details': segments,
        'total_customers': len(customers),
    }


@cache_analytics(ttl=1800)
def get_conversion_funnel(days: int = 30) -> Dict:
    """Calculate conversion funnel metrics."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    cutoff = time.time() - (days * 86400)
    
    # Count by order status
    all_orders = session.query(Order).filter(Order.created_at >= cutoff).all()
    
    session.close()
    
    created = len([o for o in all_orders if o.status == 'created'])
    paid = len([o for o in all_orders if o.status == 'paid'])
    failed = len([o for o in all_orders if o.status == 'failed'])
    
    total = created + paid + failed
    
    return {
        'stages': {
            'started': total,
            'attempted': created + paid + failed,
            'completed': paid,
            'abandoned': created,
            'failed': failed,
        },
        'conversion_rate': (paid / total * 100) if total > 0 else 0,
        'abandonment_rate': (created / total * 100) if total > 0 else 0,
        'failure_rate': (failed / total * 100) if total > 0 else 0,
    }


@cache_analytics(ttl=600)  # 10 minutes - more frequent updates
def get_realtime_stats() -> Dict:
    """Get real-time statistics for the dashboard."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    # Last 24 hours
    last_24h = time.time() - 86400
    
    revenue_24h = session.query(func.sum(Order.amount)).filter(
        Order.status == 'paid',
        Order.created_at >= last_24h
    ).scalar() or 0
    
    orders_24h = session.query(func.count(Order.id)).filter(
        Order.status == 'paid',
        Order.created_at >= last_24h
    ).scalar() or 0
    
    customers_24h = session.query(func.count(func.distinct(Order.receipt))).filter(
        Order.created_at >= last_24h
    ).scalar() or 0
    
    # Total stats
    total_revenue = session.query(func.sum(Order.amount)).filter(
        Order.status == 'paid'
    ).scalar() or 0
    
    total_orders = session.query(func.count(Order.id)).filter(
        Order.status == 'paid'
    ).scalar() or 0
    
    active_subs = session.query(func.count(Subscription.id)).filter(
        Subscription.status == 'ACTIVE'
    ).scalar() or 0
    
    session.close()
    
    return {
        'last_24h': {
            'revenue': revenue_24h / 100,
            'orders': orders_24h,
            'customers': customers_24h,
        },
        'totals': {
            'revenue': total_revenue / 100,
            'orders': total_orders,
            'active_subscriptions': active_subs,
        },
        'timestamp': time.time(),
    }


def export_analytics_csv(data: Dict, filename: str = 'analytics_export.csv') -> str:
    """Export analytics data to CSV format."""
    import csv
    import io
    
    output = io.StringIO()
    
    if 'data' in data:  # Revenue trends format
        writer = csv.DictWriter(output, fieldnames=['date', 'revenue', 'orders', 'customers', 'avg_order_value'])
        writer.writeheader()
        writer.writerows(data['data'])
    elif 'segments' in data:  # Customer segments format
        writer = csv.DictWriter(output, fieldnames=['segment', 'count'])
        writer.writeheader()
        for segment, count in data['segments'].items():
            writer.writerow({'segment': segment, 'count': count})
    
    return output.getvalue()
