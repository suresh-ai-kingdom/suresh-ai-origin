"""
Stripe integration module: checkout sessions, webhook handling, subscription state management.
Integrates with existing entitlements layer (check_entitlement) and models.

Key Features:
- Idempotent webhook processing via StripeEvent table
- Subscription state sync (created, updated, deleted, payment failures)
- Usage-based metering hooks for attribution-run scaling
- Coexists with Razorpay (provider field in Subscription model)
"""

import json
import time
import os
from datetime import datetime
import stripe
from flask import request, jsonify

# SQLAlchemy models
from models import get_session, Subscription, StripeEvent, UsageMeter, Order, Customer
from entitlements import check_entitlement, emit_alert

# Environment config
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Price tier mapping: tier -> stripe_price_id
STRIPE_PRICE_MAP = {
    'pro': os.getenv('STRIPE_PRICE_PRO', 'price_1234567890'),  # ~$29/mo
    'scale': os.getenv('STRIPE_PRICE_SCALE', 'price_0987654321'),  # ~$99/mo
}

# Success / cancel URLs for checkout
SUCCESS_URL = os.getenv('STRIPE_SUCCESS_URL', 'https://sureshaiorigin.com/api/billing/success?session_id={CHECKOUT_SESSION_ID}')
CANCEL_URL = os.getenv('STRIPE_CANCEL_URL', 'https://sureshaiorigin.com/api/billing/cancel')


def get_db():
    """Get a database session."""
    return get_session()


def create_checkout_session(receipt, tier, billing_cycle='month'):
    """
    Create a Stripe Checkout Session for the given customer and tier.
    
    Args:
        receipt: Customer receipt ID (unique identifier from our system)
        tier: Subscription tier ('pro' or 'scale')
        billing_cycle: 'month' or 'year'
    
    Returns:
        {
            'status': 'success',
            'session_id': '<checkout_session_id>',
            'url': '<Stripe checkout URL>'
        }
        OR
        {
            'status': 'error',
            'message': '<error_message>'
        }
    """
    
    db = get_db()
    
    try:
        # 1. Check entitlement: is this tier available to this customer?
        entitlement = check_entitlement('checkout', {'tier': tier, 'receipt': receipt})
        if entitlement.get('blocked'):
            return {
                'status': 'error',
                'message': f'Cannot checkout tier {tier}: {entitlement.get("reason")}',
                'code': 402
            }
        
        # 2. Get or create Stripe customer
        customer = db.query(Customer).filter_by(receipt=receipt).first()
        stripe_customer_id = None
        if customer and hasattr(customer, 'stripe_customer_id') and customer.stripe_customer_id:
            stripe_customer_id = customer.stripe_customer_id
        else:
            # Create new Stripe customer
            try:
                sc = stripe.Customer.create(
                    metadata={'receipt': receipt}
                )
                stripe_customer_id = sc['id']
                # Save to customer table (if new)
                if not customer:
                    customer = Customer(receipt=receipt)
                    db.add(customer)
                else:
                    customer.stripe_customer_id = stripe_customer_id
                db.commit()
            except Exception as e:
                db.rollback()
                emit_alert('stripe_customer_creation_failed', {
                    'receipt': receipt,
                    'error': str(e)
                })
                return {
                    'status': 'error',
                    'message': 'Failed to create Stripe customer',
                    'code': 500
                }
        
        # 3. Get price ID for tier
        price_id = STRIPE_PRICE_MAP.get(tier)
        if not price_id:
            return {
                'status': 'error',
                'message': f'Tier {tier} not configured',
                'code': 400
            }
        
        # 4. Create checkout session
        try:
            session = stripe.checkout.Session.create(
                customer=stripe_customer_id,
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    }
                ],
                mode='subscription',
                success_url=SUCCESS_URL,
                cancel_url=CANCEL_URL,
                metadata={
                    'receipt': receipt,
                    'tier': tier,
                    'billing_cycle': billing_cycle
                }
            )
            
            emit_alert('stripe_checkout_created', {
                'receipt': receipt,
                'session_id': session['id'],
                'tier': tier
            })
            
            return {
                'status': 'success',
                'session_id': session['id'],
                'url': session['url']
            }
        
        except Exception as e:
            emit_alert('stripe_checkout_failed', {
                'receipt': receipt,
                'tier': tier,
                'error': str(e)
            })
            return {
                'status': 'error',
                'message': f'Checkout failed: {str(e)}',
                'code': 500
            }
    
    finally:
        db.close()


