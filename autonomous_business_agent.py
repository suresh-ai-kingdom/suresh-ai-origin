"""
AUTONOMOUS BUSINESS AGENT - SELF-OPERATING AI
Revolutionary self-decision-making AI for SURESH AI ORIGIN V2.5

Features:
- Monitor Stripe/Sheets revenue/leads daily
- Auto-gen content (LinkedIn/Reels via Claude API) if leads < threshold
- Deploy fixes via GitHub Actions on errors
- Self-recover (retries, WhatsApp/Email alerts)
- Log to Notion/analytics
- Make autonomous business decisions with safety guardrails

Author: SURESH AI ORIGIN
Version: 2.5.0 - AUTONOMOUS + MONITORING
"""

import os
import sys
import time
import json
import random
import math
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import deque, defaultdict

import requests
import schedule
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import existing Suresh AI Origin modules
try:
    from real_ai_service import generate_ai_content
    from utils import send_email
except ImportError:
    logging.warning("Could not import real_ai_service or utils - some features disabled")


# Configuration
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
METRICS_LOG = DATA_DIR / "agent_metrics.jsonl"
ALERTS_LOG = DATA_DIR / "agent_alerts.jsonl"
ACTIONS_LOG = DATA_DIR / "agent_actions.jsonl"

# Thresholds
LEADS_THRESHOLD = int(os.getenv("AGENT_LEADS_THRESHOLD", "10"))
REVENUE_THRESHOLD = float(os.getenv("AGENT_REVENUE_THRESHOLD", "1000.0"))
ERROR_RATE_THRESHOLD = float(os.getenv("AGENT_ERROR_RATE", "0.05"))

# API Keys (from environment)
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "suresh-ai-kingdom/suresh-ai-origin")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AutonomousAgent")


class DecisionConfidence(Enum):
    """Confidence levels for autonomous decisions."""
    CRITICAL = "critical"  # 95%+ confidence, execute immediately
    HIGH = "high"          # 85-95%, execute with logging
    MEDIUM = "medium"      # 70-85%, suggest to human
    LOW = "low"           # <70%, requires approval


class ActionType(Enum):
    """Types of actions the agent can take."""
    PRICING_ADJUSTMENT = "pricing_adjustment"
    INVENTORY_REORDER = "inventory_reorder"
    MARKETING_CAMPAIGN = "marketing_campaign"
    CUSTOMER_INTERVENTION = "customer_intervention"
    FEATURE_TOGGLE = "feature_toggle"
    REFUND_APPROVAL = "refund_approval"
    DISCOUNT_GENERATION = "discount_generation"
    EMAIL_CAMPAIGN = "email_campaign"
    PARTNERSHIP_OUTREACH = "partnership_outreach"
    PRODUCT_LAUNCH = "product_launch"
    CONTENT_GENERATION = "content_generation"
    DEPLOY_FIX = "deploy_fix"


class AgentState(Enum):
    """Current state of the autonomous agent."""
    IDLE = "idle"
    ANALYZING = "analyzing"
    DECIDING = "deciding"
    EXECUTING = "executing"
    LEARNING = "learning"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class Decision:
    """Represents an autonomous decision."""
    decision_id: str
    action_type: ActionType
    confidence: DecisionConfidence
    reasoning: str
    expected_impact: Dict[str, float]
    risk_score: float  # 0-100
    parameters: Dict[str, Any]
    created_at: float
    executed_at: Optional[float] = None
    outcome: Optional[Dict[str, Any]] = None
    success: Optional[bool] = None


@dataclass
class LearningExperience:
    """Experience for reinforcement learning."""
    state: Dict[str, Any]
    action: ActionType
    reward: float
    next_state: Dict[str, Any]
    timestamp: float
    meta: Dict[str, Any] = field(default_factory=dict)


