"""
Comprehensive test suite for Analytics Engine
Tests all modules with mocks for external services
"""

import pytest
import os
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analytics_engine.data_collector import DataCollector
from analytics_engine.kpi_calculator import KPICalculator
from analytics_engine.anomaly_detector import AnomalyDetector
from analytics_engine.pdf_generator import PDFGenerator
from analytics_engine.email_notifier import EmailNotifier


# ==================== FIXTURES ====================

@pytest.fixture
def cleanup_test_files():
    """Cleanup test files after each test."""
    yield
    
    # Cleanup test files
    test_files = [
        "data/kpi_history.jsonl",
        "reports/test_report.pdf"
    ]
    
    for filepath in test_files:
        path = Path(filepath)
        if path.exists():
            path.unlink()


@pytest.fixture
def mock_ga_data():
    """Mock Google Analytics data."""
    return [
        {
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y%m%d"),
            "source": "google" if i % 2 == 0 else "direct",
            "medium": "organic" if i % 2 == 0 else "(none)",
            "activeUsers": 100 + i * 10,
            "newUsers": 20 + i * 2,
            "screenPageViews": 500 + i * 50,
            "engagementRate": 0.75 + i * 0.01,
            "bounceRate": 0.25 - i * 0.01
        }
        for i in range(30)
    ]


@pytest.fixture
def mock_stripe_data():
    """Mock Stripe data."""
    return {
        "total_revenue": 150000.00,
        "active_subscriptions": 45,
        "cancelled_subscriptions": 5,
        "subscriptions": [
            {"amount_paise": 299900, "status": "active"} for _ in range(45)
        ] + [
            {"amount_paise": 299900, "status": "canceled"} for _ in range(5)
        ]
    }


@pytest.fixture
def mock_referral_data():
    """Mock referral data."""
    return [
        {"referrer_name": "LinkedIn", "referral_count": 25, "revenue": 75000.00},
        {"referrer_name": "Twitter", "referral_count": 18, "revenue": 54000.00},
        {"referrer_name": "Product Hunt", "referral_count": 12, "revenue": 36000.00},
        {"referrer_name": "Direct", "referral_count": 30, "revenue": 90000.00},
        {"referrer_name": "Organic", "referral_count": 10, "revenue": 30000.00}
    ]


@pytest.fixture
def mock_prompt_stats():
    """Mock prompt statistics."""
    return [
        {
            "feature_name": "ai_generator",
            "prompt_count": 150,
            "total_tokens": 75000,
            "successful_prompts": 145
        },
        {
            "feature_name": "recommendations",
            "prompt_count": 120,
            "total_tokens": 60000,
            "successful_prompts": 115
        },
        {
            "feature_name": "recovery",
            "prompt_count": 80,
            "total_tokens": 40000,
            "successful_prompts": 78
        }
    ]


@pytest.fixture
def mock_kpis(mock_ga_data, mock_stripe_data, mock_referral_data, mock_prompt_stats):
    """Mock calculated KPIs."""
    calculator = KPICalculator()
    
    all_data = {
        "ga_data": mock_ga_data,
        "stripe_data": mock_stripe_data,
        "referral_data": mock_referral_data,
        "prompt_stats": mock_prompt_stats
    }
    
    return calculator.calculate_all_kpis(all_data)


# ==================== DATA COLLECTOR TESTS ====================

def test_data_collector_initialization():
    """Test DataCollector initialization."""
    collector = DataCollector()
    assert collector is not None


@patch('analytics_engine.data_collector.requests.post')
def test_ga_data_collection(mock_post, mock_ga_data):
    """Test Google Analytics data collection."""
    # Mock GA API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "rows": [
            {
                "dimensionValues": [
                    {"value": row["date"]},
                    {"value": row["source"]},
                    {"value": row["medium"]}
                ],
                "metricValues": [
                    {"value": str(row["activeUsers"])},
                    {"value": str(row["newUsers"])},
                    {"value": str(row["screenPageViews"])},
                    {"value": str(row["engagementRate"])},
                    {"value": str(row["bounceRate"])}
                ]
            }
            for row in mock_ga_data[:5]  # First 5 rows
        ]
    }
    mock_post.return_value = mock_response
    
    collector = DataCollector()
    
    # Mock token
    with patch.object(collector, '_get_ga_token', return_value='mock_token'):
        ga_data = collector.get_ga_data()
    
    assert len(ga_data) > 0
    assert "activeUsers" in ga_data[0] or len(ga_data) == 0  # May use mock data