def handle_stripe_webhook(payload, signature):
    """
    Handle Stripe webhook events with idempotent processing.
    
    Args:
        payload: Raw request body (bytes)
        signature: X-Stripe-Signature header value
    
    Returns:
        {'status': 'processed' | 'error', 'event_id': '<id>', 'message': '<msg>'}
    """
    
    db = get_db()
    
    try:
        # 1. Verify signature
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            emit_alert('stripe_webhook_invalid_payload', {})
            return {'status': 'error', 'message': 'Invalid payload'}
        except stripe.error.SignatureVerificationError:
            emit_alert('stripe_webhook_invalid_signature', {})
            return {'status': 'error', 'message': 'Invalid signature'}
        
        event_id = event['id']
        event_type = event['type']
        
        # 2. Check idempotency: has this event been processed?
        existing = db.query(StripeEvent).filter_by(id=event_id).first()
        if existing and existing.processed:
            return {
                'status': 'processed',
                'event_id': event_id,
                'message': 'Event already processed (idempotent)'
            }
        
        # 3. Save event record (mark as pending if new)
        if not existing:
            stripe_event = StripeEvent(
                id=event_id,
                event_type=event_type,
                payload=json.dumps(event),
                processed=0,
                received_at=time.time()
            )
            db.add(stripe_event)
            db.commit()
        else:
            existing.received_at = time.time()
            db.commit()
            stripe_event = existing
        
        # 4. Process the event based on type
        try:
            _process_stripe_event(event, db)
            
            # Mark as processed
            stripe_event.processed = 1
            stripe_event.processed_at = time.time()
            db.commit()
            
            return {
                'status': 'processed',
                'event_id': event_id,
                'message': f'Processed {event_type}'
            }
        
        except Exception as e:
            db.rollback()
            emit_alert('stripe_event_processing_failed', {
                'event_id': event_id,
                'event_type': event_type,
                'error': str(e)
            })
            return {
                'status': 'error',
                'event_id': event_id,
                'message': f'Failed to process event: {str(e)}'
            }
    
    finally:
        db.close()


def _process_stripe_event(event, db):
    """
    Internal: Process a single Stripe event and update subscription state.
    
    Supported events:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
    - charge.refunded
    """
    
    event_type = event['type']
    data = event['data']['object']
    
    if event_type == 'customer.subscription.created':
        _handle_subscription_created(data, db)
    elif event_type == 'customer.subscription.updated':
        _handle_subscription_updated(data, db)
    elif event_type == 'customer.subscription.deleted':
        _handle_subscription_deleted(data, db)
    elif event_type == 'invoice.payment_succeeded':
        _handle_invoice_paid(data, db)
    elif event_type == 'invoice.payment_failed':
        _handle_invoice_failed(data, db)
    elif event_type == 'charge.refunded':
        _handle_charge_refunded(data)


def _handle_subscription_created(subscription_data, db):
    """Handle customer.subscription.created event."""
    stripe_subscription_id = subscription_data['id']
    stripe_customer_id = subscription_data['customer']
    status = subscription_data['status']  # trialing, active, etc.
    
    # Get customer receipt from Stripe customer metadata
    customer_obj = stripe.Customer.retrieve(stripe_customer_id)
    receipt = customer_obj.metadata.get('receipt')
    
    if not receipt:
        raise ValueError(f'Stripe customer {stripe_customer_id} has no receipt metadata')
    
    # Infer tier from items (look at price metadata)
    tier = _infer_tier_from_subscription(subscription_data)
    
    # Create Subscription record
    sub = Subscription(
        id=f'stripe_{stripe_subscription_id}',
        receipt=receipt,
        tier=tier,
        provider='stripe',
        stripe_subscription_id=stripe_subscription_id,
        stripe_customer_id=stripe_customer_id,
        billing_cycle='monthly',
        amount_paise=int(subscription_data['items']['data'][0]['price']['unit_amount']),
        status=status.upper(),
        current_period_start=subscription_data['current_period_start'],
        current_period_end=subscription_data['current_period_end'],
        created_at=time.time()
    )
    db.add(sub)
    db.commit()
    
    emit_alert('stripe_subscription_created', {
        'receipt': receipt,
        'stripe_subscription_id': stripe_subscription_id,
        'tier': tier,
        'status': status
    })


