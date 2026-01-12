"""Subscription management system for recurring revenue."""
import time
from datetime import datetime, timedelta
from models import get_session, Order
from sqlalchemy import and_, func, or_
from enum import Enum


class SubscriptionTier(Enum):
    """Subscription tier levels."""
    STARTER = "STARTER"
    PRO = "PRO"
    PREMIUM = "PREMIUM"


class SubscriptionStatus(Enum):
    """Subscription status."""
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    TRIAL = "TRIAL"


# Pricing in paise (1 rupee = 100 paise)
SUBSCRIPTION_PRICING = {
    'STARTER': {
        'monthly': 9900,  # ₹99/month
        'yearly': 99000,  # ₹990/year (2 months free)
        'name': 'Starter Pack',
        'description': 'Essential AI prompts & templates',
        'features': [
            '100+ AI prompts',
            'Basic templates',
            'Email support',
            'Monthly updates'
        ]
    },
    'PRO': {
        'monthly': 49900,  # ₹499/month
        'yearly': 499000,  # ₹4,990/year (2 months free)
        'name': 'Pro Pack',
        'description': 'Advanced automation & workflows',
        'features': [
            'Everything in Starter',
            '500+ advanced prompts',
            'Automation workflows',
            'Priority support',
            'Weekly updates',
            'Community access'
        ]
    },
    'PREMIUM': {
        'monthly': 99900,  # ₹999/month
        'yearly': 999000,  # ₹9,990/year (2 months free)
        'name': 'Premium Pack',
        'description': 'Complete AI mastery suite',
        'features': [
            'Everything in Pro',
            '1000+ premium prompts',
            'Custom workflows',
            'Personal AI coaching',
            'Daily updates',
            'Exclusive bonuses',
            'Private community'
        ]
    }
}


def get_active_subscriptions(receipt=None):
    """Get active subscriptions.
    
    Args:
        receipt: Optional customer receipt to filter by
        
    Returns:
        list of subscription dicts
    """
    session = get_session()
    try:
        from models import Subscription
        
        query = session.query(Subscription).filter(
            Subscription.status.in_(['ACTIVE', 'TRIAL'])
        )
        
        if receipt:
            query = query.filter(Subscription.receipt == receipt)
        
        subs = query.all()
        
        result = []
        for sub in subs:
            result.append({
                'id': sub.id,
                'receipt': sub.receipt,
                'tier': sub.tier,
                'billing_cycle': sub.billing_cycle,
                'status': sub.status,
                'amount_paise': sub.amount_paise,
                'amount_rupees': sub.amount_paise / 100,
                'current_period_start': datetime.fromtimestamp(sub.current_period_start).strftime('%Y-%m-%d'),
                'current_period_end': datetime.fromtimestamp(sub.current_period_end).strftime('%Y-%m-%d'),
                'days_until_renewal': int((sub.current_period_end - time.time()) / 86400),
                'created_at': datetime.fromtimestamp(sub.created_at).strftime('%Y-%m-%d %H:%M')
            })
        
        return result
    finally:
        session.close()


def get_subscription_by_receipt(receipt):
    """Get customer's active subscription.
    
    Args:
        receipt: Customer receipt ID
        
    Returns:
        dict with subscription data or None
    """
    subscriptions = get_active_subscriptions(receipt=receipt)
    return subscriptions[0] if subscriptions else None


def calculate_mrr():
    """Calculate Monthly Recurring Revenue.
    
    Returns:
        dict with MRR metrics
    """
    session = get_session()
    try:
        from models import Subscription
        
        # Get all active subscriptions
        active_subs = session.query(Subscription).filter(
            Subscription.status.in_(['ACTIVE', 'TRIAL'])
        ).all()
        
        monthly_revenue = 0
        yearly_revenue = 0
        
        for sub in active_subs:
            if sub.billing_cycle == 'monthly':
                monthly_revenue += sub.amount_paise
            elif sub.billing_cycle == 'yearly':
                # Convert yearly to monthly equivalent
                monthly_revenue += (sub.amount_paise / 12)
                yearly_revenue += sub.amount_paise
        
        # Count by tier
        tier_counts = {}
        for tier in SubscriptionTier:
            count = session.query(func.count(Subscription.id)).filter(
                and_(
                    Subscription.tier == tier.value,
                    Subscription.status.in_(['ACTIVE', 'TRIAL'])
                )
            ).scalar() or 0
            tier_counts[tier.value] = count
        
        return {
            'mrr_paise': int(monthly_revenue),
            'mrr_rupees': round(monthly_revenue / 100, 2),
            'arr_paise': int(monthly_revenue * 12),
            'arr_rupees': round((monthly_revenue * 12) / 100, 2),
            'active_subscribers': len(active_subs),
            'tier_breakdown': tier_counts
        }
    finally:
        session.close()


