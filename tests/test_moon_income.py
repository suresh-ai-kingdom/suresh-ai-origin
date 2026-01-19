import pytest
from moon_income_engine import get_moon_income_status, run_moon_income_automation

def test_get_status():
    result = get_moon_income_status('TEST_ORDER')
    assert result['order_id'] == 'TEST_ORDER'
    assert result['income'] == 0

def test_run_automation():
    result = run_moon_income_automation('TEST_ORDER', {'amount': 500})
    assert result['order_id'] == 'TEST_ORDER'
    assert result['result'] == 'income processed'
    assert result['income'] == 500
