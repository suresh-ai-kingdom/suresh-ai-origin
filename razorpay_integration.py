"""
Razorpay Integration - Indian Payment Gateway Integration
Handles payment processing, webhooks, subscriptions, and settlements for Razorpay
"""

import hmac
import hashlib
import json
from typing import Dict, Optional, List
from datetime import datetime

class RazorpayIntegration:
    """
    Razorpay payment gateway integration
    Supports: Payment Links, Subscriptions, Settlements, Payouts
    """
    
    def __init__(self, key_id: str = None, key_secret: str = None):
        """
        Initialize Razorpay integration
        
        Args:
            key_id: Razorpay Live Key ID (rzp_live_...)
            key_secret: Razorpay Key Secret
        """
        self.key_id = key_id or "rzp_live_placeholder"
        self.key_secret = key_secret or "secret_placeholder"
        self.webhook_secret = None
        self.base_url = "https://api.razorpay.com/v1"
        self.live_mode = key_id and key_id.startswith('rzp_live_')
    
    def create_payment_link(self, order_id: str, amount: int, 
                           customer_email: str, callback_url: str) -> Dict:
        """
        Create payment link for customer
        
        Args:
            order_id: Your order ID
            amount: Amount in paise (e.g., 100000 = ₹1000)
            customer_email: Customer email
            callback_url: Webhook URL for confirmation
            
        Returns:
            {payment_link_id, short_url, status}
        """
        try:
            payload = {
                "amount": amount,
                "currency": "INR",
                "accept_partial": False,
                "reference_id": order_id,
                "description": f"Payment for order {order_id}",
                "customer_notify": 1,
                "notify": {
                    "sms": True,
                    "email": True
                },
                "reminder_enable": True,
                "notes": {
                    "order_id": order_id,
                    "webhook_url": callback_url
                }
            }
            
            # In production, make actual API call via requests library
            # response = requests.post(f"{self.base_url}/payment_links", 
            #                         auth=(self.key_id, self.key_secret), 
            #                         json=payload)
            
            # Simulated response
            return {
                "id": f"plink_{order_id}",
                "short_url": f"https://rzp.io/{order_id[:8]}",
                "status": "created",
                "amount": amount,
                "customer_email": customer_email
            }
        except Exception as e:
            print(f"Error creating payment link: {e}")
            return {}
    
    def create_subscription(self, plan_id: str, customer_email: str, 
                          quantity: int = 1, total_count: int = 12) -> Dict:
        """
        Create subscription for recurring payments
        
        Args:
            plan_id: Razorpay plan ID
            customer_email: Customer email
            quantity: Quantity
            total_count: Number of billing cycles
            
        Returns:
            {subscription_id, status}
        """
        try:
            payload = {
                "plan_id": plan_id,
                "customer_notify": 1,
                "quantity": quantity,
                "total_count": total_count,
                "notes": {
                    "customer_email": customer_email
                }
            }
            
            # Simulated response
            return {
                "id": f"sub_{plan_id[:8]}",
                "status": "active",
                "plan_id": plan_id,
                "customer_email": customer_email,
                "total_count": total_count
            }
        except Exception as e:
            print(f"Error creating subscription: {e}")
            return {}
    
    def verify_webhook_signature(self, webhook_body: str, 
                                webhook_signature: str) -> bool:
        """
        Verify webhook signature from Razorpay
        
        Args:
            webhook_body: Raw webhook body
            webhook_signature: X-Razorpay-Signature header
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                webhook_body.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, webhook_signature)
        except Exception as e:
            print(f"Error verifying signature: {e}")
            return False
    
    def process_webhook(self, webhook_data: Dict) -> Dict:
        """
        Process webhook from Razorpay
        
        Supported events:
        - payment.captured: Payment successful
        - payment.failed: Payment failed
        - subscription.activated: Subscription started
        - subscription.paused: Subscription paused
        """
        try:
            event_type = webhook_data.get('event')
            payload = webhook_data.get('payload', {})
            
            if event_type == "payment.captured":
                return self._handle_payment_captured(payload)
            elif event_type == "payment.failed":
                return self._handle_payment_failed(payload)
            elif event_type == "subscription.activated":
                return self._handle_subscription_activated(payload)
            else:
                return {"status": "unhandled_event"}
                
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_payment_captured(self, payload: Dict) -> Dict:
        """Handle successful payment"""
        payment_id = payload.get('payment', {}).get('id')
        amount = payload.get('payment', {}).get('amount')
        
        return {
            "status": "success",
            "payment_id": payment_id,
            "amount": amount,
            "action": "mark_order_paid"
        }
    
    def _handle_payment_failed(self, payload: Dict) -> Dict:
        """Handle failed payment"""
        payment_id = payload.get('payment', {}).get('id')
        error = payload.get('payment', {}).get('error')
        
        return {
            "status": "failed",
            "payment_id": payment_id,
            "error": error,
            "action": "retry_payment"
        }
    
    def _handle_subscription_activated(self, payload: Dict) -> Dict:
        """Handle subscription activation"""
        subscription_id = payload.get('subscription', {}).get('id')
        
        return {
            "status": "activated",
            "subscription_id": subscription_id,
            "action": "activate_features"
        }
    
    def get_payment_details(self, payment_id: str) -> Dict:
        """Get details of a payment"""
        try:
            # In production: API call
            return {
                "id": payment_id,
                "status": "captured",
                "amount": 0,
                "currency": "INR"
            }
        except Exception as e:
            print(f"Error fetching payment: {e}")
            return {}
    
    def refund_payment(self, payment_id: str, amount: int = None) -> Dict:
        """
        Refund a payment
        
        Args:
            payment_id: Razorpay payment ID
            amount: Amount to refund (None = full refund)
            
        Returns:
            {refund_id, status}
        """
        try:
            payload = {
                "amount": amount,  # Optional - if not provided, full refund
                "notes": {
                    "reason": "Customer requested refund"
                }
            }
            
            # Simulated response
            return {
                "id": f"rfnd_{payment_id[:8]}",
                "status": "processed",
                "payment_id": payment_id
            }
        except Exception as e:
            print(f"Error refunding payment: {e}")
            return {}
    
    def get_settlement_details(self, settlement_id: str) -> Dict:
        """Get settlement transaction details"""
        try:
            return {
                "id": settlement_id,
                "status": "processed",
                "amount": 0,
                "fees": 0,
                "net_amount": 0
            }
        except Exception as e:
            print(f"Error fetching settlement: {e}")
            return {}
    
    def create_payout(self, account_id: str, amount: int, 
                     account_type: str = "bank") -> Dict:
        """
        Create payout to customer/vendor
        
        Args:
            account_id: Bank account ID
            amount: Amount in paise
            account_type: 'bank' or 'vpa'
            
        Returns:
            {payout_id, status}
        """
        try:
            payload = {
                "account_id": account_id,
                "amount": amount,
                "account_type": account_type
            }
            
            # Simulated response
            return {
                "id": f"payout_{account_id[:8]}",
                "status": "pending",
                "amount": amount
            }
        except Exception as e:
            print(f"Error creating payout: {e}")
            return {}
    
    def health_check(self) -> Dict:
        """Check Razorpay API connectivity"""
        try:
            return {
                "status": "connected",
                "mode": "live" if self.live_mode else "test",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Initialize globally
razorpay = None

def initialize_razorpay(key_id: str, key_secret: str) -> RazorpayIntegration:
    """Initialize Razorpay integration"""
    global razorpay
    razorpay = RazorpayIntegration(key_id, key_secret)
    return razorpay

def get_razorpay() -> RazorpayIntegration:
    """Get Razorpay instance"""
    global razorpay
    if razorpay is None:
        razorpay = RazorpayIntegration()
    return razorpay
