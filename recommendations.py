"""Smart Recommendations Engine - ML-based product suggestions."""
import time
from datetime import datetime
from models import get_session, Order, Customer, Subscription, Referral
from sqlalchemy import func
import json


class Recommendation:
    """A single product recommendation."""
    def __init__(self, product_name, score, reason, confidence=0.85):
        self.product_name = product_name
        self.score = score  # 0-100 likelihood
        self.reason = reason
        self.confidence = confidence
        self.created_at = datetime.now().isoformat()


class RecommendationResult:
    """Container for recommendations."""
    def __init__(self, customer_receipt, recommendations):
        self.customer_receipt = customer_receipt
        self.recommendations = recommendations  # List of Recommendation objects
        self.generated_at = datetime.now().isoformat()
        self.total_expected_revenue = sum(r.score for r in recommendations) if recommendations else 0
    
    def to_dict(self):
        return {
            'receipt': self.customer_receipt,
            'recommendations': [
                {
                    'product': r.product_name,
                    'score': round(r.score, 1),
                    'reason': r.reason,
                    'confidence': round(r.confidence, 2),
                    'estimated_conversion_value': int(r.score * 100)  # Estimated value in rupees
                } for r in self.recommendations
            ],
            'total_recommendations': len(self.recommendations),
            'expected_revenue': round(self.total_expected_revenue, 1),
            'generated_at': self.generated_at
        }


# Product catalog with pricing and metadata
PRODUCT_CATALOG = {
    'starter': {
        'name': 'Starter Pack',
        'price': 99,
        'description': 'Perfect for beginners',
        'tags': ['beginner', 'affordable', 'entry-level']
    },
    'pro': {
        'name': 'Pro Pack',
        'price': 499,
        'description': 'For serious learners',
        'tags': ['intermediate', 'professional', 'advanced']
    },
    'premium': {
        'name': 'Premium Pack',
        'price': 999,
        'description': 'Complete mastery program',
        'tags': ['expert', 'complete', 'comprehensive', 'premium']
    },
    'platinum': {
        'name': 'Platinum VIP',
        'price': 2999,
        'description': '1-on-1 coaching + lifetime access',
        'tags': ['vip', 'coaching', 'personal', 'elite']
    }
}


def calculate_product_affinity(customer_receipt, purchased_product=None):
    """Calculate likelihood customer will buy each product.
    
    Args:
        customer_receipt: Customer's receipt ID
        purchased_product: Product already purchased (to exclude)
        
    Returns:
        dict mapping product -> affinity score (0-100)
    """
    session = get_session()
    try:
        # Get customer data
        customer = session.query(Customer).filter(Customer.receipt == customer_receipt).first()
        
        if not customer:
            # New customer - default recommendations
            return {
                'starter': 40,  # Most likely first purchase
                'pro': 25,
                'premium': 15,
                'platinum': 5
            }
        
        # Calculate based on LTV (Lifetime Value)
        ltv = customer.ltv_paise / 100 if customer.ltv_paise else 0
        order_count = customer.order_count or 0
        
        # Get customer orders
        orders = session.query(Order).filter(Order.receipt == customer_receipt).all()
        purchased_products = set(o.product for o in orders if o.product)
        
        # Calculate affinity based on purchase history
        affinity = {}
        
        # Starter affinity (entry-level)
        if 'starter' not in purchased_products:
            affinity['starter'] = max(10, 30 - (ltv / 50))  # Lower if high LTV
        
        # Pro affinity (step-up from starter)
        if 'pro' not in purchased_products:
            if 'starter' in purchased_products:
                affinity['pro'] = 70 + (order_count * 5)  # High upgrade likelihood
            else:
                affinity['pro'] = 40 + (ltv / 100)  # Medium likelihood
        
        # Premium affinity (high-value)
        if 'premium' not in purchased_products:
            if order_count >= 2:
                affinity['premium'] = 60 + (ltv / 200)  # High if repeat buyer
            elif ltv > 500:
                affinity['premium'] = 50  # High LTV customers
            else:
                affinity['premium'] = 20
        
        # Platinum affinity (ultra-premium)
        if 'platinum' not in purchased_products:
            if order_count >= 3 or ltv > 1000:
                affinity['platinum'] = 70  # VIP/repeat customers
            elif order_count >= 2:
                affinity['platinum'] = 40
            else:
                affinity['platinum'] = 10
        
        # Filter out already purchased
        return {k: v for k, v in affinity.items() if k not in purchased_products}
    
    finally:
        session.close()


