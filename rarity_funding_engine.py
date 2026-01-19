"""
Rarity Funding Engine - Suresh AI Origin
Simulates elite ($20B) funding raises with rarity gating and global investor routing.

Key features:
- Dynamic valuation sims starting at $250B baseline.
- Rarity-gated projects: only >90 score proceed to funding.
- Geo-targeted investors (Qatar sovereign, MGX-like mega funds, US/EU/IN VCs).
- MRR integration: pulls simulated revenue jumps from subscriptions_mrr.py if available.
- Produces funding report and appends to production_dashboard.json.

Methods:
- score_project(project: dict) -> dict
- global_investors(target_regions: list[str]) -> list[dict]
- simulate_raise(project: dict, target_amount_b: float = 20.0, region_hint=None)
- iterate_funding(projects: list[dict], iterations: int = 3)

Dependencies: pandas
"""

import json
import math
import time
import uuid
import random
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Optional imports
try:
    import subscriptions_mrr  # type: ignore
    HAS_MRR = True
except ImportError:
    subscriptions_mrr = None  # type: ignore
    HAS_MRR = False

PRODUCTION_DASHBOARD = "production_dashboard.json"


@dataclass
class ProjectProfile:
    project_id: str
    name: str
    sector: str
    region: str
    mrr_usd: float
    growth_rate_pct: float
    rarity_score: float
    tier: str = "one_percent"


@dataclass
class FundingRound:
    round_id: str
    amount_b: float
    post_money_b: float
    dilution_pct: float
    lead_investor: str
    region: str
    timestamp: float


