import time
import secrets


def test_keepalive_updates_session(client, monkeypatch):
    monkeypatch.setenv('ADMIN_USERNAME', 'admin')
    monkeypatch.setenv('ADMIN_PASSWORD', 'secret')
    token = secrets.token_urlsafe(32)
    with client.session_transaction() as sess:
        sess['admin_authenticated'] = True
        sess['admin_username'] = 'admin'
        sess['admin_logged_in_at'] = time.time() - 100
        sess['csrf_token'] = token
    rv = client.post('/admin/keepalive', headers={'X-CSRF-Token': token})
    assert rv.status_code == 200
    assert rv.json.get('ok') is True
    with client.session_transaction() as sess2:
        assert sess2.get('admin_logged_in_at') and sess2['admin_logged_in_at'] > time.time() - 5


def test_keepalive_requires_csrf(client, monkeypatch):
    monkeypatch.setenv('ADMIN_USERNAME', 'admin')
    monkeypatch.setenv('ADMIN_PASSWORD', 'secret')
    with client.session_transaction() as sess:
        sess['admin_authenticated'] = True
        sess['admin_username'] = 'admin'
        sess['admin_logged_in_at'] = time.time() - 100
    rv = client.post('/admin/keepalive')
    assert rv.status_code == 403


def test_header_includes_countdown(client, monkeypatch):
    monkeypatch.setenv('ADMIN_USERNAME', 'admin')
    monkeypatch.setenv('ADMIN_SESSION_TIMEOUT', '300')
    with client.session_transaction() as sess:
        sess['admin_authenticated'] = True
        sess['admin_username'] = 'admin'
        sess['admin_logged_in_at'] = time.time()
    rv = client.get('/admin/webhooks')
    assert b'session-countdown' in rv.data
    assert b'name="csrf-token"' in rv.data
