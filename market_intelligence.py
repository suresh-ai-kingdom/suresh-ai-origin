import time
from typing import Dict, List
from models import get_engine, get_session, Order
from utils import _get_db_url
from pricing import all_dynamic_prices


def _recent_orders(days: int = 90):
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    since = time.time() - days * 86400.0
    rows = session.query(Order).filter(Order.created_at >= since).all()
    session.close()
    return rows


def compute_signals(days: int = 90) -> Dict[str, Dict]:
    """Compute simple market signals per product.

    Returns keys per product: demand_index, conversion_rate, avg_price_rupees, revenue_rupees.
    """
    rows = _recent_orders(days)
    prices = all_dynamic_prices(days=days)
    by_product: Dict[str, Dict] = {}
    for r in rows:
        p = r.product or 'unknown'
        d = by_product.setdefault(p, {
            'created': 0,
            'paid': 0,
            'revenue_paise': 0,
        })
        d['created'] += 1
        if (r.status or '').lower() == 'paid':
            d['paid'] += 1
            d['revenue_paise'] += int(r.amount or 0)
    # finalize
    signals: Dict[str, Dict] = {}
    max_created = max((d['created'] for d in by_product.values()), default=0)
    for prod, d in by_product.items():
        created = d['created']
        paid = d['paid']
        demand_index = (created / max_created) if max_created > 0 else 0.5
        conv = (paid / created) if created > 0 else 0.0
        avg_price = float(prices.get(prod, 299))
        revenue_rupees = d['revenue_paise'] / 100.0
        signals[prod] = {
            'demand_index': round(demand_index, 3),
            'conversion_rate': round(conv, 3),
            'avg_price_rupees': round(avg_price, 2),
            'revenue_rupees': round(revenue_rupees, 2),
        }
    # include products with zero recent orders
    for prod in prices.keys():
        signals.setdefault(prod, {
            'demand_index': 0.0,
            'conversion_rate': 0.0,
            'avg_price_rupees': float(prices.get(prod, 299)),
            'revenue_rupees': 0.0,
        })
    return signals


def competitor_price_index(days: int = 90) -> Dict[str, float]:
    """Crude competitor index: 1.0 means parity; <1 cheaper than market; >1 more expensive.
    Uses baseline 1.0 from base prices and compares dynamic prices.
    """
    prices = all_dynamic_prices(days=days)
    # assume parity baseline at starter=99, pro=499, premium=999
    base = {'starter': 99, 'pro': 499, 'premium': 999}
    return {p: round(prices.get(p, base[p]) / float(base[p]), 3) for p in base.keys()}


def generate_insights(days: int = 90) -> List[Dict]:
    """Generate actionable market insights and recommendations."""
    sig = compute_signals(days)
    idx = competitor_price_index(days)
    out: List[Dict] = []
    for prod, s in sig.items():
        demand = s['demand_index']
        conv = s['conversion_rate']
        price_idx = idx.get(prod, 1.0)
        recommendation = None
        priority = 'MEDIUM'
        if demand >= 0.7 and conv >= 0.5:
            recommendation = 'Consider small price increase or bundle offer'
            priority = 'HIGH'
        elif conv < 0.2 and price_idx > 1.05:
            recommendation = 'Reduce price or add limited-time discount'
            priority = 'HIGH'
        elif demand < 0.3:
            recommendation = 'Boost visibility: social ads or influencer post'
            priority = 'MEDIUM'
        else:
            recommendation = 'Monitor performance; test new messaging'
        out.append({
            'product': prod,
            'demand_index': demand,
            'conversion_rate': conv,
            'competitor_index': price_idx,
            'recommendation': recommendation,
            'priority': priority,
        })
    # sort by priority then demand
    order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    out.sort(key=lambda x: (order.get(x['priority'], 9), -x['demand_index']))
    return out


def market_summary(days: int = 90) -> Dict:
    sig = compute_signals(days)
    insights = generate_insights(days)
    top = insights[0] if insights else None
    total_rev = sum(s['revenue_rupees'] for s in sig.values())
    return {
        'signals': sig,
        'insights': insights,
        'top_recommendation': top,
        'total_revenue_rupees': round(total_rev, 2),
        'generated_at': time.time(),
    }
