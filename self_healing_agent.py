"""
Self-healing agent for Suresh AI Origin.

Periodically probes critical endpoints and records health.
If failures exceed threshold, performs recovery actions:
- writes an alert to `data/alerts.jsonl`
- optional email (stubbed)

Run:
    python -m self_healing_agent --base https://sureshaiorigin.com --interval 60
"""

from __future__ import annotations

import argparse
import json
import os
import time
import logging
from typing import List

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALERTS_FILE = os.path.join(os.getcwd(), "data", "alerts.jsonl")


def write_alert(kind: str, info: dict) -> None:
    os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
    rec = {"ts": int(time.time() * 1000), "kind": kind, **info}
    with open(ALERTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def probe_endpoints(base_url: str) -> dict:
    endpoints: List[str] = [
        f"{base_url}/api/rare/stats",
        f"{base_url}/api/rare/destiny-blueprint",
        f"{base_url}/api/rare/consciousness",
        f"{base_url}/api/rare/perfect-timing",
        f"{base_url}/api/rare/market-consciousness",
        f"{base_url}/api/rare/customer-soul",
    ]
    results = {}
    for url in endpoints:
        try:
            # GET for stats, POST with minimal bodies otherwise
            if url.endswith("/stats"):
                r = requests.get(url, timeout=15)
            else:
                r = requests.post(url, json={"probe": True}, timeout=20)
            results[url] = {"status": r.status_code}
        except Exception as e:
            results[url] = {"error": str(e)}
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="Base URL of deployment")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between probes")
    parser.add_argument("--fail-threshold", type=int, default=2, help="Consecutive failures before alert")
    args = parser.parse_args()

    consecutive_failures = 0
    while True:
        results = probe_endpoints(args.base)
        failed = [u for u, r in results.items() if r.get("status", 200) >= 400 or "error" in r]
        if failed:
            consecutive_failures += 1
            logger.warning("Probe failures: %s", failed)
        else:
            consecutive_failures = 0
            logger.info("All probes OK")

        if consecutive_failures >= args.fail_threshold:
            write_alert("probe_failure", {"failed": failed})
            logger.error("Alert written: probe_failure")
            consecutive_failures = 0  # reset after alert

        time.sleep(args.interval)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
