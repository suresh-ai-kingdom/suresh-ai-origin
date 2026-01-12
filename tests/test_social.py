import time
import pytest

from utils import init_db, save_order, mark_order_paid


def _seed_social(tmp_path, monkeypatch):
    dbfile = tmp_path / 'social.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    # Seed orders to influence signals
    for i in range(3):
        oid = f'st_{i}'
        save_order(oid, amount=9900, currency='INR', receipt=f'rcpt_st_{i}', product='starter')
        mark_order_paid(oid, f'pay_{oid}')
    for i in range(2):
        oid = f'pro_{i}'
        save_order(oid, amount=49900, currency='INR', receipt=f'rcpt_pro_{i}', product='pro')
        if i == 0:
            mark_order_paid(oid, f'pay_{oid}')


def test_social_engine(tmp_path, monkeypatch):
    _seed_social(tmp_path, monkeypatch)
    from social_auto_share import generate_posts, generate_schedule

    posts = generate_posts(30)
    assert isinstance(posts, list)
    assert len(posts) >= 1
    assert all('message' in p and 'product' in p for p in posts)

    schedule = generate_schedule(30)
    assert isinstance(schedule, list)
    assert len(schedule) >= 1
    assert all('platform' in s and 'scheduled_at' in s for s in schedule)


def test_social_api_and_admin(client, tmp_path, monkeypatch):
    _seed_social(tmp_path, monkeypatch)

    rv = client.get('/admin/social')
    assert rv.status_code == 200
    assert b'Social Auto-Share' in rv.data

    r1 = client.get('/api/social/schedule?days=30')
    assert r1.status_code == 200
    d1 = r1.get_json()
    assert d1['success'] is True
    assert isinstance(d1['schedule'], list)

    r2 = client.get('/api/social/insights?days=30')
    assert r2.status_code == 200
    d2 = r2.get_json()
    assert d2['success'] is True
    assert isinstance(d2['posts'], list)
