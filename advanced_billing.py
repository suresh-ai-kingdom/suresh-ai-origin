"""Advanced Billing - Usage-based pricing, invoices, taxes, metering."""
import uuid
import time
from typing import Dict, List
from datetime import datetime, timedelta

class MeterService:
    """Track usage metrics for billing."""
    
    def __init__(self):
        self.meters = {}
    
    def record_usage(self, user_id: str, metric: str, quantity: float, timestamp: float = None) -> Dict:
        """Record usage for a metric."""
        if timestamp is None:
            timestamp = time.time()
        
        meter_id = f"{user_id}_{metric}_{int(timestamp / 86400)}"  # Daily bucket
        
        if meter_id not in self.meters:
            self.meters[meter_id] = {
                'user_id': user_id,
                'metric': metric,
                'date': datetime.fromtimestamp(timestamp).date().isoformat(),
                'quantity': 0,
                'recorded_at': timestamp,
            }
        
        self.meters[meter_id]['quantity'] += quantity
        
        return self.meters[meter_id]
    
    def get_daily_usage(self, user_id: str, date: str) -> Dict[str, float]:
        """Get daily usage for all metrics."""
        usage = {}
        for meter_id, meter in self.meters.items():
            if meter['user_id'] == user_id and meter['date'] == date:
                usage[meter['metric']] = meter['quantity']
        return usage
    
    def get_monthly_usage(self, user_id: str, year: int, month: int) -> Dict[str, float]:
        """Get monthly usage summary."""
        usage = {}
        for meter_id, meter in self.meters.items():
            if meter['user_id'] == user_id:
                date = datetime.fromisoformat(meter['date'])
                if date.year == year and date.month == month:
                    metric = meter['metric']
                    usage[metric] = usage.get(metric, 0) + meter['quantity']
        return usage


class PricingPlans:
    """Define usage-based pricing plans."""
    
    PLANS = {
        'free': {
            'name': 'Free',
            'base_price': 0,
            'currency': 'USD',
            'billing_period': 'monthly',
            'metrics': {
                'api_requests': {'unit_price': 0, 'limit': 1000},  # 1000 free requests
                'content_generations': {'unit_price': 0, 'limit': 10},
            },
        },
        'starter': {
            'name': 'Starter',
            'base_price': 29,
            'currency': 'USD',
            'billing_period': 'monthly',
            'metrics': {
                'api_requests': {'unit_price': 0.00001, 'included': 100000},  # 100k included
                'content_generations': {'unit_price': 0.10, 'included': 100},
                'storage_gb': {'unit_price': 0.50, 'included': 10},
            },
        },
        'pro': {
            'name': 'Pro',
            'base_price': 99,
            'currency': 'USD',
            'billing_period': 'monthly',
            'metrics': {
                'api_requests': {'unit_price': 0.000005, 'included': 1000000},  # 1M included
                'content_generations': {'unit_price': 0.05, 'included': 1000},
                'storage_gb': {'unit_price': 0.25, 'included': 100},
                'priority_support': {'unit_price': 0, 'included': True},
            },
        },
        'enterprise': {
            'name': 'Enterprise',
            'base_price': 'custom',
            'currency': 'USD',
            'billing_period': 'annual',
            'metrics': {
                'api_requests': {'unit_price': 'negotiable'},
                'content_generations': {'unit_price': 'negotiable'},
                'storage_gb': {'unit_price': 'negotiable'},
                'dedicated_support': {'unit_price': 0},
                'custom_sla': {'unit_price': 0},
            },
        },
    }
    
    @classmethod
    def get_plan(cls, plan_id: str) -> Dict:
        """Get plan details."""
        return cls.PLANS.get(plan_id, {})
    
    @classmethod
    def calculate_usage_charges(cls, plan_id: str, usage: Dict[str, float]) -> Dict:
        """Calculate charges based on usage."""
        plan = cls.get_plan(plan_id)
        charges = {}
        total = 0
        
        for metric, quantity in usage.items():
            metric_config = plan['metrics'].get(metric, {})
            included = metric_config.get('included', 0)
            unit_price = metric_config.get('unit_price', 0)
            
            if quantity > included:
                overage = quantity - included
                charge = overage * unit_price
                charges[metric] = {
                    'quantity': quantity,
                    'included': included,
                    'overage': overage,
                    'unit_price': unit_price,
                    'charge': charge,
                }
                total += charge
        
        return {
            'plan_id': plan_id,
            'base_price': plan['base_price'],
            'usage_charges': charges,
            'total_usage_charge': total,
            'total': plan['base_price'] + total if isinstance(plan['base_price'], (int, float)) else total,
        }


