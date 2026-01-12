import time
import pytest

from utils import init_db, save_order, mark_order_paid


def _seed_automations(tmp_path, monkeypatch):
    dbfile = tmp_path / 'automations.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    
    # Seed orders for automation triggers
    for i in range(5):
        oid = f'auto_{i}'
        save_order(oid, amount=9900, currency='INR', receipt=f'rcpt_auto_{i}', product='starter')
        if i < 2:
            mark_order_paid(oid, f'pay_{oid}')


def test_automation_engine(tmp_path, monkeypatch):
    _seed_automations(tmp_path, monkeypatch)
    from automation_workflows import (
        churn_retention_workflow, payment_retry_workflow,
        segment_campaign_workflow, voice_support_workflow,
        social_content_workflow, get_automation_history
    )
    
    # Test individual workflows
    result1 = churn_retention_workflow(days_back=90)
    assert 'executed' in result1
    
    result2 = payment_retry_workflow(days_back=7)
    assert 'executed' in result2
    assert result2['executed'] >= 0  # May have unpaid orders
    
    result3 = segment_campaign_workflow(days_back=30)
    assert 'executed' in result3
    
    result4 = voice_support_workflow(days_back=7)
    assert 'executed' in result4
    
    result5 = social_content_workflow(days_back=7)
    assert 'executed' in result5
    
    # Check history logging
    history = get_automation_history(days_back=7, limit=100)
    assert isinstance(history, list)


def test_automation_api_and_admin(client, tmp_path, monkeypatch):
    _seed_automations(tmp_path, monkeypatch)
    
    # Admin page
    rv = client.get('/admin/automations')
    assert rv.status_code == 200
    assert b'Automation Workflows' in rv.data
    
    # Trigger workflow via API
    r1 = client.post('/api/automations/trigger', json={'workflow': 'social_content', 'days': 7})
    assert r1.status_code == 200
    d1 = r1.get_json()
    assert d1['success'] is True
    assert 'executed' in d1
    
    # Get history
    r2 = client.get('/api/automations/history?days=7')
    assert r2.status_code == 200
    d2 = r2.get_json()
    assert d2['success'] is True
    assert isinstance(d2['history'], list)
