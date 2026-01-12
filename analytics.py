"""Analytics and metrics calculations for the business."""
import time
from datetime import datetime, timedelta
from models import get_session, Order, Payment, Webhook, Coupon
from sqlalchemy import func, and_


def get_time_range_filters(days=30):
    """Get start and end timestamps for the last N days."""
    now = time.time()
    start = now - (days * 86400)
    return start, now


def get_daily_revenue(days=30):
    """Get revenue grouped by day for the last N days.
    
    Returns:
        list of dicts: [{'date': 'YYYY-MM-DD', 'revenue': 1000, 'orders': 5}, ...]
    """
    session = get_session()
    try:
        start, now = get_time_range_filters(days)
        
        # Get paid orders only
        paid_orders = session.query(Order).filter(
            and_(
                Order.created_at >= start,
                Order.created_at <= now,
                Order.status == 'paid'
            )
        ).all()
        
        # Group by date
        daily = {}
        for order in paid_orders:
            date_str = datetime.fromtimestamp(order.created_at).strftime('%Y-%m-%d')
            if date_str not in daily:
                daily[date_str] = {'revenue': 0, 'orders': 0}
            daily[date_str]['revenue'] += order.amount
            daily[date_str]['orders'] += 1
        
        # Sort by date
        result = [
            {'date': date, 'revenue': data['revenue'], 'orders': data['orders']}
            for date, data in sorted(daily.items())
        ]
        return result
    finally:
        session.close()


def get_product_sales(days=30):
    """Get sales metrics by product.
    
    Returns:
        list of dicts: [{'product': 'starter_pack', 'count': 10, 'revenue': 5000}, ...]
    """
    session = get_session()
    try:
        start, now = get_time_range_filters(days)
        
        # Get paid orders grouped by product
        paid_orders = session.query(Order).filter(
            and_(
                Order.created_at >= start,
                Order.created_at <= now,
                Order.status == 'paid'
            )
        ).all()
        
        # Group by product
        products = {}
        for order in paid_orders:
            product = order.product or 'unknown'
            if product not in products:
                products[product] = {'count': 0, 'revenue': 0}
            products[product]['count'] += 1
            products[product]['revenue'] += order.amount
        
        # Sort by revenue descending
        result = [
            {'product': product, 'count': data['count'], 'revenue': data['revenue']}
            for product, data in sorted(products.items(), 
                                       key=lambda x: x[1]['revenue'], 
                                       reverse=True)
        ]
        return result
    finally:
        session.close()


def get_coupon_effectiveness(days=30):
    """Get coupon usage and discount metrics.
    
    Returns:
        dict with: total_coupons_created, active_coupons, total_uses, total_discount_given_paise
    """
    session = get_session()
    try:
        start, now = get_time_range_filters(days)
        
        # Get coupons created in period
        coupons = session.query(Coupon).filter(
            Coupon.created_at >= start
        ).all()
        
        total_uses = sum(c.current_uses for c in coupons)
        total_discount = 0
        
        # Calculate total discount given (approximate)
        # For each coupon use, estimate discount based on discount_percent
        # This is approximate since we don't track original amounts
        for coupon in coupons:
            # Estimate average order = ₹500 (5000 paise)
            estimated_discount = coupon.current_uses * 5000 * (coupon.discount_percent / 100)
            total_discount += int(estimated_discount)
        
        return {
            'total_coupons_created': len(coupons),
            'active_coupons': sum(1 for c in coupons if c.is_active),
            'total_uses': total_uses,
            'total_discount_given_paise': total_discount,
            'avg_discount_percent': sum(c.discount_percent for c in coupons) / len(coupons) if coupons else 0
        }
    finally:
        session.close()


def get_conversion_metrics(days=30):
    """Get conversion and customer metrics.
    
    Returns:
        dict with: total_orders, paid_orders, conversion_rate, unique_customers, avg_order_value
    """
    session = get_session()
    try:
        start, now = get_time_range_filters(days)
        
        # All orders
        all_orders = session.query(Order).filter(
            and_(
                Order.created_at >= start,
                Order.created_at <= now
            )
        ).all()
        
        # Paid orders
        paid_orders = [o for o in all_orders if o.status == 'paid']
        
        total_orders = len(all_orders)
        paid_count = len(paid_orders)
        conversion = (paid_count / total_orders * 100) if total_orders > 0 else 0
        
        # Unique customers (by receipt, assuming unique per customer)
        unique_customers = len(set(o.receipt for o in all_orders if o.receipt))
        
        # Average order value
        avg_order_value = sum(o.amount for o in paid_orders) / paid_count if paid_orders else 0
        
        return {
            'total_orders': total_orders,
            'paid_orders': paid_count,
            'conversion_rate': round(conversion, 2),
            'unique_customers': unique_customers,
            'avg_order_value_paise': int(avg_order_value),
            'total_revenue_paise': sum(o.amount for o in paid_orders)
        }
    finally:
        session.close()


def get_overview_stats(days=30):
    """Get high-level business metrics overview.
    
    Returns:
        dict with key metrics for display
    """
    session = get_session()
    try:
        start, now = get_time_range_filters(days)
        
        # Paid orders
        paid_orders = session.query(Order).filter(
            and_(
                Order.created_at >= start,
                Order.created_at <= now,
                Order.status == 'paid'
            )
        ).all()
        
        total_revenue = sum(o.amount for o in paid_orders)
        order_count = len(paid_orders)
        
        # Unique customers
        unique_customers = len(set(o.receipt for o in paid_orders if o.receipt))
        
        # Top product
        products = {}
        for order in paid_orders:
            p = order.product or 'unknown'
            products[p] = products.get(p, 0) + 1
        top_product = max(products.items(), key=lambda x: x[1])[0] if products else 'N/A'
        
        # Today's revenue
        today_start = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        today_orders = [o for o in paid_orders if o.created_at >= today_start]
        today_revenue = sum(o.amount for o in today_orders)
        
        return {
            'total_revenue_paise': total_revenue,
            'total_orders': order_count,
            'unique_customers': unique_customers,
            'avg_order_value_paise': int(total_revenue / order_count) if order_count > 0 else 0,
            'top_product': top_product,
            'today_revenue_paise': today_revenue,
            'days_period': days
        }
    finally:
        session.close()


def get_customer_retention(days_back=30):
    """Get repeat customer metrics.
    
    Returns:
        dict with: total_customers, repeat_customers, retention_rate
    """
    session = get_session()
    try:
        start, now = get_time_range_filters(days_back)
        
        # Get all paid orders in period
        orders = session.query(Order).filter(
            and_(
                Order.created_at >= start,
                Order.created_at <= now,
                Order.status == 'paid'
            )
        ).all()
        
        # Count orders per customer (by receipt)
        customer_orders = {}
        for order in orders:
            if order.receipt:
                customer_orders[order.receipt] = customer_orders.get(order.receipt, 0) + 1
        
        total_customers = len(customer_orders)
        repeat_customers = sum(1 for count in customer_orders.values() if count > 1)
        retention = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        return {
            'total_customers': total_customers,
            'repeat_customers': repeat_customers,
            'retention_rate': round(retention, 2),
            'one_time_buyers': total_customers - repeat_customers
        }
    finally:
        session.close()
