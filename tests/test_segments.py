import time
import pytest

from utils import init_db, save_order, mark_order_paid


def _seed_segment_data(tmp_path, monkeypatch):
    dbfile = tmp_path / 'segments.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    now = time.time()
    
    from models import get_engine, get_session, Order
    from utils import _get_db_url
    
    # VIP customer: 5+ orders, high value
    for i in range(6):
        oid = f'vip_{i}'
        save_order(oid, amount=19900, currency='INR', receipt='vip_customer', product='premium')
        mark_order_paid(oid, f'pay_{oid}')
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        order = session.query(Order).filter_by(id=oid).first()
        order.paid_at = now - (i * 10 * 86400)  # Recent purchases
        session.commit()
        session.close()
    
    # LOYAL customer: 3-4 orders, decent value
    for i in range(3):
        oid = f'loyal_{i}'
        save_order(oid, amount=9900, currency='INR', receipt='loyal_customer', product='pro')
        mark_order_paid(oid, f'pay_{oid}')
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        order = session.query(Order).filter_by(id=oid).first()
        order.paid_at = now - (i * 20 * 86400)
        session.commit()
        session.close()
    
    # PROMISING: 2 orders
    for i in range(2):
        oid = f'prom_{i}'
        save_order(oid, amount=4900, currency='INR', receipt='promising_customer', product='starter')
        mark_order_paid(oid, f'pay_{oid}')
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        order = session.query(Order).filter_by(id=oid).first()
        order.paid_at = now - (i * 25 * 86400)
        session.commit()
        session.close()
    
    # NEW: single order
    oid_new = 'new_1'
    save_order(oid_new, amount=9900, currency='INR', receipt='new_customer', product='starter')
    mark_order_paid(oid_new, f'pay_{oid_new}')
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    order = session.query(Order).filter_by(id=oid_new).first()
    order.paid_at = now - (5 * 86400)
    session.commit()
    session.close()
    
    # AT_RISK: dormant customer
    for i in range(2):
        oid_risk = f'risk_{i}'
        save_order(oid_risk, amount=9900, currency='INR', receipt='risk_customer', product='pro')
        mark_order_paid(oid_risk, f'pay_{oid_risk}')
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        order = session.query(Order).filter_by(id=oid_risk).first()
        order.paid_at = now - (70 + i * 30) * 86400  # 70, 100 days ago
        session.commit()
        session.close()


def test_analyze_segments(tmp_path, monkeypatch):
    _seed_segment_data(tmp_path, monkeypatch)
    from segment_optimization import analyze_segments
    
    segments = analyze_segments(days_back=365)
    
    assert isinstance(segments, dict)
    assert 'VIP' in segments
    assert 'LOYAL' in segments
    assert 'PROMISING' in segments
    assert 'NEW' in segments
    assert 'AT_RISK' in segments
    
    # VIP should have highest revenue
    assert segments['VIP']['count'] == 1
    assert segments['VIP']['revenue'] > 1000
    
    # NEW should have single-order customers
    assert segments['NEW']['count'] == 1
    assert segments['NEW']['avg_orders'] == 1.0


def test_identify_opportunities(tmp_path, monkeypatch):
    _seed_segment_data(tmp_path, monkeypatch)
    from segment_optimization import identify_opportunities
    
    opportunities = identify_opportunities(days_back=365)
    
    assert isinstance(opportunities, list)
    assert len(opportunities) > 0
    
    # Should have opportunities for each segment
    segments_with_opps = [o['segment'] for o in opportunities]
    assert 'AT_RISK' in segments_with_opps or 'PROMISING' in segments_with_opps
    
    # Check structure
    for opp in opportunities:
        assert 'segment' in opp
        assert 'opportunity' in opp
        assert 'potential_customers' in opp
        assert 'priority' in opp
        assert 'actions' in opp
        assert 'estimated_revenue_lift' in opp
        assert isinstance(opp['actions'], list)


def test_segment_health_metrics(tmp_path, monkeypatch):
    _seed_segment_data(tmp_path, monkeypatch)
    from segment_optimization import segment_health_metrics
    
    health = segment_health_metrics(days_back=365)
    
    assert isinstance(health, dict)
    
    for segment_name, metrics in health.items():
        assert 'count' in metrics
        assert 'revenue' in metrics
        assert 'health_score' in metrics
        assert 'status' in metrics
        assert 0 <= metrics['health_score'] <= 100
        assert metrics['status'] in ('HEALTHY', 'NEEDS_ATTENTION', 'CRITICAL')


def test_recommend_actions(tmp_path, monkeypatch):
    _seed_segment_data(tmp_path, monkeypatch)
    from segment_optimization import recommend_actions
    
    vip_actions = recommend_actions('VIP')
    assert isinstance(vip_actions, list)
    assert len(vip_actions) > 0
    
    new_actions = recommend_actions('NEW')
    assert 'welcome' in ' '.join(new_actions).lower()


def test_optimization_summary(tmp_path, monkeypatch):
    _seed_segment_data(tmp_path, monkeypatch)
    from segment_optimization import optimization_summary
    
    summary = optimization_summary(days_back=365)
    
    assert 'segments' in summary
    assert 'opportunities' in summary
    assert 'health' in summary
    assert 'summary' in summary
    
    assert summary['summary']['total_opportunities'] >= 0
    assert summary['summary']['total_revenue_potential'] >= 0
    assert 'healthiest_segment' in summary['summary']


def test_segments_api_endpoints(client, tmp_path, monkeypatch):
    _seed_segment_data(tmp_path, monkeypatch)
    
    # Admin dashboard
    rv = client.get('/admin/segments')
    assert rv.status_code == 200
    assert b'Segment Optimization' in rv.data
    
    # Analyze API
    rv2 = client.get('/api/segments/analyze?days=90')
    assert rv2.status_code == 200
    data = rv2.get_json()
    assert data['success'] is True
    assert 'segments' in data
    
    # Opportunities API
    rv3 = client.get('/api/segments/opportunities')
    assert rv3.status_code == 200
    data3 = rv3.get_json()
    assert data3['success'] is True
    assert 'opportunities' in data3
    
    # Health API
    rv4 = client.get('/api/segments/health')
    assert rv4.status_code == 200
    data4 = rv4.get_json()
    assert data4['success'] is True
    assert 'health' in data4
    
    # Actions API
    rv5 = client.get('/api/segments/actions/VIP')
    assert rv5.status_code == 200
    data5 = rv5.get_json()
    assert data5['success'] is True
    assert 'actions' in data5
    assert isinstance(data5['actions'], list)
