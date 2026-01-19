"""
Rarest Agent Economy Dashboard (2026) - Suresh AI Origin
Elite real-time observability for the 1% rarest agent economics layer.

Features
- Pulls marketplace listings/sales from skills_registry.db + monetization_log.txt.
- Integrates rarest_memory_evolution (performance history) and rarest_swarm_intelligence (swarm health).
- KPIs: total skills, sales volume (INR), top skills by price/performance, swarm health, commission earned.
- Alerts: rarity drift >5%, new listing > INR 5000, governance anomalies (unverified/pending).
- Rarity gate: access only for elite (>=95) with optional VIP flag.
- Outputs JSON API (Flask if available) plus simple HTML summary and console loop.
- Demo loop: updates every poll interval (default 30s) showing summary + alerts.
"""

import json
import os
import sqlite3
import time
import threading
import logging
from typing import Dict, List, Optional, Any

try:
    import pandas as pd
    PD_AVAILABLE = True
except Exception:
    PD_AVAILABLE = False

try:
    from flask import Flask, jsonify, request
except Exception:
    Flask = None  # type: ignore
    jsonify = None  # type: ignore
    request = None  # type: ignore

try:
    from rarest_agent_marketplace_verification import RarestMarketplace
except Exception:
    RarestMarketplace = None  # type: ignore

try:
    from rarest_memory_evolution import RarestMemoryLayer
    MEMORY_AVAILABLE = True
except Exception:
    RarestMemoryLayer = None  # type: ignore
    MEMORY_AVAILABLE = False

try:
    from rarest_swarm_intelligence import RarestSwarm
    SWARM_AVAILABLE = True
