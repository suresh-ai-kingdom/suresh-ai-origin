def test_order_to_payment_to_download(client, monkeypatch, tmp_path):
    # Use isolated DB
    dbfile = tmp_path / 'int.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))

    # Mock razorpay_client to return a deterministic order
    import app

    class DummyOrder:
        @staticmethod
        def create(data):
            return {'id': 'order_123', 'amount': data['amount'] * 100 if isinstance(data.get('amount'), int) else data.get('amount'), 'currency': data.get('currency', 'INR'), 'receipt': data.get('receipt')}

    class DummyClient:
        def __init__(self):
            self.order = DummyOrder()

    monkeypatch.setattr(app, 'razorpay_client', DummyClient())

    # 1) Create order
    rv = client.post('/create_order', json={'amount': 199, 'product': 'starter'})
    assert rv.status_code == 200
    order = rv.get_json()
    assert order.get('id') == 'order_123'

    # Verify local order exists
    import utils
    o = utils.get_order('order_123')
    assert o is not None
    assert o[0] == 'order_123'

    # 2) Simulate payment webhook (signature verification no-op)
    import razorpay

    class DummyWS:
        @staticmethod
        def verify(payload, signature, secret):
            return True

    monkeypatch.setattr(razorpay, 'WebhookSignature', DummyWS, raising=False)

    payload = {"event": "payment.captured", "payload": {"payment": {"entity": {"id": "pay_123", "order_id": "order_123"}}}}
    rv2 = client.post('/webhook', json=payload, headers={'X-Razorpay-Signature': 'sig'})
    assert rv2.status_code == 200

    # Order should be marked paid, and payment saved
    o2 = utils.get_order('order_123')
    assert o2 is not None
    assert o2[5] == 'paid'

    payments = utils.get_payments_by_order('order_123')
    assert any(p[0] == 'pay_123' for p in payments)

    # 3) Download should still be available for the product
    rv3 = client.get('/download/starter')
    assert rv3.status_code in (200, 302)
