import pytest


def test_admin_no_token_allows_access(client, monkeypatch):
    # Ensure ADMIN_TOKEN is not set -> admin pages available
    monkeypatch.delenv('ADMIN_TOKEN', raising=False)
    rv = client.get('/admin/webhooks')
    assert rv.status_code == 200
    rv2 = client.get('/admin/orders')
    assert rv2.status_code == 200


def test_admin_token_required_and_authorized(client, monkeypatch):
    monkeypatch.setenv('ADMIN_TOKEN', 'secrettoken')
    # without header -> 401
    rv = client.get('/admin/webhooks')
    assert rv.status_code == 401
    # with wrong header -> 401
    rv2 = client.get('/admin/webhooks', headers={'Authorization': 'Bearer wrong'})
    assert rv2.status_code == 401
    # with correct header -> 200
    rv3 = client.get('/admin/webhooks', headers={'Authorization': 'Bearer secrettoken'})
    assert rv3.status_code == 200


def test_admin_session_login_logout(client, monkeypatch):
    # Configure username/password-based admin login
    monkeypatch.setenv('ADMIN_USERNAME', 'admin')
    monkeypatch.setenv('ADMIN_PASSWORD', 'secret')
    # Accessing admin pages without login should redirect to login page
    rv = client.get('/admin/webhooks')
    assert rv.status_code in (302, 401)

    # GET login page
    rv = client.get('/admin/login')
    assert rv.status_code == 200

    # Grab CSRF token set in session and use it for POSTs
    with client.session_transaction() as sess:
        token = sess.get('csrf_token')
        if not token:
            import secrets
            token = secrets.token_urlsafe(32)
            sess['csrf_token'] = token

    # Invalid credentials show an error
    rv = client.post('/admin/login', data={'username': 'admin', 'password': 'wrong', 'csrf_token': token}, follow_redirects=True)
    assert b'Invalid credentials' in rv.data

    # Valid credentials should redirect and set session
    rv = client.post('/admin/login', data={'username': 'admin', 'password': 'secret', 'csrf_token': token}, follow_redirects=False)
    assert rv.status_code in (302, 303)
    # Verify session is set
    with client.session_transaction() as sess:
        assert sess.get('admin_authenticated') is True
        assert sess.get('admin_username') == 'admin'

    # Logout clears session and protects page again
    rv = client.get('/admin/logout', follow_redirects=True)
    assert rv.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get('admin_authenticated') is None
    rv3 = client.get('/admin/webhooks')
    assert rv3.status_code in (302, 401)


def test_admin_password_hash_login(client, monkeypatch):
    from werkzeug.security import generate_password_hash
    monkeypatch.setenv('ADMIN_USERNAME', 'admin')
    monkeypatch.setenv('ADMIN_PASSWORD_HASH', generate_password_hash('secret'))
    # GET login page to obtain csrf token
    rv_get = client.get('/admin/login')
    assert rv_get.status_code == 200
    with client.session_transaction() as sess:
        token = sess.get('csrf_token')
        if not token:
            import secrets
            token = secrets.token_urlsafe(32)
            sess['csrf_token'] = token
    # Should be able to log in using the hashed password
    rv = client.post('/admin/login', data={'username': 'admin', 'password': 'secret', 'csrf_token': token}, follow_redirects=False)
    assert rv.status_code in (302, 303)
    with client.session_transaction() as sess:
        assert sess.get('admin_authenticated') is True
        assert sess.get('admin_username') == 'admin'


def test_admin_session_timeout(client, monkeypatch):
    monkeypatch.setenv('ADMIN_USERNAME', 'admin')
    monkeypatch.setenv('ADMIN_PASSWORD', 'secret')
    monkeypatch.setenv('ADMIN_SESSION_TIMEOUT', '1')
    # Simulate a logged-in session directly (avoid cookie propagation issues in test client)
    import time
    with client.session_transaction() as sess:
        sess['admin_authenticated'] = True
        sess['admin_username'] = 'admin'
        sess['admin_logged_in_at'] = time.time()
    # Immediately accessing admin page should be allowed
    rv_after = client.get('/admin/webhooks')
    assert b'Logout' in rv_after.data

    # Wait past timeout
    import time
    time.sleep(2)
    # Accessing admin page should redirect to login (session expired)
    rv2 = client.get('/admin/webhooks')
    assert rv2.status_code in (302, 401)