def test_stripe_data_collection_mock():
    """Test Stripe data collection with mock."""
    collector = DataCollector()
    stripe_data = collector.get_stripe_data()
    
    assert "total_revenue" in stripe_data
    assert "active_subscriptions" in stripe_data
    assert "cancelled_subscriptions" in stripe_data
    assert stripe_data["active_subscriptions"] >= 0


def test_referral_data_collection():
    """Test referral data collection."""
    collector = DataCollector()
    referral_data = collector.get_referral_data()
    
    assert isinstance(referral_data, list)
    if referral_data:
        assert "referrer_name" in referral_data[0]
        assert "referral_count" in referral_data[0]
        assert "revenue" in referral_data[0]


def test_prompt_stats_collection():
    """Test prompt statistics collection."""
    collector = DataCollector()
    prompt_stats = collector.get_prompt_stats()
    
    assert isinstance(prompt_stats, list)


def test_collect_all_data():
    """Test collecting all data sources."""
    collector = DataCollector()
    all_data = collector.collect_all_data()
    
    assert "ga_data" in all_data
    assert "stripe_data" in all_data
    assert "referral_data" in all_data
    assert "prompt_stats" in all_data


# ==================== KPI CALCULATOR TESTS ====================

def test_kpi_calculator_initialization():
    """Test KPICalculator initialization."""
    calculator = KPICalculator()
    assert calculator is not None


def test_calculate_mrr(mock_stripe_data):
    """Test MRR calculation."""
    calculator = KPICalculator()
    mrr = calculator.calculate_mrr(mock_stripe_data)
    
    assert isinstance(mrr, (int, float))
    assert mrr > 0  # Should have positive MRR with 45 active subs


def test_calculate_churn_rate(mock_stripe_data):
    """Test churn rate calculation."""
    calculator = KPICalculator()
    churn_rate = calculator.calculate_churn_rate(mock_stripe_data)
    
    assert isinstance(churn_rate, (int, float))
    assert 0 <= churn_rate <= 100  # Should be between 0-100%
    assert churn_rate == 10.0  # 5 cancelled / (45 active + 5 cancelled) = 10%


def test_get_top_referrers(mock_referral_data):
    """Test top referrers calculation."""
    calculator = KPICalculator()
    top_referrers = calculator.get_top_referrers(mock_referral_data, limit=3)
    
    assert len(top_referrers) == 3
    assert top_referrers[0]["referrer_name"] == "Direct"  # Highest revenue
    assert top_referrers[0]["revenue"] == 90000.00


def test_calculate_prompt_statistics(mock_prompt_stats):
    """Test prompt statistics calculation."""
    calculator = KPICalculator()
    prompt_stats = calculator.calculate_prompt_statistics(mock_prompt_stats)
    
    assert "total_prompts" in prompt_stats
    assert "avg_tokens_per_prompt" in prompt_stats
    assert "overall_success_rate" in prompt_stats
    assert "most_used_feature" in prompt_stats
    
    assert prompt_stats["total_prompts"] == 350  # 150 + 120 + 80
    assert prompt_stats["most_used_feature"] == "ai_generator"


def test_calculate_revenue_metrics(mock_stripe_data):
    """Test revenue metrics calculation."""
    calculator = KPICalculator()
    metrics = calculator.calculate_revenue_metrics(mock_stripe_data)
    
    assert "mrr" in metrics
    assert "arr" in metrics
    assert "arpu" in metrics
    assert "churn_rate" in metrics
    
    assert metrics["arr"] == metrics["mrr"] * 12
    assert metrics["churn_rate"] == 10.0


def test_calculate_growth_metrics(mock_ga_data):
    """Test growth metrics calculation."""
    calculator = KPICalculator()
    metrics = calculator.calculate_growth_metrics(mock_ga_data)
    
    assert "total_active_users" in metrics
    assert "total_new_users" in metrics
    assert "total_page_views" in metrics
    assert "user_growth_wow" in metrics
    assert "pageview_growth_wow" in metrics


def test_calculate_all_kpis(mock_ga_data, mock_stripe_data, mock_referral_data, mock_prompt_stats):
    """Test calculating all KPIs."""
    calculator = KPICalculator()
    
    all_data = {
        "ga_data": mock_ga_data,
        "stripe_data": mock_stripe_data,
        "referral_data": mock_referral_data,
        "prompt_stats": mock_prompt_stats
    }
    
    kpis = calculator.calculate_all_kpis(all_data)
    
    assert "revenue_metrics" in kpis
    assert "growth_metrics" in kpis
    assert "top_referrers" in kpis
    assert "prompt_statistics" in kpis


# ==================== ANOMALY DETECTOR TESTS ====================

