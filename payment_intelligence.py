import time
from typing import Dict, List
from models import get_engine, get_session, Order, Payment
from utils import _get_db_url, reconcile_orders


def _window(days_back: int):
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    since = time.time() - days_back * 86400.0
    orders = session.query(Order).filter(Order.created_at >= since).all()
    payments = session.query(Payment).filter(Payment.received_at >= since).all()
    session.close()
    return orders, payments


def compute_payment_metrics(days_back: int = 90) -> Dict:
    orders, payments = _window(days_back)
    created = len(orders)
    paid = sum(1 for o in orders if (o.status or '').lower() == 'paid')
    pay_rate = round((paid / max(created, 1)) * 100.0, 2)
    # capture latency in hours for paid orders
    latencies = []
    for o in orders:
        if o.paid_at and o.created_at:
            latencies.append(max(0.0, (o.paid_at - o.created_at) / 3600.0))
    avg_latency_hours = round(sum(latencies) / max(len(latencies), 1), 2)
    # failed candidates: orders not paid
    failed = created - paid
    # retry candidates: unpaid orders with at least one payment recorded
    report = reconcile_orders()
    retry_candidates = report.get('candidates', [])
    return {
        'orders_created': created,
        'orders_paid': paid,
        'pay_rate_percent': pay_rate,
        'avg_capture_latency_hours': avg_latency_hours,
        'failed_orders': failed,
        'retry_candidates': len(retry_candidates),
        'payments_received': len(payments),
        'generated_at': time.time(),
    }


def failed_payment_reasons(days_back: int = 90) -> Dict[str, int]:
    """Parse payment payloads to tally failure reasons if present.
    Expects JSON-like payload text containing a 'reason' key; otherwise counts as 'unknown'.
    """
    _, payments = _window(days_back)
    import json
    reasons: Dict[str, int] = {}
    for p in payments:
        try:
            payload = json.loads(p.payload or '{}')
            reason = payload.get('reason') or payload.get('error_reason') or 'unknown'
        except Exception:
            reason = 'unknown'
        reasons[reason] = reasons.get(reason, 0) + 1
    return reasons


def payment_insights(days_back: int = 90) -> List[Dict]:
    metrics = compute_payment_metrics(days_back)
    reasons = failed_payment_reasons(days_back)
    out: List[Dict] = []
    # Heuristics
    if metrics['pay_rate_percent'] < 60.0:
        out.append({'priority': 'HIGH', 'message': 'Low pay rate; simplify checkout and add more payment options'})
    if metrics['avg_capture_latency_hours'] > 24.0:
        out.append({'priority': 'MEDIUM', 'message': 'High capture latency; send immediate confirmation and retry guidance'})
    if reasons.get('unknown', 0) > 0 and metrics['failed_orders'] > 0:
        out.append({'priority': 'MEDIUM', 'message': 'Investigate failure logs; instrument error reasons in payment payloads'})
    if metrics['retry_candidates'] > 0:
        out.append({'priority': 'MEDIUM', 'message': 'Enable smart retries and fallback to alternative methods (UPI/Card/NetBanking)'})
    if not out:
        out.append({'priority': 'LOW', 'message': 'Payments healthy; continue monitoring'})
    # sort by priority
    order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    out.sort(key=lambda x: order.get(x['priority'], 9))
    return out


def dashboard_summary(days_back: int = 90) -> Dict:
    return {
        'metrics': compute_payment_metrics(days_back),
        'reasons': failed_payment_reasons(days_back),
        'insights': payment_insights(days_back),
        'generated_at': time.time(),
    }
