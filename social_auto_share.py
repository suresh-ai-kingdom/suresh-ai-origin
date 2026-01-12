import time
from typing import List, Dict


def _fallback_signals():
    return {
        'starter': {'demand_index': 0.5, 'conversion_rate': 0.3},
        'pro': {'demand_index': 0.6, 'conversion_rate': 0.4},
        'premium': {'demand_index': 0.4, 'conversion_rate': 0.2},
    }


def _get_signals(days_back: int = 30) -> Dict[str, Dict]:
    try:
        from market_intelligence import compute_signals
        return compute_signals(days_back)
    except Exception:
        return _fallback_signals()


_PLATFORMS = ['Twitter', 'LinkedIn', 'Instagram']
_PEAK_HOURS = [9, 12, 18]  # local hours for posting


def generate_posts(days_back: int = 30) -> List[Dict]:
    signals = _get_signals(days_back)
    # Rank products by demand and conversion
    ranked = sorted(
        signals.items(),
        key=lambda kv: (kv[1].get('demand_index', 0), kv[1].get('conversion_rate', 0)),
        reverse=True,
    )
    posts: List[Dict] = []
    for product, s in ranked:
        # Simple message templates
        if s.get('conversion_rate', 0) >= 0.5:
            msg = f"Customers love our {product} pack — limited-time bonus inside!"
        elif s.get('demand_index', 0) >= 0.6:
            msg = f"Hot demand for {product}! Grab yours today."
        else:
            msg = f"Discover the {product} pack — practical prompts and workflows."
        posts.append({
            'product': product,
            'message': msg,
            'tags': ['#AI', '#Productivity', '#SureshAIOrigin'],
        })
    return posts


def generate_schedule(days_back: int = 30) -> List[Dict]:
    posts = generate_posts(days_back)
    schedule: List[Dict] = []
    # Assign posts across platforms and peak hours for next few days
    now = time.time()
    day_seconds = 86400
    idx = 0
    for d in range(3):  # next 3 days
        for hr in _PEAK_HOURS:
            for platform in _PLATFORMS:
                post = posts[idx % len(posts)] if posts else {'product': 'starter', 'message': 'Check our packs'}
                scheduled_at = now + d * day_seconds + hr * 3600
                schedule.append({
                    'platform': platform,
                    'scheduled_at': scheduled_at,
                    'local_hour': hr,
                    'product': post['product'],
                    'message': post['message'],
                })
                idx += 1
    return schedule
