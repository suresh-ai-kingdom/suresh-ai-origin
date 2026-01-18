"""
Email Notifier Module - Send email alerts and weekly reports
"""

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("EmailNotifier")


class EmailNotifier:
    """Send email notifications for anomalies and reports."""
    
    def __init__(self, 
                 smtp_host: str = None,
                 smtp_port: int = None,
                 smtp_user: str = None,
                 smtp_pass: str = None,
                 admin_email: str = None):
        """
        Initialize email notifier.
        
        Args:
            smtp_host: SMTP server host (default: EMAIL_HOST env var)
            smtp_port: SMTP server port (default: EMAIL_PORT env var)
            smtp_user: SMTP username (default: EMAIL_USER env var)
            smtp_pass: SMTP password (default: EMAIL_PASS env var)
            admin_email: Admin email address (default: ADMIN_EMAIL env var)
        """
        self.smtp_host = smtp_host or os.getenv("EMAIL_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("EMAIL_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("EMAIL_USER", "")
        self.smtp_pass = smtp_pass or os.getenv("EMAIL_PASS", "")
        self.admin_email = admin_email or os.getenv("ADMIN_EMAIL", self.smtp_user)
        
        logger.info(f"EmailNotifier initialized (host: {self.smtp_host}, port: {self.smtp_port})")
    
    def _send_email(self, 
                   to_email: str,
                   subject: str,
                   html_body: str,
                   attachments: List[str] = None) -> bool:
        """
        Send HTML email with optional attachments.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            attachments: List of file paths to attach
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Add attachments
            if attachments:
                for filepath in attachments:
                    path = Path(filepath)
                    if path.exists():
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 
                                      f'attachment; filename={path.name}')
                        msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            logger.info(f"✓ Email sent to {to_email}: {subject}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False
    
    def send_anomaly_alert(self, anomalies: Dict[str, Any]) -> bool:
        """
        Send immediate alert for detected anomalies.
        
        Args:
            anomalies: Anomaly detection results from AnomalyDetector
        
        Returns:
            True if sent successfully, False otherwise
        """
        logger.info("Sending anomaly alert email")
        
        if not anomalies.get("anomalies_detected"):
            logger.info("No anomalies to report - skipping email")
            return True
        
        critical_count = anomalies.get("critical_count", 0)
        warning_count = anomalies.get("warning_count", 0) 
        total = anomalies.get("total_anomalies", 0)
        
        # Determine severity color
        if critical_count > 0:
            severity = "CRITICAL"
            color = "#f44336"
        elif warning_count > 0:
            severity = "WARNING"
            color = "#FF9800"
        else:
            severity = "INFO"
            color = "#2196F3"
        
        subject = f"🚨 [{severity}] Analytics Anomalies Detected - {total} Alert(s)"
        
        # Build HTML body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: {color};
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .content {{
            padding: 30px;
        }}
        .summary {{
            background: #f9f9f9;
            padding: 15px;
            border-left: 4px solid {color};
            margin-bottom: 20px;
        }}
        .anomaly {{
            background: #fff3cd;
            border-left: 4px solid #ff9800;
            padding: 15px;
            margin-bottom: 15px;
        }}
        .anomaly.critical {{
            background: #ffebee;
            border-left-color: #f44336;
        }}
        .metric {{
            font-weight: bold;
            color: #333;
        }}
        .change {{
            font-size: 18px;
            font-weight: bold;
            color: #f44336;
        }}
        .footer {{
            background: #f5f5f5;
            padding: 15px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 Analytics Anomaly Alert</h1>
            <p>SURESH AI ORIGIN - {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>
        
        <div class="content">
            <div class="summary">
                <h2 style="margin-top: 0;">Summary</h2>
                <p><strong>Total Anomalies:</strong> {total}</p>
                <p><strong>Critical:</strong> {critical_count}</p>
                <p><strong>Warnings:</strong> {warning_count}</p>
            </div>
            
            <h2>Detected Anomalies</h2>
"""
        
        # Add anomalies
        for anomaly in anomalies.get("all_anomalies", []):
            css_class = "critical" if anomaly["severity"] == "critical" else "anomaly"
            
            html_body += f"""
            <div class="{css_class}">
                <p class="metric">{anomaly['metric']}</p>
                <p><strong>Current:</strong> {anomaly['current_value']:,.2f}</p>
                <p><strong>Previous:</strong> {anomaly['previous_value']:,.2f}</p>
                <p class="change">{anomaly['change_percent']:+.1f}%</p>
                <p style="margin-bottom: 0;">{anomaly['message']}</p>
            </div>
"""
        
        html_body += """
            <h3>Recommended Actions</h3>
            <ul>
                <li>Review recent changes in marketing campaigns</li>
                <li>Check product/service quality metrics</li>
                <li>Analyze customer feedback and support tickets</li>
                <li>Investigate technical issues or outages</li>
                <li>Compare with industry benchmarks</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>This is an automated alert from SURESH AI ORIGIN Analytics Engine</p>
            <p>For questions, contact your system administrator</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self._send_email(self.admin_email, subject, html_body)
    
    def send_weekly_report(self, 
                          kpis: Dict[str, Any], 
                          anomalies: Dict[str, Any],
                          pdf_path: str = None) -> bool:
        """
        Send weekly report with PDF attachment.
        
        Args:
            kpis: All calculated KPIs
            anomalies: Anomaly detection results
            pdf_path: Path to PDF report file
        
        Returns:
            True if sent successfully, False otherwise
        """
        logger.info("Sending weekly report email")
        
        revenue_metrics = kpis.get("revenue_metrics", {})
        growth_metrics = kpis.get("growth_metrics", {})
        prompt_stats = kpis.get("prompt_statistics", {})
        top_referrers = kpis.get("top_referrers", [])[:3]
        
        subject = f"📊 Weekly Analytics Report - {datetime.now().strftime('%B %d, %Y')}"
        
        # Build HTML body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 700px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .content {{
            padding: 30px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metric-label {{
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .growth-positive {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .growth-negative {{
            color: #f44336;
            font-weight: bold;
        }}
        .referrer {{
            background: #f5f5f5;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
        }}
        .footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
        .pdf-notice {{
            background: #e3f2fd;
            border: 1px solid #2196F3;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Weekly Analytics Report</h1>
            <p>SURESH AI ORIGIN</p>
            <p>{datetime.now().strftime("%B %d, %Y")}</p>
        </div>
        
        <div class="content">
            <div class="pdf-notice">
                <strong>📎 Detailed PDF Report Attached</strong><br>
                See attached PDF for comprehensive visualizations and charts
            </div>
            
            <div class="section">
                <h2>💰 Revenue Metrics</h2>
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-label">MRR</div>
                        <div class="metric-value">₹{revenue_metrics.get('mrr', 0):,.0f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">ARR</div>
                        <div class="metric-value">₹{revenue_metrics.get('arr', 0):,.0f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Active Subscriptions</div>
                        <div class="metric-value">{revenue_metrics.get('active_subscriptions', 0)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Churn Rate</div>
                        <div class="metric-value">{revenue_metrics.get('churn_rate', 0):.1f}%</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📈 Growth Metrics</h2>
                <p><strong>Total Active Users (30d):</strong> {growth_metrics.get('total_active_users', 0):,}</p>
                <p><strong>New Users (30d):</strong> {growth_metrics.get('total_new_users', 0):,}</p>
                <p><strong>User Growth (WoW):</strong> 
                    <span class="{'growth-positive' if growth_metrics.get('user_growth_wow', 0) > 0 else 'growth-negative'}">
                        {growth_metrics.get('user_growth_wow', 0):+.1f}%
                    </span>
                </p>
                <p><strong>PageView Growth (WoW):</strong> 
                    <span class="{'growth-positive' if growth_metrics.get('pageview_growth_wow', 0) > 0 else 'growth-negative'}">
                        {growth_metrics.get('pageview_growth_wow', 0):+.1f}%
                    </span>
                </p>
            </div>
            
            <div class="section">
                <h2>🤖 AI Prompt Statistics</h2>
                <p><strong>Total Prompts (30d):</strong> {prompt_stats.get('total_prompts', 0):,}</p>
                <p><strong>Success Rate:</strong> {prompt_stats.get('overall_success_rate', 0):.1f}%</p>
                <p><strong>Most Used Feature:</strong> {prompt_stats.get('most_used_feature', 'N/A')}</p>
                <p><strong>Best Performing Feature:</strong> {prompt_stats.get('best_performing_feature', 'N/A')}</p>
            </div>
            
            <div class="section">
                <h2>🔗 Top Referrers</h2>
"""
        
        for referrer in top_referrers:
            html_body += f"""
                <div class="referrer">
                    <strong>{referrer['referrer_name']}</strong><br>
                    Referrals: {referrer['referral_count']} | Revenue: ₹{referrer['revenue']:,.0f}
                </div>
"""
        
        # Add anomalies if any
        if anomalies.get("anomalies_detected"):
            html_body += f"""
            </div>
            
            <div class="section">
                <h2 style="color: #f44336;">🚨 Anomalies Detected</h2>
                <p><strong>{anomalies.get('total_anomalies', 0)} anomaly/anomalies detected this week</strong></p>
                <p>Critical: {anomalies.get('critical_count', 0)} | Warnings: {anomalies.get('warning_count', 0)}</p>
                <p style="color: #f44336;"><em>Review the PDF report for detailed anomaly analysis</em></p>
            </div>
"""
        else:
            html_body += """
            </div>
            
            <div class="section">
                <h2 style="color: #4CAF50;">✓ No Anomalies</h2>
                <p>All metrics are healthy - no significant drops detected</p>
            </div>
"""
        
        html_body += """
        </div>
        
        <div class="footer">
            <p>This report is automatically generated by SURESH AI ORIGIN Analytics Engine</p>
            <p>For questions or concerns, contact your system administrator</p>
        </div>
    </div>
</body>
</html>
"""
        
        attachments = [pdf_path] if pdf_path and Path(pdf_path).exists() else []
        return self._send_email(self.admin_email, subject, html_body, attachments)
    
    def send_test_email(self) -> bool:
        """
        Send test email to verify configuration.
        
        Returns:
            True if sent successfully, False otherwise
        """
        subject = "✓ Analytics Engine - Email Configuration Test"
        html_body = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #4CAF50;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✓ Email Configuration Test</h1>
        <p>This is a test email from SURESH AI ORIGIN Analytics Engine.</p>
        <p>If you received this email, your SMTP configuration is working correctly.</p>
        <hr>
        <p style="text-align: center; color: #666; font-size: 12px;">
            Sent: """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """
        </p>
    </div>
</body>
</html>
"""
        
        return self._send_email(self.admin_email, subject, html_body)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test email configuration
    notifier = EmailNotifier()
    
    print(f"SMTP Host: {notifier.smtp_host}")
    print(f"SMTP Port: {notifier.smtp_port}")
    print(f"SMTP User: {notifier.smtp_user}")
    print(f"Admin Email: {notifier.admin_email}")
    
    # Send test email
    success = notifier.send_test_email()
    
    if success:
        print("\n✓ Test email sent successfully!")
    else:
        print("\n✗ Failed to send test email - check credentials")
