"""
AI-POWERED CUSTOMER SUCCESS ENGINE
==================================
Predictive customer success platform with health scoring,
automated playbooks, and intervention strategies.

Features:
- Customer health scoring
- Churn risk prediction
- Automated success playbooks
- Proactive intervention triggers
- Success metrics tracking
- Customer journey optimization
"""

import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from models import get_session, Customer, Order, Subscription
from sqlalchemy import func, and_

logger = logging.getLogger(__name__)


@dataclass
class HealthScore:
    """Customer health score."""
    customer_id: str
    overall_score: float  # 0-100
    engagement_score: float
    product_adoption_score: float
    satisfaction_score: float
    growth_potential_score: float
    churn_risk: str  # 'low', 'medium', 'high', 'critical'
    status: str  # 'thriving', 'healthy', 'at-risk', 'churning'
    calculated_at: float


@dataclass
class SuccessPlaybook:
    """Automated success playbook."""
    playbook_id: str
    name: str
    trigger_conditions: List[str]
    actions: List[Dict]
    priority: str  # 'low', 'medium', 'high', 'urgent'
    automated: bool


@dataclass
class Intervention:
    """Customer intervention."""
    customer_id: str
    intervention_type: str
    reason: str
    urgency: str
    recommended_actions: List[str]
    assigned_to: Optional[str]
    created_at: float
    completed_at: Optional[float]


