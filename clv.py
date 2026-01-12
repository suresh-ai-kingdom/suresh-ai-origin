"""Customer Lifetime Value (CLV) Engine

Computes CLV per customer using:
- Historical revenue from orders
- Simple expected future value from repeat behavior
- Discounting for future cash flows

Deterministic and offline-friendly.
"""
import time
from datetime import datetime
from typing import Dict, List

from models import get_session, Order, Customer


def _rupees(paise: int) -> float:
    return round((paise or 0) / 100.0, 2)


def compute_customer_clv(receipt: str) -> Dict:
    """Compute CLV for a single customer.
    Model:
      base_revenue = sum(order.amount) in rupees
      repeat_factor = min(0.5, (order_count - 1) * 0.1)  # up to +50%
      future_value = base_revenue * repeat_factor
      discount = 0.9
      clv = base_revenue + future_value * discount
      confidence: 0.6 + min(0.35, order_count * 0.05)
    """
    session = get_session()
    try:
        customer = session.query(Customer).filter(Customer.receipt == receipt).first()
        orders = session.query(Order).filter(Order.receipt == receipt).all()
        base_paise = sum(o.amount or 0 for o in orders)
        base_rupees = _rupees(base_paise)
        order_count = len(orders)
        repeat_factor = min(0.5, max(0, order_count - 1) * 0.1)
        future_value = base_rupees * repeat_factor
        discount = 0.9
        clv_value = round(base_rupees + future_value * discount, 2)
        confidence = round(0.6 + min(0.35, order_count * 0.05), 2)
        return {
            "receipt": receipt,
            "orders": order_count,
            "base_rupees": round(base_rupees, 2),
            "future_rupees": round(future_value * discount, 2),
            "clv_rupees": clv_value,
            "confidence": confidence,
            "segment": getattr(customer, 'segment', None) if customer else None,
        }
    finally:
        session.close()


def compute_all_clv(limit: int = 50) -> List[Dict]:
    """Compute CLV for all customers and return top by CLV value."""
    session = get_session()
    try:
        receipts = [c.receipt for c in session.query(Customer).all()]
    finally:
        session.close()
    results = [compute_customer_clv(r) for r in receipts]
    results.sort(key=lambda x: x["clv_rupees"], reverse=True)
    return results[:limit]


def clv_stats() -> Dict:
    """Aggregate stats for CLV distribution."""
    session = get_session()
    try:
        customers = session.query(Customer).count()
        orders = session.query(Order).count()
    finally:
        session.close()
    top = compute_all_clv(limit=10)
    avg_clv = round(sum(x["clv_rupees"] for x in top) / max(len(top), 1), 2)
    return {
        "customers": customers,
        "orders": orders,
        "avg_clv_top10": avg_clv,
        "top": top,
        "generated_at": datetime.now().isoformat(),
    }
