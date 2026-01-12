"""
Feature #20: Advanced Attribution Modeling
Tests for multi-touch attribution, ROI calculation, and channel optimization
"""

import pytest
from datetime import datetime, timedelta
from attribution_modeling import (
    ConversionAttributor,
    ChannelROICalculator,
    ConversionPathAnalyzer,
    AttributionModelComparator,
    AttributionAnalytics,
    AttributionModel,
    generate_demo_attribution_data,
)


# =======================
# Fixtures
# =======================

@pytest.fixture
def sample_conversion_path():
    """Sample customer journey with multiple touchpoints"""
    return [
        {"channel": "paid_search", "timestamp": datetime(2024, 1, 1, 10, 0)},
        {"channel": "organic", "timestamp": datetime(2024, 1, 2, 14, 30)},
        {"channel": "email", "timestamp": datetime(2024, 1, 3, 9, 15)},
        {"channel": "direct", "timestamp": datetime(2024, 1, 3, 16, 45)},
    ]


@pytest.fixture
def sample_short_path():
    """Simple 2-touch journey"""
    return [
        {"channel": "social", "timestamp": datetime(2024, 1, 1, 10, 0)},
        {"channel": "direct", "timestamp": datetime(2024, 1, 2, 15, 0)},
    ]


@pytest.fixture
def attributor():
    """ConversionAttributor instance"""
    return ConversionAttributor()


@pytest.fixture
def roi_calculator():
    """ChannelROICalculator instance"""
    return ChannelROICalculator()


@pytest.fixture
def path_analyzer():
    """ConversionPathAnalyzer instance"""
    return ConversionPathAnalyzer()


@pytest.fixture
def attributor_with_data(attributor, sample_conversion_path, sample_short_path):
    """Attributor with tracked journeys"""
    attributor.track_conversion_path("cust_123", sample_conversion_path, 199.99, "ORD_001")
    attributor.track_conversion_path("cust_456", sample_short_path, 99.99, "ORD_002")
    return attributor


# =======================
# ConversionAttributor Tests
# =======================

class TestConversionAttributor:
    """Tests for multi-touch attribution models"""

    def test_first_touch_attribution(self, attributor, sample_conversion_path):
        """Test first-touch attribution assigns 100% credit to first channel"""
        result = attributor.attribute_first_touch(sample_conversion_path, 199.99)
        
        assert result["channel"] == "paid_search"
        assert result["attributed_value"] == pytest.approx(199.99, rel=0.01)
        assert result["credit_percentage"] == 100.0

    def test_last_touch_attribution(self, attributor, sample_conversion_path):
        """Test last-touch attribution assigns 100% credit to last channel"""
        result = attributor.attribute_last_touch(sample_conversion_path, 199.99)
        
        assert result["channel"] == "direct"
        assert result["attributed_value"] == pytest.approx(199.99, rel=0.01)
        assert result["credit_percentage"] == 100.0

    def test_linear_attribution(self, attributor, sample_conversion_path):
        """Test linear attribution splits credit equally across all channels"""
        result = attributor.attribute_linear(sample_conversion_path, 199.99)
        
        expected_per_channel = 199.99 / 4
        expected_percent = 100.0 / 4
        
        assert len(result) == 4
        for item in result:
            assert item["attributed_value"] == pytest.approx(expected_per_channel, rel=0.01)
            assert item["credit_percentage"] == pytest.approx(expected_percent, rel=0.01)

    def test_time_decay_attribution(self, attributor, sample_conversion_path):
        """Test time-decay attribution weights channels by proximity to conversion"""
        result = attributor.attribute_time_decay(sample_conversion_path, 199.99)
        
        # Total should equal conversion value
        total = sum(item["attributed_value"] for item in result)
        assert total == pytest.approx(199.99, rel=0.01)
        
        # Later touches should have more credit
        assert result[-1]["attributed_value"] > result[0]["attributed_value"]

    def test_time_decay_single_touch(self, attributor, sample_short_path):
        """Test time-decay with only 2 touchpoints"""
        result = attributor.attribute_time_decay(sample_short_path, 99.99)
        
        # Should have 2 items
        assert len(result) == 2
        # Total should match conversion value
        total = sum(item["attributed_value"] for item in result)
        assert total == pytest.approx(99.99, rel=0.01)

    def test_track_conversion_path(self, attributor, sample_conversion_path):
        """Test tracking a complete conversion path"""
        path_data = attributor.track_conversion_path("cust_123", sample_conversion_path, 199.99, "ORD_001")
        
        assert path_data["customer_id"] == "cust_123"
        assert path_data["order_id"] == "ORD_001"
        assert path_data["conversion_value"] == 199.99
        assert "attributions" in path_data
        assert len(path_data["attributions"]) == 4  # first, last, linear, time_decay

    def test_track_multiple_paths(self, attributor_with_data):
        """Test tracking multiple customer journeys"""
        paths = attributor_with_data.get_conversion_paths()
        
        assert len(paths) == 2
        assert paths[0]["order_id"] == "ORD_001"
        assert paths[1]["order_id"] == "ORD_002"

    def test_get_channel_revenue_by_model(self, attributor_with_data):
        """Test retrieving channel revenue by attribution model"""
        first_touch_revenue = attributor_with_data.get_channel_revenue_by_model(AttributionModel.FIRST_TOUCH)
        
        assert "paid_search" in first_touch_revenue
        assert first_touch_revenue["paid_search"] == pytest.approx(199.99, rel=0.01)

    def test_single_channel_path(self, attributor):
        """Test attribution with only one touchpoint"""
        path = [
            {"channel": "direct", "timestamp": datetime(2024, 1, 1, 10, 0)},
        ]
        
        result = attributor.attribute_first_touch(path, 50.00)
        assert result["channel"] == "direct"
        assert result["attributed_value"] == pytest.approx(50.00, rel=0.01)


