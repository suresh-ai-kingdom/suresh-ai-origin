"""Email notification helpers for order confirmations and alerts."""
import os
from datetime import datetime
from flask import render_template
from utils import send_email


def send_order_confirmation(order_id, product_name, amount, customer_email, download_url):
    """Send order confirmation email with HTML template.
    
    Args:
        order_id: Order ID
        product_name: Name of the product purchased
        amount: Amount paid (in paise, will be converted to rupees)
        customer_email: Customer's email address
        download_url: Full URL to download the product
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Convert paise to rupees for display
        amount_rupees = amount / 100
        
        # Format date
        date_str = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        # Render HTML email template
        html_body = render_template(
            'email_order_confirmation.html',
            order_id=order_id,
            product_name=product_name.replace('_', ' ').title(),
            amount=f'{amount_rupees:.2f}',
            date=date_str,
            download_url=download_url
        )
        
        # Plain text fallback
        plain_body = f"""
Payment Successful!

Thank you for your purchase.

Order Details:
- Order ID: {order_id}
- Product: {product_name.replace('_', ' ').title()}
- Amount Paid: ₹{amount_rupees:.2f}
- Date: {date_str}

Download your product: {download_url}

If you have any questions, reply to this email.

Best regards,
SURESH AI ORIGIN Team
"""
        
        send_email(
            subject=f'Order Confirmed - {order_id}',
            body=plain_body.strip(),
            to_addr=customer_email,
            html_body=html_body
        )
        return True
        
    except Exception as e:
        # Log but don't fail - email is not critical for order completion
        import logging
        logging.error(f"Failed to send order confirmation email: {e}")
        return False


def send_admin_alert(subject, message):
    """Send alert email to admin.
    
    Args:
        subject: Email subject
        message: Email body
    
    Returns:
        True if sent, False otherwise
    """
    admin_email = os.getenv('ADMIN_EMAIL')
    if not admin_email:
        return False
    
    try:
        send_email(subject, message, admin_email)
        return True
    except Exception:
        return False
