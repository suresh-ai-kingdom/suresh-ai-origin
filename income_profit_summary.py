"""
SURESH AI ORIGIN - INCOME & PROFIT SUMMARY (2026)

Full breakdown of all revenue streams, monthly/annual profit, growth rates, and net margins.

Streams:
- Task Automation
- Template Marketplace
- Subscriptions
- Drone Delivery
- Tree Planting
- Referral Commissions
- API Usage
- Enterprise Contracts
- White-label Licensing
- Training Courses
- Consulting Services
- Data Analytics
- Carbon Credits
- Affiliate Earnings
- Template Royalties

Calculates:
- Monthly Recurring Revenue (MRR)
- Annual Recurring Revenue (ARR)
- Growth Rate
- Cost Structure (COGS, OpEx)
- Net Profit
- Profit Margin
- Stream-wise breakdown
"""

import json
from datetime import datetime

REVENUE_STREAMS = {
    "task_automation": {"mrr": 250000, "cogs": 0.35, "opex": 0.15},
    "marketplace_sales": {"mrr": 180000, "cogs": 0.28, "opex": 0.12},
    "subscriptions": {"mrr": 320000, "cogs": 0.18, "opex": 0.10},
    "drone_delivery": {"mrr": 450000, "cogs": 0.42, "opex": 0.18},
    "tree_planting": {"mrr": 95000, "cogs": 0.55, "opex": 0.10},
    "referral_commissions": {"mrr": 75000, "cogs": 0.10, "opex": 0.08},
    "template_royalties": {"mrr": 42000, "cogs": 0.25, "opex": 0.07},
    "api_usage": {"mrr": 135000, "cogs": 0.22, "opex": 0.09},
    "enterprise_contracts": {"mrr": 680000, "cogs": 0.12, "opex": 0.13},
    "white_label": {"mrr": 220000, "cogs": 0.15, "opex": 0.09},
    "training_courses": {"mrr": 88000, "cogs": 0.20, "opex": 0.11},
    "consulting": {"mrr": 195000, "cogs": 0.08, "opex": 0.14},
    "data_analytics": {"mrr": 110000, "cogs": 0.16, "opex": 0.10},
    "carbon_credits": {"mrr": 65000, "cogs": 0.30, "opex": 0.09},
    "affiliate_earnings": {"mrr": 52000, "cogs": 0.12, "opex": 0.08},
}

GROWTH_RATE = 0.168  # 16.8% monthly

summary = {
    "streams": [],
    "total_mrr": 0,
    "total_arr": 0,
    "total_profit_month": 0,
    "total_profit_year": 0,
    "avg_margin": 0,
    "growth_rate": f"{GROWTH_RATE*100:.1f}%",
    "generated_at": datetime.now().isoformat(),
}

for name, data in REVENUE_STREAMS.items():
    mrr = data["mrr"]
    arr = mrr * 12
    cogs = mrr * data["cogs"]
    opex = mrr * data["opex"]
    profit = mrr - cogs - opex
    margin = profit / mrr if mrr else 0
    summary["streams"].append({
        "name": name,
        "mrr": mrr,
        "arr": arr,
        "cogs": cogs,
        "opex": opex,
        "profit_month": profit,
        "profit_year": profit * 12,
        "margin": f"{margin*100:.1f}%",
    })
    summary["total_mrr"] += mrr
    summary["total_arr"] += arr
    summary["total_profit_month"] += profit
    summary["total_profit_year"] += profit * 12

summary["avg_margin"] = f"{(summary['total_profit_month']/summary['total_mrr'])*100:.1f}%"

if __name__ == "__main__":
    print("\nSURESH AI ORIGIN - INCOME & PROFIT SUMMARY (2026)")
    print("="*70)
    print(f"Total MRR: ₹{summary['total_mrr']:,}")
    print(f"Total ARR: ₹{summary['total_arr']:,}")
    print(f"Monthly Growth Rate: {summary['growth_rate']}")
    print(f"Net Profit (Month): ₹{summary['total_profit_month']:,}")
    print(f"Net Profit (Year): ₹{summary['total_profit_year']:,}")
    print(f"Average Profit Margin: {summary['avg_margin']}")
    print("\nStream-wise Breakdown:")
    for s in summary["streams"]:
        print(f"- {s['name'].replace('_',' ').title()}: MRR ₹{s['mrr']:,}, Profit ₹{s['profit_month']:,}/mo, Margin {s['margin']}")
    print("\n" + "="*70)
    print("Generated at:", summary["generated_at"])
