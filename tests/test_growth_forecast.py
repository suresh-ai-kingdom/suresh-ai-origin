"""Tests for Growth Forecast Engine."""
import os
import sys
import time
import pytest
from datetime import datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import models as models_module
from models import get_engine, Base, get_session, Customer, Order
from growth_forecast import get_daily_metrics, forecast_scenarios, forecast_summary


@pytest.fixture(scope="function")
def setup_db():
    engine = get_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    original_get_engine = models_module.get_engine
    models_module.get_engine = lambda db_url=None: engine
    yield engine
    models_module.get_engine = original_get_engine


def test_daily_metrics_empty(setup_db):
    m = get_daily_metrics(60)
    assert 'orders_count' in m and 'customers_count' in m
    assert len(m['orders_count']) == 60
    assert len(m['customers_count']) == 60


def test_daily_metrics_with_data(setup_db):
    session = get_session()
    try:
        c = Customer(receipt='R1', segment='std', ltv_paise=1000, order_count=1, first_purchase_at=time.mktime(datetime(2025,12,1,10,0).timetuple()))
        o1 = Order(id='O1', receipt='R1', product='starter', amount=9900, status='completed', created_at=time.mktime(datetime(2025,12,1,11,0).timetuple()))
        o2 = Order(id='O2', receipt='R1', product='starter', amount=9900, status='completed', created_at=time.mktime(datetime(2025,12,2,11,0).timetuple()))
        session.add_all([c, o1, o2]); session.commit()
    finally:
        session.close()
    m = get_daily_metrics(60)
    assert sum(m['orders_count']) >= 2
    assert sum(m['customers_count']) >= 1


def test_forecast_scenarios_structure(setup_db):
    res = forecast_scenarios(60, 30)
    assert 'scenarios' in res and 'summary' in res
    for name in ['conservative','baseline','aggressive']:
        assert name in res['scenarios']
        assert 'orders' in res['scenarios'][name]
        assert 'customers' in res['scenarios'][name]
        assert len(res['scenarios'][name]['orders']) == 30
        assert len(res['scenarios'][name]['customers']) == 30


def test_aggressive_growth_monotonic(setup_db):
    res = forecast_scenarios(60, 30)
    arr = res['scenarios']['aggressive']['orders']
    assert all(arr[i] <= arr[i+1] for i in range(len(arr)-1))


def test_forecast_summary_recommended(setup_db):
    summary = forecast_summary()
    assert 'recommended' in summary
    assert summary['recommended'] in ['conservative','baseline','aggressive']


def test_growth_percentages_non_negative(setup_db):
    res = forecast_scenarios(60, 30)
    for name in ['conservative','baseline','aggressive']:
        assert res['summary'][name]['orders_growth_pct'] >= -50  # allow slight decline
        assert res['summary'][name]['customers_growth_pct'] >= -50
