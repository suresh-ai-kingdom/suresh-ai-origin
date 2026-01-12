"""Growth Forecast Engine

Provides scenario-based growth forecasts over a specified horizon using historical signals:
- Orders: counts and amounts per day
- Customers: first purchase dates

No external dependencies; simple deterministic math models.
"""
import time
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

from models import get_session, Order, Customer


def _date_of(ts: float) -> datetime:
    try:
        return datetime.fromtimestamp(ts).date()
    except Exception:
        return datetime.utcnow().date()


def get_daily_metrics(days: int = 180) -> Dict[str, List[int]]:
    """Aggregate daily orders and new customers for the past `days`.
    Returns dict with keys: orders_count, customers_count.
    """
    session = get_session()
    try:
        today = datetime.utcnow().date()
        start = today - timedelta(days=days)
        # Initialize arrays
        days_list = [start + timedelta(days=i) for i in range(days)]
        idx = {d: i for i, d in enumerate(days_list)}
        orders_count = [0] * days
        customers_count = [0] * days
        # Orders
        for o in session.query(Order).all():
            if o.created_at:
                d = _date_of(o.created_at)
                if d in idx:
                    orders_count[idx[d]] += 1
        # Customers (first purchase)
        for c in session.query(Customer).all():
            if c.first_purchase_at:
                d = _date_of(c.first_purchase_at)
                if d in idx:
                    customers_count[idx[d]] += 1
        return {"orders_count": orders_count, "customers_count": customers_count}
    finally:
        session.close()


def _trend(value_series: List[int]) -> float:
    """Simple trend measure: last 30 days avg vs prior 30 days avg ratio."""
    if not value_series:
        return 1.0
    n = len(value_series)
    w = min(30, n // 2)
    if w == 0:
        return 1.0
    recent = sum(value_series[-w:]) / max(w, 1)
    prior = sum(value_series[-2*w:-w]) / max(w, 1) if n >= 2*w else sum(value_series[:-w]) / max(n-w, 1)
    if prior <= 0:
        return 1.0 + (recent > 0) * 0.2
    return max(0.6, min(1.6, recent / prior))


def forecast_scenarios(days_history: int = 180, horizon_days: int = 180) -> Dict:
    """Compute baseline, conservative, aggressive scenarios for orders & customers.
    Returns dict with scenario arrays for daily forecast and summary growth percentages.
    """
    metrics = get_daily_metrics(days_history)
    orders_series = metrics["orders_count"]
    customers_series = metrics["customers_count"]

    # Base levels: recent averages
    base_orders = max(1.0, sum(orders_series[-30:]) / max(1, min(30, len(orders_series)))) if orders_series else 1.0
    base_customers = max(1.0, sum(customers_series[-30:]) / max(1, min(30, len(customers_series)))) if customers_series else 1.0

    # Trend multipliers
    t_orders = _trend(orders_series)
    t_customers = _trend(customers_series)

    # Scenario growth multipliers per day
    scenarios = {
        "conservative": 0.995,   # slight decline or flat
        "baseline": 1.002,       # slight growth
        "aggressive": 1.010,     # stronger growth
    }

    def _build_series(base: float, trend: float, mult: float) -> List[float]:
        values = []
        level = max(0.5, base * trend)
        for _ in range(horizon_days):
            level = level * mult
            values.append(round(level, 2))
        return values

    out = {}
    for name, mult in scenarios.items():
        out[name] = {
            "orders": _build_series(base_orders, t_orders, mult),
            "customers": _build_series(base_customers, t_customers, mult),
        }

    def _growth_pct(series: List[float]) -> float:
        if not series:
            return 0.0
        start = series[0]
        end = series[-1]
        if start <= 0:
            return 0.0
        return round(((end - start) / start) * 100.0, 1)

    summary = {name: {
        "orders_growth_pct": _growth_pct(data["orders"]),
        "customers_growth_pct": _growth_pct(data["customers"]),
    } for name, data in out.items()}

    return {"scenarios": out, "summary": summary, "generated_at": datetime.utcnow().isoformat()}


def forecast_summary() -> Dict:
    """Short summary selecting recommended scenario based on recent trend."""
    fc = forecast_scenarios()
    # Choose scenario by average of order/customer trend (heuristic)
    cons = fc["summary"]["conservative"]["orders_growth_pct"] + fc["summary"]["conservative"]["customers_growth_pct"]
    base = fc["summary"]["baseline"]["orders_growth_pct"] + fc["summary"]["baseline"]["customers_growth_pct"]
    aggr = fc["summary"]["aggressive"]["orders_growth_pct"] + fc["summary"]["aggressive"]["customers_growth_pct"]
    if aggr - base > 10:
        chosen = "aggressive"
    elif base - cons > 5:
        chosen = "baseline"
    else:
        chosen = "conservative"
    return {"recommended": chosen, "summary": fc["summary"], "generated_at": fc["generated_at"]}
