import time
from typing import Dict, List, Optional
from segment_optimization import analyze_segments, identify_opportunities
from churn_prediction import churn_stats, get_at_risk_customers
from pricing import all_dynamic_prices


def campaign_audience_segments(days_back: int = 90) -> Dict[str, Dict]:
    """Summarize segments to help select audiences for campaigns."""
    segments = analyze_segments(days_back)
    return {name: {
        'count': data['count'],
        'revenue': data['revenue'],
        'avg_orders': data.get('avg_orders', 0),
        'avg_revenue': data.get('avg_revenue', 0),
    } for name, data in segments.items()}


def generate_campaign(goal: str,
                      target_segment: str,
                      products: Optional[List[str]] = None,
                      discount_percent: int = 0,
                      days_back: int = 90) -> Dict:
    """Generate a campaign payload with subject, message, CTA, and estimates.
    goal: 'win-back' | 'upsell' | 'new-customer' | 'loyalty'
    target_segment: segment name from segment_optimization
    products: optional product keys (starter|pro|premium)
    discount_percent: 0-50
    """
    target_segment = (target_segment or 'NEW').upper()
    prices = all_dynamic_prices(days=days_back)
    audience = campaign_audience_segments(days_back)
    audience_count = audience.get(target_segment, {}).get('count', 0)
    discount_percent = max(0, min(50, int(discount_percent)))
    products = products or ['starter']

    # Subject and body templates
    subject_map = {
        'win-back': 'We Miss You! {{discount}} Off Just For You',
        'upsell': 'Unlock More Value on {{product}} Today',
        'new-customer': 'Welcome! Start Strong with {{discount}} Off',
        'loyalty': 'Thank You — Exclusive Rewards Inside',
    }
    subject = subject_map.get(goal, 'Exclusive Offer Just For You')

    # Build CTA and message
    product = products[0]
    dynamic_price = prices.get(product, 299)
    discount_text = f"{discount_percent}%" if discount_percent else "Special"
    cta = f"Get {product.title()} for ₹{int(round(dynamic_price * (100 - discount_percent)/100))}"

    message = (
        f"Hi there!\n\n"
        f"We curated this for our {target_segment.replace('_', ' ').title()} customers. "
        f"Grab {product.title()} at an irresistible price. "
        f"Use code SAVE{discount_percent} to claim your {discount_text} discount.\n\n"
        f"This offer helps you {('get back on track' if goal=='win-back' else 'unlock more value')} with our best picks.\n"
        f"— Team SURESH AI ORIGIN"
    )

    # Estimate conversion lift
    base_conv = 0.03
    lift = 0.02 if discount_percent >= 20 else 0.01 if discount_percent >= 10 else 0.005
    seg_boost = 0.02 if target_segment in ('AT_RISK', 'PROMISING') else 0.01 if target_segment in ('LOYAL', 'VIP') else 0.0
    estimated_conversion = min(0.25, base_conv + lift + seg_boost)
    estimated_revenue_per_100 = int(round(estimated_conversion * dynamic_price * 100))

    return {
        'goal': goal,
        'target_segment': target_segment,
        'audience_count': audience_count,
        'products': products,
        'discount_percent': discount_percent,
        'subject': subject.replace('{{discount}}', discount_text).replace('{{product}}', product.title()),
        'message': message,
        'cta': cta,
        'estimated_conversion': round(estimated_conversion, 4),
        'estimated_revenue_per_100': estimated_revenue_per_100,
        'generated_at': time.time(),
    }


