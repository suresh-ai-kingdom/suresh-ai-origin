"""Tests for Predictive Analytics Engine."""
import pytest
import numpy as np
from predictive_analytics import (
    simple_linear_forecast, exponential_smoothing_forecast,
    forecast_revenue, forecast_churn, forecast_customer_growth,
    forecast_mrr, get_all_predictions, get_prediction_summary,
    generate_recommendations
)


def test_simple_linear_forecast():
    """Test linear regression forecasting."""
    values = [100, 105, 110, 115, 120]
    forecast = simple_linear_forecast(values, 5)
    
    assert len(forecast) == 5
    assert all('value' in f and 'lower' in f and 'upper' in f for f in forecast)
    # Values should be positive
    assert all(f['value'] >= 0 for f in forecast)
    # Confidence intervals should widen
    assert forecast[-1]['upper'] - forecast[-1]['lower'] > forecast[0]['upper'] - forecast[0]['lower']


def test_linear_forecast_with_empty_data():
    """Test linear forecast with insufficient data."""
    values = [100]
    forecast = simple_linear_forecast(values, 3)
    
    assert len(forecast) == 3
    # Should return averages
    assert all(f['value'] > 0 for f in forecast)


def test_exponential_smoothing():
    """Test exponential smoothing forecast."""
    values = [100, 102, 104, 103, 105, 107, 106]
    forecast = exponential_smoothing_forecast(values, 5, alpha=0.3)
    
    assert len(forecast) == 5
    assert all(f['value'] >= 0 for f in forecast)
    assert all('lower' in f and 'upper' in f for f in forecast)


def test_exponential_smoothing_empty():
    """Test exponential smoothing with no data."""
    forecast = exponential_smoothing_forecast([], 3)
    
    assert len(forecast) == 3
    assert all(f['value'] == 0 for f in forecast)


def test_forecast_revenue():
    """Test revenue forecasting."""
    result = forecast_revenue(days_history=30, forecast_days=90)
    
    assert result.metric_name == 'Monthly Revenue (₹)'
    assert len(result.forecast_data) > 0
    assert all('date' in f and 'value' in f for f in result.forecast_data)
    assert result.confidence_level == 0.95


def test_forecast_churn():
    """Test churn rate forecasting."""
    result = forecast_churn(days_history=30, forecast_days=90)
    
    assert result.metric_name == 'Monthly Churn Rate (%)'
    assert len(result.forecast_data) > 0
    # Churn should be between 0-100%
    assert all(0 <= f['value'] <= 100 for f in result.forecast_data)
    assert all(0 <= f['lower'] <= 100 for f in result.forecast_data)
    assert all(0 <= f['upper'] <= 100 for f in result.forecast_data)


def test_forecast_customer_growth():
    """Test customer growth forecasting."""
    result = forecast_customer_growth(days_history=30, forecast_days=90)
    
    assert result.metric_name == 'Total Customers'
    assert len(result.forecast_data) > 0
    # Customer counts should be non-negative
    assert all(f['value'] >= 0 for f in result.forecast_data)


def test_forecast_mrr():
    """Test MRR forecasting."""
    result = forecast_mrr(days_history=30, forecast_days=90)
    
    assert result.metric_name == 'Monthly Recurring Revenue (₹)'
    assert len(result.forecast_data) > 0
    assert all(f['value'] >= 0 for f in result.forecast_data)


def test_get_all_predictions():
    """Test getting all predictions at once."""
    predictions = get_all_predictions()
    
    assert 'revenue' in predictions
    assert 'churn' in predictions
    assert 'growth' in predictions
    assert 'mrr' in predictions
    assert 'generated_at' in predictions
    
    # Each should have required fields
    for key in ['revenue', 'churn', 'growth', 'mrr']:
        assert 'metric' in predictions[key]
        assert 'forecast' in predictions[key]
        assert 'confidence' in predictions[key]


