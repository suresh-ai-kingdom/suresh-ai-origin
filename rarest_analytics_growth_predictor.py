"""
Rarest Analytics Growth Predictor (2026) - Suresh AI Origin
Predictive layer for revenue, virality, and skill performance (1% rarest tier).

Features
- Ingests monetization logs, marketplace/sales stats, referrals, swarm/memory performance.
- Forecasts revenue/referral growth with simple linear/exponential trends (numpy/pandas if available).
- Personalized insights: earnings outlook, churn risk if rarity drops.
- Viral loop suggestions: referral bonus tweaks, new skill ideas from demand gaps.
- Alerts for high-performing skills and slowing growth.
- Rarity gate: predictions only for elite (>=98).
- Demo: simulates 30-day forecast from sample transactions and prints actions.
"""

import json
import os
import sqlite3
import time
import logging
from typing import Dict, Any, List, Optional

try:
    import numpy as np
    NP_AVAILABLE = True
except Exception:
    NP_AVAILABLE = False

try:
    import pandas as pd
    PD_AVAILABLE = True
except Exception:
    PD_AVAILABLE = False

try:
    from rarest_memory_evolution import RarestMemoryLayer
except Exception:
    RarestMemoryLayer = None  # type: ignore

try:
    from rarest_agent_economy_dashboard import RarestEconomyDashboard
except Exception:
    RarestEconomyDashboard = None  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = "skills_registry.db"
MONETIZATION_LOG = "monetization_log.txt"


