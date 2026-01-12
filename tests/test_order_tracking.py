"""
Tests for customer order tracking page.
"""
import pytest
from utils import save_order, mark_order_paid


def test_order_tracking_paid_status(client):
    """Test order tracking page for a paid order shows download button."""
    order_id = "order_tracking_paid_123"
    save_order(order_id, 19900, "INR", "receipt_123", "starter")
    
    # Manually mark order as paid
    from utils import mark_order_paid
    mark_order_paid(order_id, "pay_123")
    
    response = client.get(f'/order/{order_id}')
    assert response.status_code == 200
    assert b'Order Tracking' in response.data
    assert b'Paid' in response.data or b'paid' in response.data.lower()
    assert b'Download Product' in response.data
    assert order_id.encode() in response.data


def test_order_tracking_unpaid_status(client):
    """Test order tracking page for unpaid order shows pending message."""
    order_id = "order_tracking_unpaid_456"
    save_order(order_id, 9900, "INR", "receipt_456", "pro")
    
    response = client.get(f'/order/{order_id}')
    assert response.status_code == 200
    assert b'Unpaid' in response.data or b'unpaid' in response.data.lower()
    assert b'awaiting payment' in response.data.lower() or b'payment confirmation' in response.data.lower()
    # Download button should be disabled
    assert b'disabled' in response.data


def test_order_tracking_not_found(client):
    """Test order tracking page returns 404 for non-existent order."""
    response = client.get('/order/nonexistent_order_999')
    assert response.status_code == 404
    assert b'not found' in response.data.lower() or b'not found' in response.data.lower()


def test_order_tracking_api_json_response(client):
    """Test /order/<id> returns JSON when Accept header specifies JSON."""
    order_id = "order_api_json_789"
    save_order(order_id, 49900, "INR", "receipt_789", "premium")
    
    # Request JSON explicitly
    response = client.get(
        f'/order/{order_id}',
        headers={'Accept': 'application/json'}
    )
    
    assert response.status_code == 200
    assert response.content_type.startswith('application/json')
    
    data = response.get_json()
    assert data['id'] == order_id
    assert data['product'] == 'premium'
    assert data['amount'] == 49900  # in paise


def test_order_tracking_api_json_404(client):
    """Test /order/<id> returns JSON 404 for non-existent order when Accept is JSON."""
    response = client.get(
        '/order/nonexistent_999',
        headers={'Accept': 'application/json'}
    )
    
    assert response.status_code == 404
    assert response.content_type.startswith('application/json')
    data = response.get_json()
    assert 'status' in data or 'error' in data


def test_order_tracking_displays_amount_in_rupees(client):
    """Test that order tracking page displays amount in rupees, not paise."""
    order_id = "order_rupees_display_111"
    amount_paise = 19900  # ₹199
    save_order(order_id, amount_paise, "INR", "receipt_111", "starter")
    
    from utils import mark_order_paid
    mark_order_paid(order_id, "pay_111")
    
    response = client.get(f'/order/{order_id}')
    assert response.status_code == 200
    # Should display ₹199.00, not ₹19900
    assert b'199' in response.data
    # Make sure paise value doesn't appear
    assert b'19900' not in response.data


def test_order_tracking_download_link_format(client):
    """Test that download link in tracking page has correct format."""
    order_id = "order_download_link_222"
    save_order(order_id, 9900, "INR", "receipt_222", "pro_pack")
    mark_order_paid(order_id, "pay_222")
    
    response = client.get(f'/order/{order_id}')
    assert response.status_code == 200
    assert b'/download/pro_pack' in response.data


def test_order_tracking_product_name_formatting(client):
    """Test that product names are formatted nicely (underscores replaced with spaces)."""
    order_id = "order_product_format_333"
    save_order(order_id, 9900, "INR", "receipt_333", "premium_pack")
    mark_order_paid(order_id, "pay_333")
    
    response = client.get(f'/order/{order_id}')
    assert response.status_code == 200
    # Should display "Premium Pack" not "premium_pack"
    assert b'Premium Pack' in response.data


def test_order_tracking_html_structure(client):
    """Test that tracking page has proper HTML structure and styling."""
    order_id = "order_html_structure_444"
    save_order(order_id, 29900, "INR", "receipt_444", "advanced")
    mark_order_paid(order_id, "pay_444")
    
    response = client.get(f'/order/{order_id}')
    assert response.status_code == 200
    # Check for key HTML elements
    assert b'<!DOCTYPE html>' in response.data
    assert b'<title>' in response.data
    assert b'Order Tracking' in response.data
    assert b'tracking-container' in response.data or b'order-details' in response.data


def test_order_tracking_api_converts_paise_to_rupees(client):
    """Test that API response converts amount from paise to rupees in displayed value."""
    order_id = "order_api_rupees_555"
    amount_paise = 29900
    save_order(order_id, amount_paise, "INR", "receipt_555", "starter")
    
    response = client.get(
        f'/order/{order_id}',
        headers={'Accept': 'application/json'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['amount'] == amount_paise  # Original paise value
    assert data['amount_rupees'] == 299.00  # Converted to rupees


def test_order_tracking_content_negotiation_prefers_html_for_browsers(client):
    """Test that browser requests get HTML page, not JSON."""
    order_id = "order_browser_request_666"
    save_order(order_id, 9900, "INR", "receipt_666", "starter")
    
    # Typical browser Accept header
    response = client.get(
        f'/order/{order_id}',
        headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    )
    
    assert response.status_code == 200
    assert response.content_type.startswith('text/html')
    assert b'Order Tracking' in response.data  # HTML page