import time
from typing import Dict, List
from models import get_engine, get_session, Order
from utils import _get_db_url


def _window_orders(days_back: int) -> List[Order]:
    engine = get_engine(_get_db_url())
    session = get_session(engine)
    since = time.time() - (days_back * 86400.0)
    rows = session.query(Order).filter(Order.created_at >= since).all()
    session.close()
    return rows


def analyze_market_trends(days_back: int = 90) -> Dict:
    """Compute simple market trends: product revenue share and momentum."""
    rows = _window_orders(days_back)
    totals: Dict[str, int] = {}
    counts: Dict[str, int] = {}
    for r in rows:
        if (r.status or '').lower() == 'paid':
            totals[r.product] = totals.get(r.product, 0) + int(r.amount or 0)
            counts[r.product] = counts.get(r.product, 0) + 1
    total_rev = sum(totals.values()) or 1
    share = {p: round(v / total_rev * 100, 2) for p, v in totals.items()}
    conv = {p: round(counts.get(p, 0) / max(counts.get(p, 0) + 1, 1), 2) for p in totals.keys()}  # proxy
    # Momentum: compare first half vs second half of window
    if not rows:
        momentum = {}
    else:
        mid = time.time() - (days_back * 86400.0) / 2
        first_totals: Dict[str, int] = {}
        second_totals: Dict[str, int] = {}
        for r in rows:
            if (r.status or '').lower() == 'paid':
                bucket = second_totals if r.created_at >= mid else first_totals
                bucket[r.product] = bucket.get(r.product, 0) + int(r.amount or 0)
        momentum = {}
        for p in set(list(first_totals.keys()) + list(second_totals.keys())):
            f = first_totals.get(p, 0)
            s = second_totals.get(p, 0)
            momentum[p] = round(((s - f) / max(f, 1)) * 100, 2) if f > 0 else (100.0 if s > 0 else 0.0)
    top_products = sorted(share.items(), key=lambda x: x[1], reverse=True)
    return {
        'revenue_share_percent': share,
        'momentum_percent': momentum,
        'top_products': top_products[:3],
        'generated_at': time.time(),
    }


def competitor_insights() -> Dict:
    """Simulate competitor pricing and positioning."""
    # Static competitor benchmarks per product
    competitor_prices = {
        'starter': 109,
        'pro': 549,
        'premium': 1049,
    }
    # Our current dynamic prices may differ
    try:
        from pricing import all_dynamic_prices
        ours = all_dynamic_prices(days=90)
    except Exception:
        ours = {'starter': 99, 'pro': 499, 'premium': 999}
    comparison = {}
    for p in ['starter', 'pro', 'premium']:
        our_price = ours.get(p, 0)
        comp_price = competitor_prices.get(p, 0)
        advantage = round(comp_price - our_price, 2)
        positioning = 'VALUE' if our_price < comp_price else 'PREMIUM' if our_price > comp_price else 'PARITY'
        comparison[p] = {
            'our_price': our_price,
            'competitor_price': comp_price,
            'price_advantage': advantage,
            'positioning': positioning,
        }
    return {'comparison': comparison, 'generated_at': time.time()}


def sentiment_proxy(days_back: int = 90) -> Dict:
    """Proxy for product sentiment based on conversion and repeat orders."""
    rows = _window_orders(days_back)
    created: Dict[str, int] = {}
    paid: Dict[str, int] = {}
    for r in rows:
        created[r.product] = created.get(r.product, 0) + 1
        if (r.status or '').lower() == 'paid':
            paid[r.product] = paid.get(r.product, 0) + 1
    sentiment = {}
    for p in set(list(created.keys()) + list(paid.keys())):
        conv = (paid.get(p, 0) / max(created.get(p, 0), 1))
        score = round(min(1.0, 0.5 + conv), 2)  # base 0.5 plus conversion
        sentiment[p] = {'score': score, 'conversion_rate': round(conv, 3)}
    return {'sentiment': sentiment, 'generated_at': time.time()}


def market_insights_summary(days_back: int = 90) -> Dict:
    trends = analyze_market_trends(days_back)
    comps = competitor_insights()
    senti = sentiment_proxy(days_back)
    return {
        'trends': trends,
        'competitors': comps,
        'sentiment': senti,
        'generated_at': time.time(),
    }
