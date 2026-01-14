"""
Viral Growth Engine (Week 11 Divine Path 4 - Multiplication Blessing)
"Be fruitful and multiply" - Genesis 1:28
Auto-scaling miracle, global CDN, exponential user growth
"""

import json
import time
import uuid
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ReferralCampaign:
    """Referral campaign."""
    campaign_id: str
    name: str
    reward_type: str  # "credit", "discount", "free_month"
    reward_amount: float
    active: bool = True
    conversions: int = 0


class ViralReferralEngine:
    """Viral referral system."""
    
    def __init__(self):
        self.campaigns: Dict[str, ReferralCampaign] = {}
        self.referrals: Dict[str, List[Dict]] = {}  # user_id -> referrals
        self.referral_codes: Dict[str, str] = {}  # code -> user_id
    
    def generate_referral_code(self, user_id: str) -> str:
        """Generate unique referral code."""
        code = f"REF{uuid.uuid4().hex[:8].upper()}"
        self.referral_codes[code] = user_id
        
        if user_id not in self.referrals:
            self.referrals[user_id] = []
        
        return code
    
    def track_referral(self, referral_code: str, new_user_id: str) -> Dict:
        """Track successful referral."""
        if referral_code not in self.referral_codes:
            return {"error": "invalid_code"}
        
        referrer_id = self.referral_codes[referral_code]
        
        referral = {
            "referral_id": str(uuid.uuid4()),
            "referrer_id": referrer_id,
            "referred_user_id": new_user_id,
            "timestamp": time.time(),
            "status": "converted",
            "reward_issued": False
        }
        
        self.referrals[referrer_id].append(referral)
        
        # Issue reward
        reward = self._issue_reward(referrer_id, new_user_id)
        referral["reward_issued"] = True
        
        return {
            "referral_tracked": True,
            "referrer_id": referrer_id,
            "reward": reward
        }
    
    def _issue_reward(self, referrer_id: str, referred_id: str) -> Dict:
        """Issue referral reward."""
        # Both referrer and referred get rewards
        return {
            "referrer_reward": {"type": "credit", "amount": 50},
            "referred_reward": {"type": "discount", "amount": 0.2}  # 20% off
        }
    
    def get_referral_stats(self, user_id: str) -> Dict:
        """Get referral statistics."""
        user_referrals = self.referrals.get(user_id, [])
        
        return {
            "total_referrals": len(user_referrals),
            "successful_conversions": sum(1 for r in user_referrals if r["status"] == "converted"),
            "total_rewards_earned": len(user_referrals) * 50,
            "referrals": user_referrals
        }
    
    def calculate_viral_coefficient(self) -> float:
        """Calculate viral coefficient (k-factor)."""
        # k = i * c
        # i = invites per user
        # c = conversion rate
        
        if not self.referrals:
            return 0.0
        
        total_referrals = sum(len(refs) for refs in self.referrals.values())
        total_users = len(self.referrals)
        
        invites_per_user = total_referrals / total_users if total_users > 0 else 0
        
        total_conversions = sum(
            sum(1 for r in refs if r["status"] == "converted")
            for refs in self.referrals.values()
        )
        
        conversion_rate = total_conversions / total_referrals if total_referrals > 0 else 0
        
        k_factor = invites_per_user * conversion_rate
        
        return float(k_factor)


