import time
import pytest

from utils import init_db, save_order, mark_order_paid


def _seed_campaign_data(tmp_path, monkeypatch):
    dbfile = tmp_path / 'campaigns.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    now = time.time()
    
    from models import get_engine, get_session, Order
    from utils import _get_db_url
    
    # Seed multiple segments
    # NEW
    oid_new = 'new_1'
    save_order(oid_new, amount=9900, currency='INR', receipt='new_customer', product='starter')
    mark_order_paid(oid_new, f'pay_{oid_new}')
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    order = session.query(Order).filter_by(id=oid_new).first()
    order.paid_at = now - (5 * 86400)
    session.commit()
    session.close()
    
    # PROMISING
    for i in range(2):
        oid = f'prom_{i}'
        save_order(oid, amount=4900, currency='INR', receipt='promising_customer', product='starter')
        mark_order_paid(oid, f'pay_{oid}')
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        order = session.query(Order).filter_by(id=oid).first()
        order.paid_at = now - (i * 20 * 86400)
        session.commit()
        session.close()
    
    # LOYAL
    for i in range(3):
        oid = f'loyal_{i}'
        save_order(oid, amount=9900, currency='INR', receipt='loyal_customer', product='pro')
        mark_order_paid(oid, f'pay_{oid}')
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        order = session.query(Order).filter_by(id=oid).first()
        order.paid_at = now - (i * 25 * 86400)
        session.commit()
        session.close()
    
    # AT_RISK
    for i in range(2):
        oid = f'risk_{i}'
        save_order(oid, amount=9900, currency='INR', receipt='risk_customer', product='pro')
        mark_order_paid(oid, f'pay_{oid}')
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        order = session.query(Order).filter_by(id=oid).first()
        order.paid_at = now - (70 + i * 30) * 86400
        session.commit()
        session.close()


def test_campaign_engine(tmp_path, monkeypatch):
    _seed_campaign_data(tmp_path, monkeypatch)
    from campaign_generator import campaign_audience_segments, generate_campaign, suggest_campaigns, campaign_stats
    
    segs = campaign_audience_segments(90)
    assert isinstance(segs, dict)
    assert 'NEW' in segs or 'CASUAL' in segs
    
    camp = generate_campaign('win-back', 'AT_RISK', products=['pro'], discount_percent=25, days_back=90)
    assert 'subject' in camp and 'cta' in camp and 'estimated_revenue_per_100' in camp
    assert camp['discount_percent'] == 25
    
    suggestions = suggest_campaigns(90)
    assert isinstance(suggestions, list) and len(suggestions) >= 1
    
    stats = campaign_stats(90)
    assert 'audiences' in stats and 'suggestion_count' in stats


def test_campaign_api_and_admin(client, tmp_path, monkeypatch):
    _seed_campaign_data(tmp_path, monkeypatch)
    
    # Admin dashboard
    rv = client.get('/admin/campaigns')
    assert rv.status_code == 200
    assert b'Campaign Generator' in rv.data
    
    # Suggestions API
    r1 = client.get('/api/campaigns/suggestions?days=90')
    assert r1.status_code == 200
    data1 = r1.get_json()
    assert data1['success'] is True
    assert isinstance(data1['suggestions'], list)
    
    # Stats API
    r2 = client.get('/api/campaigns/stats')
    assert r2.status_code == 200
    data2 = r2.get_json()
    assert data2['success'] is True
    assert 'stats' in data2
    
    # Create API
    payload = {
        'goal': 'upsell',
        'segment': 'PROMISING',
        'products': ['premium'],
        'discount_percent': 15,
        'days': 90
    }
    r3 = client.post('/api/campaigns/create', json=payload)
    assert r3.status_code in (200, 201)
    data3 = r3.get_json()
    assert data3['success'] is True
    assert 'campaign' in data3
    assert data3['campaign']['goal'] == 'upsell'
