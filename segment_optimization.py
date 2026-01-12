import time
from typing import Dict, List, Tuple
from models import get_engine, get_session, Order
from utils import _get_db_url


SEGMENT_DEFINITIONS = {
    'VIP': {'min_orders': 5, 'min_ltv_rupees': 1000, 'priority': 1},
    'LOYAL': {'min_orders': 3, 'min_ltv_rupees': 500, 'priority': 2},
    'PROMISING': {'min_orders': 2, 'min_ltv_rupees': 200, 'priority': 3},
    'NEW': {'min_orders': 1, 'max_orders': 1, 'priority': 4},
    'AT_RISK': {'dormant_days': 60, 'priority': 5},
}


def _classify_customer(receipt: str, orders: List) -> str:
    """Classify a customer into a segment based on order history."""
    if not orders:
        return 'UNKNOWN'
    
    paid_orders = [o for o in orders if o.status == 'paid']
    order_count = len(paid_orders)
    ltv_rupees = sum(o.amount for o in paid_orders) / 100.0  # Convert from paise
    
    # Check recency for at-risk
    if paid_orders:
        last_purchase = max(o.paid_at for o in paid_orders if o.paid_at)
        days_since = int((time.time() - last_purchase) / 86400.0)
        if days_since > 60 and order_count >= 2:
            return 'AT_RISK'
    
    # VIP: high value, frequent
    if order_count >= 5 and ltv_rupees >= 1000:
        return 'VIP'
    
    # LOYAL: repeat customers
    if order_count >= 3 and ltv_rupees >= 500:
        return 'LOYAL'
    
    # PROMISING: showing potential
    if order_count >= 2 and ltv_rupees >= 200:
        return 'PROMISING'
    
    # NEW: first purchase
    if order_count == 1:
        return 'NEW'
    
    return 'CASUAL'


