"""
Rarest Agent Launchpad (2026) - Suresh AI Origin
One-click creation and deployment of elite agent skills/mini-swarms for the 1% rarest tier.

Pipeline
1) Input goal/name/tools -> create skill JSON (rarity-gated >=95)
2) Sign + verify via Ed25519 (marketplace key)
3) Governance auto-approve (rarity + anomaly scan)
4) Publish to marketplace (price auto-suggested by complexity)
5) Deploy to swarm (auto-add agent)
6) Auto-scale suggestion based on demand

Methods
- create_from_goal(goal_str, tools=None)
- sign_and_verify(skill)
- governance_auto_approve(skill, verified)
- publish_to_marketplace(skill, price=None)
- deploy_to_swarm(skill, goal=None)
- auto_scale_check(usage_count, threshold=5)
- run_one_click(goal, tools=None)

Demo goal: "Create rare skill for auto-optimizing drone routes in high-traffic areas"
Outputs: skill created → signed → approved → published at auto-suggested price (e.g., ₹1499) → deployed → scaled if high demand.
"""

import json
import os
import time
import uuid
import logging
from typing import Dict, List, Optional, Any

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except Exception:
    Ed25519PublicKey = None  # type: ignore

try:
    from flask import Flask, request, jsonify
except Exception:
    Flask = None  # type: ignore
    request = None  # type: ignore
    jsonify = None  # type: ignore

try:
    from rarest_agent_skills_governance import AgentSkill, RarestAgentSkills
except Exception:
    AgentSkill = None  # type: ignore
    RarestAgentSkills = None  # type: ignore

try:
    from rarest_agent_marketplace_verification import RarestMarketplace
except Exception:
    RarestMarketplace = None  # type: ignore

try:
    from rarest_swarm_intelligence import RarestSwarm
