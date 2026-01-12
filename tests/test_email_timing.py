"""Tests for Smart Email Timing Engine."""
import os
import sys
import time
import pytest
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import models as models_module
from models import get_engine, Base, get_session, Customer, Order, AbandonedReminder
from email_timing import get_customer_activity_hours, predict_best_send_time, get_global_best_send_time, get_email_timing_stats


@pytest.fixture(scope="function")
def setup_db():
    # In-memory sqlite to avoid file locks
    engine = get_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    original_get_engine = models_module.get_engine
    models_module.get_engine = lambda db_url=None: engine
    yield engine
    models_module.get_engine = original_get_engine


def test_customer_activity_hours_empty(setup_db):
    hist = get_customer_activity_hours('NOPE')
    assert isinstance(hist, dict)
    assert len(hist) == 0


def test_predict_best_send_time_fallback(setup_db):
    res = predict_best_send_time('NOPE')
    assert 'hour' in res
    assert 0 <= res['hour'] <= 23
    assert 'confidence' in res
    assert res['sources']['global'] is True


def test_per_customer_prediction_with_orders(setup_db):
    session = get_session()
    try:
        # Create a customer and an order around 21:00
        c = Customer(receipt='CUST1', segment='standard', ltv_paise=1000, order_count=1)
        o = Order(id='OID1', receipt='CUST1', product='starter', amount=9900, status='completed', created_at=time.mktime(datetime(2025, 12, 1, 21, 15).timetuple()))
        session.add_all([c, o])
        session.commit()
    finally:
        session.close()
    res = predict_best_send_time('CUST1')
    assert res['hour'] == 21
    assert res['confidence'] > 0.5


def test_global_best_derives_from_reminders(setup_db):
    session = get_session()
    try:
        c = Customer(receipt='CUST2', segment='standard', ltv_paise=500, order_count=1)
        r = AbandonedReminder(id='REM1', order_id='OIDX', receipt='CUST2', reminder_sequence=0, status='OPENED', scheduled_at=time.time(), sent_at=time.time(), opened_at=time.mktime(datetime(2025, 12, 2, 9, 0).timetuple()))
        session.add_all([c, r])
        session.commit()
    finally:
        session.close()
    gb = get_global_best_send_time()
    assert gb['hour'] == 9
    assert gb['confidence'] >= 0.4


def test_stats(setup_db):
    stats = get_email_timing_stats()
    assert 'customers' in stats
    assert 'orders' in stats
    assert 'reminders' in stats
    assert 'global_best' in stats