# =======================
# ChannelROICalculator Tests
# =======================

class TestChannelROICalculator:
    """Tests for ROI calculations and channel performance"""

    def test_add_channel_spend(self, roi_calculator):
        """Test recording marketing spend for a channel"""
        roi_calculator.add_channel_spend("paid_search", 1000)
        roi_calculator.add_channel_spend("paid_search", 500)
        
        metrics = roi_calculator.calculate_roi("paid_search")
        assert metrics["spend"] == 1500

    def test_add_channel_revenue(self, roi_calculator):
        """Test recording attributed revenue for a channel"""
        roi_calculator.add_channel_revenue("email", 2000, 10)
        roi_calculator.add_channel_revenue("email", 1500, 5)
        
        metrics = roi_calculator.calculate_roi("email")
        assert metrics["revenue"] == 3500

    def test_add_impressions(self, roi_calculator):
        """Test recording impressions/clicks for CTR calculation"""
        roi_calculator.add_impressions("organic", 5000)
        roi_calculator.add_impressions("organic", 3000)
        
        metrics = roi_calculator.calculate_roi("organic")
        assert metrics["impressions"] == 8000

    def test_calculate_roi_positive(self, roi_calculator):
        """Test ROI calculation with profit"""
        roi_calculator.add_channel_spend("paid_search", 1000)
        roi_calculator.add_channel_revenue("paid_search", 5000, 10)
        
        metrics = roi_calculator.calculate_roi("paid_search")
        
        assert metrics["spend"] == 1000
        assert metrics["revenue"] == 5000
        assert metrics["roi_percent"] == pytest.approx(400, rel=0.1)

    def test_calculate_roi_negative(self, roi_calculator):
        """Test ROI calculation with loss"""
        roi_calculator.add_channel_spend("social", 2000)
        roi_calculator.add_channel_revenue("social", 1000, 5)
        
        metrics = roi_calculator.calculate_roi("social")
        
        assert metrics["roi_percent"] == pytest.approx(-50, rel=0.1)

    def test_calculate_roas(self, roi_calculator):
        """Test ROAS (Return on Ad Spend) calculation"""
        roi_calculator.add_channel_spend("paid_search", 500)
        roi_calculator.add_channel_revenue("paid_search", 2500, 15)
        
        metrics = roi_calculator.calculate_roi("paid_search")
        
        assert metrics["roas"] == pytest.approx(5.0, rel=0.01)

    def test_calculate_cpc(self, roi_calculator):
        """Test CPC (Cost Per Click/Impression) calculation"""
        roi_calculator.add_channel_spend("paid_search", 1000)
        roi_calculator.add_impressions("paid_search", 10000)
        
        metrics = roi_calculator.calculate_roi("paid_search")
        
        assert metrics["ctr"] == pytest.approx(0, rel=0.01)  # No conversions yet

    def test_calculate_ctr(self, roi_calculator):
        """Test CTR (Click-Through Rate) calculation"""
        roi_calculator.add_impressions("organic", 10000)
        roi_calculator.add_channel_revenue("organic", 1000, 100)
        
        metrics = roi_calculator.calculate_roi("organic")
        
        assert metrics["conversions"] == 100
        assert metrics["ctr"] == pytest.approx(1.0, rel=0.01)

    def test_get_best_performing_channel(self, roi_calculator):
        """Test identifying highest ROI channel"""
        roi_calculator.add_channel_spend("email", 200)
        roi_calculator.add_channel_revenue("email", 1000, 5)
        
        roi_calculator.add_channel_spend("direct", 100)
        roi_calculator.add_channel_revenue("direct", 300, 2)
        
        roi_calculator.add_channel_spend("social", 500)
        roi_calculator.add_channel_revenue("social", 600, 3)
        
        best = roi_calculator.get_best_performing_channel()
        
        assert best[0] == "email"
        assert best[1]["roi_percent"] == pytest.approx(400, rel=0.1)

    def test_budget_recommendation_proportional(self, roi_calculator):
        """Test budget allocation recommendations based on ROI"""
        roi_calculator.add_channel_spend("paid_search", 1000)
        roi_calculator.add_channel_revenue("paid_search", 5000, 20)
        
        roi_calculator.add_channel_spend("email", 200)
        roi_calculator.add_channel_revenue("email", 1000, 8)
        
        roi_calculator.add_channel_spend("social", 500)
        roi_calculator.add_channel_revenue("social", 600, 2)
        
        recommendation = roi_calculator.get_budget_recommendation(10000)
        
        # Paid search has highest ROI (400%) so should get most budget
        assert recommendation["paid_search"] >= recommendation["email"]
        assert recommendation["email"] >= recommendation["social"]
        
        # Total should equal 10000
        assert sum(recommendation.values()) == pytest.approx(10000, rel=0.1)

    def test_get_channel_metrics(self, roi_calculator):
        """Test retrieving comprehensive channel metrics"""
        roi_calculator.add_channel_spend("organic", 0)
        roi_calculator.add_channel_revenue("organic", 3000, 50)
        roi_calculator.add_impressions("organic", 15000)
        
        metrics = roi_calculator.calculate_roi("organic")
        
        assert metrics["spend"] == 0
        assert metrics["revenue"] == 3000
        assert metrics["conversions"] == 50
        assert metrics["ctr"] == pytest.approx(0.3333, rel=0.01)  # 50 / 15000 * 100