def get_complementary_products(purchased_product):
    """Get products that complement what customer already bought.
    
    Args:
        purchased_product: Product code (e.g., 'starter')
        
    Returns:
        list of complementary products ranked
    """
    # Define product progression
    upgrade_path = {
        'starter': ['pro', 'premium', 'platinum'],
        'pro': ['premium', 'platinum'],
        'premium': ['platinum'],
        'platinum': []
    }
    
    # Return suggested upgrades
    return upgrade_path.get(purchased_product, [])


def calculate_seasonal_boost(date=None):
    """Calculate seasonal/temporal boost to recommendations.
    
    Higher during promotion periods, quarter-end, etc.
    """
    if date is None:
        date = datetime.now()
    
    # Simple seasonal model
    month = date.month
    
    # Q4 is strong (Oct, Nov, Dec)
    if month in [10, 11, 12]:
        return 1.3
    # Q1 New Year resolutions
    elif month in [1, 2]:
        return 1.2
    # Mid-year
    else:
        return 1.0


def generate_recommendations(customer_receipt, limit=3):
    """Generate product recommendations for a customer.
    
    Args:
        customer_receipt: Customer's receipt ID
        limit: Max recommendations to return
        
    Returns:
        RecommendationResult with scored recommendations
    """
    session = get_session()
    try:
        # Get customer
        customer = session.query(Customer).filter(Customer.receipt == customer_receipt).first()
        
        if not customer:
            # New customer - basic recommendations
            return RecommendationResult(
                customer_receipt,
                [
                    Recommendation('Starter Pack', 40, 'Perfect entry point for beginners'),
                    Recommendation('Pro Pack', 20, 'For serious learners'),
                    Recommendation('Premium Pack', 10, 'Complete program'),
                ]
            )
        
        # Get last purchased product
        last_order = session.query(Order).filter(
            Order.receipt == customer_receipt
        ).order_by(Order.created_at.desc()).first()
        
        last_product = last_order.product if last_order else None
        
        # Calculate affinity scores
        affinity_scores = calculate_product_affinity(customer_receipt, last_product)
        
        # Apply seasonal boost
        seasonal_boost = calculate_seasonal_boost()
        boosted_scores = {k: v * seasonal_boost for k, v in affinity_scores.items()}
        
        # Get complementary products
        if last_product:
            complementary = get_complementary_products(last_product)
        else:
            complementary = list(PRODUCT_CATALOG.keys())
        
        # Score complementary products higher
        final_scores = {}
        for product, score in boosted_scores.items():
            if product in complementary:
                final_scores[product] = min(100, score * 1.5)  # Boost complementary
            else:
                final_scores[product] = score
        
        # Sort by score descending
        sorted_products = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Create recommendations
        recommendations = []
        for product_code, score in sorted_products[:limit]:
            product_info = PRODUCT_CATALOG.get(product_code, {})
            
            # Generate reason
            if last_product and product_code in complementary:
                reason = f"Great upgrade from {PRODUCT_CATALOG.get(last_product, {}).get('name', 'previous product')}"
            else:
                reason = f"Based on your interests and purchase history"
            
            # Adjust confidence based on customer data
            confidence = 0.85 if customer.order_count and customer.order_count > 1 else 0.70
            
            rec = Recommendation(
                product_info.get('name', product_code),
                score,
                reason,
                confidence
            )
            recommendations.append(rec)
        
        return RecommendationResult(customer_receipt, recommendations)
    
    finally:
        session.close()