def suggest_campaigns(days_back: int = 90) -> List[Dict]:
    """Suggest high-impact campaigns based on segments and churn."""
    opps = identify_opportunities(days_back)
    stats = churn_stats()
    suggestions: List[Dict] = []

    # Win-back for at-risk
    if stats.get('customers_needing_attention', 0) > 0:
        suggestions.append(generate_campaign(
            goal='win-back', target_segment='AT_RISK', products=['pro'], discount_percent=25, days_back=days_back
        ))

    # Upsell for promising
    prom = next((o for o in opps if o['segment'] == 'PROMISING'), None)
    if prom and prom['potential_customers'] > 0:
        suggestions.append(generate_campaign(
            goal='upsell', target_segment='PROMISING', products=['premium'], discount_percent=15, days_back=days_back
        ))

    # Loyalty rewards for loyal
    suggestions.append(generate_campaign(
        goal='loyalty', target_segment='LOYAL', products=['pro'], discount_percent=10, days_back=days_back
    ))

    # Welcome for new
    suggestions.append(generate_campaign(
        goal='new-customer', target_segment='NEW', products=['starter'], discount_percent=10, days_back=days_back
    ))

    return suggestions


def campaign_stats(days_back: int = 90) -> Dict:
    """Return campaign KPIs for dashboard."""
    segs = campaign_audience_segments(days_back)
    at_risk = get_at_risk_customers(min_risk=50, limit=100)
    suggestions = suggest_campaigns(days_back)
    return {
        'audiences': segs,
        'at_risk_count': len(at_risk),
        'suggestion_count': len(suggestions),
        'top_suggestion': max(suggestions, key=lambda s: s['estimated_revenue_per_100']) if suggestions else None,
        'generated_at': time.time(),
    }
import time
import hashlib
from typing import Dict, List, Optional
from models import get_engine, get_session, Base
from sqlalchemy import Column, String, Integer, Text, Float
from utils import _get_db_url


class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    campaign_type = Column(String, index=True)  # EMAIL, SOCIAL, SMS, AD
    target_segment = Column(String)  # VIP, LOYAL, etc.
    template_id = Column(String)
    subject = Column(String, nullable=True)
    content = Column(Text)
    status = Column(String, index=True)  # DRAFT, SCHEDULED, SENT, ACTIVE, PAUSED
    scheduled_at = Column(Float, nullable=True)
    sent_at = Column(Float, nullable=True)
    created_at = Column(Float)
    created_by = Column(String)
    # Performance metrics
    sent_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    converted_count = Column(Integer, default=0)
    revenue_generated = Column(Integer, default=0)  # in paise


CAMPAIGN_TEMPLATES = {
    'EMAIL': {
        'welcome_series': {
            'name': 'Welcome New Customer',
            'subject': 'Welcome to {brand_name}! Here\'s {discount}% off your next order',
            'content': '''Hi {customer_name},

Welcome to {brand_name}! We're thrilled to have you as part of our community.

As a special thank you, here's {discount}% off your next purchase. Use code: {coupon_code}

Explore our most popular products:
{product_recommendations}

Best regards,
{brand_name} Team''',
            'suggested_segment': 'NEW',
        },
        'win_back': {
            'name': 'Win-Back Campaign',
            'subject': 'We miss you! Come back for {discount}% off',
            'content': '''Hi {customer_name},

It's been a while since your last visit. We've added exciting new products that we think you'll love!

Get {discount}% off your next order with code: {coupon_code}

See what's new:
{product_recommendations}

Hope to see you soon!
{brand_name} Team''',
            'suggested_segment': 'AT_RISK',
        },
        'loyalty_reward': {
            'name': 'Loyalty Rewards',
            'subject': 'Thanks for being loyal! Exclusive {discount}% off inside',
            'content': '''Hi {customer_name},

Thank you for being a valued customer! Your loyalty means everything to us.

As a token of appreciation, enjoy {discount}% off your next purchase with code: {coupon_code}

VIP Benefits:
- Early access to new products
- Exclusive discounts
- Priority customer support

Shop now:
{product_recommendations}

Cheers,
{brand_name} Team''',
            'suggested_segment': 'LOYAL',
        },
        'abandoned_cart': {
            'name': 'Abandoned Cart Reminder',
            'subject': 'You left something behind! Complete your order now',
            'content': '''Hi {customer_name},

You were so close! Complete your purchase and get {discount}% off today.

Your cart:
{cart_items}

Use code: {coupon_code}

This offer expires in 24 hours!

Complete Order Now
{brand_name} Team''',
            'suggested_segment': 'ALL',
        },
    },
    'SOCIAL': {
        'product_launch': {
            'name': 'Product Launch Announcement',
            'content': '''🚀 NEW LAUNCH ALERT! 🚀

Introducing {product_name} - the {product_description}

✨ Limited time offer: {discount}% OFF
🎁 First 100 orders get a FREE bonus
⏰ Offer ends {expiry_date}

Shop now: {shop_url}

#NewLaunch #LimitedOffer #{brand_name}''',
            'suggested_segment': 'ALL',
        },
        'flash_sale': {
            'name': 'Flash Sale',
            'content': '''⚡ FLASH SALE ⚡

{discount}% OFF everything for the next {duration} hours!

Don't miss out - this deal won't last long!

Shop now: {shop_url}
Code: {coupon_code}

⏰ Hurry! Sale ends at {end_time}

#FlashSale #LimitedTime #{brand_name}''',
            'suggested_segment': 'ALL',
        },
        'testimonial': {
            'name': 'Customer Testimonial',
            'content': '''💬 WHAT OUR CUSTOMERS SAY 💬

"{testimonial_text}" - {customer_name}

Join {customer_count}+ happy customers!

⭐⭐⭐⭐⭐ Rated {rating}/5

Shop now: {shop_url}

#CustomerLove #Reviews #{brand_name}''',
            'suggested_segment': 'ALL',
        },
    },
}