except Exception:
    RarestSwarm = None  # type: ignore
    SWARM_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class RarestEconomyDashboard:
    def __init__(
        self,
        registry_db: str = "skills_registry.db",
        monetization_log: str = "monetization_log.txt",
        min_rarity: float = 95.0,
        poll_interval: int = 30,
    ):
        self.registry_db = registry_db
        self.monetization_log = monetization_log
        self.min_rarity = min_rarity
        self.poll_interval = poll_interval
        self.marketplace = RarestMarketplace() if RarestMarketplace else None
        self.memory = RarestMemoryLayer() if MEMORY_AVAILABLE else None
        if self.memory:
            self.memory.init_memory()
        self.swarm = RarestSwarm() if SWARM_AVAILABLE else None
        if self.swarm:
            try:
                self.swarm.init_swarm()
            except Exception:
                pass
        self.last_metrics: Dict[str, Any] = {}

    # --------------------------------------------------------------
    def check_gate(self, rarity_score: float, vip: bool = False):
        if rarity_score < self.min_rarity:
            raise PermissionError("Rarity gate: access requires rarity >=95")
        if not vip and rarity_score < 98:
            logger.info("VIP tier suggested for full detail")

    # --------------------------------------------------------------
    def fetch_marketplace_data(self) -> Dict[str, Any]:
        listings: List[Dict[str, Any]] = []
        conn = sqlite3.connect(self.registry_db)
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT skill_id, name, owner, price_inr, version, verification_status, rarity_req, created_at FROM marketplace"
            )
            rows = cur.fetchall()
            for r in rows:
                listings.append(
                    {
                        "skill_id": r[0],
                        "name": r[1],
                        "owner": r[2],
                        "price_inr": r[3],
                        "version": r[4],
                        "verification_status": r[5],
                        "rarity_req": r[6],
                        "created_at": r[7],
                    }
                )
        except Exception as exc:
            logger.warning(f"Marketplace read failed: {exc}")
        finally:
            conn.close()

        sales_log = self._load_sales_log()

        performance = []
        if self.memory:
            try:
                performance = self.memory.export_mcp().get("records", [])
            except Exception as exc:
                logger.debug(f"Memory export skipped: {exc}")

        swarm_state: Dict[str, Any] = {}
        if self.swarm:
            try:
                swarm_state = {
                    "agents_active": len(self.swarm.agents),
                    "agents": list(self.swarm.agents.keys()),
                }
            except Exception:
                swarm_state = {}

        return {
            "listings": listings,
            "sales_log": sales_log,
            "performance": performance,
            "swarm_state": swarm_state,
        }

    # --------------------------------------------------------------
    def _load_sales_log(self) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []
        if not os.path.exists(self.monetization_log):
            return entries
        with open(self.monetization_log, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5 and parts[1] == "BUY":
                    try:
                        ts = float(parts[0])
                        skill_id = parts[2]
                        amount = float(parts[4])
                        entries.append({"ts": ts, "skill_id": skill_id, "amount_inr": amount})
                    except Exception:
                        continue
        return entries

    # --------------------------------------------------------------
    def calculate_kpis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        listings = [l for l in data.get("listings", []) if l.get("rarity_req", 0) >= self.min_rarity]
        sales = data.get("sales_log", [])
        performance = data.get("performance", [])
        swarm_state = data.get("swarm_state", {})

        total_listed = len(listings)
        sales_volume = sum(s.get("amount_inr", 0) for s in sales)
        commission = sales_volume * 0.10
        recent_tx = sorted(sales, key=lambda x: x.get("ts", 0), reverse=True)[:5]

        top_price = sorted(listings, key=lambda x: x.get("price_inr", 0), reverse=True)[:5]

        perf_df = None
        perf_top: List[Dict[str, Any]] = []
        if PD_AVAILABLE and performance:
            perf_df = pd.DataFrame(performance)
            if "success_score" in perf_df.columns:
                perf_top = perf_df.sort_values(by="success_score", ascending=False).head(5).to_dict(orient="records")
        elif performance:
            perf_top = sorted(performance, key=lambda x: x.get("success_score", 0), reverse=True)[:5]

        avg_rarity = 0.0
        if performance:
            avg_rarity = sum(p.get("rarity_score", 0) for p in performance) / max(len(performance), 1)

        avg_success = 0.0
        if performance:
            avg_success = sum(p.get("success_score", 0) for p in performance) / max(len(performance), 1)

        evolution_delta = 0.0
        if perf_top:
            first = perf_top[0].get("success_score", 0)
            last = perf_top[-1].get("success_score", first)
            evolution_delta = first - last

        swarm_health = {
            "agents_active": swarm_state.get("agents_active", 0),
            "agents": swarm_state.get("agents", []),
            "avg_rarity": avg_rarity,
            "avg_success": avg_success,
            "evolution_delta": evolution_delta,
        }

        kpis = {
            "total_skills_listed": total_listed,
            "sales_volume_inr": sales_volume,
            "commission_inr": commission,
            "top_price_skills": top_price,
            "top_performance": perf_top,
            "swarm_health": swarm_health,
            "recent_transactions": recent_tx,
        }
        return kpis

    # --------------------------------------------------------------
    def generate_alerts(self, kpis: Dict[str, Any]) -> List[str]:
        alerts: List[str] = []
        current_avg = kpis.get("swarm_health", {}).get("avg_rarity", 0)
        last_avg = self.last_metrics.get("swarm_health", {}).get("avg_rarity", current_avg)
        if abs(current_avg - last_avg) > 5:
            alerts.append("Rarity drift detected >5")

        if any(item.get("price_inr", 0) > 5000 for item in kpis.get("top_price_skills", [])):
            alerts.append("New high-value listing above INR 5000")

        for item in kpis.get("top_price_skills", []):
            if item.get("verification_status") not in ("verified", "approved"):
                alerts.append(f"Governance pending for {item.get('name')}")
                break

        return alerts

    # --------------------------------------------------------------
    def render_dashboard_json(self, kpis: Dict[str, Any], alerts: List[str]) -> Dict[str, Any]:
        payload = {
            "generated_at": time.time(),
            "kpis": kpis,
            "alerts": alerts,
        }
        self.last_metrics = kpis
        return payload

    def render_html_summary(self, kpis: Dict[str, Any], alerts: List[str]) -> str:
        body = ["<h2>Rarest Economy Dashboard</h2>"]
        body.append(f"<p>Total skills listed: {kpis.get('total_skills_listed', 0)}</p>")
        body.append(f"<p>Sales volume (INR): {kpis.get('sales_volume_inr', 0):.2f}</p>")
        body.append(f"<p>Commission earned (INR): {kpis.get('commission_inr', 0):.2f}</p>")
        swarm = kpis.get("swarm_health", {})
        body.append(
            f"<p>Swarm health: agents {swarm.get('agents_active', 0)}, avg rarity {swarm.get('avg_rarity', 0):.2f}, evolution delta {swarm.get('evolution_delta', 0):.2f}</p>"
        )
        if alerts:
            body.append("<ul>")
            for a in alerts:
                body.append(f"<li>{a}</li>")
            body.append("</ul>")
        return "\n".join(body)

    # --------------------------------------------------------------
    def run_once(self, rarity_score: float = 100.0, vip: bool = True) -> Dict[str, Any]:
        self.check_gate(rarity_score, vip)
        data = self.fetch_marketplace_data()
        kpis = self.calculate_kpis(data)
        alerts = self.generate_alerts(kpis)
        return self.render_dashboard_json(kpis, alerts)

    def gateway_payload(self, rarity_score: float = 100.0, vip: bool = True) -> Dict[str, Any]:
        """Helper for ai_gateway integration to fetch a fresh dashboard snapshot."""
        return self.run_once(rarity_score, vip)

    def start_polling(self, rarity_score: float = 100.0, vip: bool = True, iterations: int = 2):
        def loop():
            for _ in range(iterations):
                payload = self.run_once(rarity_score, vip)
                logger.info(json.dumps(payload, indent=2))
                time.sleep(self.poll_interval)
        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        return thread


# ----------------------------------------------------------------------
# Flask API (optional)
# ----------------------------------------------------------------------
app = Flask(__name__) if Flask else None
_dashboard = RarestEconomyDashboard()

if app:
    @app.route("/economy/summary", methods=["GET"])  # type: ignore
    def economy_summary():
        rarity = float(request.args.get("rarity", 0)) if request else 0
        vip = request.args.get("vip", "false").lower() == "true" if request else False
        try:
            payload = _dashboard.run_once(rarity_score=rarity, vip=vip)
            return jsonify(payload)
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403
        except Exception as exc:
            logger.exception(exc)
            return jsonify({"error": "internal error"}), 500

    @app.route("/economy/html", methods=["GET"])  # type: ignore
    def economy_html():
        rarity = float(request.args.get("rarity", 0)) if request else 0
        vip = request.args.get("vip", "false").lower() == "true" if request else False
        try:
            payload = _dashboard.run_once(rarity_score=rarity, vip=vip)
            html = _dashboard.render_html_summary(payload.get("kpis", {}), payload.get("alerts", []))
            return html
        except PermissionError as exc:
            return f"Access denied: {exc}", 403
        except Exception:
            return "Error", 500


# ----------------------------------------------------------------------
# Demo loop (console)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    interval = int(os.getenv("DASHBOARD_POLL_INTERVAL", "30"))
    dashboard = RarestEconomyDashboard(poll_interval=interval)
    logger.info("Starting economy dashboard demo loop (Ctrl+C to exit)")
    t = dashboard.start_polling(rarity_score=100, vip=True, iterations=2)
    t.join()
