"""Advanced billing system - usage-based pricing, metered events, invoices."""
import uuid
import time
from typing import Dict, List
from datetime import datetime, timedelta
import json

class UsageTracker:
    """Track metered usage for billing."""
    
    METRIC_TYPES = {
        'api_calls': {'rate': 0.01, 'per': 'call'},  # $0.01 per API call
        'ai_generations': {'rate': 0.05, 'per': 'generation'},  # $0.05 per AI generation
        'storage_gb': {'rate': 0.50, 'per': 'gb/month'},  # $0.50 per GB/month
        'email_sends': {'rate': 0.001, 'per': 'email'},  # $0.001 per email
        'sms_sends': {'rate': 0.07, 'per': 'sms'},  # $0.07 per SMS
        'active_users': {'rate': 10.0, 'per': 'user/month'},  # $10 per active user/month
    }
    
    def __init__(self):
        self.events = {}  # tenant_id -> [events]
    
    def track_event(self, tenant_id: str, metric: str, value: float = 1.0) -> Dict:
        """Record usage event."""
        if metric not in self.METRIC_TYPES:
            return {'error': f'Unknown metric: {metric}'}
        
        event = {
            'id': str(uuid.uuid4()),
            'tenant_id': tenant_id,
            'metric': metric,
            'value': value,
            'timestamp': time.time(),
            'rate': self.METRIC_TYPES[metric]['rate'],
            'cost': value * self.METRIC_TYPES[metric]['rate'],
        }
        
        if tenant_id not in self.events:
            self.events[tenant_id] = []
        
        self.events[tenant_id].append(event)
        
        return event
    
    def get_current_usage(self, tenant_id: str, period_start: float = None) -> Dict:
        """Get usage metrics for current billing period."""
        if period_start is None:
            # Start of current month
            now = datetime.now()
            period_start = datetime(now.year, now.month, 1).timestamp()
        
        if tenant_id not in self.events:
            return {}
        
        usage = {}
        total_cost = 0.0
        
        for event in self.events[tenant_id]:
            if event['timestamp'] >= period_start:
                metric = event['metric']
                
                if metric not in usage:
                    usage[metric] = {'count': 0, 'cost': 0.0}
                
                usage[metric]['count'] += event['value']
                usage[metric]['cost'] += event['cost']
                total_cost += event['cost']
        
        return {
            'tenant_id': tenant_id,
            'period_start': period_start,
            'usage': usage,
            'total_cost': total_cost,
        }


class InvoiceGenerator:
    """Generate invoices for metered usage."""
    
    def __init__(self):
        self.invoices = {}
    
    def generate_invoice(self, tenant_id: str, period_start: float, period_end: float, usage: Dict) -> Dict:
        """Generate invoice for usage period."""
        invoice_id = f'INV-{int(time.time())}-{tenant_id[:8]}'
        
        # Calculate subtotal
        subtotal = sum(item['cost'] for item in usage.get('usage', {}).values())
        
        # Apply tax (10% assumed)
        tax = subtotal * 0.10
        total = subtotal + tax
        
        invoice = {
            'id': invoice_id,
            'tenant_id': tenant_id,
            'period_start': period_start,
            'period_end': period_end,
            'issued_at': time.time(),
            'subtotal': subtotal,
            'tax': tax,
            'total': total,
            'status': 'draft',  # draft, sent, paid, overdue
            'line_items': [],
        }
        
        # Generate line items
        for metric, data in usage.get('usage', {}).items():
            invoice['line_items'].append({
                'description': f'{metric}: {data["count"]}',
                'quantity': data['count'],
                'rate': UsageTracker.METRIC_TYPES[metric]['rate'],
                'amount': data['cost'],
            })
        
        self.invoices[invoice_id] = invoice
        return invoice
    
    def get_invoice(self, invoice_id: str) -> Dict:
        """Retrieve invoice."""
        return self.invoices.get(invoice_id, {})
    
    def send_invoice(self, invoice_id: str, email: str) -> Dict:
        """Send invoice to customer."""
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            return {'error': 'Invoice not found'}
        
        # In production: generate PDF, send via email
        print(f"📧 Invoice {invoice_id} sent to {email}")
        
        invoice['status'] = 'sent'
        invoice['sent_at'] = time.time()
        
        return {'invoice_id': invoice_id, 'sent_to': email}


