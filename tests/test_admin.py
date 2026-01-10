def test_admin_pages(client):
    rv = client.get('/admin/webhooks')
    assert rv.status_code == 200
    assert b'Login' in rv.data or b'Logout' in rv.data
    rv2 = client.get('/admin/orders')
    assert rv2.status_code == 200
    assert b'Login' in rv2.data or b'Logout' in rv2.data


def test_admin_login_logout_links(client, monkeypatch):
    monkeypatch.setenv('ADMIN_USERNAME', 'admin')
    monkeypatch.setenv('ADMIN_PASSWORD', 'secret')
    # Not logged in -> page shows Login link
    rv = client.get('/admin/webhooks')
    assert b'/admin/login' in rv.data

    # Simulate login by setting the session directly (avoid brittle cookie handling)
    with client.session_transaction() as sess:
        sess['admin_authenticated'] = True
        sess['admin_username'] = 'admin'
    # Confirm session is present (server-side)
    with client.session_transaction() as sess:
        assert sess.get('admin_authenticated') is True
    # Logout and confirm Login shown
    client.get('/admin/logout', follow_redirects=True)
    rv3 = client.get('/admin/webhooks')
    assert b'/admin/login' in rv3.data