def _generate_campaign_id() -> str:
    """Generate unique campaign ID."""
    return f"camp_{hashlib.md5(f"{time.time()}".encode()).hexdigest()[:12]}"


def generate_template_campaign(
    campaign_type: str,
    template_id: str,
    target_segment: str,
    variables: Dict,
    created_by: str = 'admin',
    name: Optional[str] = None,
) -> Dict:
    """Generate a new campaign from template with personalization."""
    if campaign_type not in CAMPAIGN_TEMPLATES:
        return {'error': f'Invalid campaign type: {campaign_type}'}
    
    templates = CAMPAIGN_TEMPLATES[campaign_type]
    if template_id not in templates:
        return {'error': f'Invalid template: {template_id}'}
    
    template = templates[template_id]
    
    # Merge default variables
    default_vars = {
        'brand_name': 'Suresh AI Origin',
        'discount': '20',
        'coupon_code': 'WELCOME20',
        'customer_name': 'Valued Customer',
        'product_recommendations': 'Starter Pack, Pro Pack, Premium Pack',
        'shop_url': 'https://suresh-ai-origin.com',
    }
    merged_vars = {**default_vars, **variables}
    
    # Generate content
    content = template['content']
    subject = template.get('subject', '')
    
    for key, value in merged_vars.items():
        placeholder = '{' + key + '}'
        content = content.replace(placeholder, str(value))
        subject = subject.replace(placeholder, str(value))
    
    # Create campaign record
    campaign_id = _generate_campaign_id()
    campaign_name = name or f"{template['name']} - {target_segment}"
    
    from models import get_engine, get_session
    engine = get_engine(_get_db_url())
    Base.metadata.create_all(engine)
    session = get_session(engine)
    
    campaign = Campaign(
        id=campaign_id,
        name=campaign_name,
        campaign_type=campaign_type,
        target_segment=target_segment,
        template_id=template_id,
        subject=subject if subject else None,
        content=content,
        status='DRAFT',
        created_at=time.time(),
        created_by=created_by,
    )
    
    try:
        session.add(campaign)
        session.commit()
    except Exception as e:
        session.rollback()
        return {'error': str(e)}
    finally:
        session.close()
    
    return {
        'success': True,
        'campaign_id': campaign_id,
        'name': campaign_name,
        'type': campaign_type,
        'template': template_id,
        'segment': target_segment,
        'subject': subject,
        'content': content,
        'status': 'DRAFT',
    }


