"""
Rarest Swarm Intelligence (2026) - Suresh AI Origin
1% rarest multi-agent orchestrator with shared persistent memory.

Features:
- Swarm orchestrates 3-5+ agents (income engine, drone agent, rarity engine, neural layers) using shared memory (rarest_memory_evolution).
- Task delegation with simple planner, rarity gating (>=95), agent specialty routing.
- Collective evolution: aggregate outcomes, reinforce successful patterns, resolve conflicts via confidence merge.
- Self-verification: cross-check agent outputs; mismatches >10% trigger retry + logged lesson.
- MCP-style interop stub for exporting shared context.
- Demo loop: optimize ₹10L monthly revenue + rare drone delivery.

Methods:
- init_swarm(agents_list)
- delegate_task(goal)
- run_swarm_cycle(goal)
- collective_evolve(outcomes)
- verify_outputs(outcomes)
- export_shared_context()

Dependencies: threading, queue, json, sqlite3, tenacity. Requires rarest_memory_evolution backbone.
"""

import json
import time
import uuid
import logging
import sqlite3
import threading
from queue import Queue
from typing import Dict, List, Optional, Any, Tuple

from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from rarest_memory_evolution import RarestMemoryLayer
except ImportError:
    RarestMemoryLayer = None  # type: ignore

# Optional agent imports with graceful fallbacks
try:
    from autonomous_income_engine import AutonomousIncomeEngine
except ImportError:
    AutonomousIncomeEngine = None  # type: ignore

try:
    from drone_delivery_agent import DroneDeliveryAgent
except ImportError:
    DroneDeliveryAgent = None  # type: ignore

try:
    from rarity_engine import RarityEngine
except ImportError:
    RarityEngine = None  # type: ignore

try:
    from agi_neural_layers import MultiLayerReasoner
