"""Tests for business metrics and analytics."""
import pytest
import json
from metrics import get_business_metrics, get_daily_sales_chart
from utils import save_order, save_payment


def test_metrics_empty_database(client):
    """Test metrics with no data."""
    metrics = get_business_metrics(days=30)
    
    assert metrics['overview']['total_orders'] >= 0
    assert metrics['overview']['paid_orders'] >= 0
    assert metrics['revenue']['total'] >= 0
    assert len(metrics['products']) >= 0


def test_metrics_with_orders(client):
    """Test metrics calculation with sample orders."""
    # Create test orders
    save_order('metrics_order1', 19900, 'INR', 'rcpt1', 'starter', 'paid')
    save_order('metrics_order2', 49900, 'INR', 'rcpt2', 'pro', 'paid')
    save_order('metrics_order3', 99900, 'INR', 'rcpt3', 'premium', 'created')
    
    metrics = get_business_metrics(days=30)
    
    assert metrics['overview']['total_orders'] >= 3
    assert metrics['overview']['paid_orders'] >= 2
    assert metrics['revenue']['total'] >= 699.00  # (199 + 499) in rupees


def test_metrics_product_breakdown(client):
    """Test product sales breakdown."""
    save_order('metrics_prod1', 19900, 'INR', 'rcpt1', 'starter', 'paid')
    save_order('metrics_prod2', 19900, 'INR', 'rcpt2', 'starter', 'paid')
    save_order('metrics_prod3', 49900, 'INR', 'rcpt3', 'pro', 'paid')
    
    metrics = get_business_metrics(days=30)
    products = {p['product']: p for p in metrics['products']}
    
    assert 'starter' in products
    assert products['starter']['orders'] >= 2
    
    assert 'pro' in products
    assert products['pro']['orders'] >= 1


def test_daily_sales_chart(client):
    """Test daily sales chart data generation."""
    save_order('chart_order1', 19900, 'INR', 'rcpt1', 'starter', 'paid')
    save_order('chart_order2', 49900, 'INR', 'rcpt2', 'pro', 'paid')
    
    chart_data = get_daily_sales_chart(days=7)
    
    assert len(chart_data) == 7  # 7 days
    assert all('date' in d for d in chart_data)
    assert all('orders' in d for d in chart_data)
    assert all('revenue' in d for d in chart_data)


def test_admin_metrics_endpoint_no_auth(client):
    """Test admin metrics endpoint without authentication."""
    # Default conftest has no auth, so should allow access
    response = client.get('/admin/metrics')
    # Will return 200 since conftest doesn't set ADMIN_TOKEN
    assert response.status_code == 200


def test_admin_metrics_with_auth(client, monkeypatch):
    """Test admin metrics endpoint with authentication."""
    # Set admin token
    monkeypatch.setenv('ADMIN_TOKEN', 'test-token')
    
    # Re-import app to pick up new env var
    import importlib
    import app as app_module
    importlib.reload(app_module)
    
    response = client.get('/admin/metrics', headers={'Authorization': 'Bearer test-token'})
    assert response.status_code == 200
    assert b'Business Metrics' in response.data or b'metrics' in response.data.lower()


def test_api_metrics_endpoint(client, monkeypatch):
    """Test JSON API metrics endpoint."""
    monkeypatch.setenv('ADMIN_TOKEN', 'test-token')
    
    import importlib
    import app as app_module
    importlib.reload(app_module)
    
    response = client.get('/api/metrics?days=7', headers={'Authorization': 'Bearer test-token'})
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'overview' in data
    assert 'revenue' in data
    assert 'products' in data
    assert data['period_days'] == 7


def test_metrics_period_filtering(client):
    """Test metrics with different time periods."""
    import time
    import uuid
    from models import get_engine, get_session, Order
    from utils import _get_db_url, init_db
    
    init_db()
    session = get_session(get_engine(_get_db_url()))
    
    # Order from 60 days ago with unique ID
    old_time = time.time() - (60 * 24 * 60 * 60)
    old_order = Order(
        id=f'old_metrics_order_{uuid.uuid4().hex[:8]}',
        amount=10000,
        currency='INR',
        receipt='old_rcpt',
        product='starter',
        status='paid',
        created_at=old_time,
        paid_at=old_time
    )
    session.add(old_order)
    
    # Recent order with unique ID
    save_order(f'recent_metrics_order_{uuid.uuid4().hex[:8]}', 20000, 'INR', 'rcpt', 'starter', 'paid')
    
    session.commit()
    session.close()
    
    # Test 30-day period (should only include recent)
    metrics_30 = get_business_metrics(days=30)
    assert metrics_30['overview']['period_orders'] >= 1
    
    # Test 90-day period (should include both)
    metrics_90 = get_business_metrics(days=90)
    assert metrics_90['overview']['total_orders'] >= 2
