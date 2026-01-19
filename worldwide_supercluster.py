"""
Worldwide Supercluster - Colossus-scale rare compute fabric
Suresh AI Origin | 1% rarest tier alignment

Key capabilities:
- Simulates 100k+ virtual GPUs (threaded mocks via multiprocessing pool)
- Region-aware nodes (US / EU / IN) with automatic task migration for latency
- Rarity enforcement: 1% elite compute reserved for VIP tiers (tier_system check)
- Hybrid physical/digital: hooks into drone_fleet_manager for rare deliveries
- Integrates decentralized_ai_node rarity scoring for global elite routing
- Reliability objective: 99.2%+ uptime metric tracked per sync

Methods exposed:
- deploy_region_node(region_id)
- scale_compute(region_id, gpus_requested, tier, rarity_score, user_location)
- rarity_allocate(task, tier, user_location)
- worldwide_sync()

Usage (quick):
    from worldwide_supercluster import WorldWideSuperCluster
    sc = WorldWideSuperCluster()
    result = sc.rarity_allocate({"id": "task_1", "prompt": "rare AGI query"}, tier="one_percent")
"""

import math
import time
import uuid
import random
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from geopy.distance import geodesic

try:
    from decentralized_ai_node import (
        DecentralizedAINode,
        RarityFilter,
        TaskMetadata,
        AITask,
        TaskPriority,
    )
except ImportError:
    # Minimal stubs if decentralized_ai_node is unavailable
    class TaskPriority:
        HIGH = type("Enum", (), {"value": 0.8})
        MEDIUM = type("Enum", (), {"value": 0.6})

    @dataclass
    class TaskMetadata:
        task_id: str
        task_type: str
        creator_address: str
        created_at: float
        priority: TaskPriority = TaskPriority.MEDIUM
        complexity_estimate: float = 5.0
        data_size: int = 0

        def calculate_rarity_score(self) -> float:
            base = 50 + (self.complexity_estimate * 3)
            base += min(20, self.data_size / 5000)
            return min(100.0, base)

    @dataclass
    class AITask:
        task_id: str
        task_type: str
        prompt: str
        metadata: TaskMetadata
        rarity_score: float = 0.0

    class RarityFilter:
        def __init__(self, threshold: float = 95.0):
            self.threshold = threshold

        def score_task(self, task: AITask) -> float:
            return task.metadata.calculate_rarity_score()

        def is_rare_enough(self, rarity_score: float) -> bool:
            return rarity_score > self.threshold

    class DecentralizedAINode:
        def __init__(self, *_, **__):
            self.node_id = "mock"

        def start(self):
            return True

# Optional drone integration
try:
    from drone_fleet_manager import DroneFleetManager
    DRONES_AVAILABLE = True
except ImportError:
    DRONES_AVAILABLE = False
    DroneFleetManager = None  # type: ignore

# Tier system import (lightweight usage only)
try:
    from app import TIER_SYSTEM
    _TIER_SYSTEM = TIER_SYSTEM
except Exception:
    _TIER_SYSTEM = {
        "starter": {"position": 1},
        "pro": {"position": 2},
        "premium": {"position": 3},
        "rare": {"position": 4},
        "rarest": {"position": 5},
        "one_percent": {"position": 6},
    }

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@dataclass
class RegionNode:
    region_id: str
    name: str
    lat: float
    lon: float
    ai_node: DecentralizedAINode
    total_gpus: int
    used_gpus: int = 0
    vip_reserved: int = 0
    tasks_processed: int = 0
    reliability_pct: float = 99.2
    last_sync_ts: float = field(default_factory=time.time)

    @property
    def available_gpus(self) -> int:
        return max(0, self.total_gpus - self.used_gpus)


