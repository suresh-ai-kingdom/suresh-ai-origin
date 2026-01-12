"""Business metrics and analytics endpoint for monitoring dashboard."""
import time
from datetime import datetime, timedelta
from models import get_engine, get_session, Order, Payment, Webhook
from utils import _get_db_url
from sqlalchemy import func


def get_business_metrics(days=30):
    """Get business metrics for the specified time period.
    
    Args:
        days: Number of days to look back (default: 30)
    
    Returns:
        Dictionary with key business metrics
    """
    session = get_session(get_engine(_get_db_url()))
    
    try:
        # Calculate time window
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        # Total orders
        total_orders = session.query(func.count(Order.id)).scalar() or 0
        
        # Orders in time period
        period_orders = session.query(func.count(Order.id)).filter(
            Order.created_at >= cutoff_time
        ).scalar() or 0
        
        # Paid orders
        paid_orders = session.query(func.count(Order.id)).filter(
            Order.status == 'paid'
        ).scalar() or 0
        
        period_paid_orders = session.query(func.count(Order.id)).filter(
            Order.status == 'paid',
            Order.created_at >= cutoff_time
        ).scalar() or 0
        
        # Revenue (sum of paid order amounts)
        total_revenue = session.query(func.sum(Order.amount)).filter(
            Order.status == 'paid'
        ).scalar() or 0
        
        period_revenue = session.query(func.sum(Order.amount)).filter(
            Order.status == 'paid',
            Order.created_at >= cutoff_time
        ).scalar() or 0
        
        # Average order value
        avg_order_value = (total_revenue / paid_orders) if paid_orders > 0 else 0
        
        # Conversion rate
        conversion_rate = (paid_orders / total_orders * 100) if total_orders > 0 else 0
        
        # Product breakdown
        product_sales = session.query(
            Order.product,
            func.count(Order.id).label('count'),
            func.sum(Order.amount).label('revenue')
        ).filter(
            Order.status == 'paid'
        ).group_by(Order.product).all()
        
        products = [
            {
                'product': p.product,
                'orders': p.count,
                'revenue': p.revenue / 100  # Convert paise to rupees
            }
            for p in product_sales
        ]
        
        # Recent orders (last 10)
        recent = session.query(Order).order_by(Order.created_at.desc()).limit(10).all()
        recent_orders = [
            {
                'id': o.id,
                'product': o.product,
                'amount': o.amount / 100,
                'status': o.status,
                'created_at': datetime.fromtimestamp(o.created_at).isoformat()
            }
            for o in recent
        ]
        
        # Webhook events count
        webhook_count = session.query(func.count(Webhook.id)).scalar() or 0
        
        return {
            'period_days': days,
            'timestamp': datetime.now().isoformat(),
            'overview': {
                'total_orders': total_orders,
                'period_orders': period_orders,
                'paid_orders': paid_orders,
                'period_paid_orders': period_paid_orders,
                'conversion_rate': round(conversion_rate, 2),
            },
            'revenue': {
                'total': round(total_revenue / 100, 2),  # Convert to rupees
                'period': round(period_revenue / 100, 2),
                'average_order_value': round(avg_order_value / 100, 2),
                'currency': 'INR'
            },
            'products': products,
            'recent_orders': recent_orders,
            'system': {
                'webhook_events': webhook_count
            }
        }
    finally:
        session.close()


def get_daily_sales_chart(days=7):
    """Get daily sales data for charting.
    
    Args:
        days: Number of days to include
    
    Returns:
        List of daily sales data points
    """
    session = get_session(get_engine(_get_db_url()))
    
    try:
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        # Get all paid orders in period
        orders = session.query(Order).filter(
            Order.status == 'paid',
            Order.created_at >= cutoff_time
        ).all()
        
        # Group by day
        daily_data = {}
        for order in orders:
            date = datetime.fromtimestamp(order.created_at).date()
            date_str = date.isoformat()
            
            if date_str not in daily_data:
                daily_data[date_str] = {'orders': 0, 'revenue': 0}
            
            daily_data[date_str]['orders'] += 1
            daily_data[date_str]['revenue'] += order.amount / 100
        
        # Fill in missing days with zeros
        result = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1)).date()
            date_str = date.isoformat()
            result.append({
                'date': date_str,
                'orders': daily_data.get(date_str, {}).get('orders', 0),
                'revenue': round(daily_data.get(date_str, {}).get('revenue', 0), 2)
            })
        
        return result
    finally:
        session.close()
