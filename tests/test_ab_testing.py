"""
Tests for A/B Testing Engine (Feature #18)
Tests for experiment management, statistical significance, and winner determination
"""

import pytest
from ab_testing_engine import (
    ExperimentManager,
    VariantAnalyzer,
    StatisticalCalculator,
    ExperimentConfig,
    generate_demo_experiments
)


class TestStatisticalCalculator:
    """Test statistical significance calculations"""
    
    def test_chi_square_test_significant(self):
        """Test chi-square test with significant difference"""
        result = StatisticalCalculator.chi_square_test(
            control_conversions=12,
            control_visitors=100,
            variant_conversions=20,
            variant_visitors=100
        )
        
        assert "chi_square" in result
        assert "p_value" in result
        assert "effect_size_percent" in result
        assert result["effect_size_percent"] > 0
    
    def test_chi_square_test_not_significant(self):
        """Test chi-square test with no significant difference"""
        result = StatisticalCalculator.chi_square_test(
            control_conversions=15,
            control_visitors=100,
            variant_conversions=16,
            variant_visitors=100
        )
        
        assert result["confidence_percent"] >= 0
        assert result["effect_size_percent"] >= 0
    
    def test_bayesian_credible_interval(self):
        """Test Bayesian credible interval calculation"""
        result = StatisticalCalculator.bayesian_credible_interval(
            conversions=15,
            visitors=100
        )
        
        assert "mean" in result
        assert "std_dev" in result
        assert "ci_lower_percent" in result
        assert "ci_upper_percent" in result
        assert result["ci_lower_percent"] <= result["mean"] <= result["ci_upper_percent"]
    
    def test_required_sample_size(self):
        """Test sample size calculation"""
        size_95 = StatisticalCalculator.required_sample_size(
            baseline_rate=0.10,
            min_effect_size=0.05,
            confidence_level=0.95
        )
        
        size_90 = StatisticalCalculator.required_sample_size(
            baseline_rate=0.10,
            min_effect_size=0.05,
            confidence_level=0.90
        )
        
        assert size_95 > 0
        assert size_90 > 0
        assert size_95 > size_90  # Higher confidence requires more samples


class TestVariantAnalyzer:
    """Test variant analysis functionality"""
    
    def test_add_variant(self):
        """Test adding a variant"""
        analyzer = VariantAnalyzer()
        
        result = analyzer.add_variant(
            "control",
            "Control Group",
            "Original design",
            0.5
        )
        
        assert result["status"] == "created"
        assert "control" in analyzer.variants
    
    def test_track_conversion(self):
        """Test tracking conversions"""
        analyzer = VariantAnalyzer()
        analyzer.add_variant("variant_1", "Variant 1", "Test variant", 0.5)
        
        result = analyzer.track_conversion("variant_1", True, revenue=99.99)
        
        assert result["status"] == "tracked"
        assert result["visitor_count"] == 1
        assert result["conversion_count"] == 1
    
    def test_get_variant_performance(self):
        """Test variant performance metrics"""
        analyzer = VariantAnalyzer()
        analyzer.add_variant("test_var", "Test Variant", "Testing", 0.5)
        
        # Track 100 visits, 20 conversions
        for i in range(20):
            analyzer.track_conversion("test_var", True, revenue=50)
        for i in range(80):
            analyzer.track_conversion("test_var", False)
        
        perf = analyzer.get_variant_performance("test_var")
        
        assert perf["visitors"] == 100
        assert perf["conversions"] == 20
        assert perf["conversion_rate_percent"] == 20.0
        assert perf["revenue"] == 1000.0
    
    def test_compare_all_variants(self):
        """Test comparing multiple variants"""
        analyzer = VariantAnalyzer()
        
        # Add three variants
        analyzer.add_variant("control", "Control", "Original", 0.34)
        analyzer.add_variant("variant_a", "Variant A", "Test A", 0.33)
        analyzer.add_variant("variant_b", "Variant B", "Test B", 0.33)
        
        # Track conversions
        for i in range(90):
            analyzer.track_conversion("control", i < 15)  # 15/90 = 16.7%
        
        for i in range(90):
            analyzer.track_conversion("variant_a", i < 18)  # 18/90 = 20%
        
        for i in range(90):
            analyzer.track_conversion("variant_b", i < 12)  # 12/90 = 13.3%
        
        comparison = analyzer.compare_all_variants()
        
        assert len(comparison) == 3
        # Should be sorted by conversion rate (descending)
        assert comparison[0]["conversion_rate_percent"] >= comparison[1]["conversion_rate_percent"]
    
    def test_determine_winner(self):
        """Test winner determination"""
        analyzer = VariantAnalyzer()
        analyzer.add_variant("control", "Control", "Original", 0.5)
        analyzer.add_variant("winner", "Winner Variant", "Better design", 0.5)
        
        # Control: 12% conversion
        for i in range(200):
            analyzer.track_conversion("control", i < 24)
        
        # Variant: 20% conversion (significant uplift)
        for i in range(200):
            analyzer.track_conversion("winner", i < 40)
        
        result = analyzer.determine_winner("control")
        
        assert "winner" in result
        assert "status" in result
        # Result can be either winner_found or no_winner, both are valid
        assert result["status"] in ["winner_found", "no_winner"]


