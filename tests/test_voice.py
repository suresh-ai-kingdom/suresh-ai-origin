import time
import json
import pytest

from utils import init_db


def _seed_voice(client, tmp_path, monkeypatch):
    dbfile = tmp_path / 'voice.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    # Submit a few analyses via API
    payloads = [
        {
            'receipt': 'rcpt_1',
            'transcript': 'I love the pro pack, but can I get a discount?',
            'duration_secs': 180,
        },
        {
            'receipt': 'rcpt_2',
            'transcript': 'There is a bug causing issues, need support please',
            'duration_secs': 240,
        },
        {
            'receipt': 'rcpt_3',
            'transcript': 'I want to upgrade to premium, looks excellent',
            'duration_secs': 120,
        },
    ]
    for p in payloads:
        rv = client.post('/api/voice/analyze', data=json.dumps(p), content_type='application/json')
        assert rv.status_code == 200
        d = rv.get_json()
        assert d['success'] is True
        assert 'result' in d


def test_voice_engine(tmp_path, monkeypatch, client):
    _seed_voice(client, tmp_path, monkeypatch)
    from voice_analytics import list_analyses, aggregate_metrics

    items = list_analyses(90)
    assert isinstance(items, list)
    assert len(items) >= 3
    assert any('DISCOUNT' in i['intents'] for i in items)

    m = aggregate_metrics(90)
    assert 'avg_sentiment' in m and 'top_intents' in m
    assert any(t[0] in ['SUPPORT', 'UPGRADE', 'DISCOUNT'] for t in m['top_intents'])


def test_voice_api_and_admin(tmp_path, monkeypatch, client):
    _seed_voice(client, tmp_path, monkeypatch)

    rv = client.get('/admin/voice')
    assert rv.status_code == 200
    assert b'Voice Analytics' in rv.data

    r1 = client.get('/api/voice/metrics?days=90')
    assert r1.status_code == 200
    d1 = r1.get_json()
    assert d1['success'] is True
    assert 'metrics' in d1

    r2 = client.get('/api/voice/list?days=90')
    assert r2.status_code == 200
    d2 = r2.get_json()
    assert d2['success'] is True
    assert isinstance(d2['items'], list)
