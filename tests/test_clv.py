"""Tests for CLV Engine."""
import os
import sys
import time
import pytest
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import models as models_module
from models import get_engine, Base, get_session, Customer, Order
from clv import compute_customer_clv, compute_all_clv, clv_stats


@pytest.fixture(scope="function")
def setup_db():
    engine = get_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    original_get_engine = models_module.get_engine
    models_module.get_engine = lambda db_url=None: engine
    yield engine
    models_module.get_engine = original_get_engine


def test_clv_empty_customer(setup_db):
    res = compute_customer_clv('NOPE')
    assert res['receipt'] == 'NOPE'
    assert res['clv_rupees'] == 0.0
    assert res['confidence'] >= 0.6


def test_clv_with_orders(setup_db):
    session = get_session()
    try:
        c = Customer(receipt='R1', segment='std', ltv_paise=0, order_count=2)
        o1 = Order(id='O1', receipt='R1', product='starter', amount=9900, status='completed', created_at=time.mktime(datetime(2025,12,1,11,0).timetuple()))
        o2 = Order(id='O2', receipt='R1', product='pro', amount=49900, status='completed', created_at=time.mktime(datetime(2025,12,2,12,0).timetuple()))
        session.add_all([c, o1, o2]); session.commit()
    finally:
        session.close()
    res = compute_customer_clv('R1')
    assert res['orders'] == 2
    # base rupees = 99 + 499 = 598
    assert abs(res['base_rupees'] - 598.0) < 0.01
    assert res['clv_rupees'] >= res['base_rupees']


def test_compute_all_clv_sorted(setup_db):
    session = get_session()
    try:
        c1 = Customer(receipt='A', segment='std', ltv_paise=0, order_count=1)
        c2 = Customer(receipt='B', segment='std', ltv_paise=0, order_count=2)
        o1 = Order(id='OA', receipt='A', product='starter', amount=9900, status='completed', created_at=time.time())
        o2 = Order(id='OB1', receipt='B', product='starter', amount=9900, status='completed', created_at=time.time())
        o3 = Order(id='OB2', receipt='B', product='pro', amount=49900, status='completed', created_at=time.time())
        session.add_all([c1, c2, o1, o2, o3]); session.commit()
    finally:
        session.close()
    results = compute_all_clv(limit=10)
    assert results[0]['receipt'] == 'B'
    assert results[1]['receipt'] == 'A'


def test_clv_stats(setup_db):
    stats = clv_stats()
    assert 'customers' in stats
    assert 'orders' in stats
    assert 'avg_clv_top10' in stats
    assert 'top' in stats