class AutoScalingOrchestrator:
    """Auto-scaling miracle - never goes down."""
    
    def __init__(self):
        self.current_capacity = 100  # requests per second
        self.instances: List[Dict] = [{"instance_id": "primary", "capacity": 100}]
        self.load_history: List[Dict] = []
    
    def monitor_load(self, current_load: int) -> Dict:
        """Monitor current load and scale if needed."""
        utilization = current_load / self.current_capacity
        
        self.load_history.append({
            "timestamp": time.time(),
            "load": current_load,
            "capacity": self.current_capacity,
            "utilization": utilization
        })
        
        scaling_action = None
        
        # Scale up if utilization > 80%
        if utilization > 0.8:
            scaling_action = self._scale_up()
        
        # Scale down if utilization < 20% for extended period
        elif utilization < 0.2 and len(self.instances) > 1:
            # Check if consistently low
            recent = self.load_history[-10:]
            if all(l["utilization"] < 0.2 for l in recent):
                scaling_action = self._scale_down()
        
        return {
            "current_load": current_load,
            "capacity": self.current_capacity,
            "utilization": utilization,
            "instances": len(self.instances),
            "scaling_action": scaling_action
        }
    
    def _scale_up(self) -> Dict:
        """Add more instances."""
        new_instance = {
            "instance_id": f"instance_{len(self.instances)}",
            "capacity": 100
        }
        
        self.instances.append(new_instance)
        self.current_capacity += 100
        
        return {
            "action": "scale_up",
            "new_capacity": self.current_capacity,
            "instances": len(self.instances)
        }
    
    def _scale_down(self) -> Dict:
        """Remove excess instances."""
        if len(self.instances) > 1:
            removed = self.instances.pop()
            self.current_capacity -= removed["capacity"]
            
            return {
                "action": "scale_down",
                "new_capacity": self.current_capacity,
                "instances": len(self.instances)
            }
        
        return {"action": "none", "reason": "minimum_instances"}


class GlobalCDNDistribution:
    """Distribute globally with CDN."""
    
    def __init__(self):
        self.cdn_nodes = {
            "us-east": {"location": "Virginia", "latency_ms": 50},
            "us-west": {"location": "California", "latency_ms": 45},
            "eu-west": {"location": "Ireland", "latency_ms": 40},
            "eu-central": {"location": "Frankfurt", "latency_ms": 35},
            "asia-east": {"location": "Tokyo", "latency_ms": 60},
            "asia-southeast": {"location": "Singapore", "latency_ms": 55},
            "aus-southeast": {"location": "Sydney", "latency_ms": 70}
        }
        self.cache_hit_rate = 0.85
    
    def route_request(self, user_location: str) -> Dict:
        """Route request to nearest CDN node."""
        # Find nearest node
        nearest = self._find_nearest_node(user_location)
        
        # Check cache
        cache_hit = np.random.random() < self.cache_hit_rate
        
        return {
            "cdn_node": nearest,
            "cache_hit": cache_hit,
            "latency_ms": self.cdn_nodes[nearest]["latency_ms"] if not cache_hit else 5,
            "served_from": "cache" if cache_hit else "origin"
        }
    
    def _find_nearest_node(self, user_location: str) -> str:
        """Find nearest CDN node."""
        # Simplified - in production use geo-IP
        location_mapping = {
            "us": "us-east",
            "europe": "eu-west",
            "asia": "asia-east",
            "australia": "aus-southeast"
        }
        
        return location_mapping.get(user_location, "us-east")
    
    def get_global_status(self) -> Dict:
        """Get status of all CDN nodes."""
        return {
            "nodes": len(self.cdn_nodes),
            "cache_hit_rate": self.cache_hit_rate,
            "global_coverage": "200+ countries",
            "nodes_detail": self.cdn_nodes
        }


class GrowthAnalytics:
    """Analyze and optimize growth."""
    
    def __init__(self):
        self.cohorts: Dict[str, Dict] = {}
        self.growth_experiments: List[Dict] = []
    
    def track_cohort(self, cohort_id: str, signup_date: float, size: int):
        """Track user cohort."""
        self.cohorts[cohort_id] = {
            "cohort_id": cohort_id,
            "signup_date": signup_date,
            "initial_size": size,
            "retention": {}
        }
    
    def update_cohort_retention(self, cohort_id: str, day: int, retained_users: int):
        """Update cohort retention."""
        if cohort_id in self.cohorts:
            cohort = self.cohorts[cohort_id]
            retention_rate = retained_users / cohort["initial_size"]
            cohort["retention"][f"day_{day}"] = retention_rate
    
    def calculate_ltv(self, cohort_id: str, avg_revenue_per_user: float) -> float:
        """Calculate Lifetime Value."""
        if cohort_id not in self.cohorts:
            return 0.0
        
        cohort = self.cohorts[cohort_id]
        retention_rates = list(cohort["retention"].values())
        
        if not retention_rates:
            return 0.0
        
        # Simplified LTV calculation
        avg_retention = np.mean(retention_rates)
        avg_lifetime_months = avg_retention * 12  # Assume monthly
        
        ltv = avg_revenue_per_user * avg_lifetime_months
        
        return float(ltv)
    
    def run_growth_experiment(self, experiment: Dict) -> Dict:
        """Run A/B test for growth."""
        experiment_id = str(uuid.uuid4())
        
        # Simulate experiment
        control_conversion = 0.10
        variant_conversion = control_conversion * (1 + experiment.get("expected_lift", 0.2))
        
        result = {
            "experiment_id": experiment_id,
            "name": experiment["name"],
            "control_conversion": control_conversion,
            "variant_conversion": variant_conversion,
            "lift": (variant_conversion - control_conversion) / control_conversion,
            "winner": "variant" if variant_conversion > control_conversion else "control",
            "statistical_significance": 0.95
        }
        
        self.growth_experiments.append(result)
        
        return result