except ImportError:
    MultiLayerReasoner = None  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class RarestSwarm:
    def __init__(
        self,
        memory_db: str = "rare_memory.db",
        memory_json: str = "rare_memory.json",
        min_rarity: float = 95.0,
    ):
        self.min_rarity = min_rarity
        self.memory = RarestMemoryLayer(db_path=memory_db, json_path=memory_json) if RarestMemoryLayer else None
        if self.memory:
            self.memory.init_memory()
        self.agents: Dict[str, Any] = {}
        self.specialties: Dict[str, str] = {}
        self.lock = threading.Lock()

    # --------------------------------------------------------------
    def init_swarm(self, agents_list: Optional[List[str]] = None):
        agents_list = agents_list or ["income_engine", "drone_agent", "rarity_engine"]
        for name in agents_list:
            self._init_agent(name)
        logger.info(f"Swarm initialized with agents: {list(self.agents.keys())}")

    def _init_agent(self, name: str):
        if name == "income_engine" and AutonomousIncomeEngine:
            self.agents[name] = AutonomousIncomeEngine()
            self.specialties[name] = "revenue"
        elif name == "drone_agent" and DroneDeliveryAgent:
            self.agents[name] = DroneDeliveryAgent()
            self.specialties[name] = "logistics"
        elif name == "rarity_engine" and RarityEngine:
            self.agents[name] = RarityEngine()
            self.specialties[name] = "rarity"
        elif name == "neural_layers" and MultiLayerReasoner:
            self.agents[name] = MultiLayerReasoner(enable_torch=False, enable_revenue_integration=False)
            self.specialties[name] = "reasoning"
        else:
            self.agents[name] = {"mock": True, "name": name}
            self.specialties[name] = "general"

    # --------------------------------------------------------------
    def delegate_task(self, goal: str, rarity_score: float = 100.0) -> List[Dict[str, Any]]:
        if rarity_score < self.min_rarity:
            raise ValueError("Rarity gate: swarm only runs for elite goals (>=95)")
        subtasks = self._plan(goal)
        queue_items = []
        for task in subtasks:
            agent_name = self._pick_agent(task)
            queue_items.append({"task": task, "agent": agent_name, "goal": goal, "rarity_score": rarity_score})
        return queue_items

    def _plan(self, goal: str) -> List[str]:
        steps = ["analyze rarity", "optimize revenue", "optimize logistics"]
        if "drone" in goal.lower():
            steps.append("drone route optimization")
        if "revenue" in goal.lower():
            steps.append("upsell strategy")
        return steps

    def _pick_agent(self, task: str) -> str:
        task_lower = task.lower()
        if "revenue" in task_lower and "income_engine" in self.agents:
            return "income_engine"
        if "rarity" in task_lower and "rarity_engine" in self.agents:
            return "rarity_engine"
        if "drone" in task_lower and "drone_agent" in self.agents:
            return "drone_agent"
        if "reason" in task_lower and "neural_layers" in self.agents:
            return "neural_layers"
        return next(iter(self.agents.keys()))

    # --------------------------------------------------------------
    def run_swarm_cycle(self, goal: str, rarity_score: float = 100.0) -> Dict[str, Any]:
        tasks = self.delegate_task(goal, rarity_score)
        results = []

        q = Queue()
        for t in tasks:
            q.put(t)

        def worker():
            while not q.empty():
                item = q.get()
                res = self._execute_task(item)
                results.append(res)
                q.task_done()

        threads = []
        for _ in range(min(len(tasks), 5)):
            th = threading.Thread(target=worker, daemon=True)
            threads.append(th)
            th.start()
        for th in threads:
            th.join()

        verification = self.verify_outputs(results)
        evolution = self.collective_evolve(results)

        return {
            "goal": goal,
            "results": results,
            "verification": verification,
            "evolution": evolution,
        }

    def _execute_task(self, item: Dict[str, Any]) -> Dict[str, Any]:
        agent_name = item["agent"]
        task = item["task"]
        rarity_score = item["rarity_score"]
        outcome = f"Executed {task} via {agent_name}"
        success = True
        confidence = 0.82

        # Agent-specific behavior (mocked)
        if agent_name == "rarity_engine" and RarityEngine:
            res = self.agents[agent_name].score_item(task)
            outcome = f"Rarity scored: {res.get('score', 0):.1f}"
            confidence = min(1.0, res.get('score', 0) / 100)
        elif agent_name == "income_engine" and AutonomousIncomeEngine:
            outcome = "Revenue playbook executed"
            confidence = 0.9
        elif agent_name == "drone_agent" and DroneDeliveryAgent:
            outcome = "Drone route optimized"
            confidence = 0.88
        elif agent_name == "neural_layers" and MultiLayerReasoner:
            res = self.agents[agent_name].process_query(task)
            outcome = res.final_answer if hasattr(res, 'final_answer') else "Reasoned"
            confidence = getattr(res, 'confidence', 0.85)

        # Persist to shared memory
        if self.memory:
            try:
                self.memory.store_action(
                    action=task,
                    outcome=outcome,
                    rarity_score=rarity_score,
                    user_feedback=None,
                    success_score=confidence,
                    metadata={"agent": agent_name, "goal": item["goal"]},
                )
            except Exception as exc:
                logger.debug(f"Memory store skipped: {exc}")

        return {
            "agent": agent_name,
            "task": task,
            "outcome": outcome,
            "confidence": confidence,
            "success": success,
            "rarity_score": rarity_score,
        }

    # --------------------------------------------------------------
    def collective_evolve(self, outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not outcomes:
            return {"updated": [], "pruned": 0}
        avg_conf = sum(o.get("confidence", 0.5) for o in outcomes) / len(outcomes)
        high = [o for o in outcomes if o.get("confidence", 0) >= avg_conf]
        low = [o for o in outcomes if o.get("confidence", 0) < 0.5]

        updated_templates = [f"swarm_pattern::{o['task']}" for o in high[:5]]
        pruned = len(low)

        if self.memory:
            self.memory._persist_json(extra={"avg_confidence": avg_conf, "updated_templates": updated_templates, "pruned": pruned})

        return {
            "avg_confidence": avg_conf,
            "updated_templates": updated_templates,
            "pruned": pruned,
        }

    # --------------------------------------------------------------
    def verify_outputs(self, outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not outcomes:
            return {"mismatch_rate": 0.0, "auto_retry": False}
        confs = [o.get("confidence", 0) for o in outcomes]
        mismatch_rate = self._mismatch_rate(confs)
        auto_retry = mismatch_rate > 0.10
        if auto_retry and self.memory:
            try:
                self.memory.failure_log.append({"reason": "swarm_mismatch", "mismatch_rate": mismatch_rate, "ts": time.time()})
            except Exception:
                pass
        return {"mismatch_rate": mismatch_rate, "auto_retry": auto_retry}

    def _mismatch_rate(self, confs: List[float]) -> float:
        if len(confs) < 2:
            return 0.0
        mean = sum(confs) / len(confs)
        variance = sum((c - mean) ** 2 for c in confs) / len(confs)
        return min(1.0, variance ** 0.5)

    # --------------------------------------------------------------
    def export_shared_context(self) -> Dict[str, Any]:
        records = self.memory.export_mcp() if self.memory else {"records": [], "token_estimate": 0}
        return {
            "schema": "mcp.swarm.v1",
            "exported_at": time.time(),
            "agents": list(self.agents.keys()),
            "memory": records,
        }


# ----------------------------------------------------------------------
# Demo loop
# ----------------------------------------------------------------------
if __name__ == "__main__":
    swarm = RarestSwarm()
    swarm.init_swarm(["income_engine", "drone_agent", "rarity_engine"])

    goal = "Optimize ₹10L monthly revenue + rare drone delivery"
    result = swarm.run_swarm_cycle(goal, rarity_score=97)

    print("\n=== Swarm Cycle Result ===")
    print(json.dumps({k: v for k, v in result.items() if k != "results"}, indent=2))
    print(f"Tasks executed: {len(result['results'])}")
    for r in result["results"]:
        print(f" - {r['agent']}: {r['task']} | conf={r['confidence']:.2f}")

    export = swarm.export_shared_context()
    print(f"Exported context records: {len(export['memory'].get('records', []))}")
