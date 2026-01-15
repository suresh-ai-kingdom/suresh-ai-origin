"""
Tests for email notification integration with webhook flow.
"""
import pytest
import json
from unittest.mock import MagicMock
from utils import save_order
import razorpay


class DummyWebhookSignature:
    """Mock WebhookSignature class for testing."""
    @staticmethod
    def verify(payload, signature, secret):
        return True


def test_webhook_sends_customer_email_on_payment_captured(client, monkeypatch):
    """Test that webhook sends order confirmation email to customer when payment is captured."""
    # Mock signature verification
    monkeypatch.setattr(razorpay, 'WebhookSignature', DummyWebhookSignature, raising=False)
    
    # Create an order first
    order_id = "order_test_email_123"
    save_order(order_id, 19900, "INR", "receipt_123", "pro")
    
    # Mock email sending - send_order_confirmation calls utils.send_email
    mock_send_email = MagicMock(return_value=True)
    monkeypatch.setattr('utils.send_email', mock_send_email)
    
    # Simulate Razorpay payment.captured webhook
    webhook_payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_email_123",
                    "order_id": order_id,
                    "amount": 19900,
                    "email": "customer@example.com",
                    "status": "captured"
                }
            }
        }
    }
    
    response = client.post(
        '/webhook',
        data=json.dumps(webhook_payload),
        content_type='application/json',
        headers={'X-Razorpay-Signature': 'valid_signature'}
    )
    
    assert response.status_code == 200
    
    # Verify email was sent to customer
    assert mock_send_email.called
    call_args = mock_send_email.call_args
    assert call_args is not None
    # Check that customer email was in the call (uses to_addr)
    args, kwargs = call_args
    assert "customer@example.com" in args or kwargs.get('to_addr') == "customer@example.com"


def test_webhook_handles_missing_customer_email_gracefully(client, monkeypatch):
    """Test that webhook handles payment without customer email gracefully."""
    monkeypatch.setattr(razorpay, 'WebhookSignature', DummyWebhookSignature, raising=False)
    
    order_id = "order_no_email_456"
    save_order(order_id, 9900, "INR", "receipt_456", "starter")
    
    mock_send_email = MagicMock(return_value=True)
    monkeypatch.setattr('utils.send_email', mock_send_email)
    
    # Webhook payload without customer email
    webhook_payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_no_email_456",
                    "order_id": order_id,
                    "amount": 9900,
                    "status": "captured"
                    # email field missing
                }
            }
        }
    }
    
    response = client.post(
        '/webhook',
        data=json.dumps(webhook_payload),
        content_type='application/json',
        headers={'X-Razorpay-Signature': 'valid_signature'}
    )
    
    assert response.status_code == 200
    # Should not crash even without email - webhook should still succeed


def test_webhook_email_contains_correct_order_details(client, monkeypatch):
    """Test that email contains correct order details (product, amount, order ID)."""
    monkeypatch.setattr(razorpay, 'WebhookSignature', DummyWebhookSignature, raising=False)
    
    order_id = "order_details_789"
    product = "premium"
    amount = 49900  # ₹499 in paise
    save_order(order_id, amount, "INR", "receipt_789", product)
    
    # Mock send_order_confirmation to capture its parameters
    captured_params = {}
    def mock_send_order_confirmation(order_id, product_name, amount, customer_email, download_url):
        captured_params['order_id'] = order_id
        captured_params['product_name'] = product_name
        captured_params['amount'] = amount
        captured_params['customer_email'] = customer_email
        captured_params['download_url'] = download_url
        return True
    
    mock_admin_email = MagicMock()
    monkeypatch.setattr('email_notifications.send_order_confirmation', mock_send_order_confirmation)
    monkeypatch.setattr('utils.send_email', mock_admin_email)
    
    webhook_payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_details_789",
                    "order_id": order_id,
                    "amount": amount,
                    "email": "premium@example.com",
                    "status": "captured"
                }
            }
        }
    }
    
    response = client.post(
        '/webhook',
        data=json.dumps(webhook_payload),
        content_type='application/json',
        headers={'X-Razorpay-Signature': 'valid_signature'}
    )
    
    assert response.status_code == 200
    assert len(captured_params) > 0  # Function was called
    
    # Verify order details are passed correctly
    assert captured_params['order_id'] == order_id
    assert captured_params['product_name'] == product
    assert captured_params['amount'] == amount  # Should be in paise
    assert captured_params['customer_email'] == 'premium@example.com'
    assert 'download' in captured_params['download_url']  # download URL


def test_webhook_email_failure_does_not_break_webhook(client, monkeypatch):
    """Test that email sending failure does not prevent webhook from succeeding."""
    monkeypatch.setattr(razorpay, 'WebhookSignature', DummyWebhookSignature, raising=False)
    
    order_id = "order_email_fail_999"
    save_order(order_id, 9900, "INR", "receipt_999", "starter")
    
    # Mock email function to raise exception
    mock_send_email = MagicMock(side_effect=Exception("SMTP error"))
    mock_admin_email = MagicMock()
    monkeypatch.setattr('email_notifications.send_email', mock_send_email)
    monkeypatch.setattr('utils.send_email', mock_admin_email)
    
    webhook_payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_email_fail_999",
                    "order_id": order_id,
                    "amount": 9900,
                    "email": "fail@example.com",
                    "status": "captured"
                }
            }
        }
    }
    
    response = client.post(
        '/webhook',
        data=json.dumps(webhook_payload),
        content_type='application/json',
        headers={'X-Razorpay-Signature': 'valid_signature'}
    )
    
    # Webhook should still return 200 even if email fails
    assert response.status_code == 200


def test_webhook_only_sends_email_for_payment_captured_event(client, monkeypatch):
    """Test that emails are only sent for payment.captured events, not other webhook events."""
    monkeypatch.setattr(razorpay, 'WebhookSignature', DummyWebhookSignature, raising=False)
    
    order_id = "order_other_event_111"
    save_order(order_id, 9900, "INR", "receipt_111", "starter")
    
    mock_send_email = MagicMock()
    mock_admin_email = MagicMock()
    monkeypatch.setattr('email_notifications.send_email', mock_send_email)
    monkeypatch.setattr('utils.send_email', mock_admin_email)
    
    # Test with order.paid event (different from payment.captured)
    webhook_payload = {
        "event": "order.paid",
        "payload": {
            "order": {
                "entity": {
                    "id": order_id,
                    "amount": 9900,
                    "status": "paid"
                }
            }
        }
    }
    
    response = client.post(
        '/webhook',
        data=json.dumps(webhook_payload),
        content_type='application/json',
        headers={'X-Razorpay-Signature': 'valid_signature'}
    )
    
    assert response.status_code == 200
    # Should not send customer email for non-payment.captured events
    assert not mock_send_email.called
