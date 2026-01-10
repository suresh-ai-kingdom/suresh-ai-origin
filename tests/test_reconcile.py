def test_reconcile_endpoint(client, monkeypatch, tmp_path):
    # Setup DB
    dbfile = tmp_path / 'rec.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))

    # Create an order and a payment for it
    from utils import save_order, save_payment, get_order
    save_order('o1', 19900, 'INR', 'r1', 'starter')
    save_payment('p1', 'o1', {'amount': 19900})

    # GET report
    rv = client.get('/admin/reconcile')
    assert rv.status_code == 200
    assert b'Unpaid orders' in rv.data

    # Apply reconciliation (include CSRF token)
    import secrets
    token = secrets.token_urlsafe(32)
    with client.session_transaction() as sess:
        sess['csrf_token'] = token
    rv2 = client.post('/admin/reconcile', headers={'X-CSRF-Token': token})
    assert rv2.status_code == 200

    # Order should now be marked paid
    o = get_order('o1')
    assert o is not None
    assert o[5] == 'paid'

    # Orphan payments: create orphan
    save_payment('p2', None, {'amt': 100})
    rv3 = client.get('/admin/reconcile')
    assert b'Orphan payments' in rv3.data