def list_campaigns(status: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """List all campaigns, optionally filtered by status."""
    from models import get_engine, get_session
    engine = get_engine(_get_db_url())
    Base.metadata.create_all(engine)
    session = get_session(engine)
    
    query = session.query(Campaign)
    if status:
        query = query.filter_by(status=status)
    
    campaigns = query.order_by(Campaign.created_at.desc()).limit(limit).all()
    session.close()
    
    result = []
    for c in campaigns:
        result.append({
            'id': c.id,
            'name': c.name,
            'type': c.campaign_type,
            'segment': c.target_segment,
            'template': c.template_id,
            'status': c.status,
            'created_at': c.created_at,
            'scheduled_at': c.scheduled_at,
            'sent_at': c.sent_at,
            'performance': {
                'sent': c.sent_count,
                'opened': c.opened_count,
                'clicked': c.clicked_count,
                'converted': c.converted_count,
                'revenue': c.revenue_generated / 100.0 if c.revenue_generated else 0,
            },
        })
    
    return result


def schedule_campaign(campaign_id: str, scheduled_at: float) -> Dict:
    """Schedule a campaign for future sending."""
    from models import get_engine, get_session
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    campaign = session.query(Campaign).filter_by(id=campaign_id).first()
    if not campaign:
        session.close()
        return {'error': 'Campaign not found'}
    
    campaign.scheduled_at = scheduled_at
    campaign.status = 'SCHEDULED'
    
    try:
        session.commit()
        session.close()
        return {'success': True, 'campaign_id': campaign_id, 'scheduled_at': scheduled_at}
    except Exception as e:
        session.rollback()
        session.close()
        return {'error': str(e)}


def update_campaign_performance(
    campaign_id: str,
    sent: int = 0,
    opened: int = 0,
    clicked: int = 0,
    converted: int = 0,
    revenue_paise: int = 0,
) -> Dict:
    """Update campaign performance metrics."""
    from models import get_engine, get_session
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    campaign = session.query(Campaign).filter_by(id=campaign_id).first()
    if not campaign:
        session.close()
        return {'error': 'Campaign not found'}
    
    campaign.sent_count += sent
    campaign.opened_count += opened
    campaign.clicked_count += clicked
    campaign.converted_count += converted
    campaign.revenue_generated += revenue_paise
    
    try:
        session.commit()
        session.close()
        return {'success': True}
    except Exception as e:
        session.rollback()
        session.close()
        return {'error': str(e)}


def get_campaign_stats() -> Dict:
    """Get aggregate campaign statistics."""
    from models import get_engine, get_session
    engine = get_engine(_get_db_url())
    Base.metadata.create_all(engine)
    session = get_session(engine)
    
    campaigns = session.query(Campaign).all()
    session.close()
    
    stats = {
        'total_campaigns': len(campaigns),
        'draft': 0,
        'scheduled': 0,
        'sent': 0,
        'active': 0,
        'total_sent': 0,
        'total_opened': 0,
        'total_clicked': 0,
        'total_converted': 0,
        'total_revenue': 0,
        'avg_open_rate': 0,
        'avg_click_rate': 0,
        'avg_conversion_rate': 0,
    }
    
    for c in campaigns:
        stats[c.status.lower()] = stats.get(c.status.lower(), 0) + 1
        stats['total_sent'] += c.sent_count
        stats['total_opened'] += c.opened_count
        stats['total_clicked'] += c.clicked_count
        stats['total_converted'] += c.converted_count
        stats['total_revenue'] += c.revenue_generated
    
    # Calculate rates
    if stats['total_sent'] > 0:
        stats['avg_open_rate'] = round(stats['total_opened'] / stats['total_sent'] * 100, 2)
        stats['avg_click_rate'] = round(stats['total_clicked'] / stats['total_sent'] * 100, 2)
        stats['avg_conversion_rate'] = round(stats['total_converted'] / stats['total_sent'] * 100, 2)
    
    stats['total_revenue'] = stats['total_revenue'] / 100.0  # Convert to rupees
    
    return stats


def get_available_templates() -> Dict:
    """Get all available campaign templates."""
    result = {}
    for campaign_type, templates in CAMPAIGN_TEMPLATES.items():
        result[campaign_type] = []
        for template_id, template in templates.items():
            result[campaign_type].append({
                'id': template_id,
                'name': template['name'],
                'suggested_segment': template.get('suggested_segment', 'ALL'),
            })
    return result
