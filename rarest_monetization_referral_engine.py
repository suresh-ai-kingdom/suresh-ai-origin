"""
Rarest Monetization & Referral Engine (2026) - Suresh AI Origin
Elite revenue automation for the 1% rarest agent economy.

Features
- Marketplace commissions: apply 20-30% cut on sales; log to earnings + monetization log.
- Referrals: track referrer code, credit 20-30% recurring on referred purchases/usage.
- Dynamic pricing: adjust skill price based on rarity/performance/demand.
- Creator royalties: micro-credit when skills run in swarm usage.
- Integrations: marketplace (on buy), dashboard (earnings view), launchpad (usage tracking), memory for performance signals.
- Rarity gate: monetization actions only for elite (>=98).
- Demo: simulate three transactions with referral and royalties.
"""

import json
import os
import sqlite3
import time
import random
import logging
from typing import Dict, Any, Optional

try:
    from rarest_agent_marketplace_verification import RarestMarketplace
except Exception:
    RarestMarketplace = None  # type: ignore

try:
    from rarest_agent_economy_dashboard import RarestEconomyDashboard
except Exception:
    RarestEconomyDashboard = None  # type: ignore

try:
    from rarest_memory_evolution import RarestMemoryLayer
except Exception:
    RarestMemoryLayer = None  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = "skills_registry.db"
MONETIZATION_LOG = "monetization_log.txt"


class RarestMonetizationEngine:
    def __init__(self, registry_db: str = DB_PATH, min_rarity: float = 98.0):
        self.registry_db = registry_db
        self.min_rarity = min_rarity
        self.conn = sqlite3.connect(self.registry_db)
        self._init_tables()
        self.market = RarestMarketplace() if RarestMarketplace else None
        self.dashboard = RarestEconomyDashboard() if RarestEconomyDashboard else None
        self.memory = RarestMemoryLayer() if RarestMemoryLayer else None
        if self.memory:
            self.memory.init_memory()

    # --------------------------------------------------------------
    def _rarity_gate(self, rarity_score: float):
        if rarity_score < self.min_rarity:
            raise PermissionError("Rarity gate: monetization is elite-only (>=98)")

    def _init_tables(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id TEXT,
                amount REAL,
                referrer_code TEXT,
                entry_type TEXT,
                metadata TEXT,
                created_at REAL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sales_stats (
                skill_id TEXT PRIMARY KEY,
                sales_count INTEGER DEFAULT 0,
                last_price REAL DEFAULT 0,
                last_updated REAL
            )
            """
        )
        self.conn.commit()

    # --------------------------------------------------------------
    def calculate_sale_commission(self, price_inr: float, rate: Optional[float] = None) -> float:
        rate = rate if rate is not None else random.uniform(0.20, 0.30)
        return round(price_inr * rate, 2)

    def apply_referral_bonus(self, referrer_code: str, amount_inr: float) -> float:
        bonus_rate = random.uniform(0.20, 0.30)
        bonus = round(amount_inr * bonus_rate, 2)
        self._log_earning(skill_id="referral_pool", amount=bonus, referrer=referrer_code, entry_type="referral")
        return bonus

    def dynamic_price_adjust(self, skill_id: str) -> float:
        cur = self.conn.cursor()
        cur.execute("SELECT sales_count, last_price FROM sales_stats WHERE skill_id=?", (skill_id,))
        row = cur.fetchone()
        sales = row[0] if row else 0
        last_price = row[1] if row else 1499
        perf_boost = 0
        if self.memory:
            try:
                records = [r for r in self.memory.records if r.metadata.get("skill_id") == skill_id]
                if records:
                    avg_success = sum(r.success_score for r in records) / len(records)
                    perf_boost = (avg_success - 0.8) * 500
            except Exception:
                perf_boost = 0
        demand_uplift = min(1000, sales * 25)
        new_price = max(999, last_price + perf_boost + demand_uplift)
        cur.execute(
            "INSERT OR REPLACE INTO sales_stats (skill_id, sales_count, last_price, last_updated) VALUES (?, ?, ?, ?)",
            (skill_id, sales, new_price, time.time()),
        )
        self.conn.commit()
        return round(new_price, 2)

    def credit_creator_usage(self, skill_id: str, creator: str, base_amount: float = 10.0) -> float:
        royalty = round(base_amount * random.uniform(0.5, 1.5), 2)
        self._log_earning(skill_id=skill_id, amount=royalty, referrer=creator, entry_type="royalty")
        return royalty

    # --------------------------------------------------------------
    def _log_earning(self, skill_id: str, amount: float, referrer: Optional[str], entry_type: str, metadata: Optional[Dict[str, Any]] = None):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO earnings (skill_id, amount, referrer_code, entry_type, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (skill_id, amount, referrer, entry_type, json.dumps(metadata or {}), time.time()),
        )
        self.conn.commit()
        try:
            with open(MONETIZATION_LOG, "a") as f:
                f.write(f"{time.time()} {entry_type.upper()} {skill_id} INR {amount}\n")
        except Exception:
            logger.debug("Monetization log skip")

    def log_transaction(self, skill_id: str, price_inr: float, referrer_code: Optional[str], rarity_score: float):
        self._rarity_gate(rarity_score)
        commission = self.calculate_sale_commission(price_inr)
        self._log_earning(skill_id, commission, referrer=None, entry_type="commission")
        referral_bonus = self.apply_referral_bonus(referrer_code, price_inr) if referrer_code else 0
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO sales_stats (skill_id, sales_count, last_price, last_updated) VALUES (?, 0, ?, ?)",
            (skill_id, price_inr, time.time()),
        )
        cur.execute("UPDATE sales_stats SET sales_count = sales_count + 1 WHERE skill_id=?", (skill_id,))
        self.conn.commit()
        return {"commission_inr": commission, "referral_bonus_inr": referral_bonus}

    # --------------------------------------------------------------
    def demo_transactions(self):
        rarity = 100.0
        skill_id = "skill_demo_1499"
        creator = "creator_1"
        price = 1499
        tx1 = self.log_transaction(skill_id, price, referrer_code="REF123", rarity_score=rarity)
        new_price = self.dynamic_price_adjust(skill_id)
        royalty = self.credit_creator_usage(skill_id, creator)
        tx2 = self.log_transaction(skill_id, price, referrer_code=None, rarity_score=rarity)
        tx3 = self.log_transaction(skill_id, price, referrer_code="REF999", rarity_score=rarity)
        return {
            "tx1": tx1,
            "tx2": tx2,
            "tx3": tx3,
            "new_price": new_price,
            "royalty": royalty,
        }


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    engine = RarestMonetizationEngine()
    result = engine.demo_transactions()
    print(json.dumps(result, indent=2))