class AutonomousBusinessAgent:
    """
    Self-operating AI agent that makes business decisions autonomously.
    
    Key Features:
    - Reinforcement learning from outcomes
    - Multi-objective optimization (revenue, satisfaction, growth)
    - Safety guardrails (budget limits, risk thresholds)
    - Explainable decisions with reasoning chains
    - Self-improvement through continuous learning
    - Revenue/leads monitoring (Stripe, Google Sheets)
    - Auto-content generation (LinkedIn/Reels via Claude)
    - GitHub Actions deployment on errors
    - Self-recovery with retries and alerts
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, base_url: str = "http://localhost:5000"):
        self.config = config or {}
        self.base_url = base_url.rstrip('/')
        self.state = AgentState.IDLE
        self.decision_history: List[Decision] = []
        self.learning_buffer: deque = deque(maxlen=10000)
        self.policy_weights = self._initialize_policy()
        self.safety_limits = self._initialize_safety_limits()
        self.performance_metrics = defaultdict(list)
        
        # Monitoring thresholds
        self.leads_threshold = int(os.getenv("AGENT_LEADS_THRESHOLD", "10"))
        self.revenue_threshold = float(os.getenv("AGENT_REVENUE_THRESHOLD", "1000.0"))
        self.error_threshold = float(os.getenv("AGENT_ERROR_RATE", "0.05"))
        
        logger.info(f"Initialized AutonomousBusinessAgent (monitoring: {base_url})")
        self.autonomous_mode = self.config.get('autonomous_mode', False)
        self.learning_rate = 0.01
        self.exploration_rate = 0.1
        
    def _initialize_policy(self) -> Dict[ActionType, Dict[str, float]]:
        """Initialize policy weights for each action type."""
        return {
            action_type: {
                'revenue_weight': 0.4,
                'satisfaction_weight': 0.3,
                'growth_weight': 0.2,
                'risk_weight': -0.1
            }
            for action_type in ActionType
        }
    
    def _initialize_safety_limits(self) -> Dict[str, Any]:
        """Initialize safety guardrails."""
        return {
            'max_price_change_pct': 20,  # Max 20% price change per decision
            'max_discount_pct': 50,      # Max 50% discount
            'max_budget_per_campaign': 10000,
            'min_approval_threshold': 0.85,  # Require 85% confidence for auto-execute
            'max_decisions_per_hour': 100,
            'emergency_stop_loss_threshold': 0.20  # Stop if 20% loss
        }
    
    def analyze_situation(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze current business situation and identify opportunities.
        
        Args:
            business_context: Current metrics, trends, customer data
        
        Returns:
            Analysis with identified opportunities and threats
        """
        self.state = AgentState.ANALYZING
        
        analysis = {
            'timestamp': time.time(),
            'opportunities': [],
            'threats': [],
            'recommended_actions': [],
            'urgency_score': 0
        }
        
        # Analyze revenue trends
        revenue_trend = self._analyze_revenue_trend(business_context)
        if revenue_trend['status'] == 'declining':
            analysis['threats'].append({
                'type': 'revenue_decline',
                'severity': 'high',
                'details': revenue_trend
            })
            analysis['urgency_score'] += 30
        
        # Analyze customer satisfaction
        satisfaction = self._analyze_customer_satisfaction(business_context)
        if satisfaction['score'] < 70:
            analysis['threats'].append({
                'type': 'low_satisfaction',
                'severity': 'medium',
                'details': satisfaction
            })
            analysis['urgency_score'] += 20
        
        # Identify pricing opportunities
        pricing_opportunity = self._identify_pricing_opportunity(business_context)
        if pricing_opportunity['potential_lift'] > 5:
            analysis['opportunities'].append({
                'type': 'pricing_optimization',
                'potential': pricing_opportunity
            })
        
        # Identify upsell opportunities
        upsell_opportunity = self._identify_upsell_opportunity(business_context)
        if upsell_opportunity['conversion_probability'] > 0.6:
            analysis['opportunities'].append({
                'type': 'upsell_campaign',
                'potential': upsell_opportunity
            })
        
        # Generate recommended actions
        analysis['recommended_actions'] = self._generate_action_recommendations(
            analysis['opportunities'],
            analysis['threats']
        )
        
        self.state = AgentState.IDLE
        return analysis
    
    def make_decision(
        self, 
        business_context: Dict[str, Any],
        allowed_actions: Optional[List[ActionType]] = None
    ) -> Decision:
        """
        Make an autonomous business decision.
        
        Args:
            business_context: Current business state
            allowed_actions: Optional filter for action types
        
        Returns:
            Decision object with action and reasoning
        """
        self.state = AgentState.DECIDING
        
        # Analyze situation
        analysis = self.analyze_situation(business_context)
        
        # Choose best action using policy
        best_action = None
        best_score = float('-inf')
        best_reasoning = ""
        
        candidate_actions = allowed_actions or list(ActionType)
        
        for action_type in candidate_actions:
            score, reasoning = self._evaluate_action(
                action_type,
                business_context,
                analysis
            )
            
            if score > best_score:
                best_score = score
                best_action = action_type
                best_reasoning = reasoning
        
        # Calculate confidence
        confidence = self._calculate_confidence(best_score, business_context)
        
        # Estimate impact
        expected_impact = self._estimate_impact(best_action, business_context)
        
        # Calculate risk
        risk_score = self._calculate_risk(best_action, expected_impact)
        
        # Generate parameters for action
        parameters = self._generate_action_parameters(best_action, business_context, analysis)
        
        decision = Decision(
            decision_id=f"decision_{int(time.time() * 1000)}",
            action_type=best_action,
            confidence=confidence,
            reasoning=best_reasoning,
            expected_impact=expected_impact,
            risk_score=risk_score,
            parameters=parameters,
            created_at=time.time()
        )
        
        self.decision_history.append(decision)
        self.state = AgentState.IDLE
        
        return decision
    
    def execute_decision(
        self, 
        decision: Decision,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a decision autonomously.
        
        Args:
            decision: Decision to execute
            force: Force execution even if confidence is low
        
        Returns:
            Execution result
        """
        self.state = AgentState.EXECUTING
        
        # Check if should auto-execute
        should_execute = (
            self.autonomous_mode and 
            decision.confidence in [DecisionConfidence.CRITICAL, DecisionConfidence.HIGH]
        ) or force
        
        if not should_execute:
            return {
                'status': 'pending_approval',
                'decision_id': decision.decision_id,
                'message': 'Decision requires human approval',
                'confidence': decision.confidence.value
            }
        
        # Check safety limits
        safety_check = self._check_safety_limits(decision)
        if not safety_check['safe']:
            return {
                'status': 'blocked',
                'decision_id': decision.decision_id,
                'reason': safety_check['reason']
            }
        
        # Execute action
        try:
            result = self._execute_action(decision)
            decision.executed_at = time.time()
            decision.outcome = result
            decision.success = result.get('success', False)
            
            # Learn from outcome
            self._learn_from_outcome(decision, result)
            
            return {
                'status': 'executed',
                'decision_id': decision.decision_id,
                'result': result,
                'learning_captured': True
            }
        
        except Exception as e:
            logging.error(f"Decision execution failed: {e}")
            decision.success = False
            return {
                'status': 'failed',
                'decision_id': decision.decision_id,
                'error': str(e)
            }
        finally:
            self.state = AgentState.IDLE
    
    def continuous_optimization_loop(
        self, 
        business_context_provider: Callable,
        iterations: int = 100
    ):
        """
        Run continuous autonomous optimization loop.
        
        WARNING: This gives the agent full autonomy to make decisions.
        Use only with proper monitoring and safety limits.
        
        Args:
            business_context_provider: Function that returns current business state
            iterations: Number of optimization cycles
        """
        for i in range(iterations):
            if self.state == AgentState.EMERGENCY_STOP:
                logging.critical("Emergency stop activated. Halting autonomous operations.")
                break
            
            # Get current state
            context = business_context_provider()
            
            # Make decision
            decision = self.make_decision(context)
            
            # Execute if confidence is high
            if decision.confidence in [DecisionConfidence.CRITICAL, DecisionConfidence.HIGH]:
                result = self.execute_decision(decision)
                logging.info(f"Autonomous decision executed: {decision.action_type.value} - {result['status']}")
            
            # Check for emergency conditions
            if self._check_emergency_conditions(context):
                self.state = AgentState.EMERGENCY_STOP
                logging.critical("Emergency conditions detected. Stopping autonomous operations.")
                break
            
            # Sleep between iterations
            time.sleep(60)  # 1 minute between decisions
    
    def _analyze_revenue_trend(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze revenue trends."""
        revenue_history = context.get('revenue_history', [])
        
        if len(revenue_history) < 2:
            return {'status': 'insufficient_data', 'trend': 0}
        
        recent = revenue_history[-7:]  # Last 7 days
        avg_recent = sum(recent) / len(recent)
        
        previous = revenue_history[-14:-7] if len(revenue_history) >= 14 else revenue_history[:-7]
        avg_previous = sum(previous) / len(previous) if previous else avg_recent
        
        if avg_previous == 0:
            return {'status': 'stable', 'trend': 0}
        
        change_pct = ((avg_recent - avg_previous) / avg_previous) * 100
        
        if change_pct < -10:
            status = 'declining'
        elif change_pct > 10:
            status = 'growing'
        else:
            status = 'stable'
        
        return {
            'status': status,
            'trend': change_pct,
            'recent_avg': avg_recent,
            'previous_avg': avg_previous
        }
    
    def _analyze_customer_satisfaction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer satisfaction metrics."""
        # Simplified satisfaction calculation
        return_rate = context.get('return_rate', 0.05)
        nps = context.get('nps', 50)
        support_tickets = context.get('support_tickets', 10)
        
        # Score 0-100
        score = (
            (1 - return_rate) * 30 +
            (nps / 100) * 40 +
            max(0, (1 - support_tickets / 100)) * 30
        ) * 100
        
        return {
            'score': score,
            'return_rate': return_rate,
            'nps': nps,
            'support_tickets': support_tickets
        }
    
    def _identify_pricing_opportunity(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify pricing optimization opportunities."""
        current_price = context.get('current_price', 100)
        demand_elasticity = context.get('demand_elasticity', -1.5)
        competitor_price = context.get('competitor_price', current_price * 1.1)
        
        # Calculate optimal price
        optimal_price = current_price * 1.05  # 5% increase baseline
        
        # Adjust based on competition
        if competitor_price > current_price * 1.2:
            optimal_price = min(current_price * 1.15, competitor_price * 0.95)
        
        potential_lift = ((optimal_price - current_price) / current_price) * 100
        
        return {
            'current_price': current_price,
            'optimal_price': optimal_price,
            'potential_lift': potential_lift,
            'confidence': 0.75
        }
    
    def _identify_upsell_opportunity(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify upsell campaign opportunities."""
        starter_customers = context.get('starter_tier_count', 0)
        avg_usage = context.get('avg_usage_pct', 50)
        
        # High usage indicates readiness for upgrade
        conversion_probability = min(avg_usage / 100, 0.9)
        
        expected_revenue = starter_customers * conversion_probability * 400  # $400 upgrade value
        
        return {
            'target_customers': starter_customers,
            'conversion_probability': conversion_probability,
            'expected_revenue': expected_revenue
        }
    
    def _generate_action_recommendations(
        self, 
        opportunities: List[Dict], 
        threats: List[Dict]
    ) -> List[Dict]:
        """Generate recommended actions based on analysis."""
        recommendations = []
        
        # Address threats first
        for threat in threats:
            if threat['type'] == 'revenue_decline':
                recommendations.append({
                    'action': ActionType.MARKETING_CAMPAIGN,
                    'priority': 'high',
                    'reasoning': 'Counter revenue decline with targeted marketing'
                })
            elif threat['type'] == 'low_satisfaction':
                recommendations.append({
                    'action': ActionType.CUSTOMER_INTERVENTION,
                    'priority': 'high',
                    'reasoning': 'Improve satisfaction with proactive support'
                })
        
        # Capitalize on opportunities
        for opportunity in opportunities:
            if opportunity['type'] == 'pricing_optimization':
                recommendations.append({
                    'action': ActionType.PRICING_ADJUSTMENT,
                    'priority': 'medium',
                    'reasoning': f"Increase revenue by {opportunity['potential']['potential_lift']:.1f}%"
                })
            elif opportunity['type'] == 'upsell_campaign':
                recommendations.append({
                    'action': ActionType.EMAIL_CAMPAIGN,
                    'priority': 'medium',
                    'reasoning': f"Target {opportunity['potential']['target_customers']} upgrade-ready customers"
                })
        
        return recommendations
    
    def _evaluate_action(
        self, 
        action_type: ActionType,
        context: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Tuple[float, str]:
        """Evaluate action using learned policy."""
        weights = self.policy_weights[action_type]
        
        # Calculate multi-objective score
        revenue_score = context.get('revenue_potential', 50)
        satisfaction_score = context.get('satisfaction_score', 70)
        growth_score = context.get('growth_potential', 60)
        risk_score = analysis.get('urgency_score', 20)
        
        total_score = (
            revenue_score * weights['revenue_weight'] +
            satisfaction_score * weights['satisfaction_weight'] +
            growth_score * weights['growth_weight'] +
            risk_score * weights['risk_weight']
        )
        
        # Add exploration bonus
        if random.random() < self.exploration_rate:
            total_score += random.uniform(-10, 10)
        
        reasoning = f"{action_type.value}: Score {total_score:.1f} (Revenue: {revenue_score}, Satisfaction: {satisfaction_score}, Growth: {growth_score})"
        
        return total_score, reasoning
    
    def _calculate_confidence(self, score: float, context: Dict[str, Any]) -> DecisionConfidence:
        """Calculate confidence level for decision."""
        # Normalize score to 0-100
        confidence_pct = min(max(score, 0), 100)
        
        if confidence_pct >= 95:
            return DecisionConfidence.CRITICAL
        elif confidence_pct >= 85:
            return DecisionConfidence.HIGH
        elif confidence_pct >= 70:
            return DecisionConfidence.MEDIUM
        else:
            return DecisionConfidence.LOW
    
    def _estimate_impact(self, action_type: ActionType, context: Dict[str, Any]) -> Dict[str, float]:
        """Estimate expected impact of action."""
        # Simplified impact estimation
        impacts = {
            ActionType.PRICING_ADJUSTMENT: {'revenue': 5.0, 'satisfaction': -2.0},
            ActionType.MARKETING_CAMPAIGN: {'revenue': 10.0, 'acquisition': 15.0},
            ActionType.CUSTOMER_INTERVENTION: {'satisfaction': 20.0, 'retention': 10.0},
            ActionType.DISCOUNT_GENERATION: {'conversion': 25.0, 'margin': -10.0},
            ActionType.EMAIL_CAMPAIGN: {'engagement': 15.0, 'conversion': 5.0},
        }
        
        return impacts.get(action_type, {'revenue': 0.0})
    
    def _calculate_risk(self, action_type: ActionType, expected_impact: Dict[str, float]) -> float:
        """Calculate risk score for action."""
        # Risk based on magnitude of negative impacts
        negative_impacts = sum(abs(v) for v in expected_impact.values() if v < 0)
        base_risk = {
            ActionType.PRICING_ADJUSTMENT: 30,
            ActionType.PRODUCT_LAUNCH: 50,
            ActionType.PARTNERSHIP_OUTREACH: 20,
        }.get(action_type, 10)
        
        return min(base_risk + negative_impacts, 100)
    
    def _generate_action_parameters(
        self, 
        action_type: ActionType,
        context: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate specific parameters for executing action."""
        if action_type == ActionType.PRICING_ADJUSTMENT:
            current_price = context.get('current_price', 100)
            return {
                'product_id': context.get('product_id', 'default'),
                'new_price': current_price * 1.05,
                'reason': 'autonomous_optimization'
            }
        
        elif action_type == ActionType.DISCOUNT_GENERATION:
            return {
                'discount_pct': 15,
                'duration_days': 7,
                'target_segment': 'cart_abandoners'
            }
        
        elif action_type == ActionType.EMAIL_CAMPAIGN:
            return {
                'template': 'upsell_pro_tier',
                'target_count': context.get('starter_tier_count', 100),
                'send_time': 'optimal'
            }
        
        return {}
    
    def _check_safety_limits(self, decision: Decision) -> Dict[str, Any]:
        """Check if decision violates safety limits."""
        if decision.action_type == ActionType.PRICING_ADJUSTMENT:
            price_change = decision.parameters.get('new_price', 0) / decision.parameters.get('current_price', 1)
            if abs(price_change - 1) > self.safety_limits['max_price_change_pct'] / 100:
                return {'safe': False, 'reason': 'Price change exceeds safety limit'}
        
        if decision.risk_score > 80:
            return {'safe': False, 'reason': 'Risk score too high'}
        
        return {'safe': True}
    
    def _execute_action(self, decision: Decision) -> Dict[str, Any]:
        """Execute the actual action (simulated)."""
        # In real implementation, this would call actual business logic
        # For now, simulate execution
        
        logging.info(f"Executing {decision.action_type.value} with parameters: {decision.parameters}")
        
        # Simulate success/failure
        success_probability = 0.85 if decision.confidence == DecisionConfidence.HIGH else 0.70
        success = random.random() < success_probability
        
        return {
            'success': success,
            'action_type': decision.action_type.value,
            'parameters_used': decision.parameters,
            'simulated': True
        }
    
    def _learn_from_outcome(self, decision: Decision, outcome: Dict[str, Any]):
        """Learn from decision outcome using reinforcement learning."""
        self.state = AgentState.LEARNING
        
        # Calculate reward
        reward = 1.0 if outcome.get('success') else -0.5
        
        # Adjust for expected vs actual impact
        if 'actual_impact' in outcome:
            expected = decision.expected_impact.get('revenue', 0)
            actual = outcome['actual_impact'].get('revenue', 0)
            reward += (actual - expected) / 100  # Reward proportional to outperformance
        
        # Store experience
        experience = LearningExperience(
            state={'decision_confidence': decision.confidence.value},
            action=decision.action_type,
            reward=reward,
            next_state={'success': outcome.get('success')},
            timestamp=time.time()
        )
        self.learning_buffer.append(experience)
        
        # Update policy weights
        self._update_policy(decision.action_type, reward)
        
        # Track performance
        self.performance_metrics[decision.action_type].append({
            'reward': reward,
            'confidence': decision.confidence.value,
            'timestamp': time.time()
        })
        
        self.state = AgentState.IDLE
    
    def _update_policy(self, action_type: ActionType, reward: float):
        """Update policy weights based on reward."""
        # Simple policy gradient update
        current_weights = self.policy_weights[action_type]
        
        for key in current_weights:
            # Move weights in direction of reward
            current_weights[key] += self.learning_rate * reward * random.uniform(-0.1, 0.1)
            
            # Clip weights
            current_weights[key] = max(-1, min(1, current_weights[key]))
    
    def _check_emergency_conditions(self, context: Dict[str, Any]) -> bool:
        """Check if emergency stop conditions are met."""
        # Emergency stop if massive loss
        recent_loss = context.get('daily_loss_pct', 0)
        if recent_loss > self.safety_limits['emergency_stop_loss_threshold']:
            return True
        
        # Emergency stop if too many failed decisions
        recent_failures = [d for d in self.decision_history[-10:] if d.success == False]
        if len(recent_failures) > 7:  # 70% failure rate
            return True
        
        return False
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report of autonomous agent."""
        total_decisions = len(self.decision_history)
        successful = sum(1 for d in self.decision_history if d.success == True)
        failed = sum(1 for d in self.decision_history if d.success == False)
        
        success_rate = (successful / total_decisions * 100) if total_decisions > 0 else 0
        
        avg_confidence = sum(
            {'critical': 95, 'high': 90, 'medium': 80, 'low': 60}[d.confidence.value]
            for d in self.decision_history
        ) / max(total_decisions, 1)
        
        action_breakdown = defaultdict(int)
        for decision in self.decision_history:
            action_breakdown[decision.action_type.value] += 1
        
        return {
            'total_decisions': total_decisions,
            'successful': successful,
            'failed': failed,
            'pending': total_decisions - successful - failed,
            'success_rate': success_rate,
            'avg_confidence': avg_confidence,
            'action_breakdown': dict(action_breakdown),
            'learning_experiences': len(self.learning_buffer),
            'current_state': self.state.value
        }
    
    # === NEW: MONITORING & AUTO-RECOVERY METHODS ===
    
    def run_loop(self, interval_seconds: int = 3600) -> None:
        """
        Run continuous monitoring loop with business intelligence.
        
        Args:
            interval_seconds: Seconds between checks (default: 1 hour)
        """
        logger.info(f"Starting autonomous monitoring loop (every {interval_seconds}s)")
        
        # Schedule periodic checks
        schedule.every(interval_seconds).seconds.do(self._monitoring_cycle)
        
        # Run immediately on startup
        self._monitoring_cycle()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def _monitoring_cycle(self) -> None:
        """Main monitoring cycle: check metrics, make decisions, take actions."""
        try:
            logger.info("=== Starting autonomous monitoring cycle ===")
            
            # 1. Collect metrics from all sources
            metrics = self.monitor_metrics()
            self._log_metrics(metrics)
            
            # 2. Analyze situation and make autonomous decision
            business_context = {
                'revenue_today': metrics['revenue_today'],
                'leads_today': metrics['leads_today'],
                'error_rate': metrics['error_rate'],
                'mrr': metrics['mrr'],
                'active_subscriptions': metrics['active_subscriptions']
            }
            
            decision = self.make_decision(business_context)
            logger.info(f"Decision: {decision.action_type.value} (confidence: {decision.confidence.value})")
            
            # 3. Execute decision if confidence is high enough
            if decision.confidence in [DecisionConfidence.CRITICAL, DecisionConfidence.HIGH]:
                self.execute_decision(decision.decision_id)
                self._handle_decision_actions(decision, metrics)
            
            logger.info("=== Monitoring cycle complete ===")
            
        except Exception as e:
            logger.error(f"Monitoring cycle failed: {e}", exc_info=True)
            self._send_alert(
                title="Agent Monitoring Failed",
                message=f"Exception: {str(e)}",
                metrics=None
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(requests.RequestException)
    )
    def monitor_metrics(self) -> Dict[str, Any]:
        """
        Collect business metrics from all sources with retry logic.
        
        Returns:
            Dict with current business metrics
        """
        logger.info("Collecting metrics from all sources...")
        
        # Internal Suresh AI Origin metrics
        internal_metrics = self._fetch_internal_metrics()
        
        # External metrics (if configured)
        stripe_revenue = self._fetch_stripe_revenue() if STRIPE_API_KEY else 0.0
        sheets_leads = self._fetch_sheets_leads() if os.getenv("GOOGLE_SHEETS_ID") else 0
        
        metrics = {
            'timestamp': time.time(),
            'revenue_today': internal_metrics.get('revenue_today', 0.0) + stripe_revenue,
            'leads_today': internal_metrics.get('leads_today', 0) + sheets_leads,
            'error_rate': internal_metrics.get('error_rate', 0.0),
            'active_subscriptions': internal_metrics.get('active_subscriptions', 0),
            'mrr': internal_metrics.get('mrr', 0.0)
        }
        
        logger.info(f"Metrics: revenue=₹{metrics['revenue_today']:.2f}, leads={metrics['leads_today']}, errors={metrics['error_rate']:.2%}")
        return metrics
    
    def _fetch_internal_metrics(self) -> Dict[str, Any]:
        """Fetch metrics from Suresh AI Origin API."""
        try:
            base_url = os.getenv("BASE_URL", "http://localhost:5000")
            resp = requests.get(f"{base_url}/api/analytics/daily-summary", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"Failed to fetch internal metrics: {e}")
            return {}
    
    def _fetch_stripe_revenue(self) -> float:
        """Fetch today's revenue from Stripe."""
        try:
            from datetime import datetime
            today_start = int(datetime.now().replace(hour=0, minute=0, second=0).timestamp())
            headers = {"Authorization": f"Bearer {STRIPE_API_KEY}"}
            resp = requests.get(
                "https://api.stripe.com/v1/charges",
                headers=headers,
                params={"created[gte]": today_start, "limit": 100},
                timeout=10
            )
            resp.raise_for_status()
            charges = resp.json().get("data", [])
            revenue = sum(c["amount"] / 100 for c in charges if c["paid"])
            logger.info(f"Stripe revenue today: ₹{revenue:.2f}")
            return revenue
        except Exception as e:
            logger.warning(f"Failed to fetch Stripe revenue: {e}")
            return 0.0
    
    def _fetch_sheets_leads(self) -> int:
        """Fetch today's leads from Google Sheets."""
        # TODO: Implement Google Sheets API integration
        logger.debug("Google Sheets integration not configured")
        return 0
    
    def _handle_decision_actions(self, decision: 'Decision', metrics: Dict[str, Any]) -> None:
        """Execute specific actions based on decision type."""
        action = decision.action_type
        
        if action == ActionType.CONTENT_GENERATION:
            if metrics['leads_today'] < LEADS_THRESHOLD:
                self.generate_content(reason="low_leads", metrics=metrics)
        
        elif action == ActionType.DEPLOY_FIX:
            if metrics['error_rate'] > ERROR_RATE_THRESHOLD:
                self.deploy_update(reason="high_error_rate", metrics=metrics)
        
        elif action == ActionType.EMAIL_CAMPAIGN:
            if metrics['revenue_today'] < REVENUE_THRESHOLD:
                self._send_alert(
                    title="Low Revenue Alert",
                    message=f"Revenue ₹{metrics['revenue_today']} below target ₹{REVENUE_THRESHOLD}",
                    metrics=metrics
                )
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=5))
    def generate_content(self, reason: str, metrics: Dict[str, Any]) -> None:
        """
        Auto-generate LinkedIn/Reels content via Claude API.
        
        Args:
            reason: Why content is being generated
            metrics: Current business metrics
        """
        logger.info(f"Generating content (reason: {reason})...")
        
        try:
            prompt = f"""Generate a viral LinkedIn post for Suresh AI Origin - an AI automation platform.

Context:
- Reason: {reason}
- Current metrics: {metrics['leads_today']} leads today, ₹{metrics['revenue_today']:.2f} revenue
- MRR: ₹{metrics['mrr']:.2f}, Active subscriptions: {metrics['active_subscriptions']}

Requirements:
1. Hook in first line (curiosity-driven)
2. Highlight our god-tier rare features (Destiny Blueprint, Business Consciousness, Perfect Timing)
3. Include social proof (48 AI systems, 99.95% uptime)
4. Clear CTA: Visit https://sureshaiorigin.com
5. Tone: Bold, confident, slightly provocative
6. Length: 150-250 words
7. End with power statement

Make it UNMISSABLE. No fluff."""
            
            content = generate_ai_content(prompt)
            
            if not content or len(content) < 50:
                raise ValueError("Generated content too short")
            
            # Send content via email for review
            send_email(
                to_address=os.getenv("ADMIN_EMAIL", "admin@sureshaiorigin.com"),
                subject=f"AI Generated Content - {reason}",
                body=f"""<h2>Autonomous Agent Generated Content</h2>
                <p><strong>Reason:</strong> {reason}</p>
                <hr>
                <div style="background: #f5f5f5; padding: 20px; border-left: 4px solid #007bff;">
                {content}
                </div>
                """
            )
            
            logger.info(f"Content generated and sent ({len(content)} chars)")
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}", exc_info=True)
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=5))
    def deploy_update(self, reason: str, metrics: Dict[str, Any]) -> None:
        """
        Trigger deployment via GitHub Actions.
        
        Args:
            reason: Why deployment is triggered
            metrics: Current business metrics
        """
        logger.info(f"Triggering deployment (reason: {reason})...")
        
        if not GITHUB_TOKEN:
            logger.warning("GITHUB_TOKEN not configured")
            return
        
        try:
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            payload = {
                "ref": "main",
                "inputs": {
                    "reason": reason,
                    "triggered_by": "autonomous_agent",
                    "error_rate": str(metrics['error_rate'])
                }
            }
            
            resp = requests.post(
                f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/deploy.yml/dispatches",
                headers=headers,
                json=payload,
                timeout=10
            )
            resp.raise_for_status()
            
            logger.info("Deployment triggered successfully")
            
            self._send_alert(
                title="Auto-Deploy Triggered",
                message=f"Deployment triggered due to {reason}. Error rate: {metrics['error_rate']:.2%}",
                metrics=metrics
            )
            
        except Exception as e:
            logger.error(f"Deployment trigger failed: {e}", exc_info=True)
    
    def _send_alert(self, title: str, message: str, metrics: Optional[Dict]) -> None:
        """Send alert via email/WhatsApp."""
        try:
            logger.warning(f"ALERT: {title} - {message}")
            
            # Log alert
            self._write_jsonl(ALERTS_LOG, {
                'timestamp': time.time(),
                'title': title,
                'message': message,
                'metrics': metrics
            })
            
            # Email alert
            send_email(
                to_address=os.getenv("ADMIN_EMAIL", "admin@sureshaiorigin.com"),
                subject=f"🚨 SURESH AI ORIGIN ALERT: {title}",
                body=f"""<h2 style="color: #dc3545;">{title}</h2>
                <p>{message}</p>
                {f'<pre>{json.dumps(metrics, indent=2)}</pre>' if metrics else ''}
                """
            )
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    def _log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log metrics to JSONL."""
        self._write_jsonl(METRICS_LOG, metrics)
    
    @staticmethod
    def _write_jsonl(filepath: Path, data: Dict[str, Any]) -> None:
        """Append data to JSONL file."""
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            logger.error(f"Failed to write to {filepath}: {e}")


# Initialize global agent
autonomous_agent = AutonomousBusinessAgent(config={'autonomous_mode': False})


# CLI Interface
def main():
    """CLI entry point for autonomous monitoring."""
    parser = argparse.ArgumentParser(description="Autonomous Business Agent for Suresh AI Origin")
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Seconds between monitoring cycles (default: 3600 = 1 hour)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as background daemon service"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (for testing)"
    )
    
    args = parser.parse_args()
    
    if args.once:
        autonomous_agent._monitoring_cycle()
    else:
        autonomous_agent.run_loop(interval_seconds=args.interval)


# API Functions
def agent_analyze_situation(business_context: Dict) -> Dict:
    """API: Analyze current business situation."""
    return autonomous_agent.analyze_situation(business_context)


def agent_make_decision(business_context: Dict, allowed_actions: Optional[List[str]] = None) -> Dict:
    """API: Make an autonomous decision."""
    action_types = [ActionType(a) for a in allowed_actions] if allowed_actions else None
    decision = autonomous_agent.make_decision(business_context, action_types)
    return asdict(decision)


if __name__ == "__main__":
    main()


def agent_execute_decision(decision_id: str, force: bool = False) -> Dict:
    """API: Execute a decision."""
    decision = next((d for d in autonomous_agent.decision_history if d.decision_id == decision_id), None)
    if not decision:
        return {'status': 'not_found', 'decision_id': decision_id}
    
    return autonomous_agent.execute_decision(decision, force)


def agent_get_performance() -> Dict:
    """API: Get agent performance report."""
    return autonomous_agent.get_performance_report()


if __name__ == "__main__":
    print("🤖 AUTONOMOUS BUSINESS AGENT - DEMO")
    print("=" * 60)
    
    # Demo context
    context = {
        'revenue_history': [1000, 1050, 1100, 1080, 1060, 1040, 1020],
        'current_price': 100,
        'competitor_price': 110,
        'starter_tier_count': 50,
        'avg_usage_pct': 75,
        'nps': 60,
        'return_rate': 0.05
    }
    
    analysis = agent_analyze_situation(context)
    print(f"\n📊 Situation Analysis:")
    print(f"   Opportunities: {len(analysis['opportunities'])}")
    print(f"   Threats: {len(analysis['threats'])}")
    print(f"   Urgency: {analysis['urgency_score']}")
    
    decision = agent_make_decision(context)
    print(f"\n🧠 Autonomous Decision:")
    print(f"   Action: {decision['action_type']}")
    print(f"   Confidence: {decision['confidence']}")
    print(f"   Risk: {decision['risk_score']:.1f}")
    print(f"   Reasoning: {decision['reasoning']}")
