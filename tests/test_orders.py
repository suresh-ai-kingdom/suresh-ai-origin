import pytest
from utils import save_order, get_order, save_payment, get_payments_by_order, mark_order_paid


def test_order_and_payment_flow(tmp_path, monkeypatch):
    dbfile = tmp_path / 'orders.db'
    monkeypatch.setenv('DATA_DB', str(dbfile))

    inserted = save_order('order_1', 19900, 'INR', 'r1', 'starter')
    assert inserted is True
    # duplicate insert should be False
    assert save_order('order_1', 19900, 'INR', 'r1', 'starter') is False

    row = get_order('order_1')
    assert row is not None
    assert row[0] == 'order_1'
    assert row[4] == 'starter'

    # save a payment
    p_inserted = save_payment('pay_1', 'order_1', {'amount': 19900})
    assert p_inserted is True

    payments = get_payments_by_order('order_1')
    assert len(payments) == 1

    # mark paid
    changed = mark_order_paid('order_1', 'pay_1')
    assert changed is True
    row2 = get_order('order_1')
    assert row2[5] == 'paid' or row2[5] == 'paid'
