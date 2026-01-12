"""Smart Email Timing Engine

Determines optimal send times per customer and globally by analyzing:
- Order purchase timestamps (signal of activity)
- Abandoned reminder email opened/clicked timestamps (engagement)

No external dependencies; offline deterministic.
"""
import time
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

from models import get_session, Order, Customer, AbandonedReminder


def _hour_of(ts: float) -> int:
    try:
        return datetime.fromtimestamp(ts).hour
    except Exception:
        return 12


def get_customer_activity_hours(receipt: str) -> Dict[int, float]:
    """Return weighted activity per hour for a customer (0-23).
    Weights:
      - Purchase activity (orders.created_at): +2
      - Reminder opened_at: +3
      - Reminder clicked_at: +4
    """
    session = get_session()
    try:
        weights = defaultdict(float)
        # Orders
        orders = session.query(Order).filter(Order.receipt == receipt).all()
        for o in orders:
            if o.created_at:
                weights[_hour_of(o.created_at)] += 2.0
        # Abandoned reminders
        reminders = session.query(AbandonedReminder).filter(AbandonedReminder.receipt == receipt).all()
        for r in reminders:
            if r.opened_at:
                weights[_hour_of(r.opened_at)] += 3.0
            if r.clicked_at:
                weights[_hour_of(r.clicked_at)] += 4.0
        # Normalize minimally
        return dict(weights)
    finally:
        session.close()


def predict_best_send_time(receipt: str) -> Dict:
    """Predict best hour to send email for a customer.
    Fallback to global best if no data.
    Returns dict {hour, confidence, sources}
    """
    activity = get_customer_activity_hours(receipt)
    if not activity:
        gb = get_global_best_send_time()
        return {
            "hour": gb["hour"],
            "confidence": round(gb["confidence"] * 0.8, 2),
            "sources": {"global": True, "customer": False},
        }
    # pick hour with max weight
    best_hour = max(activity.items(), key=lambda kv: kv[1])[0]
    total = sum(activity.values()) or 1.0
    confidence = min(0.95, activity.get(best_hour, 0.0) / total + 0.5)  # 0.5 base boost
    return {
        "hour": int(best_hour),
        "confidence": round(confidence, 2),
        "sources": {"orders": True, "reminders": True},
        "histogram": {str(h): round(w, 2) for h, w in activity.items()},
    }


def get_global_best_send_time() -> Dict:
    """Aggregate across all customers to determine global best hour.
    Weights same as per-customer; confidence is based on concentration.
    """
    session = get_session()
    try:
        weights = defaultdict(float)
        # All orders
        for o in session.query(Order).all():
            if o.created_at:
                weights[_hour_of(o.created_at)] += 2.0
        # All reminders
        for r in session.query(AbandonedReminder).all():
            if r.opened_at:
                weights[_hour_of(r.opened_at)] += 3.0
            if r.clicked_at:
                weights[_hour_of(r.clicked_at)] += 4.0
        if not weights:
            return {"hour": 10, "confidence": 0.6, "histogram": {}}
        best_hour, best_weight = max(weights.items(), key=lambda kv: kv[1])
        total = sum(weights.values()) or 1.0
        confidence = min(0.9, best_weight / total + 0.4)
        return {
            "hour": int(best_hour),
            "confidence": round(confidence, 2),
            "histogram": {str(h): round(w, 2) for h, w in weights.items()},
        }
    finally:
        session.close()


def get_email_timing_stats() -> Dict:
    """System-level stats for email timing engine."""
    session = get_session()
    try:
        customer_count = session.query(Customer).count()
        orders_count = session.query(Order).count()
        reminders_count = session.query(AbandonedReminder).count()
        global_best = get_global_best_send_time()
        return {
            "customers": customer_count,
            "orders": orders_count,
            "reminders": reminders_count,
            "global_best": global_best,
            "generated_at": datetime.now().isoformat(),
        }
    finally:
        session.close()


def recommend_scheduled_times(segment: Optional[str] = None) -> List[Dict]:
    """Recommend a set of hours with reasons.
    Returns a list like [{hour, reason, priority}]
    """
    base = get_global_best_send_time()
    hour = base["hour"]
    return [
        {"hour": hour, "reason": "Global peak engagement", "priority": "HIGH"},
        {"hour": (hour + 3) % 24, "reason": "Secondary window", "priority": "MEDIUM"},
        {"hour": (hour + 8) % 24, "reason": "Late-night audience", "priority": "LOW"},
    ]