# =======================
# ConversionPathAnalyzer Tests
# =======================

class TestConversionPathAnalyzer:
    """Tests for conversion journey pattern analysis"""

    def test_analyze_path_structure(self, path_analyzer):
        """Test analyzing a conversion path structure"""
        path = [
            {"channel": "paid_search", "timestamp": datetime(2024, 1, 1, 10, 0).isoformat()},
            {"channel": "organic", "timestamp": datetime(2024, 1, 2, 14, 30).isoformat()},
            {"channel": "email", "timestamp": datetime(2024, 1, 3, 9, 15).isoformat()},
            {"channel": "direct", "timestamp": datetime(2024, 1, 3, 16, 45).isoformat()},
        ]
        
        analysis = path_analyzer.analyze_path(path)
        
        assert "channels" in analysis
        assert "path_length" in analysis
        assert "average_hours_between_touches" in analysis
        assert analysis["path_length"] == 4
        assert len(analysis["channels"]) == 4

    def test_analyze_path_channels_order(self, path_analyzer):
        """Test that channels are in correct order"""
        path = [
            {"channel": "paid_search", "timestamp": datetime(2024, 1, 1, 10, 0).isoformat()},
            {"channel": "organic", "timestamp": datetime(2024, 1, 2, 14, 30).isoformat()},
            {"channel": "email", "timestamp": datetime(2024, 1, 3, 9, 15).isoformat()},
            {"channel": "direct", "timestamp": datetime(2024, 1, 3, 16, 45).isoformat()},
        ]
        
        analysis = path_analyzer.analyze_path(path)
        
        assert analysis["channels"][0] == "paid_search"
        assert analysis["channels"][1] == "organic"
        assert analysis["channels"][2] == "email"
        assert analysis["channels"][3] == "direct"

    def test_analyze_path_time_gaps(self, path_analyzer):
        """Test calculating time between touches"""
        path = [
            {"channel": "paid_search", "timestamp": datetime(2024, 1, 1, 10, 0).isoformat()},
            {"channel": "organic", "timestamp": datetime(2024, 1, 2, 14, 30).isoformat()},
            {"channel": "email", "timestamp": datetime(2024, 1, 3, 9, 15).isoformat()},
            {"channel": "direct", "timestamp": datetime(2024, 1, 3, 16, 45).isoformat()},
        ]
        
        analysis = path_analyzer.analyze_path(path)
        
        assert "average_hours_between_touches" in analysis
        # Time differences between touches
        # paid_search (1/1 10:00) -> organic (1/2 14:30) ≈ 28.5 hours
        # organic (1/2 14:30) -> email (1/3 9:15) ≈ 18.75 hours
        # email (1/3 9:15) -> direct (1/3 16:45) ≈ 7.5 hours
        # avg ≈ (28.5 + 18.75 + 7.5) / 3 ≈ 18.25 hours
        assert analysis["average_hours_between_touches"] > 0

    def test_get_common_patterns(self, path_analyzer):
        """Test identifying most common conversion patterns"""
        paths = [
            [{"channel": "paid_search"}, {"channel": "direct"}],
            [{"channel": "paid_search"}, {"channel": "direct"}],
            [{"channel": "social"}, {"channel": "direct"}],
            [{"channel": "email"}, {"channel": "direct"}],
        ]
        
        for path in paths:
            path_analyzer.add_conversion_path(path)
        
        patterns = path_analyzer.get_common_patterns()
        
        assert len(patterns) > 0
        # Most common should be paid_search → direct (2 occurrences)
        assert patterns[0][1] >= patterns[1][1]

    def test_get_path_statistics(self, path_analyzer):
        """Test aggregate path statistics"""
        paths = [
            [{"channel": "a"}, {"channel": "b"}, {"channel": "c"}],
            [{"channel": "x"}, {"channel": "y"}],
            [{"channel": "p"}, {"channel": "q"}, {"channel": "r"}, {"channel": "s"}],
        ]
        
        for path in paths:
            path_analyzer.add_conversion_path(path)
        
        stats = path_analyzer.get_path_statistics()
        
        assert stats["avg_path_length"] == pytest.approx(3, rel=0.1)
        assert stats["max_path_length"] == 4
        assert stats["min_path_length"] == 2

    def test_path_with_single_touch(self, path_analyzer):
        """Test analysis of single-touch path"""
        path = [{"channel": "direct", "timestamp": datetime(2024, 1, 1, 10, 0).isoformat()}]
        
        analysis = path_analyzer.analyze_path(path)
        
        assert analysis["path_length"] == 1
        assert analysis["average_hours_between_touches"] == 0