def get_subscription_analytics(days_back=30):
    """Get subscription analytics.
    
    Args:
        days_back: Number of days to look back
        
    Returns:
        dict with analytics
    """
    session = get_session()
    try:
        from models import Subscription
        
        cutoff = time.time() - (days_back * 86400)
        
        # New subscriptions in period
        new_subs = session.query(func.count(Subscription.id)).filter(
            Subscription.created_at >= cutoff
        ).scalar() or 0
        
        # Cancelled in period
        cancelled_subs = session.query(func.count(Subscription.id)).filter(
            and_(
                Subscription.status == 'CANCELLED',
                Subscription.cancelled_at.isnot(None),
                Subscription.cancelled_at >= cutoff
            )
        ).scalar() or 0
        
        # Active at start of period
        active_start = session.query(func.count(Subscription.id)).filter(
            and_(
                Subscription.created_at < cutoff,
                or_(
                    Subscription.status.in_(['ACTIVE', 'TRIAL']),
                    and_(
                        Subscription.status == 'CANCELLED',
                        Subscription.cancelled_at >= cutoff
                    )
                )
            )
        ).scalar() or 0
        
        # Active now
        active_now = session.query(func.count(Subscription.id)).filter(
            Subscription.status.in_(['ACTIVE', 'TRIAL'])
        ).scalar() or 0
        
        # Calculate churn rate
        if active_start > 0:
            churn_rate = (cancelled_subs / active_start) * 100
        else:
            churn_rate = 0
        
        # Revenue growth
        mrr_current = calculate_mrr()
        
        return {
            'new_subscriptions': new_subs,
            'cancelled_subscriptions': cancelled_subs,
            'net_change': new_subs - cancelled_subs,
            'active_subscriptions': active_now,
            'churn_rate_percent': round(churn_rate, 2),
            'mrr_rupees': mrr_current['mrr_rupees'],
            'arr_rupees': mrr_current['arr_rupees']
        }
    finally:
        session.close()


def get_expiring_subscriptions(days_ahead=7):
    """Get subscriptions expiring soon.
    
    Args:
        days_ahead: Number of days to look ahead
        
    Returns:
        list of expiring subscriptions
    """
    session = get_session()
    try:
        from models import Subscription
        
        cutoff = time.time() + (days_ahead * 86400)
        
        subs = session.query(Subscription).filter(
            and_(
                Subscription.status.in_(['ACTIVE', 'TRIAL']),
                Subscription.current_period_end <= cutoff,
                Subscription.current_period_end >= time.time()
            )
        ).all()
        
        result = []
        for sub in subs:
            days_left = int((sub.current_period_end - time.time()) / 86400)
            result.append({
                'id': sub.id,
                'receipt': sub.receipt,
                'tier': sub.tier,
                'days_left': days_left,
                'expires_at': datetime.fromtimestamp(sub.current_period_end).strftime('%Y-%m-%d'),
                'amount_paise': sub.amount_paise,
                'amount_rupees': sub.amount_paise / 100,
                'urgency': 'CRITICAL' if days_left <= 3 else 'HIGH' if days_left <= 5 else 'MEDIUM'
            })
        
        # Sort by urgency
        result.sort(key=lambda x: x['days_left'])
        
        return result
    finally:
        session.close()


def create_subscription(receipt, tier, billing_cycle='monthly', razorpay_sub_id=None):
    """Create a new subscription.
    
    Args:
        receipt: Customer receipt ID
        tier: Subscription tier (STARTER, PRO, PREMIUM)
        billing_cycle: 'monthly' or 'yearly'
        razorpay_sub_id: Optional Razorpay subscription ID
        
    Returns:
        dict with subscription data
    """
    session = get_session()
    try:
        from models import Subscription
        
        # Validate tier
        if tier not in SUBSCRIPTION_PRICING:
            raise ValueError(f"Invalid tier: {tier}")
        
        # Get pricing
        pricing = SUBSCRIPTION_PRICING[tier]
        amount = pricing.get(billing_cycle)
        
        if not amount:
            raise ValueError(f"Invalid billing cycle: {billing_cycle}")
        
        # Calculate period dates
        now = time.time()
        if billing_cycle == 'monthly':
            period_end = now + (30 * 86400)
        else:  # yearly
            period_end = now + (365 * 86400)
        
        # Create subscription
        sub = Subscription(
            id=razorpay_sub_id or f'SUB_{receipt}_{int(now)}',
            receipt=receipt,
            tier=tier,
            billing_cycle=billing_cycle,
            amount_paise=amount,
            status='ACTIVE',
            current_period_start=now,
            current_period_end=period_end,
            created_at=now
        )
        
        session.add(sub)
        session.commit()
        
        return {
            'id': sub.id,
            'receipt': sub.receipt,
            'tier': sub.tier,
            'billing_cycle': sub.billing_cycle,
            'amount_rupees': amount / 100,
            'status': 'ACTIVE',
            'period_end': datetime.fromtimestamp(period_end).strftime('%Y-%m-%d')
        }
    finally:
        session.close()


