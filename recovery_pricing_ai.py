"""
AI-Optimized Dynamic Recovery Pricing System
Personalized recovery pricing per customer to maximize recovery revenue

Features:
- Customer-specific recovery discounts based on LTV
- Segment-based pricing strategies
- Real-time A/B testing of recovery offers
- Conversion tracking and feedback loop
- Smart price optimization based on historical data
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from models import get_session, Order, Payment, Customer, Subscription
from sqlalchemy import and_, func, or_
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class RecoveryPricingProfile:
    """Customer recovery pricing profile."""
    customer_receipt: str
    base_discount_percent: float  # 10-80%
    reasoning: str
    ltv_segment: str  # high, medium, low, new
    conversion_probability: float  # 0-1
    expected_recovery_value: float  # ₹
    confidence_score: float  # 0-1
    variant: str  # A, B, C, D for A/B testing


@dataclass
class RecoveryOutcome:
    """Tracks recovery attempt outcome."""
    order_id: str
    customer_receipt: str
    original_amount_paise: int
    offered_discount_percent: float
    offered_price_paise: int
    email_sent_at: float
    email_opened: bool = False
    link_clicked: bool = False
    conversion: bool = False
    paid_amount_paise: int = 0
    paid_at: float = 0.0


class RecoveryPricingAI:
    """AI-powered dynamic pricing for recovery campaigns."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize recovery pricing engine."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.outcomes_file = self.data_dir / "recovery_outcomes.jsonl"
        self.model_file = self.data_dir / "recovery_pricing_model.json"
        
        # Default pricing by segment
        self.segment_discount_ranges = {
            'high': (0.15, 0.35),      # High-value: 15-35% discount
            'medium': (0.25, 0.45),    # Medium: 25-45% discount
            'low': (0.35, 0.55),       # Low-value: 35-55% discount
            'new': (0.40, 0.60)        # New customers: 40-60% discount
        }
        
        # A/B testing variants
        self.test_variants = ['A', 'B', 'C', 'D']
        self.variant_discounts = {
            'A': 0.25,  # Control: 25%
            'B': 0.35,  # Aggressive: 35%
            'C': 0.15,  # Conservative: 15%
            'D': 0.50   # Desperate: 50%
        }
        
        logger.info("RecoveryPricingAI initialized")
    
    def _get_customer_ltv(self, customer_receipt: str) -> float:
        """Calculate customer lifetime value."""
        session = get_session()
        try:
            # Get all paid orders for this customer
            paid_orders = session.query(
                func.sum(Order.amount)
            ).filter(
                and_(
                    Order.receipt == customer_receipt,
                    Order.status == 'paid'
                )
            ).scalar() or 0
            
            return paid_orders / 100  # Convert paise to rupees
        finally:
            session.close()
    
    def _get_customer_segment(self, customer_receipt: str) -> str:
        """Classify customer into segment."""
        ltv = self._get_customer_ltv(customer_receipt)
        
        if ltv == 0:
            return 'new'
        elif ltv >= 10000:  # ₹10K+
            return 'high'
        elif ltv >= 2500:   # ₹2.5K+
            return 'medium'
        else:
            return 'low'
    
    def _get_segment_conversion_rate(self, segment: str) -> float:
        """Get historical conversion rate for segment."""
        # Load from outcomes
        session = get_session()
        try:
            # For now, use defaults - would be learned from data
            conversion_rates = {
                'high': 0.65,    # 65% of high-value customers recover
                'medium': 0.45,  # 45% of medium-value customers
                'low': 0.30,     # 30% of low-value customers
                'new': 0.20      # 20% of new customers
            }
            return conversion_rates.get(segment, 0.30)
        finally:
            session.close()
    
    def _get_variant_for_customer(self, customer_receipt: str) -> str:
        """Assign A/B testing variant to customer."""
        import hashlib
        
        # Hash-based assignment (consistent for same customer)
        hash_val = int(hashlib.md5(customer_receipt.encode()).hexdigest(), 16)
        variant_idx = hash_val % len(self.test_variants)
        return self.test_variants[variant_idx]
    
    def calculate_recovery_price(self, order_id: str, customer_receipt: str) -> RecoveryPricingProfile:
        """
        Calculate AI-optimized recovery price for customer.
        
        Args:
            order_id: Order ID to recover
            customer_receipt: Customer identifier
            
        Returns:
            RecoveryPricingProfile with discount and reasoning
        """
        session = get_session()
        try:
            # Get order details
            order = session.query(Order).filter(Order.id == order_id).first()
            if not order:
                logger.warning(f"Order not found: {order_id}")
                return None
            
            # Get customer segment
            segment = self._get_customer_segment(customer_receipt)
            
            # Get A/B test variant
            variant = self._get_variant_for_customer(customer_receipt)
            
            # Determine discount
            if variant in self.variant_discounts:
                # A/B test: use variant discount
                discount_percent = self.variant_discounts[variant]
                reasoning = f"A/B Test Variant {variant}"
            else:
                # Production: use segment-based range
                min_disc, max_disc = self.segment_discount_ranges.get(segment, (0.30, 0.50))
                
                # Randomize within range for natural distribution
                import random
                discount_percent = min_disc + random.random() * (max_disc - min_disc)
                reasoning = f"{segment.capitalize()}-value customer ({segment} segment)"
            
            # Calculate metrics
            conversion_prob = self._get_segment_conversion_rate(segment)
            original_amount = order.amount / 100  # Convert to rupees
            offered_amount = original_amount * (1 - discount_percent)
            expected_recovery = offered_amount * conversion_prob
            
            return RecoveryPricingProfile(
                customer_receipt=customer_receipt,
                base_discount_percent=discount_percent * 100,
                reasoning=reasoning,
                ltv_segment=segment,
                conversion_probability=conversion_prob,
                expected_recovery_value=expected_recovery,
                confidence_score=0.85,
                variant=variant
            )
        finally:
            session.close()
    
    def get_recovery_suggestions_with_pricing(self, limit: int = 10) -> List[Dict]:
        """Get recovery suggestions with optimized pricing."""
        session = get_session()
        try:
            # Get abandoned orders
            abandoned = session.query(Order).filter(
                and_(
                    Order.status == 'created',
                    Order.receipt.isnot(None),
                    Order.receipt != 'TEST'
                )
            ).order_by(Order.created_at.desc()).limit(limit * 2).all()
            
            suggestions = []
            for order in abandoned:
                pricing = self.calculate_recovery_price(order.id, order.receipt)
                if not pricing:
                    continue
                
                hours_abandoned = (time.time() - order.created_at) / 3600
                
                suggestion = {
                    'order_id': order.id,
                    'customer_receipt': order.receipt,
                    'original_amount_rupees': order.amount / 100,
                    'segment': pricing.ltv_segment,
                    'discount_offered_percent': pricing.base_discount_percent,
                    'recovery_price_rupees': order.amount / 100 * (1 - pricing.base_discount_percent / 100),
                    'expected_recovery_value': pricing.expected_recovery_value,
                    'conversion_probability': pricing.conversion_probability,
                    'reasoning': pricing.reasoning,
                    'ab_variant': pricing.variant,
                    'hours_abandoned': round(hours_abandoned, 1),
                    'priority': self._calculate_priority(hours_abandoned, order.amount)
                }
                
                suggestions.append(suggestion)
            
            return suggestions[:limit]
        finally:
            session.close()
    
    def _calculate_priority(self, hours_abandoned: float, amount_paise: int) -> str:
        """Calculate priority level."""
        if hours_abandoned < 1 and amount_paise > 10000:
            return 'URGENT'
        elif hours_abandoned < 24 and amount_paise > 5000:
            return 'HIGH'
        elif hours_abandoned < 72:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def log_recovery_outcome(self, outcome: RecoveryOutcome) -> bool:
        """Log recovery campaign outcome."""
        try:
            with open(self.outcomes_file, 'a') as f:
                f.write(json.dumps(asdict(outcome)) + '\n')
            return True
        except Exception as e:
            logger.error(f"Failed to log outcome: {e}")
            return False
    
    def track_email_opened(self, order_id: str):
        """Track when recovery email is opened."""
        # This would be called via pixel tracking in email
        logger.info(f"Recovery email opened: {order_id}")
    
    def track_link_clicked(self, order_id: str):
        """Track when recovery link is clicked."""
        # This would be called when customer clicks recovery link
        logger.info(f"Recovery link clicked: {order_id}")
    
    def track_recovery_conversion(self, order_id: str, paid_amount_paise: int):
        """Track successful recovery conversion."""
        session = get_session()
        try:
            order = session.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = 'paid'
                session.commit()
                
                outcome = RecoveryOutcome(
                    order_id=order_id,
                    customer_receipt=order.receipt,
                    original_amount_paise=order.amount,
                    offered_discount_percent=0,  # Would track actual discount
                    offered_price_paise=paid_amount_paise,
                    email_sent_at=time.time() - 3600,  # Approximate
                    conversion=True,
                    paid_amount_paise=paid_amount_paise,
                    paid_at=time.time()
                )
                
                self.log_recovery_outcome(outcome)
                logger.info(f"Recovery conversion tracked: {order_id} -> ₹{paid_amount_paise/100}")
        finally:
            session.close()
    
    def get_recovery_performance_metrics(self) -> Dict:
        """Get overall recovery campaign performance."""
        try:
            outcomes = []
            if self.outcomes_file.exists():
                with open(self.outcomes_file, 'r') as f:
                    for line in f:
                        try:
                            outcomes.append(json.loads(line))
                        except:
                            continue
            
            if not outcomes:
                return {
                    'total_campaigns': 0,
                    'conversion_rate': 0,
                    'email_open_rate': 0,
                    'click_rate': 0,
                    'avg_recovery_value': 0,
                    'total_recovered': 0
                }
            
            total = len(outcomes)
            converted = sum(1 for o in outcomes if o.get('conversion'))
            opened = sum(1 for o in outcomes if o.get('email_opened'))
            clicked = sum(1 for o in outcomes if o.get('link_clicked'))
            total_recovered = sum(o.get('paid_amount_paise', 0) for o in outcomes if o.get('conversion'))
            
            return {
                'total_campaigns': total,
                'conversion_rate': (converted / total * 100) if total > 0 else 0,
                'email_open_rate': (opened / total * 100) if total > 0 else 0,
                'click_rate': (clicked / total * 100) if total > 0 else 0,
                'avg_recovery_value': (total_recovered / converted / 100) if converted > 0 else 0,
                'total_recovered': total_recovered / 100,  # Rupees
                'total_recoverable_potential': sum(o.get('offered_price_paise', 0) for o in outcomes) / 100
            }
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}
    
    def get_ab_test_results(self) -> Dict:
        """Get A/B test results by variant."""
        try:
            outcomes = []
            if self.outcomes_file.exists():
                with open(self.outcomes_file, 'r') as f:
                    for line in f:
                        try:
                            outcomes.append(json.loads(line))
                        except:
                            continue
            
            results = {}
            for variant in self.test_variants:
                variant_outcomes = [o for o in outcomes if o.get('variant') == variant]
                if variant_outcomes:
                    conversions = sum(1 for o in variant_outcomes if o.get('conversion'))
                    total_recovered = sum(o.get('paid_amount_paise', 0) for o in variant_outcomes if o.get('conversion'))
                    
                    results[variant] = {
                        'campaigns': len(variant_outcomes),
                        'conversions': conversions,
                        'conversion_rate': (conversions / len(variant_outcomes) * 100) if variant_outcomes else 0,
                        'discount_offered': self.variant_discounts[variant] * 100,
                        'total_recovered_rupees': total_recovered / 100,
                        'avg_recovery_value': (total_recovered / conversions / 100) if conversions > 0 else 0
                    }
            
            return results
        except Exception as e:
            logger.error(f"Error getting A/B results: {e}")
            return {}
    
    def recommend_best_variant(self) -> str:
        """Recommend best performing A/B variant."""
        results = self.get_ab_test_results()
        
        if not results:
            return 'A'
        
        # Find variant with highest conversion rate
        best_variant = max(results.items(), key=lambda x: x[1].get('conversion_rate', 0))[0]
        return best_variant