except Exception:
    RarestSwarm = None  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class RarestLaunchpad:
    def __init__(self, min_rarity: float = 95.0, monetization_log: str = "monetization_log.txt"):
        self.min_rarity = min_rarity
        self.skills = RarestAgentSkills() if RarestAgentSkills else None
        self.market = RarestMarketplace() if RarestMarketplace else None
        self.swarm = RarestSwarm() if RarestSwarm else None
        self.monetization_log = monetization_log
        if self.swarm:
            try:
                self.swarm.init_swarm()
            except Exception:
                pass

    # --------------------------------------------------------------
    def _rarity_gate(self, rarity_score: float):
        if rarity_score < self.min_rarity:
            raise PermissionError("Rarity gate: only elite (>=95) may launch")

    # --------------------------------------------------------------
    def create_from_goal(self, goal_str: str, tools: Optional[List[str]] = None, rarity_req: float = 95.0) -> AgentSkill:
        if not self.skills:
            raise RuntimeError("Skills manager unavailable")
        tools = tools or ["rarity_engine", "neural_layers", "drone_delivery_agent"]
        name = f"Rare-{goal_str[:18].strip().replace(' ', '-')}-{uuid.uuid4().hex[:4]}"
        desc = goal_str
        instructions = (
            f"Goal: {goal_str}\n"
            "- Enforce rarity-first actions\n"
            "- Use listed tools with safety and governance\n"
            "- Return confidence and rationale per step"
        )
        skill = self.skills.create_skill(name=name, desc=desc, instructions=instructions, tools=tools, rarity_req=rarity_req)
        # Register immediately for discovery/deployment
        try:
            self.skills.register_skill(skill)
        except Exception as exc:
            logger.debug(f"Skill registration skipped: {exc}")
        return skill

    # --------------------------------------------------------------
    def sign_and_verify(self, skill: AgentSkill) -> Dict[str, Any]:
        if not self.market:
            raise RuntimeError("Marketplace unavailable for signing")
        skill_json = json.dumps(skill.to_dict(), sort_keys=True)
        signature = self.market.signing_key.sign(skill_json.encode()).hex()
        verified = False
        if Ed25519PublicKey:
            try:
                pk = Ed25519PublicKey.from_public_bytes(bytes.fromhex(self.market.public_key_hex))
                pk.verify(bytes.fromhex(signature), skill_json.encode())
                verified = True
            except Exception as exc:
                logger.warning(f"Signature verify failed: {exc}")
        # Secondary verify using marketplace API if available
        if hasattr(self.market, "verify_skill") and not verified:
            try:
                verified = bool(self.market.verify_skill(skill_json, signature, self.market.public_key_hex))
            except Exception:
                pass
        return {"signature": signature, "public_key_hex": self.market.public_key_hex, "verified": verified, "skill_json": skill_json}

    # --------------------------------------------------------------
    def governance_auto_approve(self, skill: AgentSkill, verified: bool) -> Dict[str, Any]:
        status = "pending"
        anomalies: List[str] = []
        if skill.rarity_req < self.min_rarity:
            status = "rejected"
            anomalies.append("rarity_below_gate")
        if not verified:
            anomalies.append("signature_unverified")
        # Simple anomaly scan on instructions
        if "exploit" in skill.instructions.lower():
            anomalies.append("unsafe_keyword")
        if not anomalies and verified:
            status = "approved"
        return {"status": status, "anomalies": anomalies}

    # --------------------------------------------------------------
    def _suggest_price(self, skill: AgentSkill) -> int:
        complexity = len(skill.instructions.split()) + len(skill.tools) * 40
        base = 999
        uplift = min(4000, complexity * 5)
        return int(base + uplift)

    def publish_to_marketplace(self, skill: AgentSkill, price: Optional[int] = None) -> Dict[str, Any]:
        if not self.market:
            raise RuntimeError("Marketplace unavailable")
        price_inr = price or self._suggest_price(skill)
        listing = self.market.publish_skill(skill, price_inr=price_inr, owner="suresh-ai")
        return listing

    # --------------------------------------------------------------
    def deploy_to_swarm(self, skill: AgentSkill, goal: Optional[str] = None) -> Dict[str, Any]:
        if not self.swarm:
            return {"deployed": False, "reason": "swarm_unavailable"}
        goal = goal or f"Deploy {skill.name}"
        # Add as a lightweight agent
        self.swarm.agents[skill.name] = {"skill": skill.to_dict(), "mock": True}
        self.swarm.specialties[skill.name] = "rare_skill"
        try:
            outcome = self.swarm.run_swarm_cycle(goal, rarity_score=skill.rarity_req)
        except Exception as exc:
            logger.debug(f"Swarm run skipped: {exc}")
            outcome = {"results": []}
        return {"deployed": True, "agents": list(self.swarm.agents.keys()), "outcome": outcome}

    # --------------------------------------------------------------
    def auto_scale_check(self, usage_count: int, threshold: int = 5) -> Dict[str, Any]:
        scale = usage_count > threshold
        suggestion = "stable" if not scale else "Spin up duplicate nodes for surge"
        return {"scale": scale, "suggestion": suggestion, "usage": usage_count, "threshold": threshold}

    # --------------------------------------------------------------
    def _log_monetization(self, skill_id: str, price_inr: float):
        try:
            with open(self.monetization_log, "a") as f:
                f.write(f"{time.time()} LAUNCH {skill_id} INR {price_inr}\n")
        except Exception:
            logger.debug("Monetization log skipped")

    # --------------------------------------------------------------
    def run_one_click(self, goal: str, tools: Optional[List[str]] = None, rarity_score: float = 100.0) -> Dict[str, Any]:
        self._rarity_gate(rarity_score)
        skill = self.create_from_goal(goal, tools)
        signed = self.sign_and_verify(skill)
        governance = self.governance_auto_approve(skill, signed.get("verified", False))
        listing = self.publish_to_marketplace(skill, price=self._suggest_price(skill))
        # Governance acknowledgment in marketplace
        try:
            _ = self.market.governance_approve(skill.skill_id)
        except Exception:
            pass
        self._log_monetization(skill.skill_id, listing.get("price_inr", 0))
        deployed = self.deploy_to_swarm(skill, goal)
        scale = self.auto_scale_check(usage_count=7, threshold=5)
        payload = {
            "skill": skill.to_dict(),
            "signature": signed,
            "governance": governance,
            "listing": listing,
            "deployment": deployed,
            "scaling": scale,
        }
        return payload


# ----------------------------------------------------------------------
# Flask endpoint for dashboard trigger
# ----------------------------------------------------------------------
app = Flask(__name__) if Flask else None
_launchpad = RarestLaunchpad()

if app:
    @app.route("/economy/launch", methods=["POST"])  # type: ignore
    def launch_skill():
        if not request:
            return ("Request unavailable", 500)
        body = request.get_json(silent=True) or {}
        goal = body.get("goal") or request.args.get("goal") or ""
        tools = body.get("tools") or []
        rarity = float(body.get("rarity", request.args.get("rarity", 0)))
        try:
            result = _launchpad.run_one_click(goal=goal, tools=tools, rarity_score=rarity)
            return jsonify(result)
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403
        except Exception as exc:
            logger.exception(exc)
            return jsonify({"error": "internal error"}), 500


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    demo_goal = "Create rare skill for auto-optimizing drone routes in high-traffic areas"
    launchpad = RarestLaunchpad()
    result = launchpad.run_one_click(goal=demo_goal, tools=["drone_delivery_agent", "rarity_engine"], rarity_score=100)
    print(json.dumps(result, indent=2))

    # Optional: start Flask server if desired
    if app and os.getenv("LAUNCHPAD_SERVE", "false").lower() == "true":
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8002")), debug=False)