class CustomerSuccessEngine:
    """AI-powered customer success platform."""
    
    def __init__(self):
        self.session = get_session()
        self.playbooks = self._load_playbooks()
    
    def calculate_health_score(self, customer_id: str) -> HealthScore:
        """Calculate comprehensive customer health score."""
        # Get customer data
        customer = self.session.query(Customer).filter_by(receipt=customer_id).first()
        
        if not customer:
            return self._default_health_score(customer_id)
        
        # Calculate component scores
        engagement = self._calculate_engagement_score(customer)
        adoption = self._calculate_adoption_score(customer)
        satisfaction = self._calculate_satisfaction_score(customer)
        growth = self._calculate_growth_potential(customer)
        
        # Weighted overall score
        overall = (
            engagement * 0.30 +
            adoption * 0.25 +
            satisfaction * 0.25 +
            growth * 0.20
        )
        
        # Determine churn risk
        churn_risk = self._determine_churn_risk(overall, engagement)
        
        # Determine status
        if overall >= 80:
            status = 'thriving'
        elif overall >= 60:
            status = 'healthy'
        elif overall >= 40:
            status = 'at-risk'
        else:
            status = 'churning'
        
        return HealthScore(
            customer_id=customer_id,
            overall_score=overall,
            engagement_score=engagement,
            product_adoption_score=adoption,
            satisfaction_score=satisfaction,
            growth_potential_score=growth,
            churn_risk=churn_risk,
            status=status,
            calculated_at=time.time()
        )
    
    def _calculate_engagement_score(self, customer: Customer) -> float:
        """Calculate engagement score (0-100)."""
        score = 50.0  # Base score
        
        # Recent activity
        days_since_last = self._days_since_last_purchase(customer.receipt)
        
        if days_since_last <= 7:
            score += 30
        elif days_since_last <= 30:
            score += 20
        elif days_since_last <= 90:
            score += 10
        else:
            score -= 20  # Inactive
        
        # Order frequency
        order_count = customer.order_count or 0
        if order_count >= 10:
            score += 20
        elif order_count >= 5:
            score += 15
        elif order_count >= 2:
            score += 10
        
        return min(100, max(0, score))
    
    def _calculate_adoption_score(self, customer: Customer) -> float:
        """Calculate product adoption score (0-100)."""
        score = 50.0
        
        # Check subscription status
        active_sub = self.session.query(Subscription).filter_by(
            receipt=customer.receipt,
            status='ACTIVE'
        ).first()
        
        if active_sub:
            score += 30
            
            # Tier bonus
            if active_sub.tier == 'PREMIUM':
                score += 20
            elif active_sub.tier == 'PRO':
                score += 10
        
        # Product diversity (multiple product purchases)
        distinct_products = self.session.query(func.count(func.distinct(Order.product))).filter(
            and_(Order.receipt == customer.receipt, Order.status == 'paid')
        ).scalar() or 0
        
        if distinct_products >= 3:
            score += 20
        elif distinct_products >= 2:
            score += 10
        
        return min(100, max(0, score))
    
    def _calculate_satisfaction_score(self, customer: Customer) -> float:
        """Calculate satisfaction score (0-100)."""
        # Proxy metrics (in real system would use NPS, CSAT, support tickets)
        score = 70.0  # Assume neutral satisfaction
        
        # No failed orders = positive
        failed_orders = self.session.query(func.count(Order.id)).filter(
            and_(Order.receipt == customer.receipt, Order.status == 'created')
        ).scalar() or 0
        
        if failed_orders == 0:
            score += 20
        elif failed_orders <= 2:
            score += 10
        else:
            score -= 20
        
        # LTV as proxy for satisfaction
        ltv = customer.ltv_paise or 0
        if ltv > 100000:  # > ₹1000
            score += 10
        
        return min(100, max(0, score))
    
    def _calculate_growth_potential(self, customer: Customer) -> float:
        """Calculate growth potential score (0-100)."""
        score = 50.0
        
        # Current tier determines upside
        active_sub = self.session.query(Subscription).filter_by(
            receipt=customer.receipt,
            status='ACTIVE'
        ).first()
        
        if not active_sub:
            score += 30  # Not subscribed = high potential
        else:
            if active_sub.tier == 'STARTER':
                score += 25  # Room to grow
            elif active_sub.tier == 'PRO':
                score += 15
            else:  # PREMIUM
                score += 5  # Already at top
        
        # Revenue trend
        ltv = customer.ltv_paise or 0
        order_count = customer.order_count or 1
        avg_order = ltv / order_count
        
        if avg_order > 50000:  # > ₹500 avg
            score += 20
        elif avg_order > 20000:
            score += 10
        
        return min(100, max(0, score))
    
    def _determine_churn_risk(self, overall_score: float, engagement_score: float) -> str:
        """Determine churn risk level."""
        if overall_score < 40 or engagement_score < 30:
            return 'critical'
        elif overall_score < 55 or engagement_score < 50:
            return 'high'
        elif overall_score < 70:
            return 'medium'
        else:
            return 'low'
    
    def _default_health_score(self, customer_id: str) -> HealthScore:
        """Return default health score for new/unknown customer."""
        return HealthScore(
            customer_id=customer_id,
            overall_score=50,
            engagement_score=50,
            product_adoption_score=50,
            satisfaction_score=50,
            growth_potential_score=50,
            churn_risk='medium',
            status='healthy',
            calculated_at=time.time()
        )
    
    def _days_since_last_purchase(self, customer_id: str) -> int:
        """Days since last purchase."""
        last_order = self.session.query(Order).filter(
            and_(Order.receipt == customer_id, Order.status == 'paid')
        ).order_by(Order.paid_at.desc()).first()
        
        if last_order and last_order.paid_at:
            return int((time.time() - last_order.paid_at) / 86400)
        
        return 999  # Very long time
    
    def identify_at_risk_customers(self, limit: int = 50) -> List[HealthScore]:
        """Identify customers at risk of churn."""
        customers = self.session.query(Customer).limit(limit * 2).all()
        
        at_risk = []
        for customer in customers:
            health = self.calculate_health_score(customer.receipt)
            if health.churn_risk in ['high', 'critical']:
                at_risk.append(health)
        
        # Sort by score (lowest first)
        at_risk.sort(key=lambda x: x.overall_score)
        
        return at_risk[:limit]
    
    def recommend_interventions(self, customer_id: str) -> List[Intervention]:
        """Recommend interventions for customer."""
        health = self.calculate_health_score(customer_id)
        interventions = []
        
        # Check each playbook
        for playbook in self.playbooks:
            if self._should_trigger_playbook(health, playbook):
                intervention = self._create_intervention(health, playbook)
                interventions.append(intervention)
        
        # Sort by urgency
        urgency_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
        interventions.sort(key=lambda x: urgency_order.get(x.urgency, 99))
        
        return interventions
    
    def _load_playbooks(self) -> List[SuccessPlaybook]:
        """Load success playbooks."""
        return [
            SuccessPlaybook(
                playbook_id='pb_churn_critical',
                name='Critical Churn Prevention',
                trigger_conditions=['churn_risk:critical', 'overall_score:<40'],
                actions=[
                    {'type': 'email', 'template': 'save_offer', 'discount': 30},
                    {'type': 'call', 'priority': 'urgent'},
                    {'type': 'survey', 'ask_why': True}
                ],
                priority='urgent',
                automated=True
            ),
            SuccessPlaybook(
                playbook_id='pb_engagement_low',
                name='Re-engagement Campaign',
                trigger_conditions=['engagement_score:<50', 'days_inactive:>30'],
                actions=[
                    {'type': 'email', 'template': 'comeback_offer'},
                    {'type': 'product_tips', 'personalized': True},
                    {'type': 'check_in', 'schedule_in': 7}
                ],
                priority='high',
                automated=True
            ),
            SuccessPlaybook(
                playbook_id='pb_upsell_ready',
                name='Upsell to Higher Tier',
                trigger_conditions=['overall_score:>70', 'tier:STARTER|PRO'],
                actions=[
                    {'type': 'email', 'template': 'upgrade_offer'},
                    {'type': 'demo', 'feature': 'premium_features'},
                    {'type': 'trial', 'duration_days': 14}
                ],
                priority='medium',
                automated=False
            ),
            SuccessPlaybook(
                playbook_id='pb_advocate',
                name='Convert to Advocate',
                trigger_conditions=['overall_score:>85', 'satisfaction:>80'],
                actions=[
                    {'type': 'referral_invite', 'bonus': 30},
                    {'type': 'case_study', 'request': True},
                    {'type': 'review', 'platform': 'g2'}
                ],
                priority='low',
                automated=True
            )
        ]
    
    def _should_trigger_playbook(self, health: HealthScore, playbook: SuccessPlaybook) -> bool:
        """Check if playbook should be triggered."""
        for condition in playbook.trigger_conditions:
            if ':' in condition:
                metric, value = condition.split(':', 1)
                
                if metric == 'churn_risk':
                    if health.churn_risk != value:
                        return False
                
                elif metric == 'overall_score':
                    if value.startswith('<'):
                        threshold = float(value[1:])
                        if health.overall_score >= threshold:
                            return False
                    elif value.startswith('>'):
                        threshold = float(value[1:])
                        if health.overall_score <= threshold:
                            return False
                
                elif metric == 'engagement_score':
                    if value.startswith('<'):
                        threshold = float(value[1:])
                        if health.engagement_score >= threshold:
                            return False
                
                elif metric == 'tier':
                    # Check subscription tier
                    active_sub = self.session.query(Subscription).filter_by(
                        receipt=health.customer_id,
                        status='ACTIVE'
                    ).first()
                    
                    if active_sub:
                        allowed_tiers = value.split('|')
                        if active_sub.tier not in allowed_tiers:
                            return False
        
        return True
    
    def _create_intervention(self, health: HealthScore, playbook: SuccessPlaybook) -> Intervention:
        """Create intervention from playbook."""
        # Determine urgency from playbook priority and health status
        if playbook.priority == 'urgent' or health.churn_risk == 'critical':
            urgency = 'urgent'
        elif playbook.priority == 'high' or health.churn_risk == 'high':
            urgency = 'high'
        else:
            urgency = playbook.priority
        
        # Extract action descriptions
        actions = [
            f"{action['type']}: {action.get('template', action.get('feature', 'execute'))}"
            for action in playbook.actions
        ]
        
        return Intervention(
            customer_id=health.customer_id,
            intervention_type=playbook.playbook_id,
            reason=f"Health score: {health.overall_score:.1f}, Status: {health.status}",
            urgency=urgency,
            recommended_actions=actions,
            assigned_to=None,
            created_at=time.time(),
            completed_at=None
        )
    
    def get_success_metrics(self) -> Dict:
        """Get customer success metrics."""
        try:
            # Sample customers for analysis
            customers = self.session.query(Customer).limit(100).all()
            
            if not customers:
                return self._empty_metrics()
            
            health_scores = [self.calculate_health_score(c.receipt) for c in customers]
            
            # Calculate aggregates
            avg_health = sum(h.overall_score for h in health_scores) / len(health_scores)
            
            status_counts = {
                'thriving': len([h for h in health_scores if h.status == 'thriving']),
                'healthy': len([h for h in health_scores if h.status == 'healthy']),
                'at-risk': len([h for h in health_scores if h.status == 'at-risk']),
                'churning': len([h for h in health_scores if h.status == 'churning'])
            }
            
            risk_counts = {
                'low': len([h for h in health_scores if h.churn_risk == 'low']),
                'medium': len([h for h in health_scores if h.churn_risk == 'medium']),
                'high': len([h for h in health_scores if h.churn_risk == 'high']),
                'critical': len([h for h in health_scores if h.churn_risk == 'critical'])
            }
            
            return {
                'average_health_score': avg_health,
                'status_distribution': status_counts,
                'risk_distribution': risk_counts,
                'customers_analyzed': len(customers),
                'interventions_needed': status_counts['at-risk'] + status_counts['churning']
            }
            
        except Exception as e:
            logger.error(f"Failed to get success metrics: {e}")
            return self._empty_metrics()
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure."""
        return {
            'average_health_score': 0,
            'status_distribution': {'thriving': 0, 'healthy': 0, 'at-risk': 0, 'churning': 0},
            'risk_distribution': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
            'customers_analyzed': 0,
            'interventions_needed': 0
        }


# ---------------------------------------------------------------------------
# API Functions
# ---------------------------------------------------------------------------

def get_customer_health(customer_id: str) -> Dict:
    """Get customer health score."""
    engine = CustomerSuccessEngine()
    health = engine.calculate_health_score(customer_id)
    
    return {
        'customer_id': health.customer_id,
        'overall_score': health.overall_score,
        'engagement': health.engagement_score,
        'adoption': health.product_adoption_score,
        'satisfaction': health.satisfaction_score,
        'growth_potential': health.growth_potential_score,
        'churn_risk': health.churn_risk,
        'status': health.status,
        'calculated_at': health.calculated_at
    }


def get_at_risk_customers(limit: int = 50) -> Dict:
    """Get customers at risk of churn."""
    engine = CustomerSuccessEngine()
    at_risk = engine.identify_at_risk_customers(limit)
    
    return {
        'at_risk_customers': [
            {
                'customer_id': h.customer_id,
                'health_score': h.overall_score,
                'churn_risk': h.churn_risk,
                'status': h.status
            }
            for h in at_risk
        ],
        'total': len(at_risk)
    }


def get_recommended_interventions(customer_id: str) -> Dict:
    """Get recommended interventions for customer."""
    engine = CustomerSuccessEngine()
    interventions = engine.recommend_interventions(customer_id)
    
    return {
        'customer_id': customer_id,
        'interventions': [
            {
                'type': i.intervention_type,
                'reason': i.reason,
                'urgency': i.urgency,
                'actions': i.recommended_actions
            }
            for i in interventions
        ],
        'count': len(interventions)
    }


def get_customer_success_dashboard() -> Dict:
    """Get customer success dashboard metrics."""
    engine = CustomerSuccessEngine()
    return engine.get_success_metrics()
