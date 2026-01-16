"""
Free Trial System
Implements 14-day trial with email verification and auto-upgrade prompts.
"""
import time
import secrets
from utils import get_session, get_engine, _get_db_url, send_email
from models import Customer, Subscription
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

# Trial configuration
TRIAL_DAYS = 14
TRIAL_AMOUNT_PAISE = 0  # Free trial


def create_trial_user(email: str, name: str, phone: str = None, plan: str = 'professional') -> dict:
    """
    Create a free trial user with 14-day access.
    
    Args:
        email: User email
        name: User name
        phone: Optional phone number
        plan: Trial plan (default: professional)
        
    Returns:
        dict with trial details and access credentials
    """
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    try:
        # Check if user already exists
        existing = session.query(Customer).filter_by(email=email).first()
        if existing:
            session.close()
            return {
                'success': False,
                'error': 'Email already registered',
                'message': 'This email is already associated with an account.'
            }
        
        # Generate trial credentials
        trial_id = f"TRIAL_{int(time.time())}_{secrets.token_hex(4).upper()}"
        access_token = secrets.token_urlsafe(32)
        
        # Create customer record
        customer = Customer(
            id=trial_id,
            name=name,
            email=email,
            phone=phone,
            created_at=time.time(),
            status='trial'
        )
        session.add(customer)
        
        # Create trial subscription
        trial_start = time.time()
        trial_end = trial_start + (TRIAL_DAYS * 24 * 60 * 60)
        
        subscription = Subscription(
            id=f"sub_trial_{int(time.time())}",
            customer_id=trial_id,
            plan=plan,
            status='trialing',
            amount_paise=TRIAL_AMOUNT_PAISE,
            currency='INR',
            billing_cycle='trial',
            trial_start=trial_start,
            trial_end=trial_end,
            current_period_start=trial_start,
            current_period_end=trial_end,
            created_at=trial_start
        )
        session.add(subscription)
        
        session.commit()
        
        # Send welcome email with trial details
        _send_trial_welcome_email(email, name, trial_id, access_token, trial_end)
        
        logger.info(f"Trial created: {trial_id} for {email} on plan {plan}")
        
        session.close()
        return {
            'success': True,
            'trial_id': trial_id,
            'access_token': access_token,
            'email': email,
            'plan': plan,
            'trial_days': TRIAL_DAYS,
            'trial_end': trial_end,
            'message': f'Trial activated! Check {email} for login credentials.'
        }
        
    except Exception as e:
        session.rollback()
        session.close()
        logger.exception(f"Trial creation error: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def check_trial_status(trial_id: str) -> dict:
    """
    Check trial status and days remaining.
    
    Args:
        trial_id: Trial user ID
        
    Returns:
        dict with trial status details
    """
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    try:
        customer = session.query(Customer).filter_by(id=trial_id).first()
        if not customer:
            session.close()
            return {'success': False, 'error': 'Trial not found'}
        
        subscription = session.query(Subscription).filter_by(
            customer_id=trial_id,
            status='trialing'
        ).first()
        
        if not subscription:
            session.close()
            return {
                'success': True,
                'status': 'expired',
                'message': 'Trial has ended. Please upgrade to continue.'
            }
        
        now = time.time()
        days_remaining = int((subscription.trial_end - now) / (24 * 60 * 60))
        hours_remaining = int((subscription.trial_end - now) / 3600)
        
        is_active = now < subscription.trial_end
        
        session.close()
        return {
            'success': True,
            'status': 'active' if is_active else 'expired',
            'trial_id': trial_id,
            'email': customer.email,
            'plan': subscription.plan,
            'trial_start': subscription.trial_start,
            'trial_end': subscription.trial_end,
            'days_remaining': max(0, days_remaining),
            'hours_remaining': max(0, hours_remaining),
            'is_active': is_active
        }
        
    except Exception as e:
        session.close()
        logger.exception(f"Trial status check error: {e}")
        return {'success': False, 'error': str(e)}


def get_expiring_trials(days_before: int = 3) -> list:
    """
    Get trials expiring within specified days.
    Used for sending reminder emails.
    
    Args:
        days_before: Days before expiration
        
    Returns:
        list of trial dictionaries
    """
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    try:
        now = time.time()
        threshold = now + (days_before * 24 * 60 * 60)
        
        expiring_subs = session.query(Subscription).filter(
            Subscription.status == 'trialing',
            Subscription.trial_end <= threshold,
            Subscription.trial_end > now
        ).all()
        
        results = []
        for sub in expiring_subs:
            customer = session.query(Customer).filter_by(id=sub.customer_id).first()
            if customer:
                days_left = int((sub.trial_end - now) / (24 * 60 * 60))
                results.append({
                    'trial_id': customer.id,
                    'email': customer.email,
                    'name': customer.name,
                    'plan': sub.plan,
                    'days_remaining': days_left,
                    'trial_end': sub.trial_end
                })
        
        session.close()
        return results
        
    except Exception as e:
        session.close()
        logger.exception(f"Get expiring trials error: {e}")
        return []


def convert_trial_to_paid(trial_id: str, payment_id: str, order_id: str) -> dict:
    """
    Convert trial subscription to paid after successful payment.
    
    Args:
        trial_id: Trial user ID
        payment_id: Razorpay payment ID
        order_id: Razorpay order ID
        
    Returns:
        dict with conversion status
    """
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    try:
        # Find trial subscription
        trial_sub = session.query(Subscription).filter_by(
            customer_id=trial_id,
            status='trialing'
        ).first()
        
        if not trial_sub:
            session.close()
            return {'success': False, 'error': 'Trial not found'}
        
        # Update subscription to active
        now = time.time()
        billing_cycle_seconds = 30 * 24 * 60 * 60  # 30 days
        
        trial_sub.status = 'active'
        trial_sub.billing_cycle = 'monthly'
        trial_sub.current_period_start = now
        trial_sub.current_period_end = now + billing_cycle_seconds
        trial_sub.razorpay_payment_id = payment_id
        trial_sub.razorpay_order_id = order_id
        
        # Update customer status
        customer = session.query(Customer).filter_by(id=trial_id).first()
        if customer:
            customer.status = 'active'
        
        session.commit()
        
        # Send upgrade confirmation email
        if customer:
            _send_upgrade_confirmation_email(customer.email, customer.name, trial_sub.plan)
        
        logger.info(f"Trial converted to paid: {trial_id} -> {order_id}")
        
        session.close()
        return {
            'success': True,
            'message': 'Trial converted to paid subscription',
            'subscription_id': trial_sub.id,
            'status': 'active'
        }
        
    except Exception as e:
        session.rollback()
        session.close()
        logger.exception(f"Trial conversion error: {e}")
        return {'success': False, 'error': str(e)}


def send_trial_reminders():
    """
    Send reminder emails to trials expiring in 3, 1 days.
    Run this as a daily cron job.
    """
    # 3-day reminder
    trials_3d = get_expiring_trials(days_before=3)
    for trial in trials_3d:
        if trial['days_remaining'] == 3:
            _send_trial_reminder_email(
                trial['email'],
                trial['name'],
                trial['days_remaining'],
                trial['plan']
            )
            logger.info(f"3-day reminder sent to {trial['email']}")
    
    # 1-day reminder
    trials_1d = get_expiring_trials(days_before=1)
    for trial in trials_1d:
        if trial['days_remaining'] == 1:
            _send_trial_reminder_email(
                trial['email'],
                trial['name'],
                trial['days_remaining'],
                trial['plan']
            )
            logger.info(f"1-day reminder sent to {trial['email']}")


def _send_trial_welcome_email(email: str, name: str, trial_id: str, access_token: str, trial_end: float):
    """Send welcome email to trial user."""
    subject = "🎉 Welcome to SURESH AI ORIGIN - Your 14-Day Trial Starts Now!"
    
    trial_end_date = time.strftime('%B %d, %Y', time.localtime(trial_end))
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #667eea;">🚀 Welcome to SURESH AI ORIGIN!</h1>
        
        <p>Hi {name},</p>
        
        <p>Your <strong>14-day free trial</strong> has been activated! You now have full access to all 48 AI systems.</p>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Your Trial Details</h3>
            <p><strong>Trial ID:</strong> {trial_id}</p>
            <p><strong>Access Token:</strong> {access_token}</p>
            <p><strong>Trial Ends:</strong> {trial_end_date}</p>
        </div>
        
        <h3>🎯 Get Started in 3 Steps:</h3>
        <ol>
            <li><strong>Login:</strong> <a href="https://sureshaiorigin.com/admin">Admin Dashboard</a></li>
            <li><strong>Explore:</strong> Try chatbot, analytics, AI Eye Observer</li>
            <li><strong>Integrate:</strong> Connect your business data</li>
        </ol>
        
        <h3>💡 Quick Tips:</h3>
        <ul>
            <li>Check AI Eye Observer for real-time monitoring</li>
            <li>Set up customer segments for personalization</li>
            <li>Enable email automation for recovery campaigns</li>
            <li>Test A/B experiments on your landing pages</li>
        </ul>
        
        <div style="background: #667eea; color: white; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">
            <h3 style="margin-top: 0;">Need Help?</h3>
            <p>Reply to this email or visit our documentation:</p>
            <a href="https://sureshaiorigin.com/docs" style="color: white; text-decoration: underline;">View Docs</a>
        </div>
        
        <p>Let's build something amazing together! 🔥</p>
        
        <p>Best,<br>Suresh<br>Founder, SURESH AI ORIGIN</p>
    </body>
    </html>
    """
    
    try:
        send_email(to_email=email, subject=subject, html_body=html)
    except Exception as e:
        logger.exception(f"Failed to send trial welcome email: {e}")


def _send_trial_reminder_email(email: str, name: str, days_remaining: int, plan: str):
    """Send trial expiration reminder."""
    subject = f"⏰ Your Trial Ends in {days_remaining} Day{'s' if days_remaining > 1 else ''}!"
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #EF4444;">⏰ Your Trial is Ending Soon</h1>
        
        <p>Hi {name},</p>
        
        <p>Your 14-day free trial ends in <strong>{days_remaining} day{'s' if days_remaining > 1 else ''}</strong>.</p>
        
        <p>To continue using all 48 AI systems, upgrade to a paid plan:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://sureshaiorigin.com/pricing" 
               style="background: #667eea; color: white; padding: 15px 40px; 
                      text-decoration: none; border-radius: 10px; font-weight: bold; 
                      display: inline-block;">
                Upgrade Now
            </a>
        </div>
        
        <h3>💰 Current Plan: {plan.title()}</h3>
        <p>Continue with the same features you've been enjoying.</p>
        
        <h3>✨ What You'll Keep:</h3>
        <ul>
            <li>All 48 AI systems</li>
            <li>Unlimited automation</li>
            <li>Priority support</li>
            <li>All your data and integrations</li>
        </ul>
        
        <p style="color: #EF4444;"><strong>Don't lose access!</strong> Upgrade before your trial ends.</p>
        
        <p>Questions? Reply to this email.</p>
        
        <p>Best,<br>Suresh<br>Founder, SURESH AI ORIGIN</p>
    </body>
    </html>
    """
    
    try:
        send_email(to_email=email, subject=subject, html_body=html)
    except Exception as e:
        logger.exception(f"Failed to send trial reminder: {e}")


def _send_upgrade_confirmation_email(email: str, name: str, plan: str):
    """Send confirmation after trial upgrade."""
    subject = "🎉 Welcome to the Pro League! Your Subscription is Active"
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #10B981;">🎉 Subscription Activated!</h1>
        
        <p>Hi {name},</p>
        
        <p>Thank you for upgrading! Your <strong>{plan.title()} Plan</strong> is now active.</p>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3>What's Included:</h3>
            <ul>
                <li>✅ All 48 AI Systems</li>
                <li>✅ Unlimited Automation</li>
                <li>✅ Priority Support</li>
                <li>✅ White-Label Option</li>
                <li>✅ Custom Integrations</li>
            </ul>
        </div>
        
        <h3>🚀 Next Steps:</h3>
        <ol>
            <li>Set up advanced features in the admin dashboard</li>
            <li>Enable white-label branding (if available)</li>
            <li>Schedule a 1-on-1 onboarding call</li>
        </ol>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://sureshaiorigin.com/admin" 
               style="background: #667eea; color: white; padding: 15px 40px; 
                      text-decoration: none; border-radius: 10px; font-weight: bold; 
                      display: inline-block;">
                Go to Dashboard
            </a>
        </div>
        
        <p>Questions? Reply to this email or book a call: <a href="https://sureshaiorigin.com/support">Get Support</a></p>
        
        <p>Let's scale your business! 💪</p>
        
        <p>Best,<br>Suresh<br>Founder, SURESH AI ORIGIN</p>
    </body>
    </html>
    """
    
    try:
        send_email(to_email=email, subject=subject, html_body=html)
    except Exception as e:
        logger.exception(f"Failed to send upgrade confirmation: {e}")


def get_trial_stats() -> dict:
    """Get trial statistics for admin dashboard."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    try:
        total_trials = session.query(func.count(Subscription.id)).filter(
            Subscription.billing_cycle == 'trial'
        ).scalar() or 0
        
        active_trials = session.query(func.count(Subscription.id)).filter(
            Subscription.status == 'trialing',
            Subscription.trial_end > time.time()
        ).scalar() or 0
        
        expired_trials = session.query(func.count(Subscription.id)).filter(
            Subscription.billing_cycle == 'trial',
            Subscription.trial_end <= time.time()
        ).scalar() or 0
        
        converted = session.query(func.count(Subscription.id)).filter(
            Subscription.billing_cycle != 'trial',
            Subscription.customer_id.like('TRIAL_%')
        ).scalar() or 0
        
        conversion_rate = (converted / total_trials * 100) if total_trials > 0 else 0
        
        session.close()
        return {
            'total_trials': total_trials,
            'active_trials': active_trials,
            'expired_trials': expired_trials,
            'converted': converted,
            'conversion_rate': round(conversion_rate, 2)
        }
        
    except Exception as e:
        session.close()
        logger.exception(f"Trial stats error: {e}")
        return {
            'total_trials': 0,
            'active_trials': 0,
            'expired_trials': 0,
            'converted': 0,
            'conversion_rate': 0
        }
