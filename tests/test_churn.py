import time
import pytest

from utils import init_db, save_order, mark_order_paid


def _seed_churn_data(tmp_path, monkeypatch):
    dbfile = tmp_path / 'churn.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    now = time.time()
    
    # Customer 1: active, low risk (recent purchase, multiple orders)
    for i in range(3):
        oid = f'active_{i}'
        save_order(oid, amount=9900, currency='INR', receipt='active_customer', product='starter')
        mark_order_paid(oid, f'pay_{oid}')
        # Artificially set paid_at times
        from models import get_engine, get_session, Order
        from utils import _get_db_url
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        order = session.query(Order).filter_by(id=oid).first()
        order.paid_at = now - (i * 15 * 86400)  # 15, 30, 45 days ago
        session.commit()
        session.close()
    
    # Customer 2: high risk (last purchase 90 days ago, single order)
    oid2 = 'dormant_1'
    save_order(oid2, amount=49900, currency='INR', receipt='dormant_customer', product='pro')
    mark_order_paid(oid2, f'pay_{oid2}')
    from models import get_engine, get_session, Order
    from utils import _get_db_url
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    order2 = session.query(Order).filter_by(id=oid2).first()
    order2.paid_at = now - (90 * 86400)
    session.commit()
    session.close()
    
    # Customer 3: critical risk (last purchase 120 days ago, multiple but declining)
    for i in range(2):
        oid3 = f'critical_{i}'
        save_order(oid3, amount=99900, currency='INR', receipt='critical_customer', product='premium')
        mark_order_paid(oid3, f'pay_{oid3}')
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        order3 = session.query(Order).filter_by(id=oid3).first()
        order3.paid_at = now - (120 + i * 30) * 86400  # 120, 150 days ago
        session.commit()
        session.close()


def test_compute_churn_risk(tmp_path, monkeypatch):
    _seed_churn_data(tmp_path, monkeypatch)
    from churn_prediction import compute_churn_risk
    
    # Active customer - should have low risk
    active_risk = compute_churn_risk('active_customer')
    assert active_risk['risk_level'] in ('LOW', 'MEDIUM')
    assert active_risk['order_count'] == 3
    assert active_risk['last_purchase_days'] < 20
    
    # Dormant customer - should have high/critical risk
    dormant_risk = compute_churn_risk('dormant_customer')
    assert dormant_risk['risk_level'] in ('HIGH', 'CRITICAL')
    assert dormant_risk['order_count'] == 1
    assert dormant_risk['last_purchase_days'] >= 80
    assert 'No purchase in' in ' '.join(dormant_risk['reasons'])
    
    # Critical customer - should have critical risk
    critical_risk = compute_churn_risk('critical_customer')
    assert critical_risk['risk_level'] in ('HIGH', 'CRITICAL')
    assert critical_risk['order_count'] == 2
    assert critical_risk['last_purchase_days'] >= 100


def test_get_at_risk_customers(tmp_path, monkeypatch):
    _seed_churn_data(tmp_path, monkeypatch)
    from churn_prediction import get_at_risk_customers
    
    at_risk = get_at_risk_customers(min_risk=50, limit=10)
    assert isinstance(at_risk, list)
    
    # Should have at least dormant and critical customers
    assert len(at_risk) >= 1
    
    # Should be sorted by risk score descending
    if len(at_risk) > 1:
        assert at_risk[0]['risk_score'] >= at_risk[-1]['risk_score']
    
    # All should meet min_risk threshold
    for customer in at_risk:
        assert customer['risk_score'] >= 50


def test_churn_stats(tmp_path, monkeypatch):
    _seed_churn_data(tmp_path, monkeypatch)
    from churn_prediction import churn_stats
    
    stats = churn_stats()
    assert stats['total_customers'] == 3
    assert stats['critical_risk'] >= 0
    assert stats['high_risk'] >= 0
    assert stats['medium_risk'] >= 0
    assert stats['low_risk'] >= 0
    assert stats['avg_risk_score'] >= 0
    assert stats['customers_needing_attention'] >= 1


def test_generate_alerts(tmp_path, monkeypatch):
    _seed_churn_data(tmp_path, monkeypatch)
    from churn_prediction import generate_alerts
    
    alerts = generate_alerts(min_risk=70)
    assert isinstance(alerts, list)
    
    for alert in alerts:
        assert 'receipt' in alert
        assert 'risk_level' in alert
        assert 'risk_score' in alert
        assert 'priority' in alert
        assert 'action' in alert
        assert alert['risk_score'] >= 70


def test_churn_api_endpoints(client, tmp_path, monkeypatch):
    _seed_churn_data(tmp_path, monkeypatch)
    
    # Admin dashboard
    rv = client.get('/admin/churn')
    assert rv.status_code == 200
    assert b'Churn Prediction' in rv.data
    
    # Customer risk API
    rv2 = client.get('/api/churn/customer/active_customer')
    assert rv2.status_code == 200
    data = rv2.get_json()
    assert data['success'] is True
    assert 'result' in data
    assert data['result']['receipt'] == 'active_customer'
    
    # At-risk customers API
    rv3 = client.get('/api/churn/at-risk?min_risk=50&limit=10')
    assert rv3.status_code == 200
    data3 = rv3.get_json()
    assert data3['success'] is True
    assert 'customers' in data3
    
    # Stats API
    rv4 = client.get('/api/churn/stats')
    assert rv4.status_code == 200
    data4 = rv4.get_json()
    assert data4['success'] is True
    assert 'stats' in data4
    assert data4['stats']['total_customers'] == 3
    
    # Alerts API
    rv5 = client.get('/api/churn/alerts?min_risk=70')
    assert rv5.status_code == 200
    data5 = rv5.get_json()
    assert data5['success'] is True
    assert 'alerts' in data5