def get_recommendations_for_all_customers(limit=3):
    """Get recommendations for all active customers.
    
    Returns:
        dict mapping receipt -> recommendations
    """
    session = get_session()
    try:
        customers = session.query(Customer).all()
        
        results = {}
        for customer in customers:
            result = generate_recommendations(customer.receipt, limit)
            results[customer.receipt] = result.to_dict()
        
        return results
    finally:
        session.close()


def calculate_recommendation_impact():
    """Calculate impact of recommendations on revenue.
    
    Returns:
        dict with metrics
    """
    session = get_session()
    try:
        # Get all customers with recommendations
        customers = session.query(Customer).all()
        
        total_ltv = 0
        avg_ltv = 0
        recommendations_made = 0
        estimated_lift = 0
        
        for customer in customers:
            total_ltv += (customer.ltv_paise or 0) / 100
            recommendations_made += 1
            
            # Estimate lift if they convert on recommendation (conservative: 15% conversion)
            rec_result = generate_recommendations(customer.receipt, 1)
            if rec_result.total_expected_revenue > 0:
                estimated_lift += rec_result.total_expected_revenue * 0.15
        
        avg_ltv = total_ltv / len(customers) if customers else 0
        
        return {
            'total_customers': len(customers),
            'recommendations_made': recommendations_made,
            'total_customer_ltv': round(total_ltv, 2),
            'average_customer_ltv': round(avg_ltv, 2),
            'estimated_revenue_lift': round(estimated_lift, 2),
            'estimated_lift_percentage': round((estimated_lift / max(total_ltv, 1)) * 100, 1),
            'generated_at': datetime.now().isoformat()
        }
    finally:
        session.close()


def get_product_performance():
    """Analyze product performance for recommendations.
    
    Returns:
        dict with product stats
    """
    session = get_session()
    try:
        stats = {}
        
        for product_code, product_info in PRODUCT_CATALOG.items():
            orders = session.query(func.count(Order.id)).filter(
                Order.product == product_code
            ).scalar() or 0
            
            total_revenue = session.query(func.sum(Order.amount)).filter(
                Order.product == product_code
            ).scalar() or 0
            
            customers = session.query(func.count(func.distinct(Order.receipt))).filter(
                Order.product == product_code
            ).scalar() or 0
            
            stats[product_code] = {
                'name': product_info['name'],
                'total_orders': orders,
                'total_revenue': total_revenue / 100 if total_revenue else 0,
                'unique_customers': customers,
                'avg_order_value': (total_revenue / max(orders, 1)) / 100 if orders else 0
            }
        
        return stats
    finally:
        session.close()


def get_recommendation_stats():
    """Get statistics about recommendation system.
    
    Returns:
        dict with metrics
    """
    return {
        'product_performance': get_product_performance(),
        'recommendation_impact': calculate_recommendation_impact(),
        'generated_at': datetime.now().isoformat()
    }


def get_cross_sell_opportunities():
    """Find customers most likely to cross-sell to.
    
    Returns:
        list of customers ranked by cross-sell likelihood
    """
    session = get_session()
    try:
        customers = session.query(Customer).filter(
            Customer.ltv_paise > 0,
            Customer.order_count > 0
        ).order_by(Customer.ltv_paise.desc()).limit(20).all()
        
        opportunities = []
        for customer in customers:
            rec = generate_recommendations(customer.receipt, 1)
            
            if rec.recommendations:
                top_rec = rec.recommendations[0]
                opportunities.append({
                    'receipt': customer.receipt,
                    'ltv': (customer.ltv_paise or 0) / 100,
                    'order_count': customer.order_count,
                    'segment': customer.segment,
                    'recommended_product': top_rec.product_name,
                    'confidence': top_rec.score
                })
        
        return opportunities
    finally:
        session.close()
