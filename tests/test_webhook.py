import pytest
import json


def test_webhook_persistence(client, monkeypatch, tmp_path):
    # Make webhook signature verification a no-op for test
    import razorpay

    class DummyWS:
        @staticmethod
        def verify(payload, signature, secret):
            return True

    monkeypatch.setattr(razorpay, 'WebhookSignature', DummyWS, raising=False)

    # Use temporary DB
    dbfile = tmp_path / 'test.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))

    payload = {"event": "payment.captured", "payload": {"payment": {"entity": {"id":"pay_1"}}}}
    rv = client.post('/webhook', json=payload, headers={'X-Razorpay-Signature': 'sig'})
    assert rv.status_code == 200

    # Check the webhook was saved
    import utils
    row = utils.get_webhook_by_id('pay_1')
    assert row is not None
    assert row[1] == 'payment.captured'