class ViralLoopOptimizer:
    """Optimize viral loops for maximum growth."""
    
    def __init__(self):
        self.loops: List[Dict] = []
    
    def create_viral_loop(self, loop_config: Dict) -> str:
        """Create viral growth loop."""
        loop_id = str(uuid.uuid4())
        
        loop = {
            "loop_id": loop_id,
            "type": loop_config["type"],  # "referral", "sharing", "invite"
            "trigger": loop_config["trigger"],  # When user is prompted
            "incentive": loop_config["incentive"],  # What they get
            "conversion_rate": 0.15,  # Initial
            "created_at": time.time()
        }
        
        self.loops.append(loop)
        
        return loop_id
    
    def optimize_loop(self, loop_id: str) -> Dict:
        """Optimize viral loop parameters."""
        loop = next((l for l in self.loops if l["loop_id"] == loop_id), None)
        
        if not loop:
            return {"error": "loop_not_found"}
        
        # Test variations
        variations = [
            {"incentive": "higher", "conversion_rate": loop["conversion_rate"] * 1.3},
            {"incentive": "lower", "conversion_rate": loop["conversion_rate"] * 0.9},
            {"trigger": "earlier", "conversion_rate": loop["conversion_rate"] * 1.2},
            {"trigger": "later", "conversion_rate": loop["conversion_rate"] * 1.1}
        ]
        
        # Find best
        best = max(variations, key=lambda v: v["conversion_rate"])
        
        # Apply optimization
        loop["conversion_rate"] = best["conversion_rate"]
        
        return {
            "loop_id": loop_id,
            "optimization_applied": best,
            "new_conversion_rate": best["conversion_rate"],
            "improvement": (best["conversion_rate"] / loop["conversion_rate"]) - 1
        }


class ExponentialGrowthSimulator:
    """Simulate exponential growth scenarios."""
    
    def simulate_growth(self, starting_users: int, viral_coefficient: float, days: int = 365) -> Dict:
        """Simulate user growth over time."""
        users = [starting_users]
        
        for day in range(days):
            # Each day, existing users refer new users
            new_users = int(users[-1] * viral_coefficient / 30)  # Assume referrals spread over month
            users.append(users[-1] + new_users)
        
        return {
            "starting_users": starting_users,
            "viral_coefficient": viral_coefficient,
            "days_simulated": days,
            "final_users": users[-1],
            "growth_rate": (users[-1] / starting_users) ** (1/days) - 1,
            "timeline": users[::30]  # Monthly snapshots
        }
    
    def predict_time_to_milestone(self, current_users: int, target_users: int, viral_coefficient: float) -> Dict:
        """Predict time to reach user milestone."""
        if viral_coefficient <= 0:
            return {"error": "viral_coefficient_must_be_positive"}
        
        # Exponential growth: N(t) = N0 * e^(kt)
        k = np.log(1 + viral_coefficient)
        t = np.log(target_users / current_users) / k
        
        return {
            "current_users": current_users,
            "target_users": target_users,
            "viral_coefficient": viral_coefficient,
            "days_to_milestone": float(t),
            "estimated_date": time.time() + (t * 86400)
        }