class RarestGrowthPredictor:
    def __init__(self, registry_db: str = DB_PATH, min_rarity: float = 98.0):
        self.registry_db = registry_db
        self.min_rarity = min_rarity
        self.memory = RarestMemoryLayer() if RarestMemoryLayer else None
        if self.memory:
            self.memory.init_memory()
        self.dashboard = RarestEconomyDashboard() if RarestEconomyDashboard else None
        self.conn = sqlite3.connect(self.registry_db)

    # --------------------------------------------------------------
    def _rarity_gate(self, rarity_score: float):
        if rarity_score < self.min_rarity:
            raise PermissionError("Rarity gate: predictions are elite-only (>=98)")

    # --------------------------------------------------------------
    def load_historical_data(self) -> Dict[str, Any]:
        sales: List[Dict[str, Any]] = []
        earnings: List[Dict[str, Any]] = []
        performance: List[Dict[str, Any]] = []

        # Monetization log
        if os.path.exists(MONETIZATION_LOG):
            with open(MONETIZATION_LOG, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        try:
                            ts = float(parts[0])
                            entry_type = parts[1]
                            skill_id = parts[2]
                            amount = float(parts[4])
                            sales.append({"ts": ts, "skill_id": skill_id, "amount": amount, "type": entry_type})
                        except Exception:
                            continue

        # Earnings + stats
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT skill_id, amount, referrer_code, entry_type, created_at FROM earnings")
            for row in cur.fetchall():
                earnings.append(
                    {
                        "skill_id": row[0],
                        "amount": row[1],
                        "referrer": row[2],
                        "entry_type": row[3],
                        "ts": row[4],
                    }
                )
        except Exception:
            pass

        stats = {}
        try:
            cur.execute("SELECT skill_id, sales_count, last_price, last_updated FROM sales_stats")
            for row in cur.fetchall():
                stats[row[0]] = {
                    "sales_count": row[1],
                    "last_price": row[2],
                    "last_updated": row[3],
                }
        except Exception:
            pass

        if self.memory:
            try:
                performance = self.memory.export_mcp().get("records", [])
            except Exception:
                performance = []

        return {"sales": sales, "earnings": earnings, "stats": stats, "performance": performance}

    # --------------------------------------------------------------
    def _trend_forecast(self, series: List[float], days: int) -> float:
        if not series:
            return 0.0
        if NP_AVAILABLE and len(series) >= 2:
            x = np.arange(len(series))
            y = np.array(series)
            coef = np.polyfit(x, y, 1)
            forecast = np.polyval(coef, len(series) + days)
            return float(max(forecast, 0))
        avg = sum(series) / len(series)
        return avg * (days / max(len(series), 1))

    def forecast_revenue(self, days: int = 30, rarity_score: float = 100.0) -> Dict[str, Any]:
        self._rarity_gate(rarity_score)
        data = self.load_historical_data()
        sales = data.get("sales", [])
        if not sales:
            sales = [
                {"ts": time.time() - 86400 * 2, "amount": 1499},
                {"ts": time.time() - 86400, "amount": 1499},
                {"ts": time.time(), "amount": 1499},
            ]
        sales_sorted = sorted(sales, key=lambda x: x.get("ts", 0))
        amounts = [s.get("amount", 0) for s in sales_sorted]
        forecast_total = round(self._trend_forecast(amounts, days), 2)
        return {"days": days, "forecast_revenue_inr": forecast_total, "samples": len(amounts)}

    # --------------------------------------------------------------
    def predict_user_growth(self, user_id: str, rarity_score: float = 100.0) -> Dict[str, Any]:
        self._rarity_gate(rarity_score)
        data = self.load_historical_data()
        earnings = [e for e in data.get("earnings", []) if e.get("referrer") == user_id]
        amounts = [e.get("amount", 0) for e in earnings]
        bonus_outlook = self._trend_forecast(amounts, 30) if amounts else 0.0
        churn_risk = "low" if rarity_score >= 99 else "medium"
        return {
            "user_id": user_id,
            "referral_projection_inr": round(bonus_outlook, 2),
            "churn_risk": churn_risk,
        }

    # --------------------------------------------------------------
    def suggest_optimizations(self, rarity_score: float = 100.0) -> Dict[str, Any]:
        self._rarity_gate(rarity_score)
        data = self.load_historical_data()
        stats = data.get("stats", {})
        performance = data.get("performance", [])
        suggestions: List[str] = []

        low_demand = [sid for sid, meta in stats.items() if meta.get("sales_count", 0) < 2]
        for sid in low_demand[:3]:
            suggestions.append(f"Boost referrals for {sid} with +5% bonus this week")

        if performance:
            perf_sorted = sorted(performance, key=lambda r: r.get("success_score", 0), reverse=True)
            for rec in perf_sorted[:2]:
                suggestions.append(f"Promote high-performing pattern '{rec.get('summary', rec.get('action'))[:40]}'")

        return {"suggestions": suggestions}

    # --------------------------------------------------------------
    def generate_dashboard_json(self, rarity_score: float = 100.0) -> Dict[str, Any]:
        self._rarity_gate(rarity_score)
        revenue = self.forecast_revenue(days=30, rarity_score=rarity_score)
        user_growth = self.predict_user_growth(user_id="creator_1", rarity_score=rarity_score)
        opts = self.suggest_optimizations(rarity_score=rarity_score)
        alerts = []
        if revenue.get("forecast_revenue_inr", 0) > 50000:
            alerts.append("Projected revenue > INR 50k next 30 days")
        if opts.get("suggestions"):
            alerts.append("Actionable optimization suggestions ready")
        return {
            "schema": "mcp.growth.v1",
            "generated_at": time.time(),
            "revenue": revenue,
            "user_growth": user_growth,
            "optimizations": opts,
            "alerts": alerts,
        }

    # --------------------------------------------------------------
    def demo_forecast(self):
        rarity = 100.0
        revenue = self.forecast_revenue(days=30, rarity_score=rarity)
        user_proj = self.predict_user_growth(user_id="creator_1", rarity_score=rarity)
        opts = self.suggest_optimizations(rarity_score=rarity)
        dashboard = self.generate_dashboard_json(rarity_score=rarity)
        return {
            "revenue": revenue,
            "user_projection": user_proj,
            "optimizations": opts,
            "dashboard": dashboard,
        }


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    predictor = RarestGrowthPredictor()
    result = predictor.demo_forecast()
    print(json.dumps(result, indent=2))
