def test_admin_webhooks_pagination_and_filter(client, monkeypatch, tmp_path):
    dbfile = tmp_path / 'pg.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    from utils import save_webhook
    # insert 25 webhooks with alternating events
    for i in range(25):
        eid = f'wh_{i}'
        event = 'payment.captured' if i % 2 == 0 else 'order.created'
        save_webhook(eid, event, {'i': i})

    # page 1, per_page=10 => 10 rows
    rv = client.get('/admin/webhooks?page=1&per_page=10')
    assert rv.status_code == 200
    rows_count = rv.data.count(b'<tr>') - 1
    assert rows_count == 10

    # page 3 should have 5 rows
    rv2 = client.get('/admin/webhooks?page=3&per_page=10')
    rows_count2 = rv2.data.count(b'<tr>') - 1
    assert rows_count2 == 5

    # filter by event
    rv3 = client.get('/admin/webhooks?event=payment.captured')
    assert b'payment.captured' in rv3.data


def test_admin_orders_pagination_and_filter(client, monkeypatch, tmp_path):
    dbfile = tmp_path / 'pg2.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    from utils import save_order
    # create 15 orders with products 'starter' or 'pro'
    for i in range(15):
        oid = f'o_{i}'
        product = 'starter' if i < 10 else 'pro'
        save_order(oid, 19900, 'INR', f'r{i}', product)

    rv = client.get('/admin/orders?page=1&per_page=7')
    assert rv.status_code == 200
    rows_count = rv.data.count(b'<tr>') - 1
    assert rows_count == 7

    # filter by product=pro should show 5 rows
    rv2 = client.get('/admin/orders?product=pro')
    rows_count2 = rv2.data.count(b'<tr>') - 1
    assert rows_count2 == 5