class RarityFundingEngine:
    def __init__(self, base_valuation_b: float = 250.0, reliability_target: float = 99.2):
        self.base_valuation_b = base_valuation_b
        self.reliability_target = reliability_target
        self.history: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    def score_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Compute rarity score for funding eligibility."""
        words = len(project.get("vision", "").split())
        sector = project.get("sector", "general").lower()
        geo = project.get("region", "global").lower()
        mrr = float(project.get("mrr_usd", 0))
        growth = float(project.get("growth_rate_pct", 0))

        # Base rarity from narrative + sector heat
        sector_bonus = {
            "agi": 12,
            "space": 10,
            "quantum": 9,
            "defense": 8,
            "ai": 6,
        }.get(sector, 3)
        geo_bonus = 5 if geo in ["qatar", "me", "mena"] else 2
        narrative = min(30, words * 0.4)
        mrr_bonus = min(25, math.log1p(max(mrr, 1)) * 3)
        growth_bonus = min(15, growth * 0.6)

        rarity = 20 + sector_bonus + geo_bonus + narrative + mrr_bonus + growth_bonus
        rarity = min(100.0, rarity)

        return {
            "rarity_score": rarity,
            "sector": sector,
            "region": geo,
            "mrr_usd": mrr,
            "growth_rate_pct": growth,
            "fundable": rarity >= 90,
        }

    # ------------------------------------------------------------------
    def global_investors(self, target_regions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Return geo-targeted investor mocks (Qatar/MGX-like, US/EU/IN)."""
        regions = target_regions or ["qatar", "us", "eu", "in"]
        investors = []
        for region in regions:
            region_lower = region.lower()
            if region_lower in ["qatar", "mena", "me"]:
                investors.append({
                    "name": "Qatar Sovereign Catalyst",
                    "region": "Qatar",
                    "ticket_b": 5.0,
                    "speed_days": 10,
                })
                investors.append({
                    "name": "MGX Global Growth",
                    "region": "MENA",
                    "ticket_b": 3.0,
                    "speed_days": 12,
                })
            if region_lower in ["us", "na"]:
                investors.append({
                    "name": "Sequoia Apex",
                    "region": "US",
                    "ticket_b": 2.0,
                    "speed_days": 15,
                })
            if region_lower in ["eu", "emea"]:
                investors.append({
                    "name": "Index Quantum",
                    "region": "EU",
                    "ticket_b": 1.5,
                    "speed_days": 18,
                })
            if region_lower in ["in", "apac"]:
                investors.append({
                    "name": "Peak India Ultra",
                    "region": "IN",
                    "ticket_b": 1.0,
                    "speed_days": 14,
                })
        return investors

    # ------------------------------------------------------------------
    def _pull_mrr(self, project: Dict[str, Any]) -> float:
        """Fetch MRR from subscriptions_mrr if available; else simulate."""
        if HAS_MRR and hasattr(subscriptions_mrr, "get_mrr_snapshot"):
            try:
                snap = subscriptions_mrr.get_mrr_snapshot(project_id=project.get("id"))
                return float(snap.get("mrr_usd", 0))
            except Exception as exc:
                logger.warning(f"MRR fetch failed: {exc}")
        # simulate: random between $500M and $2B
        return random.uniform(500_000_000, 2_000_000_000)

    # ------------------------------------------------------------------
    def simulate_raise(
        self,
        project: Dict[str, Any],
        target_amount_b: float = 20.0,
        region_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Simulate a $20B raise with dynamic valuation and dilution."""
        scored = self.score_project(project)
        rarity = scored["rarity_score"]
        if not scored["fundable"]:
            return {"accepted": False, "reason": "rarity_below_90", **scored}

        mrr = self._pull_mrr(project)
        growth = max(0.15, project.get("growth_rate_pct", 0.25))

        # Build a valuation trajectory DataFrame
        df = pd.DataFrame({
            "round": ["pre", "raise"],
            "valuation_b": [self.base_valuation_b, None],
            "mrr_usd": [mrr, mrr * (1 + growth)],
        })
        df.loc[df["round"] == "raise", "valuation_b"] = (
            self.base_valuation_b
            * (1 + (rarity - 90) * 0.02)
            * (1 + growth)
            + target_amount_b
        )

        post_money_b = float(df.loc[df["round"] == "raise", "valuation_b"].iloc[0])
        dilution_pct = round((target_amount_b / max(post_money_b, 1e-6)) * 100, 2)

        investors = self.global_investors(target_regions=[region_hint] if region_hint else None)
        lead = investors[0]["name"] if investors else "Global Syndicate"

        round_info = FundingRound(
            round_id=f"raise_{uuid.uuid4().hex[:6]}",
            amount_b=target_amount_b,
            post_money_b=post_money_b,
            dilution_pct=dilution_pct,
            lead_investor=lead,
            region=region_hint or "global",
            timestamp=time.time(),
        )

        report = {
            "accepted": True,
            "project_id": project.get("id", uuid.uuid4().hex[:6]),
            "name": project.get("name", "Unnamed Project"),
            "rarity_score": rarity,
            "mrr_usd": mrr,
            "growth_rate_pct": growth * 100 if growth < 1 else growth,
            "round": asdict(round_info),
            "valuation_table": df.to_dict(orient="records"),
            "investors": investors,
        }

        self._append_dashboard(report)
        self.history.append(report)
        return report

    # ------------------------------------------------------------------
    def iterate_funding(self, projects: List[Dict[str, Any]], iterations: int = 3) -> List[Dict[str, Any]]:
        """Run multiple funding simulations; stop early if target met."""
        results = []
        for i in range(iterations):
            for proj in projects:
                res = self.simulate_raise(proj)
                results.append(res)
            # Optional early stop if majority accepted
            accepted = [r for r in results if r.get("accepted")]
            if accepted and (len(accepted) / max(len(results), 1)) > 0.6:
                break
        return results

    # ------------------------------------------------------------------
    def _append_dashboard(self, report: Dict[str, Any]):
        """Write funding report into production_dashboard.json."""
        try:
            dashboard = {}
            try:
                with open(PRODUCTION_DASHBOARD, "r") as f:
                    dashboard = json.load(f)
            except FileNotFoundError:
                dashboard = {}

            funding_section = dashboard.get("funding_reports", [])
            funding_section.append({
                "timestamp": time.time(),
                "project": report.get("name"),
                "round": report.get("round"),
                "rarity_score": report.get("rarity_score"),
                "mrr_usd": report.get("mrr_usd"),
                "post_money_b": report.get("round", {}).get("post_money_b"),
            })
            dashboard["funding_reports"] = funding_section

            # Reliability snapshot
            dashboard["funding_engine"] = {
                "reliability_target": self.reliability_target,
                "last_rarity": report.get("rarity_score"),
                "reports": len(funding_section),
            }

            with open(PRODUCTION_DASHBOARD, "w") as f:
                json.dump(dashboard, f, indent=2)
            logger.info(f"📊 Funding report appended to {PRODUCTION_DASHBOARD}")
        except Exception as exc:
            logger.warning(f"Dashboard append failed: {exc}")


# ----------------------------------------------------------------------
# Demo usage
# ----------------------------------------------------------------------
if __name__ == "__main__":
    engine = RarityFundingEngine()

    sample_project = {
        "id": "proj_elon_world",
        "name": "Elon-Scale World Model",
        "sector": "agi",
        "region": "qatar",
        "mrr_usd": 750_000_000,
        "growth_rate_pct": 0.35,
        "vision": "Build an interplanetary AGI supply chain with quantum-grade autonomy and rarest tier economics.",
    }

    print("=== Single Raise Simulation ===")
    result = engine.simulate_raise(sample_project, target_amount_b=20.0, region_hint="qatar")
    print(json.dumps({k: v for k, v in result.items() if k != "valuation_table"}, indent=2))

    print("\n=== Iterative Funding (2 iterations) ===")
    proj2 = {"id": "proj_in", "name": "India AI Rail", "sector": "ai", "region": "in", "mrr_usd": 600_000_000, "growth_rate_pct": 0.28, "vision": "AI rail for Bharat"}
    res_iter = engine.iterate_funding([sample_project, proj2], iterations=2)
    print(f"Simulations: {len(res_iter)} | accepted: {sum(1 for r in res_iter if r.get('accepted'))}")