def test_get_prediction_summary():
    """Test getting prediction summary with recommendations."""
    summary = get_prediction_summary()
    
    assert 'summary' in summary
    assert 'predictions' in summary
    assert 'recommendations' in summary
    
    # Summary should have key metrics
    assert 'revenue_growth' in summary['summary']
    assert 'mrr_growth' in summary['summary']
    assert 'customer_growth' in summary['summary']
    assert 'average_churn' in summary['summary']
    assert 'forecast_confidence' in summary['summary']
    
    # Should have recommendations
    assert len(summary['recommendations']) > 0


def test_generate_recommendations_high_churn():
    """Test recommendation generation for high churn."""
    predictions = {
        'revenue': {'forecast': [{'value': 100}, {'value': 100}]},
        'churn': {'forecast': [{'value': 15}, {'value': 14}]},
        'growth': {'forecast': [{'value': 100}, {'value': 110}]},
        'mrr': {'forecast': [{'value': 10}, {'value': 11}]}
    }
    
    recommendations = generate_recommendations(predictions)
    
    assert any('Churn' in r['title'] for r in recommendations)


def test_generate_recommendations_revenue_decline():
    """Test recommendation generation for revenue decline."""
    predictions = {
        'revenue': {'forecast': [{'value': 100}, {'value': 70}]},
        'churn': {'forecast': [{'value': 5}, {'value': 5}]},
        'growth': {'forecast': [{'value': 100}, {'value': 100}]},
        'mrr': {'forecast': [{'value': 10}, {'value': 10}]}
    }
    
    recommendations = generate_recommendations(predictions)
    
    assert any('Decline' in r['title'] for r in recommendations)


def test_prediction_result_to_dict():
    """Test converting prediction result to dict."""
    from predictive_analytics import PredictionResult
    
    forecast_data = [
        {'date': '2026-02', 'value': 100, 'lower': 80, 'upper': 120}
    ]
    result = PredictionResult('Test Metric', forecast_data)
    
    result_dict = result.to_dict()
    
    assert result_dict['metric'] == 'Test Metric'
    assert result_dict['confidence'] == 0.95
    assert 'generated_at' in result_dict
    assert result_dict['forecast'] == forecast_data


def test_forecast_confidence_intervals():
    """Test that confidence intervals are properly calculated."""
    values = [100, 105, 110, 115, 120]
    forecast = simple_linear_forecast(values, 5)
    
    for f in forecast:
        assert f['lower'] <= f['value'] <= f['upper']


def test_forecast_positive_values():
    """Test that forecasts are always non-negative."""
    values = [10, 12, 15, 11, 9]  # Small values
    forecast = simple_linear_forecast(values, 5)
    
    assert all(f['value'] >= 0 for f in forecast)


def test_multiple_forecast_methods_consistency():
    """Test that different methods produce reasonable forecasts."""
    values = [100, 110, 120, 130, 140, 150]
    
    linear = simple_linear_forecast(values, 3)
    exponential = exponential_smoothing_forecast(values, 3)
    
    # Both should produce positive values
    assert all(f['value'] >= 0 for f in linear)
    assert all(f['value'] >= 0 for f in exponential)
    
    # Magnitude should be similar
    linear_avg = np.mean([f['value'] for f in linear])
    exp_avg = np.mean([f['value'] for f in exponential])
    assert abs(linear_avg - exp_avg) < linear_avg * 0.5  # Within 50%


@pytest.mark.parametrize("days_history,forecast_days", [
    (30, 90),
    (90, 180),
    (180, 365),
])
def test_forecast_with_different_periods(days_history, forecast_days):
    """Test forecasting with different time periods."""
    result = forecast_revenue(days_history, forecast_days)
    
    assert result.metric_name == 'Monthly Revenue (₹)'
    assert len(result.forecast_data) > 0


def test_recommendation_priorities():
    """Test that recommendations have proper priority levels."""
    summary = get_prediction_summary()
    
    for rec in summary['recommendations']:
        assert rec['priority'] in ['HIGH', 'MEDIUM', 'LOW']
        assert 'category' in rec
        assert 'title' in rec
        assert 'action' in rec