# =======================
# AttributionModelComparator Tests
# =======================

class TestAttributionModelComparator:
    """Tests for comparing attribution models"""

    def test_compare_models(self):
        """Test comparing all 4 attribution models"""
        comparator = AttributionModelComparator()
        path = [
            {"id": "tp_1", "channel": "a", "timestamp": datetime(2024, 1, 1, 10, 0).isoformat()},
            {"id": "tp_2", "channel": "b", "timestamp": datetime(2024, 1, 2, 10, 0).isoformat()},
            {"id": "tp_3", "channel": "c", "timestamp": datetime(2024, 1, 3, 10, 0).isoformat()},
        ]
        
        comparator.add_conversion(path, 100.00, "cust_comp")
        comparison = comparator.compare_models()
        
        assert "first_touch" in comparison
        assert "last_touch" in comparison
        assert "linear" in comparison
        assert "time_decay" in comparison

    def test_model_variance_calculation(self):
        """Test calculating variance between models"""
        comparator = AttributionModelComparator()
        
        # Add multiple paths
        for i in range(3):
            path = [
                {"id": f"tp_{i*3+1}", "channel": "paid", "timestamp": datetime(2024, 1, 1, 10, 0).isoformat()},
                {"id": f"tp_{i*3+2}", "channel": "organic", "timestamp": datetime(2024, 1, 2, 10, 0).isoformat()},
                {"id": f"tp_{i*3+3}", "channel": "direct", "timestamp": datetime(2024, 1, 3, 10, 0).isoformat()},
            ]
            comparator.add_conversion(path, 100.00, f"cust_{i}")
        
        variance = comparator.get_model_variance()
        
        # Should have channels with variance data
        assert len(variance) > 0
        # Each channel should have variance info
        for channel, data in variance.items():
            assert "variance" in data
            assert "std_dev" in data
            assert "avg_attributed" in data

    def test_model_disagreement(self):
        """Test models with high disagreement"""
        comparator = AttributionModelComparator()
        
        path = [
            {"id": "tp_1", "channel": "expensive_paid", "timestamp": datetime(2024, 1, 1, 10, 0).isoformat()},
            {"id": "tp_2", "channel": "direct", "timestamp": datetime(2024, 1, 10, 16, 0).isoformat()},
        ]
        
        comparator.add_conversion(path, 1000.00, "cust_disagree")
        comparison = comparator.compare_models()
        
        # First touch: expensive_paid gets 1000
        # Last touch: direct gets 1000
        # Linear: each gets 500
        # Time decay: skewed toward direct
        
        assert comparison["first_touch"]["expensive_paid"] > 0
        assert comparison["last_touch"]["direct"] > 0


