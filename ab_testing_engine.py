"""
Feature #18: A/B Testing Engine
Real-time experiment management with statistical significance testing
Supports multi-variant testing, traffic allocation, and winner selection
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict
import json


@dataclass
class ExperimentConfig:
    """Configuration for an A/B test experiment"""
    experiment_id: str
    name: str
    description: str
    hypothesis: str
    start_date: str
    end_date: str
    status: str  # DRAFT, RUNNING, COMPLETED, PAUSED
    primary_metric: str  # conversion_rate, revenue_per_visitor, etc.
    sample_size: int  # target sample size
    confidence_level: float  # 0.90, 0.95, 0.99
    min_effect_size: float  # minimum uplift to detect (e.g., 0.1 for 10%)


class StatisticalCalculator:
    """Calculate statistical significance for A/B test results"""
    
    @staticmethod
    def chi_square_test(control_conversions: int, control_visitors: int, 
                       variant_conversions: int, variant_visitors: int) -> Dict:
        """
        Perform chi-square test for statistical significance
        Returns p-value, effect size, and interpretation
        """
        # Handle edge cases
        if control_visitors == 0 or variant_visitors == 0:
            return {
                "chi_square": 0,
                "p_value": 1.0,
                "is_significant": False,
                "confidence_percent": 0,
                "effect_size_percent": 0,
                "control_conversion_rate": 0,
                "variant_conversion_rate": 0,
                "recommendation": "Insufficient data"
            }
        
        control_rate = control_conversions / control_visitors
        variant_rate = variant_conversions / variant_visitors
        
        # Chi-square calculation
        expected_control = (control_conversions + variant_conversions) * control_visitors / (control_visitors + variant_visitors)
        expected_variant = (control_conversions + variant_conversions) * variant_visitors / (control_visitors + variant_visitors)
        
        chi_square = 0
        if expected_control > 0:
            chi_square += (control_conversions - expected_control) ** 2 / expected_control
        if expected_variant > 0:
            chi_square += (variant_conversions - expected_variant) ** 2 / expected_variant
        
        # Approximate p-value (simplified)
        p_value = 0.05 if chi_square > 3.841 else 0.10  # 3.841 ≈ chi-square critical value at 0.05
        
        # Effect size (relative uplift)
        uplift = ((variant_rate - control_rate) / max(control_rate, 0.001)) * 100
        
        # Confidence level determination
        is_significant = chi_square > 3.841
        confidence = 95 if is_significant else 0
        
        return {
            "chi_square": round(chi_square, 4),
            "p_value": p_value,
            "is_significant": is_significant,
            "confidence_percent": confidence,
            "effect_size_percent": round(uplift, 2),
            "control_conversion_rate": round(control_rate * 100, 2),
            "variant_conversion_rate": round(variant_rate * 100, 2),
            "recommendation": "Variant wins!" if uplift > 5 and is_significant else ("Keep running" if not is_significant else "No clear winner")
        }
    
    @staticmethod
    def bayesian_credible_interval(conversions: int, visitors: int) -> Dict:
        """Calculate Bayesian credible interval for conversion rate"""
        # Beta distribution approximation
        alpha = conversions + 1
        beta = visitors - conversions + 1
        
        mean = alpha / (alpha + beta)
        variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
        std_dev = math.sqrt(variance)
        
        # 95% credible interval
        ci_lower = max(0, mean - 1.96 * std_dev)
        ci_upper = min(1, mean + 1.96 * std_dev)
        
        return {
            "mean": round(mean * 100, 2),
            "std_dev": round(std_dev * 100, 2),
            "ci_lower_percent": round(ci_lower * 100, 2),
            "ci_upper_percent": round(ci_upper * 100, 2),
        }
    
    @staticmethod
    def required_sample_size(baseline_rate: float, min_effect_size: float, 
                            confidence_level: float = 0.95) -> int:
        """
        Calculate required sample size for experiment
        baseline_rate: current conversion rate (0-1)
        min_effect_size: minimum detectable effect (0-1)
        confidence_level: statistical power (0.90, 0.95, 0.99)
        """
        z_alpha = 1.96 if confidence_level == 0.95 else (1.645 if confidence_level == 0.90 else 2.576)
        
        p1 = baseline_rate
        p2 = baseline_rate + min_effect_size
        
        pbar = (p1 + p2) / 2
        
        # Sample size formula
        n = (2 * z_alpha ** 2 * pbar * (1 - pbar)) / ((p2 - p1) ** 2)
        
        return int(math.ceil(n))


class VariantAnalyzer:
    """Analyze and compare experiment variants"""
    
    def __init__(self):
        self.variants = {}  # variant_id -> variant_data
        self.results = defaultdict(lambda: {"conversions": 0, "visitors": 0, "revenue": 0})
    
    def add_variant(self, variant_id: str, variant_name: str, description: str, 
                   traffic_allocation: float) -> Dict:
        """Add a variant to the experiment"""
        if variant_id in self.variants:
            return {"status": "error", "message": "Variant already exists"}
        
        self.variants[variant_id] = {
            "id": variant_id,
            "name": variant_name,
            "description": description,
            "traffic_allocation": traffic_allocation,
            "created_at": datetime.now().isoformat(),
        }
        
        return {"status": "created", "variant_id": variant_id}
    
    def track_conversion(self, variant_id: str, converted: bool, revenue: float = 0) -> Dict:
        """Track a conversion for a variant"""
        if variant_id not in self.variants:
            return {"status": "error", "message": "Variant not found"}
        
        self.results[variant_id]["visitors"] += 1
        if converted:
            self.results[variant_id]["conversions"] += 1
            self.results[variant_id]["revenue"] += revenue
        
        return {
            "status": "tracked",
            "variant_id": variant_id,
            "visitor_count": self.results[variant_id]["visitors"],
            "conversion_count": self.results[variant_id]["conversions"]
        }
    
    def get_variant_performance(self, variant_id: str) -> Dict:
        """Get performance metrics for a variant"""
        if variant_id not in self.variants:
            return {}
        
        result = self.results[variant_id]
        visitors = result["visitors"]
        conversions = result["conversions"]
        rate = (conversions / max(visitors, 1)) * 100
        
        return {
            "variant_id": variant_id,
            "variant_name": self.variants[variant_id]["name"],
            "visitors": visitors,
            "conversions": conversions,
            "conversion_rate_percent": round(rate, 2),
            "revenue": round(result["revenue"], 2),
            "revenue_per_visitor": round(result["revenue"] / max(visitors, 1), 2),
        }
    
    def compare_all_variants(self) -> List[Dict]:
        """Compare all variants and rank by performance"""
        performances = []
        
        for variant_id in self.variants:
            perf = self.get_variant_performance(variant_id)
            if perf:
                performances.append(perf)
        
        # Sort by conversion rate
        performances.sort(key=lambda x: x["conversion_rate_percent"], reverse=True)
        
        return performances
    
    def determine_winner(self, control_variant_id: str, significance_level: float = 0.05) -> Dict:
        """Determine which variant is the winner using statistical test"""
        if control_variant_id not in self.results:
            return {"status": "error", "message": "Control variant not found"}
        
        control = self.results[control_variant_id]
        
        best_variant = None
        best_uplift = 0
        significance_test = None
        
        for variant_id in self.variants:
            if variant_id == control_variant_id:
                continue
            
            variant = self.results[variant_id]
            
            # Chi-square test
            test_result = StatisticalCalculator.chi_square_test(
                control["conversions"], control["visitors"],
                variant["conversions"], variant["visitors"]
            )
            
            if test_result["is_significant"] and test_result["effect_size_percent"] > best_uplift:
                best_uplift = test_result["effect_size_percent"]
                best_variant = variant_id
                significance_test = test_result
        
        if best_variant:
            return {
                "winner": best_variant,
                "winner_name": self.variants[best_variant]["name"],
                "uplift_percent": round(best_uplift, 2),
                "statistical_test": significance_test,
                "status": "winner_found"
            }
        
        return {
            "winner": None,
            "status": "no_winner",
            "message": "No variant shows statistically significant improvement"
        }


class ExperimentManager:
    """Manage A/B testing experiments"""
    
    def __init__(self):
        self.experiments = {}  # experiment_id -> experiment
        self.variant_analyzers = {}  # experiment_id -> VariantAnalyzer
    
    def create_experiment(self, experiment_id: str, name: str, description: str, 
                         hypothesis: str, primary_metric: str, 
                         confidence_level: float = 0.95) -> Dict:
        """Create a new experiment"""
        
        if experiment_id in self.experiments:
            return {"status": "error", "message": "Experiment already exists"}
        
        config = ExperimentConfig(
            experiment_id=experiment_id,
            name=name,
            description=description,
            hypothesis=hypothesis,
            start_date=datetime.now().isoformat(),
            end_date=(datetime.now() + timedelta(days=14)).isoformat(),
            status="DRAFT",
            primary_metric=primary_metric,
            sample_size=1000,
            confidence_level=confidence_level,
            min_effect_size=0.1
        )
        
        self.experiments[experiment_id] = asdict(config)
        self.variant_analyzers[experiment_id] = VariantAnalyzer()
        
        return {
            "status": "created",
            "experiment_id": experiment_id,
            "experiment": self.experiments[experiment_id]
        }
    
    def start_experiment(self, experiment_id: str) -> Dict:
        """Start an experiment"""
        if experiment_id not in self.experiments:
            return {"status": "error", "message": "Experiment not found"}
        
        self.experiments[experiment_id]["status"] = "RUNNING"
        self.experiments[experiment_id]["start_date"] = datetime.now().isoformat()
        
        return {"status": "started", "experiment_id": experiment_id}
    
    def pause_experiment(self, experiment_id: str) -> Dict:
        """Pause an experiment"""
        if experiment_id not in self.experiments:
            return {"status": "error", "message": "Experiment not found"}
        
        self.experiments[experiment_id]["status"] = "PAUSED"
        
        return {"status": "paused", "experiment_id": experiment_id}
    
    def end_experiment(self, experiment_id: str) -> Dict:
        """End an experiment and determine winner"""
        if experiment_id not in self.experiments:
            return {"status": "error", "message": "Experiment not found"}
        
        analyzer = self.variant_analyzers[experiment_id]
        winner_result = analyzer.determine_winner(list(analyzer.variants.keys())[0] if analyzer.variants else None)
        
        self.experiments[experiment_id]["status"] = "COMPLETED"
        self.experiments[experiment_id]["end_date"] = datetime.now().isoformat()
        self.experiments[experiment_id]["winner"] = winner_result.get("winner")
        
        return {
            "status": "completed",
            "experiment_id": experiment_id,
            "winner_result": winner_result
        }
    
    def add_variant(self, experiment_id: str, variant_id: str, 
                   variant_name: str, description: str, 
                   traffic_allocation: float) -> Dict:
        """Add variant to experiment"""
        if experiment_id not in self.variant_analyzers:
            return {"status": "error", "message": "Experiment not found"}
        
        analyzer = self.variant_analyzers[experiment_id]
        return analyzer.add_variant(variant_id, variant_name, description, traffic_allocation)
    
    def track_visitor(self, experiment_id: str, visitor_id: str) -> str:
        """Assign visitor to variant based on traffic allocation"""
        if experiment_id not in self.variant_analyzers:
            return None
        
        analyzer = self.variant_analyzers[experiment_id]
        if not analyzer.variants:
            return None
        
        # Weighted random selection based on traffic allocation
        total_traffic = sum(v["traffic_allocation"] for v in analyzer.variants.values())
        rand = random.uniform(0, total_traffic)
        
        cumulative = 0
        for variant_id, variant in analyzer.variants.items():
            cumulative += variant["traffic_allocation"]
            if rand <= cumulative:
                return variant_id
        
        return list(analyzer.variants.keys())[0]
    
    def track_conversion(self, experiment_id: str, variant_id: str, 
                        converted: bool, revenue: float = 0) -> Dict:
        """Track conversion for a variant"""
        if experiment_id not in self.variant_analyzers:
            return {"status": "error", "message": "Experiment not found"}
        
        analyzer = self.variant_analyzers[experiment_id]
        return analyzer.track_conversion(variant_id, converted, revenue)
    
    def get_experiment_results(self, experiment_id: str) -> Dict:
        """Get comprehensive results for an experiment"""
        if experiment_id not in self.experiments:
            return {"status": "error", "message": "Experiment not found"}
        
        analyzer = self.variant_analyzers[experiment_id]
        variants_performance = analyzer.compare_all_variants()
        winner_analysis = analyzer.determine_winner(
            list(analyzer.variants.keys())[0] if analyzer.variants else None
        )
        
        # Calculate aggregate stats
        total_visitors = sum(v["visitors"] for v in variants_performance)
        total_conversions = sum(v["conversions"] for v in variants_performance)
        overall_rate = (total_conversions / max(total_visitors, 1)) * 100
        
        return {
            "experiment_id": experiment_id,
            "experiment_name": self.experiments[experiment_id]["name"],
            "status": self.experiments[experiment_id]["status"],
            "total_visitors": total_visitors,
            "total_conversions": total_conversions,
            "overall_conversion_rate_percent": round(overall_rate, 2),
            "variants_performance": variants_performance,
            "winner_analysis": winner_analysis,
            "confidence_level": self.experiments[experiment_id]["confidence_level"],
        }
    
    def get_all_experiments(self) -> List[Dict]:
        """Get all experiments with summary stats"""
        experiments = []
        
        for exp_id in self.experiments:
            result = self.get_experiment_results(exp_id)
            experiments.append(result)
        
        return experiments


def generate_demo_experiments() -> Tuple[ExperimentManager, List[str]]:
    """Generate demo A/B testing experiments for testing"""
    manager = ExperimentManager()
    
    # Experiment 1: CTA Button Color
    exp1_id = "cta_color_test"
    manager.create_experiment(
        exp1_id,
        "CTA Button Color Test",
        "Testing if red vs blue CTA button improves conversions",
        "Red CTA buttons will have higher conversion rate than blue",
        "conversion_rate",
        confidence_level=0.95
    )
    manager.start_experiment(exp1_id)
    
    # Add variants
    manager.add_variant(exp1_id, "control", "Blue Button (Control)", "Original blue CTA button", 0.5)
    manager.add_variant(exp1_id, "variant_red", "Red Button", "Red CTA button", 0.5)
    
    # Simulate visitors
    for i in range(150):
        control_converted = random.random() < 0.12  # 12% conversion
        manager.track_conversion(exp1_id, "control", control_converted, 49.99 if control_converted else 0)
    
    for i in range(150):
        variant_converted = random.random() < 0.16  # 16% conversion (uplift)
        manager.track_conversion(exp1_id, "variant_red", variant_converted, 49.99 if variant_converted else 0)
    
    # Experiment 2: Pricing Page
    exp2_id = "pricing_layout_test"
    manager.create_experiment(
        exp2_id,
        "Pricing Page Layout Test",
        "Testing card vs table layout for pricing presentation",
        "Card layout will improve plan selection rate",
        "conversion_rate",
        confidence_level=0.90
    )
    manager.start_experiment(exp2_id)
    
    # Add variants
    manager.add_variant(exp2_id, "control", "Table Layout", "Traditional pricing table", 0.5)
    manager.add_variant(exp2_id, "variant_cards", "Card Layout", "Modern card-based layout", 0.5)
    
    # Simulate visitors
    for i in range(100):
        control_converted = random.random() < 0.18  # 18% selection rate
        manager.track_conversion(exp2_id, "control", control_converted, 99.99 if control_converted else 0)
    
    for i in range(100):
        variant_converted = random.random() < 0.22  # 22% selection rate
        manager.track_conversion(exp2_id, "variant_cards", variant_converted, 99.99 if variant_converted else 0)
    
    # Experiment 3: Email Subject Line (just started)
    exp3_id = "email_subject_test"
    manager.create_experiment(
        exp3_id,
        "Email Subject Line Test",
        "Testing curiosity gap vs direct benefit in subject lines",
        "Curiosity gap will improve open rate",
        "open_rate",
        confidence_level=0.95
    )
    manager.start_experiment(exp3_id)
    
    manager.add_variant(exp3_id, "control", "Direct Benefit", "Exclusive Offer: Get 50% Off Now", 0.5)
    manager.add_variant(exp3_id, "variant_curiosity", "Curiosity Gap", "3 Things You're Getting Wrong", 0.5)
    
    # Simulate visitors (early data)
    for i in range(80):
        control_converted = random.random() < 0.22
        manager.track_conversion(exp3_id, "control", control_converted)
    
    for i in range(80):
        variant_converted = random.random() < 0.28
        manager.track_conversion(exp3_id, "variant_curiosity", variant_converted)
    
    return manager, [exp1_id, exp2_id, exp3_id]


# Global instance for demo
_demo_manager = None
_demo_experiment_ids = []


def get_demo_manager():
    """Get or create demo experiment manager"""
    global _demo_manager, _demo_experiment_ids
    if _demo_manager is None:
        _demo_manager, _demo_experiment_ids = generate_demo_experiments()
    return _demo_manager, _demo_experiment_ids