def _handle_subscription_updated(subscription_data, db):
    """Handle customer.subscription.updated event."""
    stripe_subscription_id = subscription_data['id']
    status = subscription_data['status']
    
    sub = db.query(Subscription).filter_by(
        stripe_subscription_id=stripe_subscription_id
    ).first()
    
    if not sub:
        raise ValueError(f'Subscription {stripe_subscription_id} not found')
    
    old_status = sub.status
    sub.status = status.upper()
    sub.current_period_start = subscription_data['current_period_start']
    sub.current_period_end = subscription_data['current_period_end']
    db.commit()
    
    emit_alert('stripe_subscription_updated', {
        'receipt': sub.receipt,
        'stripe_subscription_id': stripe_subscription_id,
        'old_status': old_status,
        'new_status': status,
        'tier': sub.tier
    })


def _handle_subscription_deleted(subscription_data, db):
    """Handle customer.subscription.deleted event (cancellation)."""
    stripe_subscription_id = subscription_data['id']
    
    sub = db.query(Subscription).filter_by(
        stripe_subscription_id=stripe_subscription_id
    ).first()
    
    if not sub:
        raise ValueError(f'Subscription {stripe_subscription_id} not found')
    
    sub.status = 'CANCELLED'
    sub.cancelled_at = time.time()
    db.commit()
    
    emit_alert('stripe_subscription_deleted', {
        'receipt': sub.receipt,
        'stripe_subscription_id': stripe_subscription_id,
        'tier': sub.tier
    })


def _handle_invoice_paid(invoice_data, db):
    """Handle invoice.payment_succeeded event."""
    stripe_subscription_id = invoice_data.get('subscription')
    
    if stripe_subscription_id:
        sub = db.query(Subscription).filter_by(
            stripe_subscription_id=stripe_subscription_id
        ).first()
        
        if sub and sub.status in ('PAST_DUE', 'TRIAL'):
            sub.status = 'ACTIVE'
            db.commit()
    
    emit_alert('stripe_invoice_paid', {
        'invoice_id': invoice_data['id'],
        'amount': invoice_data['amount_paid'],
        'subscription_id': stripe_subscription_id
    })


def _handle_invoice_failed(invoice_data, db):
    """Handle invoice.payment_failed event."""
    stripe_subscription_id = invoice_data.get('subscription')
    
    if stripe_subscription_id:
        sub = db.query(Subscription).filter_by(
            stripe_subscription_id=stripe_subscription_id
        ).first()
        
        if sub:
            sub.status = 'PAST_DUE'
            db.commit()
    
    emit_alert('stripe_invoice_failed', {
        'invoice_id': invoice_data['id'],
        'subscription_id': stripe_subscription_id,
        'reason': invoice_data.get('failure_reason', 'unknown')
    })


def _handle_charge_refunded(charge_data):
    """Handle charge.refunded event."""
    emit_alert('stripe_charge_refunded', {
        'charge_id': charge_data['id'],
        'amount_refunded': charge_data['amount_refunded']
    })


def _infer_tier_from_subscription(subscription_data):
    """Extract tier from subscription items/prices."""
    try:
        # Get first item's price
        price_id = subscription_data['items']['data'][0]['price']['id']
        
        # Map price_id back to tier
        for tier, pid in STRIPE_PRICE_MAP.items():
            if pid == price_id:
                return tier
        
        # Fallback: look at metadata
        return subscription_data['metadata'].get('tier', 'pro')
    except:
        return 'pro'  # Safe default