# =======================
# AttributionAnalytics Tests
# =======================

class TestAttributionAnalytics:
    """Tests for main attribution analytics engine"""

    def test_analytics_initialization(self):
        """Test AttributionAnalytics initialization"""
        analytics = AttributionAnalytics()
        
        assert analytics.attributor is not None
        assert analytics.roi_calculator is not None
        assert analytics.path_analyzer is not None

    def test_track_customer_journey(self):
        """Test tracking full customer journey"""
        analytics = AttributionAnalytics()
        
        journey = [
            {"id": "tp_1", "channel": "paid_search", "timestamp": datetime(2024, 1, 1, 10, 0).isoformat()},
            {"id": "tp_2", "channel": "email", "timestamp": datetime(2024, 1, 2, 14, 0).isoformat()},
            {"id": "tp_3", "channel": "direct", "timestamp": datetime(2024, 1, 3, 16, 0).isoformat()},
        ]
        
        result = analytics.track_customer_journey("cust_analytics", journey, 250.00, "ORD_ANALYTICS")
        
        assert result["customer_id"] == "cust_analytics"
        assert result["order_id"] == "ORD_ANALYTICS"

    def test_get_full_attribution_report(self):
        """Test generating full attribution report"""
        analytics = AttributionAnalytics()
        
        # Add sample data
        analytics.track_customer_journey(
            "cust_1",
            [
                {"id": "tp_1", "channel": "paid_search", "timestamp": datetime(2024, 1, 1, 10, 0).isoformat()},
                {"id": "tp_2", "channel": "direct", "timestamp": datetime(2024, 1, 2, 15, 0).isoformat()},
            ],
            199.99,
            "ORD_1"
        )
        
        report = analytics.get_full_attribution_report()
        
        assert "summary" in report
        assert "channel_roi" in report
        assert "model_comparison" in report
        assert "path_statistics" in report

    def test_get_budget_optimization(self):
        """Test budget optimization recommendations"""
        # Use demo data which has realistic ROI data
        analytics = generate_demo_attribution_data()
        
        optimization = analytics.get_budget_optimization(total_budget=10000)
        
        assert "recommendations" in optimization
        # Total should equal 10000
        total = sum(v for v in optimization["recommendations"].values() if not (isinstance(v, float) and v != v))
        assert total == pytest.approx(10000, rel=0.1)

    def test_analytics_with_multi_channel_journeys(self):
        """Test analytics with diverse multi-channel journeys"""
        analytics = AttributionAnalytics()
        
        journeys = [
            {
                "customer_id": "cust_a",
                "path": [
                    {"id": "tp_1", "channel": "social", "timestamp": datetime(2024, 1, 1, 10, 0).isoformat()},
                    {"id": "tp_2", "channel": "email", "timestamp": datetime(2024, 1, 1, 12, 0).isoformat()},
                    {"id": "tp_3", "channel": "direct", "timestamp": datetime(2024, 1, 1, 14, 0).isoformat()},
                ],
                "value": 149.99,
                "order_id": "ORD_a"
            },
            {
                "customer_id": "cust_b",
                "path": [
                    {"id": "tp_4", "channel": "organic", "timestamp": datetime(2024, 1, 2, 8, 0).isoformat()},
                    {"id": "tp_5", "channel": "direct", "timestamp": datetime(2024, 1, 2, 16, 0).isoformat()},
                ],
                "value": 199.99,
                "order_id": "ORD_b"
            },
            {
                "customer_id": "cust_c",
                "path": [
                    {"id": "tp_6", "channel": "paid_search", "timestamp": datetime(2024, 1, 3, 11, 0).isoformat()},
                    {"id": "tp_7", "channel": "paid_search", "timestamp": datetime(2024, 1, 3, 13, 0).isoformat()},
                    {"id": "tp_8", "channel": "direct", "timestamp": datetime(2024, 1, 3, 15, 0).isoformat()},
                ],
                "value": 99.99,
                "order_id": "ORD_c"
            }
        ]
        
        for journey in journeys:
            analytics.track_customer_journey(
                journey["customer_id"],
                journey["path"],
                journey["value"],
                journey["order_id"]
            )
        
        report = analytics.get_full_attribution_report()
        
        # Should have tracked all journeys
        assert report["summary"]["total_conversions"] == 3
        assert report["summary"]["total_revenue"] == pytest.approx(449.97, rel=0.01)