class Invoice:
    """Generate invoices for billing."""
    
    def __init__(self, tenant_id: str, billing_period_start: str, billing_period_end: str):
        self.id = str(uuid.uuid4())
        self.tenant_id = tenant_id
        self.number = f"INV-{int(time.time())}"
        self.billing_period_start = billing_period_start
        self.billing_period_end = billing_period_end
        self.issued_at = datetime.now().isoformat()
        self.due_date = (datetime.now() + timedelta(days=30)).isoformat()
        self.line_items = []
        self.subtotal = 0
        self.tax = 0
        self.total = 0
    
    def add_line_item(self, description: str, quantity: float, unit_price: float, tax_rate: float = 0) -> None:
        """Add line item to invoice."""
        subtotal = quantity * unit_price
        tax = subtotal * tax_rate
        total = subtotal + tax
        
        self.line_items.append({
            'description': description,
            'quantity': quantity,
            'unit_price': unit_price,
            'subtotal': subtotal,
            'tax': tax,
            'total': total,
        })
        
        self.subtotal += subtotal
        self.tax += tax
        self.total += total
    
    def to_dict(self) -> Dict:
        """Convert invoice to dictionary."""
        return {
            'id': self.id,
            'number': self.number,
            'tenant_id': self.tenant_id,
            'issued_at': self.issued_at,
            'due_date': self.due_date,
            'billing_period': f"{self.billing_period_start} to {self.billing_period_end}",
            'line_items': self.line_items,
            'subtotal': self.subtotal,
            'tax': self.tax,
            'total': self.total,
        }


class TaxCalculator:
    """Calculate taxes based on location."""
    
    TAX_RATES = {
        'US': {'CA': 0.0725, 'NY': 0.08, 'TX': 0.0625},
        'EU': {'default': 0.21},  # VAT
        'UK': 0.20,
        'AU': 0.10,
    }
    
    @staticmethod
    def get_tax_rate(country: str, state: str = None) -> float:
        """Get tax rate for location."""
        if country in TaxCalculator.TAX_RATES:
            rates = TaxCalculator.TAX_RATES[country]
            if isinstance(rates, dict) and state:
                return rates.get(state, 0)
            elif isinstance(rates, dict):
                return rates.get('default', 0)
            else:
                return rates
        return 0  # No tax
    
    @staticmethod
    def calculate_tax(amount: float, country: str, state: str = None) -> float:
        """Calculate tax amount."""
        rate = TaxCalculator.get_tax_rate(country, state)
        return amount * rate


class SubscriptionManager:
    """Manage subscription lifecycles."""
    
    def __init__(self):
        self.subscriptions = {}
    
    def create_subscription(self, tenant_id: str, plan_id: str, payment_method_id: str) -> Dict:
        """Create new subscription."""
        sub_id = str(uuid.uuid4())
        
        subscription = {
            'id': sub_id,
            'tenant_id': tenant_id,
            'plan_id': plan_id,
            'status': 'active',
            'payment_method_id': payment_method_id,
            'billing_cycle_start': datetime.now().isoformat(),
            'billing_cycle_end': (datetime.now() + timedelta(days=30)).isoformat(),
            'auto_renew': True,
            'created_at': time.time(),
        }
        
        self.subscriptions[sub_id] = subscription
        return subscription
    
    def upgrade_plan(self, subscription_id: str, new_plan_id: str) -> Dict:
        """Upgrade subscription to different plan."""
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id]['plan_id'] = new_plan_id
            self.subscriptions[subscription_id]['upgraded_at'] = time.time()
        
        return self.subscriptions[subscription_id]
    
    def cancel_subscription(self, subscription_id: str) -> Dict:
        """Cancel subscription."""
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id]['status'] = 'cancelled'
            self.subscriptions[subscription_id]['cancelled_at'] = time.time()
        
        return self.subscriptions[subscription_id]
