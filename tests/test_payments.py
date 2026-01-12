import time
import json
import pytest

from utils import init_db, save_order, mark_order_paid, save_payment


def _seed_payments(tmp_path, monkeypatch):
    dbfile = tmp_path / 'payments.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    now = time.time()

    # Create 6 orders, 3 paid quickly, 1 paid after delay, 2 unpaid
    for i in range(6):
        oid = f'ord_{i}'
        save_order(oid, amount=9900 if i < 3 else 49900, currency='INR', receipt=f'rcpt_{i}', product='starter' if i < 3 else 'pro')
        if i in (0, 1, 2, 3):
            mark_order_paid(oid, f'pay_{oid}')
    # Add failed payments for unpaid orders with reasons
    for i in (4, 5):
        pid = f'fail_{i}'
        payload = {'order_id': f'ord_{i}', 'reason': 'insufficient_funds'}
        save_payment(pid, f'ord_{i}', payload)


def test_payment_engine(tmp_path, monkeypatch):
    _seed_payments(tmp_path, monkeypatch)
    from payment_intelligence import compute_payment_metrics, failed_payment_reasons, payment_insights, dashboard_summary

    metrics = compute_payment_metrics(90)
    assert metrics['orders_created'] == 6
    assert metrics['orders_paid'] == 4
    assert metrics['failed_orders'] == 2
    assert 'avg_capture_latency_hours' in metrics

    reasons = failed_payment_reasons(90)
    assert reasons.get('insufficient_funds', 0) >= 1

    insights = payment_insights(90)
    assert isinstance(insights, list)
    assert len(insights) >= 1

    summary = dashboard_summary(90)
    assert 'metrics' in summary and 'reasons' in summary and 'insights' in summary


def test_payment_api_and_admin(client, tmp_path, monkeypatch):
    _seed_payments(tmp_path, monkeypatch)

    rv = client.get('/admin/payments')
    assert rv.status_code == 200
    assert b'Payment Intelligence' in rv.data

    r1 = client.get('/api/payments/metrics?days=90')
    assert r1.status_code == 200
    d1 = r1.get_json()
    assert d1['success'] is True
    assert 'metrics' in d1

    r2 = client.get('/api/payments/insights?days=90')
    assert r2.status_code == 200
    d2 = r2.get_json()
    assert d2['success'] is True
    assert isinstance(d2['insights'], list)
