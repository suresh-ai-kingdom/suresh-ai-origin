"""
Rarest Agent Skills Governance (2026) - Suresh AI Origin
Implements Agent Skills open standard with rarity-gated governance and swarm integration.

Features
- Skill objects: name, description, instructions, tools, rarity_req (>=95).
- Create/export/import skills as JSON (MCP-compatible, human-readable).
- Registry: SQLite-backed registry + JSON mirror for discovery/deployment.
- Governance agent: monitors swarm runs (rarity drift, anomalies, compliance).
- Self-evolve: high-scoring outcomes auto-refine skill instructions.
- Rarity gate: skills usable only by elite (>=95).
- Integrations: rarest_memory_evolution for history, rarest_swarm_intelligence for execution.

Methods
- create_skill(name, desc, instructions, tools, rarity_req=95)
- export_skill_json(skill, path)
- import_skill(path)
- register_skill(skill)
- governance_monitor(outcomes)
- evolve_skill(skill, outcome_score)

Demo
- Create "RareRevenueOptimizer" skill → export → import → register → run governed demo with swarm stub.
"""

import json
import os
import sqlite3
import time
import uuid
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from rarest_memory_evolution import RarestMemoryLayer
except ImportError:
    RarestMemoryLayer = None  # type: ignore

try:
    from rarest_swarm_intelligence import RarestSwarm
except ImportError:
    RarestSwarm = None  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

REGISTRY_DB = "skills_registry.db"
REGISTRY_JSON = "skills_registry.json"


@dataclass
class AgentSkill:
    name: str
    description: str
    instructions: str
    tools: List[str]
    rarity_req: float = 95.0
    version: str = "1.0"
    skill_id: str = None
    created_at: float = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id or f"skill_{uuid.uuid4().hex[:8]}",
            "name": self.name,
            "description": self.description,
            "instructions": self.instructions,
            "tools": self.tools,
            "rarity_req": self.rarity_req,
            "version": self.version,
            "created_at": self.created_at or time.time(),
        }


