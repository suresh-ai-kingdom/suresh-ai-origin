import time
import secrets


def test_keepalive_rate_limit_allowed(client, monkeypatch):
    monkeypatch.setenv('ADMIN_USERNAME', 'admin')
    monkeypatch.setenv('ADMIN_PASSWORD', 'secret')
    monkeypatch.setenv('ADMIN_KEEPALIVE_RATE_LIMIT', '3')
    monkeypatch.setenv('ADMIN_KEEPALIVE_RATE_WINDOW', '60')
    token = secrets.token_urlsafe(32)
    with client.session_transaction() as sess:
        sess['admin_authenticated'] = True
        sess['admin_username'] = 'admin'
        sess['admin_logged_in_at'] = time.time()
        sess['csrf_token'] = token
    for i in range(3):
        rv = client.post('/admin/keepalive', headers={'X-CSRF-Token': token})
        assert rv.status_code == 200
    # cleanup
    from app import _reset_rate_limit_store
    _reset_rate_limit_store()


def test_keepalive_rate_limit_exceeded(client, monkeypatch):
    monkeypatch.setenv('ADMIN_USERNAME', 'admin')
    monkeypatch.setenv('ADMIN_PASSWORD', 'secret')
    monkeypatch.setenv('ADMIN_KEEPALIVE_RATE_LIMIT', '2')
    monkeypatch.setenv('ADMIN_KEEPALIVE_RATE_WINDOW', '60')
    token = secrets.token_urlsafe(32)
    with client.session_transaction() as sess:
        sess['admin_authenticated'] = True
        sess['admin_username'] = 'admin'
        sess['admin_logged_in_at'] = time.time()
        sess['csrf_token'] = token
    rv1 = client.post('/admin/keepalive', headers={'X-CSRF-Token': token})
    assert rv1.status_code == 200
    rv2 = client.post('/admin/keepalive', headers={'X-CSRF-Token': token})
    assert rv2.status_code == 200
    rv3 = client.post('/admin/keepalive', headers={'X-CSRF-Token': token})
    assert rv3.status_code == 429
    assert 'Retry-After' in rv3.headers
    # cleanup
    from app import _reset_rate_limit_store
    _reset_rate_limit_store()