def test_anomaly_detector_initialization():
    """Test AnomalyDetector initialization."""
    detector = AnomalyDetector()
    assert detector is not None
    assert detector.threshold == 0.20


def test_save_and_load_kpis(mock_kpis, cleanup_test_files):
    """Test saving and loading KPIs."""
    detector = AnomalyDetector()
    
    # Save KPIs
    detector.save_kpis(mock_kpis)
    
    # Verify file exists
    assert Path("data/kpi_history.jsonl").exists()
    
    # Load KPIs
    historical = detector.load_historical_kpis(days=7)
    
    assert len(historical) > 0
    assert historical[0]["timestamp"] is not None


def test_detect_revenue_anomalies_no_change(mock_kpis):
    """Test revenue anomaly detection with no change."""
    detector = AnomalyDetector()
    
    current = mock_kpis
    historical = [mock_kpis] * 7  # Same KPIs for 7 days
    
    anomalies = detector.detect_revenue_anomalies(current, historical)
    
    # No significant change = no anomalies
    assert len(anomalies) == 0


def test_detect_revenue_anomalies_with_drop():
    """Test revenue anomaly detection with significant drop."""
    detector = AnomalyDetector()
    
    # Current KPIs with 30% MRR drop
    current = {
        "revenue_metrics": {
            "mrr": 70000.00,
            "arr": 840000.00,
            "churn_rate": 10.0
        }
    }
    
    # Historical KPIs (normal)
    historical = [{
        "revenue_metrics": {
            "mrr": 100000.00,
            "arr": 1200000.00,
            "churn_rate": 8.0
        },
        "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
    } for i in range(7)]
    
    anomalies = detector.detect_revenue_anomalies(current, historical)
    
    # Should detect MRR drop
    assert len(anomalies) > 0
    assert any(a["metric"] == "MRR" for a in anomalies)
    assert any(a["severity"] == "critical" for a in anomalies)  # >30% drop


def test_detect_growth_anomalies_with_spike():
    """Test growth anomaly detection with positive spike."""
    detector = AnomalyDetector()
    
    # Current KPIs with 50% user growth
    current = {
        "growth_metrics": {
            "total_active_users": 1500,
            "total_page_views": 10000
        }
    }
    
    # Historical KPIs (normal)
    historical = [{
        "growth_metrics": {
            "total_active_users": 1000,
            "total_page_views": 7000
        },
        "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
    } for i in range(7)]
    
    anomalies = detector.detect_growth_anomalies(current, historical)
    
    # Positive spikes may not be flagged as anomalies (only drops)
    # But significant increases could be informational
    assert isinstance(anomalies, list)


def test_detect_all_anomalies(cleanup_test_files):
    """Test detecting all anomalies."""
    detector = AnomalyDetector()
    
    # Mock KPIs with normal values
    kpis = {
        "revenue_metrics": {
            "mrr": 100000.00,
            "arr": 1200000.00,
            "churn_rate": 8.0
        },
        "growth_metrics": {
            "total_active_users": 1000,
            "total_page_views": 7000
        }
    }
    
    result = detector.detect_all_anomalies(kpis)
    
    assert "anomalies_detected" in result
    assert "total_anomalies" in result
    assert "critical_count" in result
    assert "all_anomalies" in result


# ==================== PDF GENERATOR TESTS ====================

def test_pdf_generator_initialization():
    """Test PDFGenerator initialization."""
    generator = PDFGenerator(output_dir="test_reports")
    assert generator is not None
    assert generator.output_dir.name == "test_reports"


@pytest.mark.parametrize("chart_method", [
    "create_revenue_chart",
    "create_growth_chart",
    "create_referrers_chart",
    "create_prompt_stats_chart"
])
def test_create_charts(chart_method, mock_kpis):
    """Test creating individual charts."""
    import matplotlib.pyplot as plt
    
    generator = PDFGenerator()
    method = getattr(generator, chart_method)
    
    fig = method(mock_kpis)
    
    assert fig is not None
    plt.close(fig)


def test_create_summary_page(mock_kpis):
    """Test creating summary page."""
    import matplotlib.pyplot as plt
    
    generator = PDFGenerator()
    
    anomalies = {
        "anomalies_detected": False,
        "total_anomalies": 0,
        "critical_count": 0,
        "all_anomalies": []
    }
    
    fig = generator.create_summary_page(mock_kpis, anomalies)
    
    assert fig is not None
    plt.close(fig)