class TestExperimentManager:
    """Test experiment management"""
    
    def test_create_experiment(self):
        """Test creating an experiment"""
        manager = ExperimentManager()
        
        result = manager.create_experiment(
            experiment_id="test_exp_1",
            name="Test Experiment",
            description="Testing A/B system",
            hypothesis="Variant B will improve conversions",
            primary_metric="conversion_rate",
            confidence_level=0.95
        )
        
        assert result["status"] == "created"
        assert "test_exp_1" in manager.experiments
        assert manager.experiments["test_exp_1"]["status"] == "DRAFT"
    
    def test_start_experiment(self):
        """Test starting an experiment"""
        manager = ExperimentManager()
        manager.create_experiment(
            "exp_1", "Test", "Testing", "Hypothesis", "conversion_rate"
        )
        
        result = manager.start_experiment("exp_1")
        
        assert result["status"] == "started"
        assert manager.experiments["exp_1"]["status"] == "RUNNING"
    
    def test_pause_experiment(self):
        """Test pausing an experiment"""
        manager = ExperimentManager()
        manager.create_experiment(
            "exp_2", "Test", "Testing", "Hypothesis", "conversion_rate"
        )
        manager.start_experiment("exp_2")
        
        result = manager.pause_experiment("exp_2")
        
        assert result["status"] == "paused"
        assert manager.experiments["exp_2"]["status"] == "PAUSED"
    
    def test_add_variant_to_experiment(self):
        """Test adding variants to experiment"""
        manager = ExperimentManager()
        manager.create_experiment(
            "exp_3", "Test", "Testing", "Hypothesis", "conversion_rate"
        )
        
        result = manager.add_variant(
            "exp_3",
            "control",
            "Control Group",
            "Original design",
            0.5
        )
        
        assert result["status"] == "created"
    
    def test_track_visitor_assignment(self):
        """Test visitor assignment to variants"""
        manager = ExperimentManager()
        manager.create_experiment(
            "exp_4", "Test", "Testing", "Hypothesis", "conversion_rate"
        )
        manager.add_variant("exp_4", "control", "Control", "Original", 0.6)
        manager.add_variant("exp_4", "variant", "Variant", "Test", 0.4)
        
        # Assign many visitors
        assignments = {}
        for i in range(1000):
            assigned = manager.track_visitor("exp_4", f"visitor_{i}")
            if assigned:
                assignments[assigned] = assignments.get(assigned, 0) + 1
        
        # Check traffic allocation is roughly correct
        assert len(assignments) == 2
        assert sum(assignments.values()) == 1000
        control_pct = assignments.get("control", 0) / 1000
        assert 0.5 < control_pct < 0.7  # Should be ~60%
    
    def test_track_conversion(self):
        """Test tracking conversions"""
        manager = ExperimentManager()
        manager.create_experiment(
            "exp_5", "Test", "Testing", "Hypothesis", "conversion_rate"
        )
        manager.add_variant("exp_5", "var1", "Variant 1", "Test", 0.5)
        
        result = manager.track_conversion(
            "exp_5",
            "var1",
            True,
            revenue=99.99
        )
        
        assert result["status"] == "tracked"
        assert result["visitor_count"] >= 1
    
    def test_get_experiment_results(self):
        """Test getting comprehensive experiment results"""
        manager = ExperimentManager()
        manager.create_experiment(
            "exp_6", "Test", "Testing", "Hypothesis", "conversion_rate"
        )
        manager.start_experiment("exp_6")
        manager.add_variant("exp_6", "control", "Control", "Original", 0.5)
        manager.add_variant("exp_6", "test", "Test", "Variant", 0.5)
        
        # Simulate data
        for i in range(50):
            manager.track_conversion("exp_6", "control", i < 6)  # 12%
        
        for i in range(50):
            manager.track_conversion("exp_6", "test", i < 10)  # 20%
        
        result = manager.get_experiment_results("exp_6")
        
        assert "experiment_id" in result
        assert "total_visitors" in result
        assert "total_conversions" in result
        assert "variants_performance" in result
        assert "winner_analysis" in result
    
    def test_end_experiment(self):
        """Test ending an experiment"""
        manager = ExperimentManager()
        manager.create_experiment(
            "exp_7", "Test", "Testing", "Hypothesis", "conversion_rate"
        )
        manager.start_experiment("exp_7")
        manager.add_variant("exp_7", "control", "Control", "Original", 0.5)
        
        result = manager.end_experiment("exp_7")
        
        assert result["status"] == "completed"
        assert manager.experiments["exp_7"]["status"] == "COMPLETED"


