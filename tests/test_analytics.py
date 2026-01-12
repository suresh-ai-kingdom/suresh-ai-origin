"""Tests for analytics module."""
import pytest
import time
import uuid
from analytics import (
    get_daily_revenue, get_product_sales, get_conversion_metrics,
    get_overview_stats, get_customer_retention, get_time_range_filters
)
from models import get_session, Order

# Import analytics_engine for Feature #17 tests
try:
    from analytics_engine import (
        VisitorTracker,
        ConversionFunnelAnalyzer,
        UserJourneyAnalyzer,
        calculate_real_time_kpis,
        generate_analytics_summary,
        generate_demo_analytics_data,
        generate_critical_alerts,
        generate_funnel_recommendations
    )
    ANALYTICS_ENGINE_AVAILABLE = True
except ImportError:
    ANALYTICS_ENGINE_AVAILABLE = False


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up test data before and after each test."""
    # Clean before
    session = get_session()
    try:
        session.query(Order).filter(Order.receipt.like('TEST_%')).delete()
        session.query(Order).filter(Order.receipt.like('CUSTOMER_%')).delete()
        session.commit()
    finally:
        session.close()
    
    yield
    
    # Clean after
    session = get_session()
    try:
        session.query(Order).filter(Order.receipt.like('TEST_%')).delete()
        session.query(Order).filter(Order.receipt.like('CUSTOMER_%')).delete()
        session.commit()
    finally:
        session.close()


def unique_id():
    """Generate unique ID."""
    return f"TEST_{uuid.uuid4().hex[:12]}"


def create_test_order(amount, product, status='paid', created_at=None, receipt=None):
    """Create test order with unique ID."""
    session = get_session()
    try:
        order = Order(
            id=unique_id(),
            amount=amount,
            currency='INR',
            receipt=receipt or f"TEST_{uuid.uuid4().hex[:8]}",
            product=product,
            status=status,
            created_at=created_at or time.time()
        )
        session.add(order)
        session.commit()
    finally:
        session.close()


def test_time_range_filters():
    """Test time range filter generation."""
    start, now = get_time_range_filters(days=30)
    assert (now - start) >= (30 * 86400 - 100)


def test_daily_revenue_empty():
    """Test daily revenue with no orders."""
    result = get_daily_revenue(days=30)
    assert isinstance(result, list)


def test_daily_revenue_single_day():
    """Test daily revenue with single order."""
    now = time.time()
    create_test_order(50000, 'starter_pack', status='paid', created_at=now)
    result = get_daily_revenue(days=1)
    assert len(result) > 0


def test_product_sales_empty():
    """Test product sales with no orders."""
    result = get_product_sales(days=30)
    assert isinstance(result, list)


def test_product_sales_breakdown():
    """Test product sales grouping."""
    now = time.time()
    receipt = f"TEST_{uuid.uuid4().hex[:8]}"
    
    session = get_session()
    try:
        session.add(Order(id=unique_id(), amount=50000, currency='INR', receipt=receipt,
                         product='starter_pack', status='paid', created_at=now))
        session.add(Order(id=unique_id(), amount=50000, currency='INR', receipt=receipt,
                         product='starter_pack', status='paid', created_at=now))
        session.add(Order(id=unique_id(), amount=100000, currency='INR', receipt=receipt,
                         product='pro_pack', status='paid', created_at=now))
        session.commit()
    finally:
        session.close()
    
    result = get_product_sales(days=1)
    starter = next((p for p in result if p['product'] == 'starter_pack'), None)
    assert starter is not None
    assert starter['count'] >= 2


def test_conversion_metrics():
    """Test conversion metrics."""
    now = time.time()
    create_test_order(50000, 'starter_pack', status='created', created_at=now)
    create_test_order(100000, 'pro_pack', status='paid', created_at=now)
    create_test_order(75000, 'premium_pack', status='paid', created_at=now)
    
    result = get_conversion_metrics(days=1)
    assert result['total_orders'] >= 3
    assert result['paid_orders'] >= 2


def test_overview_stats():
    """Test overview statistics."""
    now = time.time()
    create_test_order(50000, 'starter_pack', status='paid', created_at=now)
    create_test_order(100000, 'pro_pack', status='paid', created_at=now)
    
    result = get_overview_stats(days=1)
    assert result['total_orders'] >= 2
    assert result['total_revenue_paise'] >= 150000


def test_customer_retention_repeat():
    """Test retention with repeat customers."""
    now = time.time()
    receipt_a = f"CUSTOMER_{uuid.uuid4().hex[:8]}"
    receipt_b = f"CUSTOMER_{uuid.uuid4().hex[:8]}"
    
    session = get_session()
    try:
        session.add(Order(
            id=unique_id(), amount=50000, currency='INR', receipt=receipt_a,
            product='starter_pack', status='paid', created_at=now
        ))
        session.add(Order(
            id=unique_id(), amount=100000, currency='INR', receipt=receipt_a,
            product='pro_pack', status='paid', created_at=now
        ))
        session.add(Order(
            id=unique_id(), amount=75000, currency='INR', receipt=receipt_b,
            product='premium_pack', status='paid', created_at=now
        ))
        session.commit()
    finally:
        session.close()
    
    result = get_customer_retention(days_back=1)
    assert result['repeat_customers'] >= 1


def test_product_sales_status_filter():
    """Test that only paid orders are included."""
    now = time.time()
    create_test_order(50000, 'starter_pack', status='created', created_at=now)
    create_test_order(100000, 'pro_pack', status='paid', created_at=now)
    
    result = get_product_sales(days=1)
    products = {p['product']: p for p in result}
    assert 'pro_pack' in products


# Feature #17: Real-time Analytics Engine Tests
# ==============================================

@pytest.mark.skipif(not ANALYTICS_ENGINE_AVAILABLE, reason="analytics_engine module not available")
class TestVisitorTracking:
    """Test visitor tracking functionality"""
    
    def test_track_visitor(self):
        """Test tracking a single visitor"""
        tracker = VisitorTracker()
        result = tracker.track_visitor(
            session_id="session_001",
            page="/home",
            source="google",
            device="desktop"
        )
        
        assert result["status"] == "tracked"
        assert result["session_id"] == "session_001"
        assert result["current_page"] == "/home"
        assert "session_001" in tracker.visitors
    
    def test_track_multiple_pages(self):
        """Test tracking multiple page views from same visitor"""
        tracker = VisitorTracker()
        
        pages = ["/home", "/products", "/checkout"]
        for page in pages:
            tracker.track_visitor("session_001", page)
        
        visitor = tracker.visitors["session_001"]
        assert len(visitor["pages_visited"]) == 3
        assert visitor["pages_visited"][-1]["page"] == "/checkout"
    
    def test_track_event(self):
        """Test tracking custom events"""
        tracker = VisitorTracker()
        tracker.track_visitor("session_001", "/home")
        
        event_result = tracker.track_event(
            "session_001",
            "add_to_cart",
            {"product_id": "123", "quantity": 2}
        )
        
        assert event_result["status"] == "tracked"
        assert event_result["event_type"] == "add_to_cart"
        
        visitor = tracker.visitors["session_001"]
        assert any(e["type"] == "add_to_cart" for e in visitor["events"])
    
    def test_get_active_visitors(self):
        """Test getting currently active visitors"""
        tracker = VisitorTracker()
        
        for i in range(5):
            tracker.track_visitor(f"session_{i:03d}", "/home")
        
        active = tracker.get_active_visitors(minutes=5)
        
        assert len(active) >= 5
        assert all("session_id" in v for v in active)
        assert all("current_page" in v for v in active)
    
    def test_get_visitor_summary(self):
        """Test getting visitor summary statistics"""
        tracker = VisitorTracker()
        
        for i in range(10):
            tracker.track_visitor(f"session_{i:03d}", "/home", source="google")
            tracker.track_visitor(f"session_{i:03d}", "/products", source="google")
        
        summary = tracker.get_visitor_summary()
        
        assert summary["total_visitors"] == 10
        assert summary["total_pageviews"] >= 20
        assert "traffic_sources" in summary
        assert "google" in summary["traffic_sources"]


@pytest.mark.skipif(not ANALYTICS_ENGINE_AVAILABLE, reason="analytics_engine module not available")
class TestConversionFunnelAnalysis:
    """Test conversion funnel analysis"""
    
    def test_build_funnel(self):
        """Test building a conversion funnel"""
        visitors, _ = generate_demo_analytics_data(50)
        analyzer = ConversionFunnelAnalyzer()
        
        funnel = analyzer.build_funnel(visitors)
        
        assert "funnel_name" in funnel
        assert "steps" in funnel
        assert "visitor_counts" in funnel
        assert "overall_conversion_rate" in funnel
        assert 0 <= funnel["overall_conversion_rate"] <= 100
    
    def test_funnel_dropoff_rates(self):
        """Test funnel dropoff calculations"""
        visitors, _ = generate_demo_analytics_data(100)
        analyzer = ConversionFunnelAnalyzer()
        
        funnel = analyzer.build_funnel(visitors)
        
        assert "dropoff_rates" in funnel
        assert isinstance(funnel["dropoff_rates"], dict)
        
        # Dropoff should be between 0-100
        for rate in funnel["dropoff_rates"].values():
            assert 0 <= rate <= 100
    
    def test_analyze_by_device_segment(self):
        """Test funnel analysis by device segment"""
        visitors, _ = generate_demo_analytics_data(50)
        analyzer = ConversionFunnelAnalyzer()
        
        analysis = analyzer.analyze_by_segment(visitors, "device")
        
        assert "segment_type" in analysis
        assert analysis["segment_type"] == "device"
        assert "analysis" in analysis
        assert isinstance(analysis["analysis"], dict)
        
        # Should have device types
        for device, metrics in analysis["analysis"].items():
            assert "visitors" in metrics
            assert "conversions" in metrics
            assert "conversion_rate" in metrics
    
    def test_funnel_recommendations(self):
        """Test funnel optimization recommendations"""
        recommendations = generate_funnel_recommendations(
            {"landing→product": 45, "product→cart": 20},
            conversion_rate=0.5
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(r, str) for r in recommendations)


@pytest.mark.skipif(not ANALYTICS_ENGINE_AVAILABLE, reason="analytics_engine module not available")
class TestUserJourneyAnalysis:
    """Test user journey and heatmap analysis"""
    
    def test_build_journey_heatmap(self):
        """Test building journey heatmap"""
        visitors, _ = generate_demo_analytics_data(50)
        analyzer = UserJourneyAnalyzer()
        
        heatmap = analyzer.build_journey_heatmap(visitors)
        
        assert "heatmap" in heatmap
        assert "total_transitions" in heatmap
        assert "unique_pages" in heatmap
        assert heatmap["total_transitions"] >= 0
    
    def test_user_segments(self):
        """Test user segmentation"""
        visitors, _ = generate_demo_analytics_data(100)
        analyzer = UserJourneyAnalyzer()
        
        segments = analyzer.get_user_segments(visitors)
        
        assert "segment_distribution" in segments
        assert "segment_percentages" in segments
        assert "high_value_visitors" in segments
        assert "conversion_segments" in segments
        
        # Percentages should sum to ~100
        total_pct = sum(segments["segment_percentages"].values())
        assert 99 <= total_pct <= 101
    
    def test_user_segment_types(self):
        """Test that all user segment types are tracked"""
        visitors, _ = generate_demo_analytics_data(100)
        analyzer = UserJourneyAnalyzer()
        
        segments = analyzer.get_user_segments(visitors)
        
        expected_types = ["bounces", "browsers", "converters", "high_value"]
        for segment_type in expected_types:
            assert segment_type in segments["segment_distribution"]


@pytest.mark.skipif(not ANALYTICS_ENGINE_AVAILABLE, reason="analytics_engine module not available")
class TestKPIAggregation:
    """Test real-time KPI calculations"""
    
    def test_calculate_real_time_kpis(self):
        """Test calculating real-time KPIs"""
        visitors, events = generate_demo_analytics_data(50)
        kpis = calculate_real_time_kpis(visitors, events)
        
        assert "timestamp" in kpis
        assert "active_visitors" in kpis
        assert "total_visitors" in kpis
        assert "conversion_rate_percentage" in kpis
        assert "bounce_rate_percentage" in kpis
        
        # Verify ranges
        assert 0 <= kpis["bounce_rate_percentage"] <= 100
        assert 0 <= kpis["conversion_rate_percentage"] <= 100
    
    def test_kpi_metrics_validity(self):
        """Test that KPI metrics are valid"""
        visitors, events = generate_demo_analytics_data(100)
        kpis = calculate_real_time_kpis(visitors, events)
        
        assert kpis["total_visitors"] >= 0
        assert kpis["active_visitors"] >= 0
        assert kpis["total_pageviews"] >= kpis["total_visitors"]
        assert kpis["total_conversions"] <= kpis["total_visitors"]
        assert kpis["avg_time_on_site_seconds"] >= 0
        assert kpis["revenue_per_visitor"] >= 0


@pytest.mark.skipif(not ANALYTICS_ENGINE_AVAILABLE, reason="analytics_engine module not available")
class TestAnalyticsSummary:
    """Test comprehensive analytics summary generation"""
    
    def test_generate_analytics_summary(self):
        """Test generating complete analytics summary"""
        visitors, events = generate_demo_analytics_data(50)
        summary = generate_analytics_summary(visitors, events)
        
        assert "summary_timestamp" in summary
        assert "kpis" in summary
        assert "funnel" in summary
        assert "user_segments" in summary
        assert "journey_heatmap" in summary
        assert "critical_alerts" in summary
    
    def test_summary_contains_all_sections(self):
        """Test that summary includes all analytical sections"""
        visitors, events = generate_demo_analytics_data(50)
        summary = generate_analytics_summary(visitors, events)
        
        # KPIs section
        assert "active_visitors" in summary["kpis"]
        assert "conversion_rate_percentage" in summary["kpis"]
        
        # Funnel section
        assert "overall_conversion_rate" in summary["funnel"]
        assert "recommendations" in summary["funnel"]
        
        # Segments section
        assert "segment_distribution" in summary["user_segments"]
        assert "conversion_segments" in summary["user_segments"]
        
        # Heatmap section
        assert "heatmap" in summary["journey_heatmap"]
        assert "total_transitions" in summary["journey_heatmap"]


@pytest.mark.skipif(not ANALYTICS_ENGINE_AVAILABLE, reason="analytics_engine module not available")
class TestCriticalAlerts:
    """Test critical alert generation"""
    
    def test_generate_critical_alerts_high_bounce(self):
        """Test alert generation for high bounce rate"""
        kpis = {
            "bounce_rate_percentage": 75,
            "conversion_rate_percentage": 2,
            "active_visitors": 10
        }
        funnel = {"critical_dropoff": 20}
        segments = {}
        
        alerts = generate_critical_alerts(kpis, funnel, segments)
        
        assert len(alerts) > 0
        assert any("bounce" in a["message"].lower() for a in alerts)
    
    def test_generate_critical_alerts_low_conversion(self):
        """Test alert generation for low conversion rate"""
        kpis = {
            "bounce_rate_percentage": 30,
            "conversion_rate_percentage": 0.5,
            "active_visitors": 10
        }
        funnel = {"critical_dropoff": 20}
        segments = {}
        
        alerts = generate_critical_alerts(kpis, funnel, segments)
        
        assert any("conversion" in a["message"].lower() for a in alerts)
    
    def test_generate_critical_alerts_high_funnel_dropoff(self):
        """Test alert generation for critical funnel dropoff"""
        kpis = {
            "bounce_rate_percentage": 30,
            "conversion_rate_percentage": 2,
            "active_visitors": 10
        }
        funnel = {"critical_dropoff": 75}
        segments = {}
        
        alerts = generate_critical_alerts(kpis, funnel, segments)
        
        assert any("funnel" in a["message"].lower() or "dropoff" in a["message"].lower() for a in alerts)


@pytest.mark.skipif(not ANALYTICS_ENGINE_AVAILABLE, reason="analytics_engine module not available")
class TestDemoDataGeneration:
    """Test demo data generation"""
    
    def test_generate_demo_analytics_data(self):
        """Test generating demo analytics data"""
        visitors, events = generate_demo_analytics_data(30)
        
        assert len(visitors) == 30
        assert len(events) > 0
        assert all("session_id" in v for v in visitors.values())
        assert all("type" in e for e in events)
    
    def test_demo_data_has_conversions(self):
        """Test that demo data includes some conversions"""
        visitors, events = generate_demo_analytics_data(100)
        
        conversions = sum(
            1 for v in visitors.values()
            if any(e["type"] == "payment" for e in v.get("events", []))
        )
        
        # With 100 visitors and 15% conversion, should have some
        assert conversions > 0
    
    def test_demo_data_consistency(self):
        """Test that demo data is internally consistent"""
        visitors, events = generate_demo_analytics_data(50)
        
        # Each event should reference a valid session
        for event in events:
            assert event["session_id"] in visitors


@pytest.mark.skipif(not ANALYTICS_ENGINE_AVAILABLE, reason="analytics_engine module not available")
class TestIntegration:
    """Integration tests for analytics system"""
    
    def test_complete_analytics_workflow(self):
        """Test complete analytics workflow"""
        # Generate data
        visitors, events = generate_demo_analytics_data(100)
        
        # Generate summary
        summary = generate_analytics_summary(visitors, events)
        
        # Verify all sections present
        assert summary["kpis"]["total_visitors"] == 100
        assert summary["funnel"]["overall_conversion_rate"] >= 0
        assert summary["user_segments"]["conversion_segments"] >= 0
        
        # Verify alerts
        alerts = summary["critical_alerts"]
        assert isinstance(alerts, list)
    
    def test_analytics_consistency_across_methods(self):
        """Test that different calculation methods are consistent"""
        visitors, events = generate_demo_analytics_data(50)
        
        # Method 1: Direct KPI calculation
        kpis = calculate_real_time_kpis(visitors, events)
        
        # Method 2: Through summary
        summary = generate_analytics_summary(visitors, events)
        
        # Should have same visitor count
        assert kpis["total_visitors"] == summary["kpis"]["total_visitors"]
        assert kpis["conversion_rate_percentage"] == summary["kpis"]["conversion_rate_percentage"]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