def cancel_subscription(subscription_id, reason=None):
    """Cancel a subscription.
    
    Args:
        subscription_id: Subscription ID to cancel
        reason: Optional cancellation reason
        
    Returns:
        bool indicating success
    """
    session = get_session()
    try:
        from models import Subscription
        
        sub = session.query(Subscription).filter(Subscription.id == subscription_id).first()
        
        if not sub:
            return False
        
        sub.status = 'CANCELLED'
        sub.cancelled_at = time.time()
        sub.cancellation_reason = reason
        
        session.commit()
        return True
    finally:
        session.close()


def renew_subscription(subscription_id):
    """Renew a subscription for next period.
    
    Args:
        subscription_id: Subscription ID to renew
        
    Returns:
        dict with updated subscription data
    """
    session = get_session()
    try:
        from models import Subscription
        
        sub = session.query(Subscription).filter(Subscription.id == subscription_id).first()
        
        if not sub:
            raise ValueError("Subscription not found")
        
        # Calculate new period
        period_length = 30 * 86400 if sub.billing_cycle == 'monthly' else 365 * 86400
        
        sub.current_period_start = sub.current_period_end
        sub.current_period_end = sub.current_period_end + period_length
        
        session.commit()
        
        return {
            'id': sub.id,
            'new_period_start': datetime.fromtimestamp(sub.current_period_start).strftime('%Y-%m-%d'),
            'new_period_end': datetime.fromtimestamp(sub.current_period_end).strftime('%Y-%m-%d')
        }
    finally:
        session.close()


def get_subscription_revenue_forecast(months_ahead=12):
    """Forecast subscription revenue.
    
    Args:
        months_ahead: Number of months to forecast
        
    Returns:
        dict with forecast data
    """
    mrr = calculate_mrr()
    
    # Assume 5% monthly growth (conservative)
    growth_rate = 0.05
    
    forecast = []
    current_mrr = mrr['mrr_paise']
    
    for month in range(1, months_ahead + 1):
        projected_mrr = current_mrr * ((1 + growth_rate) ** month)
        forecast.append({
            'month': month,
            'projected_mrr_rupees': round(projected_mrr / 100, 2),
            'projected_arr_rupees': round((projected_mrr * 12) / 100, 2)
        })
    
    return {
        'current_mrr_rupees': mrr['mrr_rupees'],
        'forecast': forecast,
        'total_projected_revenue_12m_rupees': sum(f['projected_mrr_rupees'] for f in forecast)
    }


def get_tier_upgrade_opportunities():
    """Identify customers who should upgrade tiers.
    
    Returns:
        list of upgrade opportunities
    """
    session = get_session()
    try:
        from models import Subscription
        
        # Get starter subscribers who have been active for 30+ days
        cutoff = time.time() - (30 * 86400)
        
        starters = session.query(Subscription).filter(
            and_(
                Subscription.tier == 'STARTER',
                Subscription.status.in_(['ACTIVE', 'TRIAL']),
                Subscription.created_at <= cutoff
            )
        ).all()
        
        opportunities = []
        
        for sub in starters:
            days_active = int((time.time() - sub.created_at) / 86400)
            
            # Calculate potential revenue increase
            current_monthly = SUBSCRIPTION_PRICING['STARTER']['monthly']
            pro_monthly = SUBSCRIPTION_PRICING['PRO']['monthly']
            uplift = pro_monthly - current_monthly
            
            opportunities.append({
                'receipt': sub.receipt,
                'current_tier': 'STARTER',
                'suggested_tier': 'PRO',
                'days_active': days_active,
                'current_monthly': current_monthly / 100,
                'suggested_monthly': pro_monthly / 100,
                'revenue_uplift': uplift / 100,
                'annual_uplift': (uplift * 12) / 100
            })
        
        return opportunities
    finally:
        session.close()