def analyze_segments(days_back: int = 90) -> Dict:
    """Analyze all customer segments and return distribution and metrics."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    since = time.time() - (days_back * 86400.0)
    all_orders = session.query(Order).filter(Order.created_at >= since).all()
    session.close()
    
    # Group by receipt
    customers = {}
    for order in all_orders:
        receipt = order.receipt
        if receipt not in customers:
            customers[receipt] = []
        customers[receipt].append(order)
    
    # Classify and aggregate
    segments = {
        'VIP': {'count': 0, 'revenue': 0, 'avg_orders': 0, 'customers': []},
        'LOYAL': {'count': 0, 'revenue': 0, 'avg_orders': 0, 'customers': []},
        'PROMISING': {'count': 0, 'revenue': 0, 'avg_orders': 0, 'customers': []},
        'NEW': {'count': 0, 'revenue': 0, 'avg_orders': 0, 'customers': []},
        'AT_RISK': {'count': 0, 'revenue': 0, 'avg_orders': 0, 'customers': []},
        'CASUAL': {'count': 0, 'revenue': 0, 'avg_orders': 0, 'customers': []},
    }
    
    for receipt, orders in customers.items():
        segment = _classify_customer(receipt, orders)
        paid_orders = [o for o in orders if o.status == 'paid']
        revenue = sum(o.amount for o in paid_orders)
        
        segments[segment]['count'] += 1
        segments[segment]['revenue'] += revenue / 100.0  # Convert to rupees
        segments[segment]['customers'].append({
            'receipt': receipt,
            'orders': len(paid_orders),
            'revenue': revenue / 100.0,
        })
    
    # Calculate averages
    for seg in segments.values():
        if seg['count'] > 0:
            total_orders = sum(c['orders'] for c in seg['customers'])
            seg['avg_orders'] = round(total_orders / seg['count'], 1)
            seg['avg_revenue'] = round(seg['revenue'] / seg['count'], 2)
    
    return segments


def identify_opportunities(days_back: int = 90) -> List[Dict]:
    """Identify segment optimization opportunities with priority and actions."""
    segments = analyze_segments(days_back)
    opportunities = []
    
    # Opportunity 1: Move PROMISING to LOYAL
    promising = segments['PROMISING']
    if promising['count'] > 0:
        opportunities.append({
            'segment': 'PROMISING',
            'opportunity': 'Upgrade to LOYAL',
            'potential_customers': promising['count'],
            'priority': 'HIGH',
            'actions': [
                'Offer loyalty program enrollment',
                'Send personalized product bundles',
                'Provide 15% discount on next purchase',
            ],
            'estimated_revenue_lift': promising['count'] * 200,  # Avg ₹200 per upgrade
        })
    
    # Opportunity 2: Retain AT_RISK
    at_risk = segments['AT_RISK']
    if at_risk['count'] > 0:
        opportunities.append({
            'segment': 'AT_RISK',
            'opportunity': 'Win-back campaign',
            'potential_customers': at_risk['count'],
            'priority': 'CRITICAL',
            'actions': [
                'Send 25% off win-back email',
                'Highlight new products since last visit',
                'Offer free shipping',
            ],
            'estimated_revenue_lift': int(at_risk['revenue'] * 0.3),  # 30% recovery
        })
    
    # Opportunity 3: Convert NEW to repeat
    new = segments['NEW']
    if new['count'] > 0:
        opportunities.append({
            'segment': 'NEW',
            'opportunity': 'Convert to repeat customers',
            'potential_customers': new['count'],
            'priority': 'HIGH',
            'actions': [
                'Send welcome series (3 emails)',
                'Offer second purchase discount',
                'Request feedback and reviews',
            ],
            'estimated_revenue_lift': new['count'] * 150,  # Avg ₹150 second purchase
        })
    
    # Opportunity 4: Expand VIP value
    vip = segments['VIP']
    if vip['count'] > 0:
        opportunities.append({
            'segment': 'VIP',
            'opportunity': 'Maximize lifetime value',
            'potential_customers': vip['count'],
            'priority': 'MEDIUM',
            'actions': [
                'Offer premium/exclusive products',
                'Early access to new releases',
                'VIP-only events or content',
            ],
            'estimated_revenue_lift': int(vip['revenue'] * 0.2),  # 20% upsell
        })
    
    # Sort by priority
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    opportunities.sort(key=lambda x: priority_order.get(x['priority'], 99))
    
    return opportunities


def segment_health_metrics(days_back: int = 90) -> Dict:
    """Calculate health metrics for each segment."""
    segments = analyze_segments(days_back)
    total_customers = sum(s['count'] for s in segments.values())
    total_revenue = sum(s['revenue'] for s in segments.values())
    
    health = {}
    for name, data in segments.items():
        count = data['count']
        revenue = data['revenue']
        
        # Health score (0-100)
        # Based on: size %, revenue %, avg order value
        size_pct = (count / total_customers * 100) if total_customers > 0 else 0
        revenue_pct = (revenue / total_revenue * 100) if total_revenue > 0 else 0
        avg_value = data.get('avg_revenue', 0)
        
        # VIP and LOYAL should have high revenue %
        if name in ('VIP', 'LOYAL'):
            health_score = min(100, int(revenue_pct * 2 + avg_value / 10))
        # AT_RISK is unhealthy by definition
        elif name == 'AT_RISK':
            health_score = max(0, 50 - count * 5)  # More at-risk = worse
        # NEW is healthy if growing
        elif name == 'NEW':
            health_score = min(100, int(size_pct * 3))  # Good if many new customers
        else:
            health_score = min(100, int(size_pct + revenue_pct))
        
        health[name] = {
            'count': count,
            'revenue': round(revenue, 2),
            'size_percent': round(size_pct, 1),
            'revenue_percent': round(revenue_pct, 1),
            'avg_order_value': data.get('avg_revenue', 0),
            'health_score': max(0, min(100, health_score)),
            'status': 'HEALTHY' if health_score >= 70 else 'NEEDS_ATTENTION' if health_score >= 40 else 'CRITICAL',
        }
    
    return health


def recommend_actions(segment: str) -> List[str]:
    """Get recommended actions for a specific segment."""
    actions = {
        'VIP': [
            'Maintain engagement with exclusive content',
            'Offer early access to premium products',
            'Request testimonials and referrals',
            'Provide white-glove customer service',
        ],
        'LOYAL': [
            'Reward with loyalty points or discounts',
            'Cross-sell complementary products',
            'Invite to join VIP tier',
            'Send personalized recommendations',
        ],
        'PROMISING': [
            'Encourage repeat purchases with incentives',
            'Educate on product value through content',
            'Offer bundle deals',
            'Collect feedback to improve experience',
        ],
        'NEW': [
            'Send welcome email series',
            'Offer second purchase discount (10-15%)',
            'Request first purchase feedback',
            'Highlight best-selling products',
        ],
        'AT_RISK': [
            'Launch win-back campaign with 20-25% off',
            'Survey to understand drop-off reasons',
            'Highlight new products/features',
            'Offer free shipping or gift',
        ],
        'CASUAL': [
            'Re-engage with seasonal promotions',
            'Send product recommendations',
            'Offer time-limited discounts',
            'Simplify purchase process',
        ],
    }
    return actions.get(segment, ['Monitor and analyze behavior'])


def optimization_summary(days_back: int = 90) -> Dict:
    """Generate comprehensive optimization summary."""
    segments = analyze_segments(days_back)
    opportunities = identify_opportunities(days_back)
    health = segment_health_metrics(days_back)
    
    total_revenue_potential = sum(o['estimated_revenue_lift'] for o in opportunities)
    critical_segments = [name for name, h in health.items() if h['status'] == 'CRITICAL']
    
    return {
        'segments': segments,
        'opportunities': opportunities,
        'health': health,
        'summary': {
            'total_opportunities': len(opportunities),
            'total_revenue_potential': total_revenue_potential,
            'critical_segments': critical_segments,
            'healthiest_segment': max(health.items(), key=lambda x: x[1]['health_score'])[0] if health else None,
        },
        'generated_at': time.time(),
    }
