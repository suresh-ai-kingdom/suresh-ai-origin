"""Weekly KPI email automation."""
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict

from models import get_engine, get_session, Order, Subscription, Customer
from utils import _get_db_url
from sqlalchemy import func
from automation_workflows import get_automation_history


def calculate_weekly_kpis(days: int = 7) -> Dict:
    """Calculate key performance indicators for the past week."""
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    
    cutoff = time.time() - (days * 86400)
    
    # Revenue metrics
    total_revenue = session.query(func.sum(Order.amount)).filter(
        Order.status == 'paid',
        Order.created_at >= cutoff
    ).scalar() or 0
    
    order_count = session.query(func.count(Order.id)).filter(
        Order.status == 'paid',
        Order.created_at >= cutoff
    ).scalar() or 0
    
    # Subscription metrics
    new_subs = session.query(func.count(Subscription.id)).filter(
        Subscription.created_at >= cutoff
    ).scalar() or 0
    
    active_subs = session.query(func.count(Subscription.id)).filter(
        Subscription.status == 'ACTIVE'
    ).scalar() or 0
    
    # Customer metrics
    total_customers = session.query(func.count(func.distinct(Order.receipt))).scalar() or 0
    
    new_customers = session.query(func.count(func.distinct(Order.receipt))).filter(
        Order.created_at >= cutoff
    ).scalar() or 0
    
    # MRR calculation
    mrr = session.query(func.sum(Subscription.amount_paise)).filter(
        Subscription.status == 'ACTIVE',
        Subscription.billing_cycle == 'monthly',
        Subscription.current_period_end > time.time()
    ).scalar() or 0
    
    session.close()
    
    # Automation stats
    automation_logs = get_automation_history(days_back=days, limit=1000)
    automation_success = sum(1 for log in automation_logs if log.get('status') == 'SUCCESS')
    automation_failed = sum(1 for log in automation_logs if log.get('status') == 'FAILED')
    
    return {
        'period_days': days,
        'revenue': {
            'total': total_revenue / 100,  # Convert paise to rupees
            'orders': order_count,
            'avg_order_value': (total_revenue / order_count / 100) if order_count > 0 else 0,
        },
        'subscriptions': {
            'new': new_subs,
            'active': active_subs,
            'mrr': mrr / 100,
        },
        'customers': {
            'total': total_customers,
            'new': new_customers,
        },
        'automations': {
            'total': len(automation_logs),
            'success': automation_success,
            'failed': automation_failed,
            'success_rate': (automation_success / len(automation_logs) * 100) if automation_logs else 0,
        }
    }


def format_kpi_email(kpis: Dict) -> str:
    """Format KPI data as HTML email."""
    period = kpis['period_days']
    revenue = kpis['revenue']
    subs = kpis['subscriptions']
    customers = kpis['customers']
    automations = kpis['automations']
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .metric-group {{ background: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 15px 0; }}
        .metric-group h2 {{ color: #2c3e50; margin-top: 0; font-size: 18px; }}
        .metric {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #dee2e6; }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-label {{ font-weight: bold; color: #495057; }}
        .metric-value {{ color: #28a745; font-size: 18px; font-weight: bold; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 12px; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Weekly KPI Report - SURESH AI ORIGIN</h1>
        <p><strong>Period:</strong> Last {period} days | <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        
        <div class="metric-group">
            <h2>💰 Revenue</h2>
            <div class="metric">
                <span class="metric-label">Total Revenue</span>
                <span class="metric-value">₹{revenue['total']:,.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Orders</span>
                <span class="metric-value">{revenue['orders']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Avg Order Value</span>
                <span class="metric-value">₹{revenue['avg_order_value']:,.2f}</span>
            </div>
        </div>
        
        <div class="metric-group">
            <h2>🔄 Subscriptions</h2>
            <div class="metric">
                <span class="metric-label">New Subscriptions</span>
                <span class="metric-value">{subs['new']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Active Subscriptions</span>
                <span class="metric-value">{subs['active']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Monthly Recurring Revenue (MRR)</span>
                <span class="metric-value">₹{subs['mrr']:,.2f}</span>
            </div>
        </div>
        
        <div class="metric-group">
            <h2>👥 Customers</h2>
            <div class="metric">
                <span class="metric-label">Total Customers</span>
                <span class="metric-value">{customers['total']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">New Customers</span>
                <span class="metric-value">{customers['new']}</span>
            </div>
        </div>
        
        <div class="metric-group">
            <h2>🤖 Automations</h2>
            <div class="metric">
                <span class="metric-label">Total Actions</span>
                <span class="metric-value">{automations['total']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Successful</span>
                <span class="metric-value" style="color: #28a745;">{automations['success']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Failed</span>
                <span class="metric-value" style="color: #dc3545;">{automations['failed']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Success Rate</span>
                <span class="metric-value">{automations['success_rate']:.1f}%</span>
            </div>
        </div>
        
        <div class="footer">
            <p>This is an automated weekly report from SURESH AI ORIGIN.</p>
            <p>View detailed analytics: <a href="https://suresh-ai-origin.onrender.com/admin">Admin Dashboard</a></p>
        </div>
    </div>
</body>
</html>
"""
    return html


def send_weekly_kpi_email(recipients: list = None, days: int = 7) -> bool:
    """Generate and send weekly KPI email."""
    if recipients is None:
        recipients = [os.getenv('ALERT_EMAIL', 'suresh.ai.origin@outlook.com')]
    
    email_user = os.getenv('EMAIL_USER', 'suresh.ai.origin@outlook.com')
    email_pass = os.getenv('EMAIL_PASS')
    
    if not email_pass:
        print("⚠️  EMAIL_PASS not set; cannot send KPI email")
        return False
    
    try:
        # Calculate KPIs
        kpis = calculate_weekly_kpis(days=days)
        
        # Format email
        html_content = format_kpi_email(kpis)
        
        # Send email
        msg = MIMEMultipart('alternative')
        msg['From'] = email_user
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = f"📊 Weekly KPI Report - SURESH AI ORIGIN ({datetime.now().strftime('%Y-%m-%d')})"
        
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        server.login(email_user, email_pass)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Weekly KPI email sent to {', '.join(recipients)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send KPI email: {e}")
        return False


if __name__ == '__main__':
    # Test run
    send_weekly_kpi_email()