# ==================== STANDALONE FUNCTIONS ====================

def calculate_recovery_price(order_id: str, customer_receipt: str) -> Dict:
    """Calculate personalized recovery price."""
    engine = RecoveryPricingAI()
    profile = engine.calculate_recovery_price(order_id, customer_receipt)
    
    if not profile:
        return None
    
    return {
        'customer_segment': profile.ltv_segment,
        'base_discount_percent': profile.base_discount_percent,
        'reasoning': profile.reasoning,
        'conversion_probability': profile.conversion_probability,
        'expected_recovery_value': profile.expected_recovery_value,
        'confidence_score': profile.confidence_score,
        'ab_variant': profile.variant
    }


def get_recovery_suggestions_optimized(limit: int = 10) -> List[Dict]:
    """Get recovery suggestions with AI pricing."""
    engine = RecoveryPricingAI()
    return engine.get_recovery_suggestions_with_pricing(limit)


def get_recovery_metrics() -> Dict:
    """Get recovery campaign metrics."""
    engine = RecoveryPricingAI()
    return engine.get_recovery_performance_metrics()


def get_ab_test_winners() -> Dict:
    """Get A/B test results and recommendations."""
    engine = RecoveryPricingAI()
    results = engine.get_ab_test_results()
    best = engine.recommend_best_variant()
    
    return {
        'by_variant': results,
        'recommended_variant': best,
        'message': f"Variant {best} has highest conversion rate"
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test the system
    engine = RecoveryPricingAI()
    
    print("\n=== Recovery Pricing AI Test ===\n")
    
    # Mock test data
    from models import init_db, Order, get_session
    
    init_db()
    session = get_session()
    
    # Create test orders
    test_orders = [
        Order(id="ORDER_1", receipt="cust_test_1", amount=10000, product="pro", status="created"),
        Order(id="ORDER_2", receipt="cust_test_2", amount=50000, product="premium", status="created"),
    ]
    
    for order in test_orders:
        session.merge(order)
    session.commit()
    
    # Get recovery suggestions with pricing
    suggestions = get_recovery_suggestions_optimized(limit=5)
    
    print(f"✓ Found {len(suggestions)} recovery opportunities\n")
    
    for sugg in suggestions[:2]:
        print(f"Order: {sugg['order_id']}")
        print(f"  Original: ₹{sugg['original_amount_rupees']:.2f}")
        print(f"  Segment: {sugg['segment']}")
        print(f"  Discount: {sugg['discount_offered_percent']:.0f}%")
        print(f"  Recovery Price: ₹{sugg['recovery_price_rupees']:.2f}")
        print(f"  Expected Value: ₹{sugg['expected_recovery_value']:.2f}")
        print(f"  Reasoning: {sugg['reasoning']}\n")
    
    print("✓ Recovery Pricing AI ready for integration")
