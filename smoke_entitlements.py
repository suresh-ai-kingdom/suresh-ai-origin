import os
from pprint import pprint

# Set enforcement flags for smoke
os.environ['ENFORCE_ENTITLEMENTS'] = 'true'
os.environ['ENFORCE_IDEMPOTENCY'] = 'false'
os.environ['BIND_DOWNLOAD_TOKEN_TO_IP'] = 'false'
os.environ['DOWNLOAD_TOKEN_TTL'] = '900'
os.environ['PLAN_TIER'] = 'pro'

from app import app
from entitlements import generate_download_token, check_entitlement


def status_label(code: int) -> str:
    if code == 402:
        return 'BLOCKED_402'
    elif 200 <= code < 300:
        return 'ALLOWED_2xx'
    elif code == 404:
        return 'ALLOWED_ROUTE_404 (file missing)'  # expected locally without zip files
    else:
        return f'OTHER_{code}'


def smoke_downloads():
    print('\n=== Smoke: Downloads (gated at ingress) ===')
    with app.test_client() as c:
        # 1) Premium without token → 402
        r1 = c.get('/download/pro')
        print('pro without token:', status_label(r1.status_code))

        # 2) Starter (free) without token → allowed (likely 404 due to missing zip)
        r2 = c.get('/download/starter')
        print('starter without token:', status_label(r2.status_code))

        # 3) Premium with signed token → allowed (likely 404)
        token = generate_download_token('pro')
        r3 = c.get(f'/download/pro?token={token}')
        print('pro with token:', status_label(r3.status_code))


def smoke_attribution_thresholds():
    print('\n=== Smoke: Attribution thresholds (80/90/100/110) ===')
    # pro cap = 5000
    cap = 5000
    scenarios = [
        ('80%', int(cap * 0.80)),
        ('90%', int(cap * 0.90)),
        ('100%', int(cap * 1.00)),
        ('110%', int(cap * 1.10)),
    ]
    results = []
    for label, used in scenarios:
        os.environ['PLAN_ATTRIBUTION_RUNS_USED'] = str(used)
        d = check_entitlement('attribution_run', {})
        # summarize
        results.append({'label': label, 'used': used, 'allow': d['allow'], 'reason': d['reason']})
    pprint(results)


if __name__ == '__main__':
    smoke_downloads()
    smoke_attribution_thresholds()
    print('\nDone.')
