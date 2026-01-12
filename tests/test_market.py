import time
import pytest

from utils import init_db, save_order, mark_order_paid


def _seed_market_data(tmp_path, monkeypatch):
    dbfile = tmp_path / 'market.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    now = time.time()
    
    from models import get_engine, get_session, Order
    from utils import _get_db_url
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    # High demand & conversion for starter
    for i in range(10):
        oid = f'st_{i}'
        save_order(oid, amount=9900, currency='INR', receipt=f'rcpt_st_{i}', product='starter')
        mark_order_paid(oid, f'pay_{oid}')
        order = session.query(Order).filter_by(id=oid).first()
        order.paid_at = now - (i * 10 * 86400)
        session.commit()
    
    # Moderate for pro
    for i in range(5):
        oid = f'pro_{i}'
        save_order(oid, amount=49900, currency='INR', receipt=f'rcpt_pro_{i}', product='pro')
        if i % 2 == 0:
            mark_order_paid(oid, f'pay_{oid}')
            order = session.query(Order).filter_by(id=oid).first()
            order.paid_at = now - (i * 12 * 86400)
            session.commit()
    
    session.close()


def test_market_engine(tmp_path, monkeypatch):
    _seed_market_data(tmp_path, monkeypatch)
    from market_intelligence import compute_signals, competitor_price_index, generate_insights, market_summary
    
    sig = compute_signals(90)
    assert isinstance(sig, dict)
    assert 'starter' in sig and 'pro' in sig
    
    idx = competitor_price_index(90)
    assert isinstance(idx, dict)
    assert 'starter' in idx
    
    insights = generate_insights(90)
    assert isinstance(insights, list)
    assert len(insights) >= 1
    
    summary = market_summary(90)
    assert 'signals' in summary and 'insights' in summary


def test_market_api_and_admin(client, tmp_path, monkeypatch):
    _seed_market_data(tmp_path, monkeypatch)
    
    rv = client.get('/admin/market')
    assert rv.status_code == 200
    assert b'Market Intelligence' in rv.data
    
    r1 = client.get('/api/market/insights?days=90')
    assert r1.status_code == 200
    d1 = r1.get_json()
    assert d1['success'] is True
    assert isinstance(d1['insights'], list)
    
    r2 = client.get('/api/market/summary')
    assert r2.status_code == 200
    d2 = r2.get_json()
    assert d2['success'] is True
    assert 'summary' in d2
import time
import pytest

from utils import init_db, save_order, mark_order_paid


def _seed_market_data(tmp_path, monkeypatch):
    dbfile = tmp_path / 'market.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    now = time.time()
    
    from models import get_engine, get_session, Order
    from utils import _get_db_url
    
    # Starter grows in second half
    for i in range(4):
        oid = f'st_{i}'
        save_order(oid, amount=9900, currency='INR', receipt=f'rcpt_{i}', product='starter')
        mark_order_paid(oid, f'pay_{oid}')
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        order = session.query(Order).filter_by(id=oid).first()
        order.created_at = now - (90 * 86400) + (i * 10 * 86400)  # spread across window
        order.paid_at = order.created_at
        session.commit()
        session.close()
    
    # Pro baseline across halves
    for i in range(4):
        oid = f'pro_{i}'
        save_order(oid, amount=49900, currency='INR', receipt=f'rcpt_pro_{i}', product='pro')
        mark_order_paid(oid, f'pay_{oid}')
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        order = session.query(Order).filter_by(id=oid).first()
        order.created_at = now - (90 * 86400) + (i * 15 * 86400)
        order.paid_at = order.created_at
        session.commit()
        session.close()


def test_market_engine(tmp_path, monkeypatch):
    _seed_market_data(tmp_path, monkeypatch)
    from market_intelligence import analyze_market_trends, competitor_insights, sentiment_proxy, market_insights_summary
    
    trends = analyze_market_trends(90)
    assert 'revenue_share_percent' in trends
    assert 'momentum_percent' in trends
    assert isinstance(trends['top_products'], list)
    
    comps = competitor_insights()
    assert 'comparison' in comps
    assert 'starter' in comps['comparison']
    
    senti = sentiment_proxy(90)
    assert 'sentiment' in senti
    assert isinstance(senti['sentiment'], dict)
    
    summary = market_insights_summary(90)
    assert 'trends' in summary and 'competitors' in summary and 'sentiment' in summary


def test_market_api_and_admin(client, tmp_path, monkeypatch):
    _seed_market_data(tmp_path, monkeypatch)
    
    # Admin dashboard
    rv = client.get('/admin/market')
    assert rv.status_code == 200
    assert b'Market Intelligence' in rv.data
    
    # Trends API
    r1 = client.get('/api/market/trends?days=90')
    assert r1.status_code == 200
    data1 = r1.get_json()
    assert data1['success'] is True
    assert 'trends' in data1
    
    # Competitors API
    r2 = client.get('/api/market/competitors')
    assert r2.status_code == 200
    data2 = r2.get_json()
    assert data2['success'] is True
    assert 'competitors' in data2
    
    # Sentiment API
    r3 = client.get('/api/market/sentiment?days=90')
    assert r3.status_code == 200
    data3 = r3.get_json()
    assert data3['success'] is True
    assert 'sentiment' in data3
