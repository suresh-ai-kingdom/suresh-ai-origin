import time
import pytest

from utils import init_db, save_order, mark_order_paid


def _seed_orders(tmp_path, monkeypatch):
    dbfile = tmp_path / 'pricing.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    # starter: high demand and good conversion
    for i in range(12):
        oid = f'st_{i}'
        save_order(oid, amount=9900, currency='INR', receipt=f'rcpt_st_{i}', product='starter')
        if i % 2 == 0:
            mark_order_paid(oid, f'pay_{oid}')
    # pro: moderate demand low conversion
    for i in range(6):
        oid = f'pro_{i}'
        save_order(oid, amount=49900, currency='INR', receipt=f'rcpt_pro_{i}', product='pro')
        if i % 3 == 0:
            mark_order_paid(oid, f'pay_{oid}')
    # premium: low demand, no conversion
    for i in range(2):
        oid = f'pm_{i}'
        save_order(oid, amount=99900, currency='INR', receipt=f'rcpt_pm_{i}', product='premium')


def test_engine_dynamic_prices(tmp_path, monkeypatch):
    _seed_orders(tmp_path, monkeypatch)
    from pricing import compute_base_price, compute_dynamic_price, simulate_price_scenarios
    base_starter = compute_base_price('starter')
    dyn_starter = compute_dynamic_price('starter')
    assert isinstance(dyn_starter, int)
    # starter should be adjusted near/above base under good metrics
    assert dyn_starter >= int(base_starter * 0.9)

    base_premium = compute_base_price('premium')
    dyn_premium = compute_dynamic_price('premium')
    assert isinstance(dyn_premium, int)
    # premium likely below or near base with poor metrics
    assert dyn_premium <= int(base_premium * 1.1)

    scenarios = simulate_price_scenarios('starter')
    assert isinstance(scenarios, list) and len(scenarios) == 3
    for s in scenarios:
        assert 'price_rupees' in s and 'estimated_conversion' in s and 'estimated_revenue_per_100' in s


def test_pricing_api_and_admin(client, tmp_path, monkeypatch):
    _seed_orders(tmp_path, monkeypatch)
    # admin dashboard page
    rv = client.get('/admin/pricing')
    assert rv.status_code == 200
    assert b'Dynamic Pricing' in rv.data
    # product API
    r1 = client.get('/api/pricing/product/starter')
    assert r1.status_code == 200
    data1 = r1.get_json()
    assert data1['success'] is True
    assert 'dynamic_price_rupees' in data1
    # all prices API
    r2 = client.get('/api/pricing/all')
    assert r2.status_code == 200
    data2 = r2.get_json()
    assert data2['success'] is True
    assert 'prices' in data2 and 'starter' in data2['prices']
    # stats API
    r3 = client.get('/api/pricing/stats')
    assert r3.status_code == 200
    data3 = r3.get_json()
    assert data3['success'] is True
    assert 'stats' in data3 and 'starter' in data3['stats']
