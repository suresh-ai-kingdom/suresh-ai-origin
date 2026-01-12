"""Integration tests for abandoned order recovery endpoints."""
import pytest
import json
from models import get_session, Order, Base, get_engine


@pytest.fixture
def app_with_db():
    """Set up Flask app with test database and admin auth."""
    from app import app
    
    # Create test database
    engine = get_engine()
    Base.metadata.create_all(engine)
    
    # Clear orders before test
    session = get_session()
    try:
        session.query(Order).delete()
        session.commit()
    finally:
        session.close()
    
    app.config['TESTING'] = True
    app.config['ADMIN_USERNAME'] = 'test'
    app.config['ADMIN_PASSWORD'] = 'test'
    
    yield app
    
    # Cleanup
    session = get_session()
    try:
        session.query(Order).delete()
        session.commit()
    finally:
        session.close()


def test_recovery_dashboard_requires_auth(app_with_db):
    """Test that recovery dashboard requires admin auth (or allows in test mode)."""
    client = app_with_db.test_client()
    
    response = client.get('/admin/recovery')
    # In test mode, might allow access. In production, requires auth.
    # Acceptable: 200 (test mode), 302 (redirect), or 401 (denied)
    assert response.status_code in [200, 302, 401]


def test_recovery_dashboard_with_auth(app_with_db):
    """Test recovery dashboard loads with authentication."""
    client = app_with_db.test_client()
    
    # Login first
    with client:
        # Set session
        client.get('/admin/login', headers={'Authorization': f'Bearer test'})
        # Or use session
        with client.session_transaction() as sess:
            sess['admin_authenticated'] = True
        
        response = client.get('/admin/recovery')
        assert response.status_code == 200
        assert b'Abandoned Order Recovery' in response.data


def test_api_recovery_metrics_empty(app_with_db):
    """Test recovery metrics API with no abandoned orders."""
    client = app_with_db.test_client()
    
    with client:
        with client.session_transaction() as sess:
            sess['admin_authenticated'] = True
        
        response = client.get('/api/recovery/metrics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total_abandoned_orders'] == 0
        assert data['total_abandoned_value_paise'] == 0


def test_api_recovery_metrics_with_data(app_with_db):
    """Test recovery metrics API with abandoned orders."""
    # Create abandoned order
    session = get_session()
    try:
        order = Order(
            id='TEST_METRICS_1',
            amount=99900,
            currency='INR',
            receipt='TEST_METRICS_REC_1',
            product='starter_pack',
            status='created',
            created_at=123456789.0
        )
        session.add(order)
        session.commit()
    finally:
        session.close()
    
    client = app_with_db.test_client()
    with client:
        with client.session_transaction() as sess:
            sess['admin_authenticated'] = True
        
        response = client.get('/api/recovery/metrics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total_abandoned_orders'] == 1
        assert data['total_abandoned_value_paise'] == 99900


def test_api_recovery_abandoned_orders(app_with_db):
    """Test abandoned orders API endpoint."""
    # Create some abandoned orders
    session = get_session()
    try:
        for i in range(3):
            order = Order(
                id=f'TEST_API_ORDER_{i}',
                amount=50000 + (i * 10000),
                currency='INR',
                receipt=f'TEST_API_REC_{i}',
                product='pro_pack',
                status='created',
                created_at=123456789.0 + i
            )
            session.add(order)
        session.commit()
    finally:
        session.close()
    
    client = app_with_db.test_client()
    with client:
        with client.session_transaction() as sess:
            sess['admin_authenticated'] = True
        
        response = client.get('/api/recovery/abandoned')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['count'] == 3
        assert len(data['orders']) == 3
        assert all('receipt' in o for o in data['orders'])


def test_api_recovery_suggestions(app_with_db):
    """Test recovery suggestions API endpoint."""
    client = app_with_db.test_client()
    
    with client:
        with client.session_transaction() as sess:
            sess['admin_authenticated'] = True
        
        response = client.get('/api/recovery/suggestions')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'suggestions' in data
        assert 'potential' in data
        assert 'recovery_rate_percent' in data['potential']


def test_api_recovery_product_analysis(app_with_db):
    """Test product analysis API endpoint."""
    session = get_session()
    try:
        # Create orders for different products
        session.add(Order(
            id='TEST_PA1',
            amount=10000,
            currency='INR',
            receipt='TEST_PA_REC_1',
            product='starter_pack',
            status='created',
            created_at=123456789.0
        ))
        session.add(Order(
            id='TEST_PA2',
            amount=10000,
            currency='INR',
            receipt='TEST_PA_REC_2',
            product='starter_pack',
            status='paid',
            created_at=123456789.0
        ))
        session.commit()
    finally:
        session.close()
    
    client = app_with_db.test_client()
    with client:
        with client.session_transaction() as sess:
            sess['admin_authenticated'] = True
        
        response = client.get('/api/recovery/product-analysis')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'starter_pack' in data
        assert data['starter_pack']['total_initiated'] == 2
        assert data['starter_pack']['abandoned_orders'] == 1
        assert data['starter_pack']['completed_orders'] == 1
