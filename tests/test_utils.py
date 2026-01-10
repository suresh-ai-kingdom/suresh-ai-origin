import os
import pytest

from utils import init_db, save_webhook, get_webhook_by_id, send_email


def test_save_and_get_webhook(tmp_path, monkeypatch):
    dbfile = tmp_path / 'test.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))
    init_db()
    payload = {'event': 'payment.captured', 'payload': {'payment': {'entity': {'id': 'pay_1'}}}}
    inserted = save_webhook('pay_1', 'payment.captured', payload)
    assert inserted is True
    # second insert should return False (idempotent)
    inserted2 = save_webhook('pay_1', 'payment.captured', payload)
    assert inserted2 is False
    row = get_webhook_by_id('pay_1')
    assert row is not None
    assert row[0] == 'pay_1'
    assert row[1] == 'payment.captured'


def test_send_email(monkeypatch):
    sent = {}

    class DummySMTP:
        def __init__(self, host, port, context):
            pass

        def login(self, user, password):
            sent['login'] = (user, password)

        def send_message(self, msg):
            sent['msg'] = msg

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr('smtplib.SMTP_SSL', DummySMTP)
    monkeypatch.setenv('EMAIL_USER', 'test@example.com')
    monkeypatch.setenv('EMAIL_PASS', 'pass')

    res = send_email('sub', 'body', 'to@example.com')
    assert res is True
    assert 'msg' in sent
    assert sent['login'] == ('test@example.com', 'pass')