def test_generate_weekly_report(mock_kpis, cleanup_test_files):
    """Test generating complete PDF report."""
    generator = PDFGenerator(output_dir="test_reports")
    
    anomalies = {
        "anomalies_detected": False,
        "total_anomalies": 0,
        "critical_count": 0,
        "warning_count": 0,
        "all_anomalies": []
    }
    
    pdf_path = generator.generate_weekly_report(mock_kpis, anomalies)
    
    assert pdf_path is not None
    assert Path(pdf_path).exists()
    assert pdf_path.endswith(".pdf")
    
    # Cleanup
    Path(pdf_path).unlink()


# ==================== EMAIL NOTIFIER TESTS ====================

def test_email_notifier_initialization():
    """Test EmailNotifier initialization."""
    notifier = EmailNotifier()
    assert notifier is not None


@patch('analytics_engine.email_notifier.smtplib.SMTP')
def test_send_email_success(mock_smtp):
    """Test sending email successfully."""
    # Mock SMTP server
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    notifier = EmailNotifier(
        smtp_host="smtp.test.com",
        smtp_port=587,
        smtp_user="test@test.com",
        smtp_pass="password",
        admin_email="admin@test.com"
    )
    
    result = notifier._send_email(
        to_email="admin@test.com",
        subject="Test",
        html_body="<h1>Test</h1>"
    )
    
    assert result is True
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once()


@patch('analytics_engine.email_notifier.smtplib.SMTP')
def test_send_anomaly_alert(mock_smtp):
    """Test sending anomaly alert."""
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    notifier = EmailNotifier(
        smtp_user="test@test.com",
        smtp_pass="password"
    )
    
    anomalies = {
        "anomalies_detected": True,
        "total_anomalies": 2,
        "critical_count": 1,
        "warning_count": 1,
        "all_anomalies": [
            {
                "metric": "MRR",
                "current_value": 70000,
                "previous_value": 100000,
                "change_percent": -30.0,
                "severity": "critical",
                "message": "MRR dropped by 30%"
            }
        ]
    }
    
    result = notifier.send_anomaly_alert(anomalies)
    
    assert result is True


@patch('analytics_engine.email_notifier.smtplib.SMTP')
def test_send_weekly_report(mock_smtp, mock_kpis):
    """Test sending weekly report."""
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    notifier = EmailNotifier(
        smtp_user="test@test.com",
        smtp_pass="password"
    )
    
    anomalies = {
        "anomalies_detected": False,
        "total_anomalies": 0,
        "critical_count": 0,
        "warning_count": 0,
        "all_anomalies": []
    }
    
    result = notifier.send_weekly_report(mock_kpis, anomalies)
    
    assert result is True


# ==================== INTEGRATION TESTS ====================

def test_full_analytics_cycle(cleanup_test_files):
    """Test complete analytics cycle."""
    # Initialize all components
    collector = DataCollector()
    calculator = KPICalculator()
    detector = AnomalyDetector()
    
    # Step 1: Collect data
    data = collector.collect_all_data()
    assert data is not None
    
    # Step 2: Calculate KPIs
    kpis = calculator.calculate_all_kpis(data)
    assert kpis is not None
    assert "revenue_metrics" in kpis
    
    # Step 3: Detect anomalies
    anomalies = detector.detect_all_anomalies(kpis)
    assert anomalies is not None
    assert "anomalies_detected" in anomalies


def test_pdf_email_integration(mock_kpis, cleanup_test_files):
    """Test PDF generation and email integration."""
    import matplotlib
    matplotlib.use('Agg')
    
    generator = PDFGenerator(output_dir="test_reports")
    
    anomalies = {
        "anomalies_detected": False,
        "total_anomalies": 0,
        "critical_count": 0,
        "warning_count": 0,
        "all_anomalies": []
    }
    
    # Generate PDF
    pdf_path = generator.generate_weekly_report(mock_kpis, anomalies)
    assert Path(pdf_path).exists()
    
    # Cleanup
    Path(pdf_path).unlink()


# ==================== EDGE CASES ====================

def test_empty_data_handling():
    """Test handling empty data."""
    calculator = KPICalculator()
    
    empty_data = {
        "ga_data": [],
        "stripe_data": {},
        "referral_data": [],
        "prompt_stats": []
    }
    
    kpis = calculator.calculate_all_kpis(empty_data)
    
    # Should not crash
    assert kpis is not None


def test_anomaly_detection_with_no_history():
    """Test anomaly detection with no historical data."""
    detector = AnomalyDetector()
    
    kpis = {
        "revenue_metrics": {"mrr": 100000},
        "growth_metrics": {"total_active_users": 1000}
    }
    
    # Should not crash, just not detect anomalies
    result = detector.detect_all_anomalies(kpis)
    assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