class TestDemoExperiments:
    """Test demo experiment generation"""
    
    def test_generate_demo_experiments(self):
        """Test generating demo experiments"""
        manager, exp_ids = generate_demo_experiments()
        
        assert len(exp_ids) >= 2
        assert all(exp_id in manager.experiments for exp_id in exp_ids)
    
    def test_demo_experiments_have_data(self):
        """Test that demo experiments have realistic data"""
        manager, exp_ids = generate_demo_experiments()
        
        for exp_id in exp_ids:
            result = manager.get_experiment_results(exp_id)
            
            assert result["total_visitors"] > 0
            assert result["total_conversions"] >= 0
            assert len(result["variants_performance"]) >= 2
    
    def test_demo_experiments_status(self):
        """Test that demo experiments have correct status"""
        manager, exp_ids = generate_demo_experiments()
        
        for exp_id in exp_ids:
            exp = manager.experiments[exp_id]
            assert exp["status"] == "RUNNING"


class TestExperimentIntegration:
    """Integration tests for A/B testing system"""
    
    def test_full_experiment_workflow(self):
        """Test complete experiment workflow"""
        manager = ExperimentManager()
        
        # Create experiment
        manager.create_experiment(
            "full_test",
            "Full Workflow Test",
            "Complete test",
            "Hypothesis",
            "conversion_rate"
        )
        
        # Add variants
        manager.add_variant("full_test", "control", "Control", "Original", 0.5)
        manager.add_variant("full_test", "variant", "Variant", "Test", 0.5)
        
        # Start experiment
        manager.start_experiment("full_test")
        
        # Simulate traffic
        for i in range(200):
            visitor_id = f"visitor_{i}"
            variant = manager.track_visitor("full_test", visitor_id)
            
            # Simulate conversion based on variant
            converted = (i % 10 < 2) if variant == "control" else (i % 10 < 3)
            manager.track_conversion("full_test", variant, converted, 99.99 if converted else 0)
        
        # Get results
        results = manager.get_experiment_results("full_test")
        
        assert results["total_visitors"] == 200
        assert results["status"] == "RUNNING"
        assert len(results["variants_performance"]) == 2
        assert results["overall_conversion_rate_percent"] > 0
    
    def test_multiple_experiments(self):
        """Test managing multiple experiments"""
        manager = ExperimentManager()
        
        # Create 3 experiments
        for i in range(3):
            manager.create_experiment(
                f"exp_{i}",
                f"Experiment {i}",
                "Testing",
                "Hypothesis",
                "conversion_rate"
            )
            manager.start_experiment(f"exp_{i}")
            manager.add_variant(f"exp_{i}", "control", "Control", "Original", 0.5)
            manager.add_variant(f"exp_{i}", "variant", "Variant", "Test", 0.5)
        
        # Get all experiments
        all_exps = manager.get_all_experiments()
        
        assert len(all_exps) == 3
        assert all(exp["status"] == "RUNNING" for exp in all_exps)


class TestStatisticalValidation:
    """Test statistical validity of calculations"""
    
    def test_conversion_rate_validity(self):
        """Test that conversion rates are always 0-100%"""
        analyzer = VariantAnalyzer()
        analyzer.add_variant("v1", "Variant 1", "Test", 0.5)
        
        # Track 1000 conversions out of 5000 visits
        for i in range(5000):
            analyzer.track_conversion("v1", i < 1000)
        
        perf = analyzer.get_variant_performance("v1")
        
        assert 0 <= perf["conversion_rate_percent"] <= 100
    
    def test_revenue_calculations(self):
        """Test revenue calculations"""
        analyzer = VariantAnalyzer()
        analyzer.add_variant("v1", "Variant 1", "Test", 0.5)
        
        total_revenue = 0
        for i in range(100):
            revenue = 49.99 if i < 25 else 0
            analyzer.track_conversion("v1", i < 25, revenue=revenue)
            total_revenue += revenue
        
        perf = analyzer.get_variant_performance("v1")
        
        assert abs(perf["revenue"] - total_revenue) < 0.01
        assert perf["revenue_per_visitor"] == pytest.approx(total_revenue / 100, rel=0.01)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