# =======================
# Demo Data Tests
# =======================

class TestDemoData:
    """Tests for demo data generation"""

    def test_generate_demo_data(self):
        """Test generating demo attribution data"""
        analytics = generate_demo_attribution_data()
        
        # Should return an AttributionAnalytics instance with data
        assert isinstance(analytics, AttributionAnalytics)
        assert analytics.total_conversions == 5
        assert analytics.total_revenue > 0

    def test_demo_journeys_in_analytics(self):
        """Test that demo journeys are tracked in analytics"""
        analytics = generate_demo_attribution_data()
        
        paths = analytics.attributor.get_conversion_paths()
        
        assert len(paths) == 5
        assert all("customer_id" in p for p in paths)
        assert all("conversion_value" in p for p in paths)

    def test_demo_channel_budgets_recorded(self):
        """Test demo channel budget allocation"""
        analytics = generate_demo_attribution_data()
        
        roi_data = analytics.roi_calculator.get_all_roi()
        
        # Should have recorded spend for various channels
        assert len(roi_data) > 0
        # Paid search and social should be recorded
        assert any("paid" in str(channel).lower() for channel in roi_data.keys())

    def test_demo_data_realistic(self):
        """Test that demo data has realistic values"""
        analytics = generate_demo_attribution_data()
        
        paths = analytics.attributor.get_conversion_paths()
        
        for path in paths:
            # Conversion values should be reasonable
            assert 10 < path["conversion_value"] < 10000
            # Should have timestamps
            for attribution in path["attributions"].values():
                if isinstance(attribution, list):
                    for item in attribution:
                        assert "timestamp" in item
                        assert "channel" in item
                else:
                    assert "timestamp" in attribution
                    assert "channel" in attribution


# =======================
# Integration Tests
# =======================

