"""
Self-healing autonomous agent for SURESH AI ORIGIN platform health.

Features:
  - Probes key endpoints (rare features, webhooks) every N seconds
  - Logs to `data/health_log.jsonl` with timestamp, endpoint, status, latency
  - Simple recovery: backoff + retry, alert on repeated failures
  - CLI: python self_healing_agent.py --base https://sureshaiorigin.com --interval 60

Run locally:
    python self_healing_agent.py --base http://localhost:5000 --interval 30

Production (Render):
    python self_healing_agent.py --base https://sureshaiorigin.com --interval 60
"""

from __future__ import annotations

import argparse
import json
import os
import time
import logging
import threading
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

HEALTH_LOG_FILE = os.path.join(os.getcwd(), "data", "health_log.jsonl")
ALERTS_FILE = os.path.join(os.getcwd(), "data", "alerts.jsonl")




def write_event(file_path: str, kind: str, info: Dict) -> None:
    """Write JSON event to file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        event = {
            "ts": int(time.time() * 1000),
            "kind": kind,
            **info,
        }
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning(f"Failed to write event to {file_path}: {e}")


def probe_endpoint(url: str, method: str = "GET", timeout: int = 10) -> Dict:
    """Probe a single endpoint."""
    if not requests:
        logger.error("requests not installed; skipping probe")
        return {"success": False, "error": "requests not installed"}

    start = time.time()
    try:
        if method == "GET":
            resp = requests.get(url, timeout=timeout)
        elif method == "POST":
            resp = requests.post(url, json={"test": True}, timeout=timeout)
        else:
            return {"success": False, "error": f"unknown method {method}"}

        latency_ms = int((time.time() - start) * 1000)
        return {
            "success": 200 <= resp.status_code < 300,
            "status_code": resp.status_code,
            "latency_ms": latency_ms,
            "error": None,
        }
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        return {
            "success": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "error": str(e),
        }


def probe_endpoints(base_url: str) -> Dict[str, Dict]:
    """Probe all critical rare feature endpoints."""
    endpoints = {
        "rare_stats": f"{base_url}/api/rare/stats",
        "rare_destiny": f"{base_url}/api/rare/destiny-blueprint",
        "rare_consciousness": f"{base_url}/api/rare/consciousness",
        "rare_timing": f"{base_url}/api/rare/perfect-timing",
        "rare_market": f"{base_url}/api/rare/market-consciousness",
        "rare_soul": f"{base_url}/api/rare/customer-soul",
        "webhook_make": f"{base_url}/hooks/make",
        "webhook_zapier": f"{base_url}/hooks/zapier",
    }

    results = {}
    for name, url in endpoints.items():
        method = "GET" if "stats" in name else "POST"
        probe = probe_endpoint(url, method=method)
        results[name] = probe
        write_event(
            HEALTH_LOG_FILE,
            "probe",
            {
                "endpoint": name,
                "url": url,
                **probe,
            },
        )

    return results
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