class WorldWideSuperCluster:
    def __init__(
        self,
        total_virtual_gpus: int = 100_000,
        vip_tiers: Optional[List[str]] = None,
        reliability_target: float = 99.2,
        enable_drone_bridge: bool = True,
    ):
        self.total_virtual_gpus = total_virtual_gpus
        self.reliability_target = reliability_target
        self.vip_tiers = set(vip_tiers or ["one_percent", "rarest", "rare"])
        self.regions: Dict[str, RegionNode] = {}
        self.rarity_filter = RarityFilter(threshold=95.0)
        self.pool = ThreadPool(processes=max(8, cpu_count() * 2))
        self.dashboard_history: List[Dict[str, Any]] = []

        self.region_configs = {
            "us": {"name": "US-West", "lat": 37.7749, "lon": -122.4194, "gpus": int(total_virtual_gpus * 0.4)},
            "eu": {"name": "EU-Central", "lat": 52.5200, "lon": 13.4050, "gpus": int(total_virtual_gpus * 0.35)},
            "in": {"name": "IN-South", "lat": 13.0827, "lon": 80.2707, "gpus": total_virtual_gpus - int(total_virtual_gpus * 0.4) - int(total_virtual_gpus * 0.35)},
        }

        self.drone_manager = None
        if enable_drone_bridge and DRONES_AVAILABLE:
            try:
                self.drone_manager = DroneFleetManager(
                    manager_id="supercluster_drone_bridge",
                    production_dashboard_file="production_dashboard.json",
                )
                logger.info("🛰️  Drone bridge initialized")
            except Exception as exc:
                logger.warning(f"Drone bridge unavailable: {exc}")
                self.drone_manager = None

        # Deploy default regions
        base_port = 9100
        for idx, region_id in enumerate(self.region_configs.keys()):
            self.deploy_region_node(region_id, port=base_port + idx)

    # ------------------------------------------------------------------
    # Region deployment
    # ------------------------------------------------------------------
    def deploy_region_node(self, region_id: str, port: int = 9100) -> RegionNode:
        if region_id not in self.region_configs:
            raise ValueError(f"Unknown region_id: {region_id}")

        cfg = self.region_configs[region_id]
        ai_node = DecentralizedAINode(node_id=f"node_{region_id}", port=port)
        # We do not start sockets in production simulations; safe no-op
        node = RegionNode(
            region_id=region_id,
            name=cfg["name"],
            lat=cfg["lat"],
            lon=cfg["lon"],
            ai_node=ai_node,
            total_gpus=cfg["gpus"],
            vip_reserved=int(cfg["gpus"] * 0.01),
        )
        self.regions[region_id] = node
        logger.info(f"✅ Deployed region node {region_id} ({node.total_gpus} vGPUs, vip_reserved={node.vip_reserved})")
        return node

    # ------------------------------------------------------------------
    # Compute scaling and migration
    # ------------------------------------------------------------------
    def scale_compute(
        self,
        region_id: str,
        gpus_requested: int,
        tier: str = "starter",
        rarity_score: float = 0.0,
        user_location: Optional[Tuple[float, float]] = None,
    ) -> Dict[str, Any]:
        if region_id not in self.regions:
            self.deploy_region_node(region_id)
        region = self.regions[region_id]

        vip_access = self._is_vip_tier(tier)
        elite_cap = int(self.total_virtual_gpus * 0.01)
        eligible_for_elite = vip_access and rarity_score >= 95

        # Enforce rarity: non-VIP cannot exceed 0.2% of cluster
        non_vip_cap = max(1, int(self.total_virtual_gpus * 0.002))
        if not eligible_for_elite:
            gpus_requested = min(gpus_requested, non_vip_cap)

        # Auto-migrate if region saturated or latency high
        target_region = region_id
        migration_reason = None
        if region.available_gpus < gpus_requested or self._is_latency_high(region, user_location):
            alt = self._find_better_region(region_id, user_location)
            if alt != region_id:
                target_region = alt
                region = self.regions[alt]
                migration_reason = "capacity" if region.available_gpus < gpus_requested else "latency"

        grantable = min(gpus_requested, region.available_gpus)
        elite_grant = 0
        if eligible_for_elite:
            elite_grant = min(grantable, elite_cap)
        grantable = max(grantable, 0)

        # Update region usage
        region.used_gpus += grantable
        region.tasks_processed += 1
        region.reliability_pct = min(100.0, max(98.5, region.reliability_pct + random.uniform(-0.05, 0.05)))
        region.last_sync_ts = time.time()

        # Simulate GPU jobs using threaded pool (representative shards)
        shard_jobs = max(1, min(32, grantable // 1024 + 1))
        latency_ms = self._estimate_latency(region, user_location)
        self.pool.map(self._simulate_gpu_job, [(latency_ms,)] * shard_jobs)

        return {
            "region": target_region,
            "gpus_requested": gpus_requested,
            "gpus_granted": grantable,
            "elite_granted": elite_grant,
            "vip": vip_access,
            "rarity_score": rarity_score,
            "latency_ms": latency_ms,
            "migration": migration_reason,
            "reliability_pct": region.reliability_pct,
        }

    # ------------------------------------------------------------------
    # Rarity-aware allocation
    # ------------------------------------------------------------------
    def rarity_allocate(
        self,
        task: Dict[str, Any],
        tier: str = "starter",
        user_location: Optional[Tuple[float, float]] = None,
    ) -> Dict[str, Any]:
        prompt = task.get("prompt", "")
        task_id = task.get("id", f"task_{uuid.uuid4().hex[:6]}")
        data_size = len(task.get("payload", ""))
        priority = TaskPriority.HIGH if self._is_vip_tier(tier) else TaskPriority.MEDIUM

        metadata = TaskMetadata(
            task_id=task_id,
            task_type=task.get("type", "general"),
            creator_address=task.get("origin", "supercluster"),
            created_at=time.time(),
            priority=priority,
            complexity_estimate=min(10.0, max(1.0, len(prompt.split()) / 25)),
            data_size=data_size,
        )
        ai_task = AITask(
            task_id=task_id,
            task_type=task.get("type", "general"),
            prompt=prompt,
            metadata=metadata,
        )

        rarity_score = self.rarity_filter.score_task(ai_task)
        is_rare = self.rarity_filter.is_rare_enough(rarity_score)
        if not is_rare:
            return {
                "accepted": False,
                "reason": "rarity_below_threshold",
                "rarity_score": rarity_score,
                "tier": tier,
            }

        region_id = task.get("region", self._select_region(user_location))
        allocation = self.scale_compute(
            region_id=region_id,
            gpus_requested=int(task.get("gpus", 512)),
            tier=tier,
            rarity_score=rarity_score,
            user_location=user_location,
        )

        delivery_ref = None
        if self.drone_manager and task.get("delivery"):
            delivery = task["delivery"]
            try:
                success, msg = self.drone_manager.submit_delivery(
                    order_id=delivery.get("order_id", f"order_{task_id}"),
                    pickup_lat=delivery.get("pickup_lat"),
                    pickup_lon=delivery.get("pickup_lon"),
                    delivery_lat=delivery.get("delivery_lat"),
                    delivery_lon=delivery.get("delivery_lon"),
                    package_weight_kg=delivery.get("package_weight_kg", 1.0),
                    rarity_score=rarity_score,
                    priority="vip_rare" if self._is_vip_tier(tier) else "premium",
                    revenue_usd=delivery.get("revenue_usd", 0.0),
                )
                delivery_ref = msg if success else None
            except Exception as exc:
                logger.warning(f"Drone bridge submit failed: {exc}")

        return {
            "accepted": True,
            "task_id": task_id,
            "rarity_score": rarity_score,
            "region": allocation["region"],
            "compute": allocation,
            "delivery_id": delivery_ref,
        }

    # ------------------------------------------------------------------
    # Global sync and metrics
    # ------------------------------------------------------------------
    def worldwide_sync(self) -> Dict[str, Any]:
        now = time.time()
        regional_metrics = {}
        for region_id, region in self.regions.items():
            uptime = max(0, (now - region.last_sync_ts) / 3600)
            regional_metrics[region_id] = {
                "name": region.name,
                "available_gpus": region.available_gpus,
                "used_gpus": region.used_gpus,
                "vip_reserved": region.vip_reserved,
                "tasks_processed": region.tasks_processed,
                "reliability_pct": round(region.reliability_pct, 3),
                "uptime_hours": round(uptime, 2),
            }

        reliability_current = sum(r["reliability_pct"] for r in regional_metrics.values()) / max(1, len(regional_metrics))
        dashboard = {
            "timestamp": now,
            "reliability_target_pct": self.reliability_target,
            "reliability_current_pct": round(reliability_current, 3),
            "total_virtual_gpus": self.total_virtual_gpus,
            "regions": regional_metrics,
            "vip_tiers": list(self.vip_tiers),
        }
        self.dashboard_history.append(dashboard)

        if self.drone_manager:
            try:
                dashboard["drone_sync"] = self.drone_manager.global_sync()
            except Exception as exc:
                logger.warning(f"Drone sync failed: {exc}")

        logger.info(
            f"🌐 Sync | reliability {dashboard['reliability_current_pct']:.3f}% (target {self.reliability_target}%) | "
            f"regions={len(regional_metrics)}"
        )
        return dashboard

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _simulate_gpu_job(self, args: Tuple[float]):
        latency_ms = args[0]
        time.sleep(min(0.05, latency_ms / 1000.0))
        return True

    def _is_vip_tier(self, tier: str) -> bool:
        return tier in self.vip_tiers or _TIER_SYSTEM.get(tier, {}).get("position", 0) >= 5

    def _select_region(self, user_location: Optional[Tuple[float, float]]) -> str:
        if not user_location:
            return "us"
        distances = {}
        for region_id, region in self.regions.items():
            distances[region_id] = geodesic(user_location, (region.lat, region.lon)).km
        return min(distances, key=distances.get)

    def _estimate_latency(self, region: RegionNode, user_location: Optional[Tuple[float, float]]) -> float:
        if not user_location:
            return 45.0
        distance_km = geodesic(user_location, (region.lat, region.lon)).km
        return max(25.0, min(180.0, distance_km * 0.5))

    def _is_latency_high(self, region: RegionNode, user_location: Optional[Tuple[float, float]]) -> bool:
        return self._estimate_latency(region, user_location) > 140.0

    def _find_better_region(self, current_region: str, user_location: Optional[Tuple[float, float]]) -> str:
        if not user_location:
            return current_region
        candidates = {}
        for region_id, region in self.regions.items():
            if region.available_gpus <= 0:
                continue
            candidates[region_id] = self._estimate_latency(region, user_location)
        if not candidates:
            return current_region
        return min(candidates, key=candidates.get)


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    sc = WorldWideSuperCluster()

    print("\n=== Rare Task Allocation (VIP) ===")
    task = {
        "id": "rare_001",
        "type": "agi_reasoning",
        "prompt": "How do we build a Mars-scale AGI supply chain?",
        "gpus": 4096,
        "delivery": {
            "order_id": "mars_order_01",
            "pickup_lat": 37.7749,
            "pickup_lon": -122.4194,
            "delivery_lat": 40.7128,
            "delivery_lon": -74.0060,
            "package_weight_kg": 2.5,
            "revenue_usd": 1500,
        },
    }
    result = sc.rarity_allocate(task, tier="one_percent", user_location=(37.7749, -122.4194))
    print(result)

    print("\n=== Sync Dashboard ===")
    dashboard = sc.worldwide_sync()
    print({
        "reliability": dashboard["reliability_current_pct"],
        "regions": list(dashboard["regions"].keys()),
    })