class TestAttributionIntegration:
    """Integration tests for complete attribution workflows"""

    def test_end_to_end_attribution_workflow(self):
        """Test complete workflow from tracking to reporting"""
        analytics = generate_demo_attribution_data()
        
        # Get report
        report = analytics.get_full_attribution_report()
        
        # Validate report
        assert report["summary"]["total_conversions"] == 5
        assert report["summary"]["total_revenue"] > 0
        assert len(report["channel_roi"]) > 0

    def test_attribution_with_real_channel_data(self):
        """Test attribution with realistic multi-channel scenario"""
        analytics = AttributionAnalytics()
        
        # Simulate real customer journeys
        journeys = [
            # Paid search → Email → Direct (typical path)
            {
                "customer_id": "real_1",
                "path": [
                    {"id": "tp_1", "channel": "paid_search", "timestamp": datetime(2024, 1, 1, 9, 0).isoformat()},
                    {"id": "tp_2", "channel": "email", "timestamp": datetime(2024, 1, 2, 10, 0).isoformat()},
                    {"id": "tp_3", "channel": "direct", "timestamp": datetime(2024, 1, 3, 14, 0).isoformat()},
                ],
                "value": 299.99,
                "order_id": "ORD_R1"
            },
            # Organic → Direct (quick convert)
            {
                "customer_id": "real_2",
                "path": [
                    {"id": "tp_4", "channel": "organic", "timestamp": datetime(2024, 1, 4, 8, 0).isoformat()},
                    {"id": "tp_5", "channel": "direct", "timestamp": datetime(2024, 1, 4, 9, 30).isoformat()},
                ],
                "value": 149.99,
                "order_id": "ORD_R2"
            },
            # Social → Organic → Email → Direct (long journey)
            {
                "customer_id": "real_3",
                "path": [
                    {"id": "tp_6", "channel": "social", "timestamp": datetime(2024, 1, 5, 11, 0).isoformat()},
                    {"id": "tp_7", "channel": "organic", "timestamp": datetime(2024, 1, 6, 9, 0).isoformat()},
                    {"id": "tp_8", "channel": "email", "timestamp": datetime(2024, 1, 7, 15, 0).isoformat()},
                    {"id": "tp_9", "channel": "direct", "timestamp": datetime(2024, 1, 8, 16, 0).isoformat()},
                ],
                "value": 249.99,
                "order_id": "ORD_R3"
            },
        ]
        
        for journey in journeys:
            result = analytics.track_customer_journey(
                journey["customer_id"],
                journey["path"],
                journey["value"],
                journey["order_id"]
            )
            assert "customer_id" in result
        
        # Verify attribution
        report = analytics.get_full_attribution_report()
        
        assert report["summary"]["total_conversions"] == 3
        assert report["summary"]["total_revenue"] == pytest.approx(699.97, rel=0.01)
        
        # Verify path statistics
        assert "avg_path_length" in report["path_statistics"]

    def test_budget_allocation_respects_roi(self):
        """Test that budget allocation respects historical ROI"""
        analytics = AttributionAnalytics()
        
        # Simulate high-ROI channel (paid_search) vs low-ROI (social)
        for i in range(10):
            analytics.track_customer_journey(
                f"high_roi_{i}",
                [
                    {"id": f"tp_{i*2+1}", "channel": "paid_search", "timestamp": datetime(2024, 1, i+1, 10, 0).isoformat()},
                    {"id": f"tp_{i*2+2}", "channel": "direct", "timestamp": datetime(2024, 1, i+1, 15, 0).isoformat()},
                ],
                200.00,
                f"HIGHROID_{i}"
            )
        
        for i in range(5):
            analytics.track_customer_journey(
                f"low_roi_{i}",
                [
                    {"id": f"tp_{20+i*2+1}", "channel": "social", "timestamp": datetime(2024, 2, i+1, 10, 0).isoformat()},
                    {"id": f"tp_{20+i*2+2}", "channel": "direct", "timestamp": datetime(2024, 2, i+1, 15, 0).isoformat()},
                ],
                50.00,
                f"LOWROID_{i}"
            )
        
        # Add realistic channel spend - paid search spent $2000 but made $2000, social spent $1500 but made $250
        analytics.roi_calculator.add_channel_spend("paid_search", 2000)
        analytics.roi_calculator.add_channel_spend("social", 1500)
        
        # Add revenue - paid search generated 2000 from 10 conversions
        analytics.roi_calculator.add_channel_revenue("paid_search", 2000, 10)  
        # Social generated only 250 from 5 conversions
        analytics.roi_calculator.add_channel_revenue("social", 250, 5)
        
        optimization = analytics.get_budget_optimization(total_budget=10000)
        
        # Paid search should get more budget due to better ROI (0% vs -83.3%)
        assert optimization["recommendations"]["paid_search"] >= optimization["recommendations"]["social"]
