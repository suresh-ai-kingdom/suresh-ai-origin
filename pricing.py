import time
from typing import Dict, List, Tuple
from models import get_engine, get_session, Order
from utils import _get_db_url


BASE_PRICES_RUPEES: Dict[str, int] = {
    'starter': 99,
    'pro': 499,
    'premium': 999,
}


def _recent_window_seconds(days: int = 30) -> float:
    return days * 86400.0


def _get_product_metrics(days: int = 30) -> Dict[str, Dict[str, float]]:
    """Aggregate simple demand and conversion metrics for each product.

    Returns a dict keyed by product with:
    - created_count
    - paid_count
    - conversion_rate (paid/created)
    - revenue_paise (sum of paid order amounts)
    """
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    since = time.time() - _recent_window_seconds(days)
    rows = session.query(Order).filter(Order.created_at >= since).all()
    session.close()

    metrics: Dict[str, Dict[str, float]] = {}
    for r in rows:
        prod = r.product or 'unknown'
        m = metrics.setdefault(prod, {
            'created_count': 0.0,
            'paid_count': 0.0,
            'conversion_rate': 0.0,
            'revenue_paise': 0.0,
        })
        m['created_count'] += 1.0
        if (r.status or '').lower() == 'paid':
            m['paid_count'] += 1.0
            m['revenue_paise'] += float(r.amount or 0)
    # finalize conversion
    for prod, m in metrics.items():
        created = m['created_count']
        paid = m['paid_count']
        m['conversion_rate'] = (paid / created) if created > 0 else 0.0
    # ensure all known products are present
    for prod in BASE_PRICES_RUPEES.keys():
        metrics.setdefault(prod, {
            'created_count': 0.0,
            'paid_count': 0.0,
            'conversion_rate': 0.0,
            'revenue_paise': 0.0,
        })
    return metrics


def compute_base_price(product: str) -> int:
    """Return baseline price in rupees for a product."""
    return BASE_PRICES_RUPEES.get(product, 299)


def compute_dynamic_price(product: str, days: int = 30, bounds: Tuple[float, float] = (0.8, 1.25)) -> int:
    """Compute a dynamic price suggestion in rupees.

    Adjust based on recent demand and conversion rates; clamp within bounds of base price.
    """
    base = float(compute_base_price(product))
    metrics = _get_product_metrics(days)
    # demand index across products
    max_created = max((m['created_count'] for m in metrics.values()), default=0.0)
    created = metrics.get(product, {}).get('created_count', 0.0)
    demand_idx = (created / max_created) if max_created > 0 else 0.5
    # conversion rate
    conv = metrics.get(product, {}).get('conversion_rate', 0.0)
    conv = conv if conv > 0 else 0.3  # default reasonable baseline
    # adjustment: demand (±0.2), conversion (±0.1)
    adj = 1.0 + 0.2 * (demand_idx - 0.5) + 0.1 * (conv - 0.5)
    # clamp
    min_f, max_f = bounds
    factor = max(min_f, min(max_f, adj))
    price = int(round(base * factor))
    # avoid zero
    return max(price, 1)


def simulate_price_scenarios(product: str, days: int = 30) -> List[Dict[str, float]]:
    """Simulate simple price scenarios with estimated conversion & revenue impact.

    Uses a basic price elasticity model with elasticity -1.2 against baseline conversion.
    """
    base_price = float(compute_base_price(product))
    metrics = _get_product_metrics(days)
    base_conv = metrics.get(product, {}).get('conversion_rate', 0.3) or 0.3
    elasticity = -1.2
    scenarios: List[Dict[str, float]] = []
    for factor in (0.9, 1.0, 1.1):
        price = base_price * factor
        # conv_est = base_conv * (price/base) ** elasticity
        conv_est = base_conv * (price / base_price) ** elasticity
        conv_est = max(0.05, min(0.95, conv_est))
        # estimated revenue per 100 site visitors
        revenue = price * conv_est * 100.0
        scenarios.append({
            'factor': round(factor, 2),
            'price_rupees': round(price, 2),
            'estimated_conversion': round(conv_est, 4),
            'estimated_revenue_per_100': round(revenue, 2),
        })
    return scenarios


def pricing_stats(days: int = 30) -> Dict[str, Dict[str, float]]:
    """Return per-product metrics and baseline prices."""
    metrics = _get_product_metrics(days)
    for prod in metrics.keys():
        metrics[prod]['base_price_rupees'] = float(compute_base_price(prod))
    return metrics


def all_dynamic_prices(days: int = 30) -> Dict[str, int]:
    """Return dynamic prices for all known products."""
    return {p: compute_dynamic_price(p, days=days) for p in BASE_PRICES_RUPEES.keys()}
