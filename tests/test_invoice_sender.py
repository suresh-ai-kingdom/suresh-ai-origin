import pytest
from invoice_sender import get_invoice_sender_status, run_invoice_sender_automation

def test_get_status():
    result = get_invoice_sender_status('TEST_ORDER')
    assert result['order_id'] == 'TEST_ORDER'

def test_run_automation():
    result = run_invoice_sender_automation('TEST_ORDER', {'email': 'test@example.com', 'amount': 100})
    assert result['order_id'] == 'TEST_ORDER'
    assert result['result'] == 'invoice sent'