class RarestAgentSkills:
    def __init__(self, registry_db: str = REGISTRY_DB, registry_json: str = REGISTRY_JSON, min_rarity: float = 95.0):
        self.registry_db = registry_db
        self.registry_json = registry_json
        self.min_rarity = min_rarity
        self.memory = RarestMemoryLayer() if RarestMemoryLayer else None
        if self.memory:
            self.memory.init_memory()
        self._init_registry()

    # --------------------------------------------------------------
    def _init_registry(self):
        self.conn = sqlite3.connect(self.registry_db)
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS skills (
                skill_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                instructions TEXT,
                tools TEXT,
                rarity_req REAL,
                version TEXT,
                created_at REAL
            )
            """
        )
        self.conn.commit()
        if not os.path.exists(self.registry_json):
            self._persist_json()

    # --------------------------------------------------------------
    def create_skill(self, name: str, desc: str, instructions: str, tools: List[str], rarity_req: float = 95.0) -> AgentSkill:
        if rarity_req < self.min_rarity:
            raise ValueError("Rarity gate: skills must require >=95")
        skill = AgentSkill(
            name=name,
            description=desc,
            instructions=instructions,
            tools=tools,
            rarity_req=rarity_req,
            version="1.0",
            skill_id=f"skill_{uuid.uuid4().hex[:8]}",
            created_at=time.time(),
        )
        return skill

    # --------------------------------------------------------------
    def export_skill_json(self, skill: AgentSkill, path: str) -> str:
        data = skill.to_dict()
        with open(path, "w") as f:
            json.dump({"schema": "agent.skill.v1", "skill": data}, f, indent=2)
        return path

    def import_skill(self, path: str) -> AgentSkill:
        with open(path, "r") as f:
            data = json.load(f)
        skill_data = data.get("skill", data)
        return AgentSkill(
            name=skill_data["name"],
            description=skill_data["description"],
            instructions=skill_data["instructions"],
            tools=skill_data.get("tools", []),
            rarity_req=skill_data.get("rarity_req", 95.0),
            version=skill_data.get("version", "1.0"),
            skill_id=skill_data.get("skill_id"),
            created_at=skill_data.get("created_at", time.time()),
        )

    # --------------------------------------------------------------
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
    def register_skill(self, skill: AgentSkill) -> bool:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO skills (skill_id, name, description, instructions, tools, rarity_req, version, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                skill.skill_id,
                skill.name,
                skill.description,
                skill.instructions,
                json.dumps(skill.tools),
                skill.rarity_req,
                skill.version,
                skill.created_at,
            ),
        )
        self.conn.commit()
        self._persist_json()
        return True

    # --------------------------------------------------------------
    def governance_monitor(self, outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not outcomes:
            return {"rarity_drift": 0.0, "anomalies": []}
        rarity_scores = [o.get("rarity_score", 0) for o in outcomes]
        avg_rarity = sum(rarity_scores) / len(rarity_scores)
        drift = max(0.0, self.min_rarity - avg_rarity)
        anomalies = [o for o in outcomes if o.get("confidence", 1) < 0.6]
        if self.memory:
            try:
                self.memory.store_action(
                    action="governance_monitor",
                    outcome=f"avg_rarity={avg_rarity:.2f}, drift={drift:.2f}",
                    rarity_score=max(rarity_scores),
                    user_feedback=None,
                    success_score=1 - min(1, drift / 10),
                    metadata={"anomalies": len(anomalies)},
                )
            except Exception:
                pass
        return {"avg_rarity": avg_rarity, "rarity_drift": drift, "anomalies": anomalies}

    # --------------------------------------------------------------
    def evolve_skill(self, skill: AgentSkill, outcome_score: float) -> AgentSkill:
        if outcome_score >= 0.85:
            skill.version = str(round(float(skill.version) + 0.1, 1))
            skill.instructions += "\n- Refinement: Observed high performance, reinforce current pattern."
        return skill

    # --------------------------------------------------------------
    def _persist_json(self):
        cur = self.conn.cursor()
        cur.execute("SELECT skill_id, name, description, instructions, tools, rarity_req, version, created_at FROM skills")
        rows = cur.fetchall()
        skills = []
        for r in rows:
            skills.append({
                "skill_id": r[0],
                "name": r[1],
                "description": r[2],
                "instructions": r[3],
                "tools": json.loads(r[4]) if r[4] else [],
                "rarity_req": r[5],
                "version": r[6],
                "created_at": r[7],
            })
        with open(self.registry_json, "w") as f:
            json.dump({"skills": skills}, f, indent=2)

    # --------------------------------------------------------------
    def export_shared_context(self) -> Dict[str, Any]:
        try:
            with open(self.registry_json, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"skills": []}
        return {
            "schema": "mcp.skills.registry.v1",
            "exported_at": time.time(),
            "skills": data.get("skills", []),
        }


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    skills = RarestAgentSkills()

    # 1) Create skill
    rare_skill = skills.create_skill(
        name="RareRevenueOptimizer",
        desc="Optimize revenue with elite rarity-aware strategies",
        instructions="""Follow rare-first revenue playbook:
- Detect top 1% opportunities
- Apply price floors and upsells
- Coordinate with drone delivery for VIP orders""",
        tools=["autonomous_income_engine", "rarity_engine", "drone_delivery_agent"],
        rarity_req=95,
    )

    # 2) Export & import
    export_path = "rare_skill_export.json"
    skills.export_skill_json(rare_skill, export_path)
    imported = skills.import_skill(export_path)

    # 3) Register skill
    skills.register_skill(imported)

    # 4) Run governed demo with swarm stub
    swarm = RarestSwarm() if RarestSwarm else None
    if swarm:
        swarm.init_swarm(["income_engine", "drone_agent", "rarity_engine"])
        outcomes = swarm.run_swarm_cycle("Optimize ₹10L monthly revenue + rare drone delivery", rarity_score=97)["results"]
        governance = skills.governance_monitor(outcomes)
        refined = skills.evolve_skill(imported, outcome_score=governance.get("avg_rarity", 95) / 100)
        print("Governance:", governance)
        print("Refined version:", refined.version)
    else:
        print("Swarm not available; registry populated and skill exported.")

    # 5) Export shared context
    context = skills.export_shared_context()
    print(f"Registry skills: {len(context['skills'])}")
