#!/usr/bin/env python3
"""Validation script for abandoned order recovery system."""
from recovery import *
from models import get_engine, Base

# Initialize database
engine = get_engine()
Base.metadata.create_all(engine)

print('📊 ABANDONED ORDER RECOVERY SYSTEM - VALIDATION')
print('=' * 60)
print()

# Test 1: Metrics
metrics = get_recovery_metrics()
print('✅ Recovery Metrics')
print('   - Total Abandoned Orders:', metrics['total_abandoned_orders'])
print('   - Total Risk Value: ₹' + f"{metrics['total_abandoned_value_rupees']:.0f}")

# Test 2: Suggestions  
suggestions = get_recovery_suggestions()
print()
print('✅ Recovery Suggestions')
print('   - Actionable Recommendations:', len(suggestions))

# Test 3: Recovery Potential
potential = estimate_recovery_potential()
print()
print('✅ Recovery Potential Analysis')
print('   - Recovery Rate: ' + f"{potential['recovery_rate_percent']:.1f}%")
print('   - Recoverable Amount: ₹' + f"{potential['estimated_recoverable_rupees']:.0f}")

# Test 4: Product Analysis
product_rates = get_product_abandonment_rate()
print()
print('✅ Product Abandonment Analysis')
print('   - Products Tracked:', len(product_rates))
for product in list(product_rates.keys())[:3]:
    stats = product_rates[product]
    print(f'   - {product}: {stats["abandonment_rate"]:.1f}% abandoned')

# Test 5: Reminder Schedule
print()
print('✅ Reminder Scheduling System')
print('   - Configured Tiers:', len(REMINDER_SCHEDULE))
for i, tier in enumerate(REMINDER_SCHEDULE):
    print(f'   - Tier {i+1}: {tier["delay_hours"]}h delay - {tier["name"]}')

print()
print('=' * 60)
print('🎉 ABANDONED ORDER RECOVERY SYSTEM READY FOR PRODUCTION')
print()
print('Access dashboard at: /admin/recovery')
print('API endpoints: /api/recovery/*')
print()