class TaxCalculator:
    """Calculate taxes based on tenant location."""
    
    RATES = {
        'US': {'state': {'CA': 0.0725, 'NY': 0.08, 'TX': 0.0625}},
        'EU': {'vat': 0.19},  # 19% standard
        'UK': {'vat': 0.20},
        'DEFAULT': 0.10,
    }
    
    @staticmethod
    def calculate_tax(amount: float, country: str, state: str = None) -> Dict:
        """Calculate tax for amount."""
        country_rates = TaxCalculator.RATES.get(country, {})
        
        if not country_rates:
            rate = TaxCalculator.RATES['DEFAULT']
        elif country == 'US' and state:
            rate = country_rates['state'].get(state, 0.07)
        elif country in ['EU', 'UK']:
            rate = country_rates.get('vat', 0.10)
        else:
            rate = TaxCalculator.RATES['DEFAULT']
        
        tax = amount * rate
        
        return {
            'amount': amount,
            'rate': rate,
            'tax': tax,
            'total': amount + tax,
            'country': country,
            'state': state,
        }


class PaymentPlan:
    """Manage subscription payment plans."""
    
    PLANS = {
        'starter': {
            'name': 'Starter',
            'price': 29.99,
            'billing_cycle': 'monthly',
            'limits': {'api_calls': 10000, 'ai_generations': 100},
            'included_users': 1,
        },
        'pro': {
            'name': 'Pro',
            'price': 99.99,
            'billing_cycle': 'monthly',
            'limits': {'api_calls': 100000, 'ai_generations': 1000},
            'included_users': 5,
        },
        'enterprise': {
            'name': 'Enterprise',
            'price': 999.99,
            'billing_cycle': 'monthly',
            'limits': {'api_calls': -1, 'ai_generations': -1},  # Unlimited
            'included_users': -1,
        },
    }
    
    def __init__(self):
        self.subscriptions = {}
    
    def create_subscription(self, tenant_id: str, plan_id: str) -> Dict:
        """Create subscription."""
        if plan_id not in self.PLANS:
            return {'error': f'Plan not found: {plan_id}'}
        
        plan = self.PLANS[plan_id]
        sub_id = f'SUB-{int(time.time())}-{tenant_id[:8]}'
        
        subscription = {
            'id': sub_id,
            'tenant_id': tenant_id,
            'plan_id': plan_id,
            'plan': plan,
            'status': 'active',
            'created_at': time.time(),
            'renewal_at': time.time() + 30 * 86400,  # 30 days
        }
        
        self.subscriptions[sub_id] = subscription
        return subscription
    
    def upgrade_plan(self, subscription_id: str, new_plan_id: str) -> Dict:
        """Upgrade to higher tier plan."""
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return {'error': 'Subscription not found'}
        
        old_plan = self.PLANS[sub['plan_id']]
        new_plan = self.PLANS.get(new_plan_id)
        
        if not new_plan:
            return {'error': f'Plan not found: {new_plan_id}'}
        
        # Prorate credits
        prorated = self._calculate_proration(old_plan, new_plan, sub['renewal_at'])
        
        sub['plan_id'] = new_plan_id
        sub['plan'] = new_plan
        sub['prorated_credit'] = prorated
        
        print(f"📈 Upgraded {subscription_id} to {new_plan_id} (credit: ${prorated})")
        
        return sub
    
    def _calculate_proration(self, old_plan: Dict, new_plan: Dict, renewal_at: float) -> float:
        """Calculate prorated credit for plan upgrade."""
        days_remaining = (renewal_at - time.time()) / 86400
        old_daily = old_plan['price'] / 30
        new_daily = new_plan['price'] / 30
        daily_difference = new_daily - old_daily
        
        return daily_difference * days_remaining


# Usage Example
if __name__ == '__main__':
    # Initialize
    tracker = UsageTracker()
    invoicer = InvoiceGenerator()
    
    # Track usage
    tracker.track_event('tenant_1', 'api_calls', 1000)
    tracker.track_event('tenant_1', 'ai_generations', 50)
    tracker.track_event('tenant_1', 'email_sends', 5000)
    
    # Get current usage
    usage = tracker.get_current_usage('tenant_1')
    print(f"Usage: {json.dumps(usage, indent=2)}")
    
    # Generate invoice
    invoice = invoicer.generate_invoice(
        'tenant_1',
        usage['period_start'],
        time.time(),
        usage
    )
    print(f"Invoice: ${invoice['total']:.2f}")
    
    # Calculate tax
    tax_info = TaxCalculator.calculate_tax(invoice['total'], 'US', 'CA')
    print(f"Tax (CA): ${tax_info['tax']:.2f}")
