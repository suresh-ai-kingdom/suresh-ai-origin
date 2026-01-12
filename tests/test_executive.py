import time
import pytest

from utils import init_db, save_order, mark_order_paid


def _seed_executive(tmp_path, monkeypatch):
    dbfile = tmp_path / 'executive.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    
    # Seed some basic orders for revenue
    for i in range(5):
        oid = f'exec_{i}'
        save_order(oid, amount=9900, currency='INR', receipt=f'rcpt_exec_{i}', product='starter')
        if i < 3:
            mark_order_paid(oid, f'pay_{oid}')


def test_executive_engine(tmp_path, monkeypatch):
    _seed_executive(tmp_path, monkeypatch)
    from executive_dashboard import executive_summary, critical_alerts
    
    summary = executive_summary(days=30)
    assert 'revenue' in summary
    assert 'subscriptions' in summary
    assert 'clv' in summary
    assert 'churn' in summary
    assert 'market' in summary
    assert 'payments' in summary
    assert 'campaigns' in summary
    assert 'voice' in summary
    assert 'growth' in summary
    assert 'social' in summary
    
    # Check revenue aggregation works
    assert summary['revenue']['total_orders'] == 5
    assert summary['revenue']['paid_orders'] == 3
    
    alerts = critical_alerts(days=30)
    assert isinstance(alerts, list)


def test_executive_dashboard_route(client, tmp_path, monkeypatch):
    _seed_executive(tmp_path, monkeypatch)
    
    rv = client.get('/admin/executive')
    assert rv.status_code == 200
    assert b'Executive Dashboard' in rv.data
    assert b'Revenue' in rv.data
    assert b'MRR' in rv.data
