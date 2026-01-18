"""
Drone Fleet Manager - Global Operations Hub
Suresh AI Origin: 100+ Virtual Drones Worldwide
Auto-assign, self-heal, VIP prioritization, production logging
Threading-based multi-drone simulation with decentralized node integration
"""

import json
import threading
import time
import uuid
import math
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict
import random
import queue

# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class DroneStatus(Enum):
    """Drone operational states"""
    IDLE = "idle"
    ASSIGNED = "assigned"
    IN_FLIGHT = "in_flight"
    DELIVERING = "delivering"
    RETURNING = "returning"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"
    FAILED = "failed"


class DeliveryPriority(Enum):
    """Delivery priority levels"""
    STANDARD = 1
    EXPRESS = 2
    PREMIUM = 3
    VIP_RARE = 4  # 1% rare, elite medical/exclusive e-commerce


class WeatherCondition(Enum):
    """Weather conditions affecting flight"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    WINDY = "windy"
    SEVERE = "severe"


@dataclass
class Region:
    """Geographic region with weather & hub info"""
    region_id: str
    name: str
    center_lat: float
    center_lon: float
    timezone: str
    weather: WeatherCondition = WeatherCondition.CLEAR
    wind_speed_kmh: float = 5.0
    humidity: float = 60.0
    temperature_c: float = 20.0


@dataclass
class DroneMetrics:
    """Performance metrics for individual drone"""
    total_flights: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    total_distance_km: float = 0.0
    total_battery_cycles: int = 0
    avg_delivery_time_min: float = 0.0
    reliability_score: float = 1.0
    last_maintenance: str = field(default_factory=lambda: datetime.now().isoformat())
    maintenance_needed: bool = False


@dataclass
class VirtualDrone:
    """Virtual drone asset in fleet"""
    drone_id: str
    region_id: str
    lat: float
    lon: float
    status: DroneStatus = DroneStatus.IDLE
    battery_percent: float = 100.0
    max_payload_kg: float = 5.0
    current_payload_kg: float = 0.0
    altitude_m: float = 0.0
    heading: int = 0  # 0-360 degrees
    speed_kmh: float = 0.0
    assigned_delivery_id: Optional[str] = None
    metrics: DroneMetrics = field(default_factory=DroneMetrics)
    last_sync: str = field(default_factory=lambda: datetime.now().isoformat())
    fault_count: int = 0
    
    def to_dict(self) -> dict:
        return {
            "drone_id": self.drone_id,
            "region_id": self.region_id,
            "location": {"lat": self.lat, "lon": self.lon},
            "status": self.status.value,
            "battery_percent": self.battery_percent,
            "payload_kg": self.current_payload_kg,
            "metrics": asdict(self.metrics),
            "reliability_score": self.metrics.reliability_score
        }


@dataclass
class FleetDelivery:
    """Delivery assignment in fleet"""
    delivery_id: str
    order_id: str
    drone_id: Optional[str] = None
    priority: DeliveryPriority = DeliveryPriority.STANDARD
    pickup_lat: float = 0.0
    pickup_lon: float = 0.0
    delivery_lat: float = 0.0
    delivery_lon: float = 0.0
    package_weight_kg: float = 0.0
    rarity_score: float = 0.0
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    assigned_at: Optional[str] = None
    completed_at: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


# ============================================================================
# FLIGHT SIMULATION ENGINE
# ============================================================================

class FlightSimulator:
    """Simulate drone flight physics and behavior"""
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points (Haversine)"""
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    @staticmethod
    def calculate_flight_time(distance_km: float, drone_speed_kmh: float = 50, weather_wind_kmh: float = 0) -> float:
        """Calculate flight time with weather effects"""
        # Wind resistance affects speed
        effective_speed = max(10, drone_speed_kmh - (weather_wind_kmh * 0.3))
        flight_time = (distance_km / effective_speed) * 60  # Convert to minutes
        return flight_time + 5  # Add 5 min for takeoff/landing
    
    @staticmethod
    def battery_consumption(distance_km: float, payload_kg: float = 0, weather_severity: int = 0) -> float:
        """Calculate battery consumption percentage"""
        # Base consumption: 1% per km
        base = distance_km * 1.0
        # Payload adds 0.5% per kg
        payload_cost = payload_kg * 0.5
        # Weather adds up to 20% cost
        weather_cost = weather_severity * 5
        return min(100, base + payload_cost + weather_cost)
    
    @staticmethod
    def simulate_failure_probability(drone_fault_count: int, weather_severity: int = 0) -> float:
        """Calculate probability of flight failure"""
        base_failure = 0.001  # 0.1%
        fault_multiplier = 1.0 + (drone_fault_count * 0.05)  # +5% per fault
        weather_multiplier = 1.0 + (weather_severity * 0.1)  # +10% per weather level
        return min(0.3, base_failure * fault_multiplier * weather_multiplier)  # Cap at 30%


# ============================================================================
# INTELLIGENT ASSIGNMENT ENGINE
# ============================================================================

class IntelligentAssignmentEngine:
    """AI-powered drone assignment based on multiple factors"""
    
    def __init__(self, flight_sim: FlightSimulator = None):
        self.flight_sim = flight_sim or FlightSimulator()
    
    def score_drone_for_delivery(
        self,
        drone: VirtualDrone,
        delivery: FleetDelivery,
        region: Region,
        weather_conditions: Dict[str, Region]
    ) -> float:
        """
        Score drone suitability for delivery (0-100, higher = better)
        Factors:
        - Distance to pickup
        - Battery available
        - Payload capacity
        - Reliability score
        - Weather conditions
        - Current load
        """
        score = 100.0
        
        # 1. Distance penalty (within region preferred)
        distance = self.flight_sim.calculate_distance(
            drone.lat, drone.lon, delivery.pickup_lat, delivery.pickup_lon
        )
        if distance > 50:
            score -= 20
        elif distance > 20:
            score -= 10
        
        # 2. Battery check (need at least 40% after delivery)
        flight_distance = self.flight_sim.calculate_distance(
            delivery.pickup_lat, delivery.pickup_lon,
            delivery.delivery_lat, delivery.delivery_lon
        )
        battery_needed = self.flight_sim.battery_consumption(
            distance + flight_distance + 10,
            delivery.package_weight_kg,
            self._weather_severity(region)
        )
        if drone.battery_percent < battery_needed + 20:
            score -= 30
        
        # 3. Payload capacity
        if delivery.package_weight_kg > drone.max_payload_kg:
            return 0  # Cannot carry
        elif delivery.package_weight_kg > drone.max_payload_kg * 0.8:
            score -= 15  # Low capacity margin
        
        # 4. Reliability score multiplier
        score *= drone.metrics.reliability_score
        
        # 5. VIP rare priority boost
        if delivery.priority == DeliveryPriority.VIP_RARE:
            # Prefer drones with high reliability for VIP
            if drone.metrics.reliability_score > 0.95:
                score += 20
            elif drone.metrics.reliability_score < 0.9:
                score -= 20
        
        # 6. Weather impact
        wind_resistance = region.wind_speed_kmh
        if wind_resistance > 20:
            score -= 15
        
        # 7. Current status
        if drone.status == DroneStatus.IDLE:
            score += 10
        elif drone.status == DroneStatus.CHARGING:
            score = 0  # Not available
        elif drone.status == DroneStatus.MAINTENANCE:
            score = 0  # Not available
        
        return max(0, min(100, score))
    
    def _weather_severity(self, region: Region) -> int:
        """Convert weather to severity level 0-4"""
        severity_map = {
            WeatherCondition.CLEAR: 0,
            WeatherCondition.CLOUDY: 1,
            WeatherCondition.RAINY: 2,
            WeatherCondition.WINDY: 3,
            WeatherCondition.SEVERE: 4
        }
        return severity_map.get(region.weather, 0)


# ============================================================================
# SELF-HEALING & FAILURE RECOVERY
# ============================================================================

class SelfHealingEngine:
    """Automatic failure detection and recovery"""
    
    def __init__(self, flight_sim: FlightSimulator = None):
        self.flight_sim = flight_sim or FlightSimulator()
    
    def detect_failure(
        self,
        drone: VirtualDrone,
        delivery: FleetDelivery,
        region: Region
    ) -> Tuple[bool, Optional[str]]:
        """
        Detect potential flight failure
        Returns: (failed, reason)
        """
        # 1. Battery critical
        if drone.battery_percent < 10:
            return True, "battery_critical"
        
        # 2. Payload exceeds capacity
        if delivery.package_weight_kg > drone.max_payload_kg:
            return True, "payload_exceeds_capacity"
        
        # 3. Severe weather
        if region.weather == WeatherCondition.SEVERE:
            return True, "severe_weather"
        
        # 4. Maintenance needed
        if drone.metrics.maintenance_needed or drone.fault_count > 5:
            return True, "maintenance_required"
        
        # 5. Random failure based on reliability
        failure_prob = self.flight_sim.simulate_failure_probability(
            drone.fault_count,
            self._weather_severity(region)
        )
        if random.random() < failure_prob:
            return True, "random_failure"
        
        return False, None
    
    def handle_failure(
        self,
        drone: VirtualDrone,
        delivery: FleetDelivery,
        reason: str,
        all_drones: Dict[str, VirtualDrone]
    ) -> Tuple[bool, Optional[str]]:
        """
        Handle failure and attempt recovery
        Returns: (recovered, action_taken)
        """
        # 1. Log failure
        drone.fault_count += 1
        delivery.retry_count += 1
        
        # 2. Battery critical → Reroute to nearest hub
        if reason == "battery_critical":
            drone.status = DroneStatus.RETURNING
            return True, "reroute_to_charging_hub"
        
        # 3. Severe weather → Hold or reroute
        if reason == "severe_weather":
            if delivery.retry_count < delivery.max_retries:
                return True, "retry_after_weather_clears"
            else:
                return False, "exceeded_max_retries"
        
        # 4. Payload exceeds → Find larger drone
        if reason == "payload_exceeds_capacity":
            larger_drone = self._find_replacement_drone(
                delivery.package_weight_kg,
                all_drones
            )
            if larger_drone:
                return True, f"reassign_to_drone_{larger_drone.drone_id}"
            else:
                return False, "no_suitable_replacement_drone"
        
        # 5. Maintenance needed → Take offline
        if reason == "maintenance_required":
            drone.status = DroneStatus.MAINTENANCE
            drone.metrics.maintenance_needed = True
            # Try to reassign
            new_drone = self._find_replacement_drone(
                delivery.package_weight_kg,
                all_drones
            )
            if new_drone:
                return True, f"reassign_to_drone_{new_drone.drone_id}"
            else:
                return False, "no_replacement_available"
        
        # 6. Random failure → Retry with different drone
        if reason == "random_failure":
            if delivery.retry_count < delivery.max_retries:
                new_drone = self._find_replacement_drone(
                    delivery.package_weight_kg,
                    all_drones
                )
                if new_drone:
                    return True, f"retry_with_drone_{new_drone.drone_id}"
            return False, "exceeded_max_retries"
        
        return False, "unknown_failure"
    
    def _find_replacement_drone(
        self,
        required_payload_kg: float,
        all_drones: Dict[str, VirtualDrone]
    ) -> Optional[VirtualDrone]:
        """Find a suitable replacement drone"""
        candidates = [
            d for d in all_drones.values()
            if d.status in [DroneStatus.IDLE, DroneStatus.CHARGING]
            and d.max_payload_kg >= required_payload_kg
            and d.battery_percent > 50
        ]
        if candidates:
            return max(candidates, key=lambda d: d.metrics.reliability_score)
        return None
    
    def _weather_severity(self, region: Region) -> int:
        """Convert weather to severity level 0-4"""
        severity_map = {
            WeatherCondition.CLEAR: 0,
            WeatherCondition.CLOUDY: 1,
            WeatherCondition.RAINY: 2,
            WeatherCondition.WINDY: 3,
            WeatherCondition.SEVERE: 4
        }
        return severity_map.get(region.weather, 0)


# ============================================================================
# DRONE FLEET MANAGER - MAIN ORCHESTRATOR
# ============================================================================

class DroneFleetManager:
    """
    Global drone fleet orchestrator
    Manages 100+ virtual drones worldwide with auto-assignment, self-healing, VIP prioritization
    """
    
    def __init__(self, manager_id: str = None, production_dashboard_file: str = None):
        """
        Initialize fleet manager
        
        Args:
            manager_id: Unique fleet manager identifier
            production_dashboard_file: Path to production_dashboard.json
        """
        self.manager_id = manager_id or f"fleet_mgr_{uuid.uuid4().hex[:8]}"
        self.dashboard_file = production_dashboard_file or "production_dashboard.json"
        
        # Core fleet management
        self.drones: Dict[str, VirtualDrone] = {}
        self.regions: Dict[str, Region] = self._initialize_regions()
        self.pending_deliveries: Dict[str, FleetDelivery] = {}
        self.active_deliveries: Dict[str, FleetDelivery] = {}
        self.completed_deliveries: List[FleetDelivery] = []
        self.failed_deliveries: List[FleetDelivery] = []
        
        # Engines
        self.flight_sim = FlightSimulator()
        self.assignment_engine = IntelligentAssignmentEngine(self.flight_sim)
        self.healing_engine = SelfHealingEngine(self.flight_sim)
        
        # Threading & synchronization
        self.lock = threading.RLock()
        self.command_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_threads: List[threading.Thread] = []
        
        # Fleet statistics
        self.total_deliveries_assigned = 0
        self.total_deliveries_completed = 0
        self.total_deliveries_failed = 0
        self.total_distance_flown_km = 0.0
        self.total_revenue_usd = 0.0
        self.rare_orders_completed = 0
        
        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"FleetManager-{self.manager_id}")
        
        self.logger.info(f"🚁 Drone Fleet Manager initialized: {self.manager_id}")
    
    # ========================================================================
    # FLEET INITIALIZATION & MANAGEMENT
    # ========================================================================
    
    def _initialize_regions(self) -> Dict[str, Region]:
        """Initialize global regions with weather & hubs"""
        return {
            "us_west": Region("us_west", "US West", 37.7749, -122.4194, "PST"),
            "us_east": Region("us_east", "US East", 40.7128, -74.0060, "EST"),
            "eu_central": Region("eu_central", "EU Central", 52.5200, 13.4050, "CET"),
            "apac": Region("apac", "Asia Pacific", 1.3521, 103.8198, "SGT"),
            "middle_east": Region("middle_east", "Middle East", 25.2048, 55.2708, "GST"),
            "africa": Region("africa", "Africa", -1.9536, 30.0606, "EAT"),
            "south_america": Region("south_america", "South America", -23.5505, -46.6333, "BRT"),
        }
    
    def add_drone(
        self,
        region_id: str,
        drone_type: str = "standard",
        lat: float = None,
        lon: float = None
    ) -> str:
        """
        Add drone to fleet
        
        Args:
            region_id: Region where drone is based
            drone_type: Type (economy, premium, elite, bvlos)
            lat: Starting latitude (default: region hub)
            lon: Starting longitude (default: region hub)
        
        Returns:
            Drone ID
        """
        if region_id not in self.regions:
            self.logger.error(f"Unknown region: {region_id}")
            return ""
        
        region = self.regions[region_id]
        
        # Default to region hub if not specified
        if lat is None:
            lat = region.center_lat + random.uniform(-0.1, 0.1)
        if lon is None:
            lon = region.center_lon + random.uniform(-0.1, 0.1)
        
        # Drone specifications by type
        specs = {
            "economy": {"max_payload": 2.0, "speed": 40},
            "premium": {"max_payload": 5.0, "speed": 50},
            "elite": {"max_payload": 3.0, "speed": 60},
            "bvlos": {"max_payload": 10.0, "speed": 70},
        }
        
        spec = specs.get(drone_type, specs["economy"])
        
        drone_id = f"drone_{region_id}_{uuid.uuid4().hex[:6]}"
        
        drone = VirtualDrone(
            drone_id=drone_id,
            region_id=region_id,
            lat=lat,
            lon=lon,
            max_payload_kg=spec["max_payload"]
        )
        
        with self.lock:
            self.drones[drone_id] = drone
        
        self.logger.info(f"✅ Added drone: {drone_id} ({drone_type}) to {region_id}")
        return drone_id
    
    def build_global_fleet(self, drones_per_region: int = 15) -> List[str]:
        """
        Build global fleet with specified drones per region
        
        Args:
            drones_per_region: Number of drones per region (default 15 = 105 total)
        
        Returns:
            List of added drone IDs
        """
        drone_ids = []
        drone_distribution = {
            "economy": 0.4,   # 40%
            "premium": 0.35,  # 35%
            "elite": 0.15,    # 15% (rare drones)
            "bvlos": 0.1,     # 10% (long-range)
        }
        
        for region_id in self.regions.keys():
            for i in range(drones_per_region):
                # Distribute drone types
                rand = random.random()
                cumulative = 0
                drone_type = "economy"
                for dtype, ratio in drone_distribution.items():
                    cumulative += ratio
                    if rand < cumulative:
                        drone_type = dtype
                        break
                
                drone_id = self.add_drone(region_id, drone_type)
                drone_ids.append(drone_id)
        
        self.logger.info(f"🌍 Global fleet built: {len(drone_ids)} drones across {len(self.regions)} regions")
        return drone_ids
    
    # ========================================================================
    # DELIVERY ASSIGNMENT
    # ========================================================================
    
    def submit_delivery(
        self,
        order_id: str,
        pickup_lat: float,
        pickup_lon: float,
        delivery_lat: float,
        delivery_lon: float,
        package_weight_kg: float,
        rarity_score: float,
        priority: str = "standard",
        revenue_usd: float = 0.0
    ) -> Tuple[bool, str]:
        """
        Submit delivery order for fleet processing
        
        Args:
            order_id: Order identifier
            pickup_lat/lon: Pickup coordinates
            delivery_lat/lon: Delivery coordinates
            package_weight_kg: Package weight
            rarity_score: Rarity score (0-100, >90 = VIP rare)
            priority: Priority level (standard, express, premium, vip_rare)
            revenue_usd: Revenue amount for this delivery
        
        Returns:
            (success, message)
        """
        delivery_id = f"delivery_{uuid.uuid4().hex[:8]}"
        
        # Map priority string to enum
        priority_map = {
            "standard": DeliveryPriority.STANDARD,
            "express": DeliveryPriority.EXPRESS,
            "premium": DeliveryPriority.PREMIUM,
            "vip_rare": DeliveryPriority.VIP_RARE,
        }
        priority_enum = priority_map.get(priority, DeliveryPriority.STANDARD)
        
        # Force VIP_RARE if rarity > 90
        if rarity_score > 90:
            priority_enum = DeliveryPriority.VIP_RARE
        
        delivery = FleetDelivery(
            delivery_id=delivery_id,
            order_id=order_id,
            priority=priority_enum,
            pickup_lat=pickup_lat,
            pickup_lon=pickup_lon,
            delivery_lat=delivery_lat,
            delivery_lon=delivery_lon,
            package_weight_kg=package_weight_kg,
            rarity_score=rarity_score
        )
        
        with self.lock:
            self.pending_deliveries[delivery_id] = delivery
        
        self.logger.info(
            f"📦 Delivery submitted: {delivery_id} | "
            f"Order: {order_id} | Rarity: {rarity_score:.0f} | "
            f"Priority: {priority_enum.name}"
        )
        
        return True, delivery_id
    
    def assign_delivery(self, delivery_id: str) -> Tuple[bool, Optional[str]]:
        """
        Assign delivery to best available drone
        
        Args:
            delivery_id: Delivery ID from submit_delivery()
        
        Returns:
            (success, assigned_drone_id)
        """
        if delivery_id not in self.pending_deliveries:
            self.logger.error(f"Delivery not found: {delivery_id}")
            return False, None
        
        delivery = self.pending_deliveries[delivery_id]
        
        # Determine target region (closest to delivery location)
        target_region = self._find_closest_region(
            delivery.delivery_lat,
            delivery.delivery_lon
        )
        
        region = self.regions[target_region]
        
        # Score all available drones
        best_drone = None
        best_score = -1
        
        with self.lock:
            for drone in self.drones.values():
                if drone.status in [DroneStatus.IDLE, DroneStatus.CHARGING]:
                    score = self.assignment_engine.score_drone_for_delivery(
                        drone, delivery, region, self.regions
                    )
                    
                    if score > best_score:
                        best_score = score
                        best_drone = drone
        
        if not best_drone or best_score <= 0:
            self.logger.warning(
                f"❌ No suitable drone for delivery {delivery_id} "
                f"(weight: {delivery.package_weight_kg}kg, priority: {delivery.priority.name})"
            )
            return False, None
        
        # Assign drone
        with self.lock:
            best_drone.assigned_delivery_id = delivery_id
            best_drone.status = DroneStatus.ASSIGNED
            delivery.drone_id = best_drone.drone_id
            delivery.assigned_at = datetime.now().isoformat()
            delivery.status = "assigned"
            
            # Move from pending to active
            self.active_deliveries[delivery_id] = self.pending_deliveries.pop(delivery_id)
        
        self.total_deliveries_assigned += 1
        
        self.logger.info(
            f"✅ Delivery {delivery_id} assigned to {best_drone.drone_id} "
            f"(Score: {best_score:.0f}, Region: {target_region})"
        )
        
        return True, best_drone.drone_id
    
    def _find_closest_region(self, lat: float, lon: float) -> str:
        """Find closest region to coordinates"""
        closest = None
        min_distance = float('inf')
        
        for region_id, region in self.regions.items():
            distance = self.flight_sim.calculate_distance(
                region.center_lat, region.center_lon, lat, lon
            )
            if distance < min_distance:
                min_distance = distance
                closest = region_id
        
        return closest
    
    # ========================================================================
    # FLIGHT SIMULATION & MONITORING
    # ========================================================================
    
    def simulate_flight(self, delivery_id: str) -> Tuple[bool, str]:
        """
        Simulate drone flight for delivery
        
        Args:
            delivery_id: Active delivery ID
        
        Returns:
            (success, message)
        """
        if delivery_id not in self.active_deliveries:
            return False, "delivery_not_active"
        
        delivery = self.active_deliveries[delivery_id]
        drone = self.drones.get(delivery.drone_id)
        
        if not drone:
            return False, "drone_not_found"
        
        region = self.regions[drone.region_id]
        
        # Check for failure conditions
        failed, reason = self.healing_engine.detect_failure(drone, delivery, region)
        
        if failed:
            self.logger.warning(
                f"⚠️  Flight failure detected: {delivery_id} ({reason})"
            )
            
            # Attempt recovery
            recovered, action = self.healing_engine.handle_failure(
                drone, delivery, reason, self.drones
            )
            
            if not recovered:
                # Permanent failure
                delivery.status = "failed"
                with self.lock:
                    self.active_deliveries.pop(delivery_id)
                    self.failed_deliveries.append(delivery)
                self.total_deliveries_failed += 1
                
                self.logger.error(
                    f"❌ Delivery failed: {delivery_id} ({action})"
                )
                return False, action
            else:
                self.logger.info(f"🔄 Recovery action: {action}")
                return True, f"recovery_in_progress: {action}"
        
        # Simulate flight
        drone.status = DroneStatus.IN_FLIGHT
        
        # Calculate flight distance & time
        flight_distance = self.flight_sim.calculate_distance(
            delivery.pickup_lat, delivery.pickup_lon,
            delivery.delivery_lat, delivery.delivery_lon
        )
        
        flight_time = self.flight_sim.calculate_flight_time(
            flight_distance,
            50,  # Standard speed
            region.wind_speed_kmh
        )
        
        # Battery consumption
        battery_used = self.flight_sim.battery_consumption(
            flight_distance,
            delivery.package_weight_kg,
            self.healing_engine._weather_severity(region)
        )
        
        # Update drone
        with self.lock:
            drone.battery_percent = max(0, drone.battery_percent - battery_used)
            drone.status = DroneStatus.DELIVERING
            drone.current_payload_kg = delivery.package_weight_kg
            drone.metrics.total_flights += 1
            drone.metrics.total_distance_km += flight_distance
            
            # Update delivery
            delivery.status = "in_flight"
        
        # Track fleet metrics
        self.total_distance_flown_km += flight_distance
        
        self.logger.info(
            f"✈️  Flight {delivery_id}: {flight_distance:.1f}km in {flight_time:.0f}min "
            f"(Battery: -{battery_used:.0f}%)"
        )
        
        # Simulate delivery completion
        time.sleep(0.1)  # Brief simulation delay
        
        with self.lock:
            drone.status = DroneStatus.DELIVERING
            drone.current_payload_kg = 0
            drone.altitude_m = 0
            drone.metrics.successful_deliveries += 1
            delivery.status = "completed"
            delivery.completed_at = datetime.now().isoformat()
            
            # Move to completed
            self.active_deliveries.pop(delivery_id)
            self.completed_deliveries.append(delivery)
        
        self.total_deliveries_completed += 1
        
        # VIP rare bonus tracking
        if delivery.priority == DeliveryPriority.VIP_RARE:
            self.rare_orders_completed += 1
        
        self.logger.info(f"🎉 Delivery completed: {delivery_id}")
        
        return True, "completed"
    
    # ========================================================================
    # GLOBAL MONITORING & SYNCHRONIZATION
    # ========================================================================
    
    def monitor_fleet(self) -> Dict:
        """
        Get comprehensive fleet status
        
        Returns:
            Fleet monitoring data
        """
        with self.lock:
            # Count drones by status
            status_counts = defaultdict(int)
            for drone in self.drones.values():
                status_counts[drone.status.value] += 1
            
            # Aggregate metrics
            total_flights = sum(d.metrics.total_flights for d in self.drones.values())
            total_successful = sum(d.metrics.successful_deliveries for d in self.drones.values())
            avg_battery = sum(d.battery_percent for d in self.drones.values()) / len(self.drones) if self.drones else 0
            avg_reliability = sum(d.metrics.reliability_score for d in self.drones.values()) / len(self.drones) if self.drones else 0
            
            return {
                "manager_id": self.manager_id,
                "timestamp": datetime.now().isoformat(),
                "fleet": {
                    "total_drones": len(self.drones),
                    "status_distribution": dict(status_counts),
                    "average_battery_percent": round(avg_battery, 1),
                    "average_reliability_score": round(avg_reliability, 3),
                },
                "deliveries": {
                    "pending": len(self.pending_deliveries),
                    "active": len(self.active_deliveries),
                    "completed": len(self.completed_deliveries),
                    "failed": len(self.failed_deliveries),
                },
                "statistics": {
                    "total_assigned": self.total_deliveries_assigned,
                    "total_completed": self.total_deliveries_completed,
                    "total_failed": self.total_deliveries_failed,
                    "success_rate": self._calculate_success_rate(),
                    "total_distance_km": round(self.total_distance_flown_km, 1),
                    "total_revenue_usd": round(self.total_revenue_usd, 2),
                    "rare_orders_completed": self.rare_orders_completed,
                },
                "regions": {
                    region_id: {
                        "drones_active": sum(1 for d in self.drones.values() if d.region_id == region_id and d.status != DroneStatus.CHARGING),
                        "drones_total": sum(1 for d in self.drones.values() if d.region_id == region_id),
                    }
                    for region_id in self.regions.keys()
                }
            }
    
    def global_sync(self) -> Dict:
        """
        Synchronize global fleet state with decentralized nodes
        
        Returns:
            Sync status
        """
        monitoring_data = self.monitor_fleet()
        
        # Update production dashboard
        self._update_dashboard(monitoring_data)
        
        # Simulate sync with decentralized nodes
        sync_data = {
            "sync_id": f"sync_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now().isoformat(),
            "fleet_snapshot": monitoring_data,
            "active_deliveries": [
                {
                    "delivery_id": d.delivery_id,
                    "order_id": d.order_id,
                    "drone_id": d.drone_id,
                    "status": d.status,
                    "priority": d.priority.name,
                    "rarity_score": d.rarity_score
                }
                for d in self.active_deliveries.values()
            ]
        }
        
        self.logger.info(
            f"🔄 Global sync: {len(self.active_deliveries)} active, "
            f"{len(self.completed_deliveries)} completed"
        )
        
        return sync_data
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall delivery success rate"""
        total = self.total_deliveries_completed + self.total_deliveries_failed
        if total == 0:
            return 0.0
        return (self.total_deliveries_completed / total) * 100
    
    def _update_dashboard(self, monitoring_data: Dict):
        """Update production dashboard JSON"""
        try:
            dashboard = {
                "fleet_manager": self.manager_id,
                "last_updated": datetime.now().isoformat(),
                "monitoring": monitoring_data,
                "top_performers": self._get_top_drones(5),
                "alerts": self._get_fleet_alerts()
            }
            
            with open(self.dashboard_file, 'w') as f:
                json.dump(dashboard, f, indent=2)
            
            self.logger.info(f"📊 Dashboard updated: {self.dashboard_file}")
        except Exception as e:
            self.logger.error(f"Dashboard update failed: {e}")
    
    def _get_top_drones(self, limit: int = 5) -> List[Dict]:
        """Get top performing drones"""
        sorted_drones = sorted(
            self.drones.values(),
            key=lambda d: (d.metrics.successful_deliveries, d.metrics.reliability_score),
            reverse=True
        )
        
        return [
            {
                "drone_id": d.drone_id,
                "successful_deliveries": d.metrics.successful_deliveries,
                "reliability_score": round(d.metrics.reliability_score, 3),
                "total_distance_km": round(d.metrics.total_distance_km, 1),
            }
            for d in sorted_drones[:limit]
        ]
    
    def _get_fleet_alerts(self) -> List[Dict]:
        """Get fleet alerts and warnings"""
        alerts = []
        
        # Low battery drones
        low_battery = [d for d in self.drones.values() if d.battery_percent < 20 and d.status != DroneStatus.CHARGING]
        if low_battery:
            alerts.append({
                "type": "low_battery",
                "severity": "warning",
                "count": len(low_battery),
                "message": f"{len(low_battery)} drones with low battery (<20%)"
            })
        
        # Maintenance needed
        maintenance_needed = [d for d in self.drones.values() if d.metrics.maintenance_needed or d.fault_count > 5]
        if maintenance_needed:
            alerts.append({
                "type": "maintenance_required",
                "severity": "critical",
                "count": len(maintenance_needed),
                "message": f"{len(maintenance_needed)} drones need maintenance"
            })
        
        # High failure rate
        if self.total_deliveries_completed > 10:
            failure_rate = self._calculate_success_rate()
            if failure_rate < 95:
                alerts.append({
                    "type": "high_failure_rate",
                    "severity": "warning",
                    "rate": round(failure_rate, 1),
                    "message": f"Success rate below 95%: {failure_rate:.1f}%"
                })
        
        return alerts
    
    # ========================================================================
    # THREADING & WORKER MANAGEMENT
    # ========================================================================
    
    def start_fleet_operations(self, num_workers: int = 4):
        """
        Start fleet operation workers (threaded)
        
        Args:
            num_workers: Number of worker threads
        """
        if self.worker_threads:
            self.logger.warning("Fleet operations already running")
            return
        
        self.stop_event.clear()
        
        for i in range(num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"FleetWorker-{i}",
                daemon=True
            )
            worker.start()
            self.worker_threads.append(worker)
        
        self.logger.info(f"🚀 Fleet operations started ({num_workers} workers)")
    
    def stop_fleet_operations(self, timeout: int = 5):
        """Stop all fleet workers"""
        self.stop_event.set()
        
        for worker in self.worker_threads:
            worker.join(timeout=timeout)
        
        self.worker_threads.clear()
        self.logger.info("⏹️  Fleet operations stopped")
    
    def _worker_loop(self):
        """Worker thread main loop"""
        while not self.stop_event.is_set():
            try:
                # Process pending deliveries (assign to drones)
                pending_list = list(self.pending_deliveries.keys())
                for delivery_id in pending_list:
                    if delivery_id in self.pending_deliveries:
                        self.assign_delivery(delivery_id)
                        time.sleep(0.1)
                
                # Simulate active flights
                active_list = list(self.active_deliveries.keys())
                for delivery_id in active_list:
                    if delivery_id in self.active_deliveries:
                        self.simulate_flight(delivery_id)
                        time.sleep(0.1)
                
                # Brief pause before next iteration
                time.sleep(0.5)
            
            except Exception as e:
                self.logger.error(f"Worker error: {e}")
                time.sleep(1)
    
    # ========================================================================
    # SIMULATION UTILITIES
    # ========================================================================
    
    def simulate_weather_change(self, region_id: str, weather: str):
        """Simulate weather change in region"""
        if region_id not in self.regions:
            return
        
        weather_map = {
            "clear": WeatherCondition.CLEAR,
            "cloudy": WeatherCondition.CLOUDY,
            "rainy": WeatherCondition.RAINY,
            "windy": WeatherCondition.WINDY,
            "severe": WeatherCondition.SEVERE,
        }
        
        self.regions[region_id].weather = weather_map.get(weather, WeatherCondition.CLEAR)
        self.logger.info(f"🌤️  Weather changed in {region_id}: {weather}")
    
    def charge_all_drones(self):
        """Charge all drones to 100%"""
        with self.lock:
            for drone in self.drones.values():
                if drone.status != DroneStatus.IN_FLIGHT:
                    drone.battery_percent = 100.0
                    drone.fault_count = max(0, drone.fault_count - 1)  # Reduce fault count on maintenance
        
        self.logger.info("🔌 All drones charged")
    
    def get_drone_info(self, drone_id: str) -> Optional[Dict]:
        """Get detailed drone information"""
        if drone_id not in self.drones:
            return None
        
        drone = self.drones[drone_id]
        return drone.to_dict()
    
    def get_fleet_summary(self) -> Dict:
        """Get quick fleet summary"""
        with self.lock:
            return {
                "total_drones": len(self.drones),
                "regions": len(self.regions),
                "pending_deliveries": len(self.pending_deliveries),
                "active_deliveries": len(self.active_deliveries),
                "completed_deliveries": len(self.completed_deliveries),
                "failed_deliveries": len(self.failed_deliveries),
                "success_rate": round(self._calculate_success_rate(), 1),
                "total_distance_km": round(self.total_distance_flown_km, 1),
                "rare_orders_completed": self.rare_orders_completed,
            }


# ============================================================================
# SIMULATION & TESTING
# ============================================================================

def run_full_simulation():
    """Full fleet manager simulation"""
    print("\n" + "="*80)
    print("🚁 DRONE FLEET MANAGER - GLOBAL OPERATIONS SIMULATION")
    print("="*80 + "\n")
    
    # 1. Initialize fleet manager
    print("📋 Initializing Fleet Manager...")
    manager = DroneFleetManager(
        manager_id="global_fleet_01",
        production_dashboard_file="production_dashboard.json"
    )
    
    # 2. Build global fleet (105 drones across 7 regions)
    print("🌍 Building global fleet...")
    drone_ids = manager.build_global_fleet(drones_per_region=15)
    print(f"✅ Fleet built: {len(drone_ids)} drones\n")
    
    # 3. Simulate weather
    print("🌤️  Simulating weather conditions...")
    manager.simulate_weather_change("us_west", "clear")
    manager.simulate_weather_change("eu_central", "rainy")
    manager.simulate_weather_change("apac", "windy")
    print()
    
    # 4. Submit deliveries
    print("📦 Submitting deliveries...")
    delivery_ids = []
    
    # Standard deliveries
    for i in range(5):
        success, delivery_id = manager.submit_delivery(
            order_id=f"order_std_{i:03d}",
            pickup_lat=37.7749 + random.uniform(-0.5, 0.5),
            pickup_lon=-122.4194 + random.uniform(-0.5, 0.5),
            delivery_lat=37.5 + random.uniform(-0.5, 0.5),
            delivery_lon=-122.2 + random.uniform(-0.5, 0.5),
            package_weight_kg=random.uniform(1, 5),
            rarity_score=random.uniform(20, 75),
            priority="standard",
            revenue_usd=random.uniform(25, 50)
        )
        if success:
            delivery_ids.append(delivery_id)
    
    # VIP rare deliveries (1% elite)
    for i in range(3):
        success, delivery_id = manager.submit_delivery(
            order_id=f"order_vip_{i:03d}",
            pickup_lat=40.7128 + random.uniform(-0.2, 0.2),
            pickup_lon=-74.0060 + random.uniform(-0.2, 0.2),
            delivery_lat=40.6 + random.uniform(-0.2, 0.2),
            delivery_lon=-73.95 + random.uniform(-0.2, 0.2),
            package_weight_kg=random.uniform(0.5, 3),
            rarity_score=random.uniform(92, 100),  # High rarity
            priority="vip_rare",
            revenue_usd=random.uniform(500, 2500)  # High revenue
        )
        if success:
            delivery_ids.append(delivery_id)
    
    print(f"✅ Submitted {len(delivery_ids)} deliveries\n")
    
    # 5. Start fleet operations (threaded)
    print("🚀 Starting fleet operations...")
    manager.start_fleet_operations(num_workers=4)
    
    # 6. Simulate operations
    print("⏳ Running simulation (10 seconds)...\n")
    for i in range(10):
        time.sleep(1)
        
        # Monitor
        summary = manager.get_fleet_summary()
        monitoring = manager.monitor_fleet()
        
        print(f"[{i+1}s] Status: "
              f"Pending:{summary['pending_deliveries']} | "
              f"Active:{summary['active_deliveries']} | "
              f"Completed:{summary['completed_deliveries']} | "
              f"Failed:{summary['failed_deliveries']} | "
              f"Success:{summary['success_rate']:.0f}% | "
              f"Rare:{summary['rare_orders_completed']}")
    
    print()
    
    # 7. Stop operations
    manager.stop_fleet_operations()
    
    # 8. Final report
    print("\n" + "="*80)
    print("📊 FINAL FLEET REPORT")
    print("="*80 + "\n")
    
    final_summary = manager.get_fleet_summary()
    print(f"Total Drones: {final_summary['total_drones']}")
    print(f"Regions: {final_summary['regions']}")
    print(f"Completed Deliveries: {final_summary['completed_deliveries']}")
    print(f"Failed Deliveries: {final_summary['failed_deliveries']}")
    print(f"Success Rate: {final_summary['success_rate']:.1f}%")
    print(f"Total Distance: {final_summary['total_distance_km']:.1f} km")
    print(f"Rare Orders Completed: {final_summary['rare_orders_completed']}")
    
    # 9. Global sync
    print("\n🔄 Performing global sync...")
    sync_result = manager.global_sync()
    print(f"✅ Sync complete - {len(sync_result['active_deliveries'])} active deliveries")
    
    # 10. Top drones
    print("\n🏆 Top Performing Drones:")
    monitoring = manager.monitor_fleet()
    for i, drone in enumerate(monitoring['fleet'], 1):
        print(f"  {i}. {drone}")
    
    print("\n" + "="*80)
    print("✅ SIMULATION COMPLETE")
    print("="*80 + "\n")
    
    return manager


if __name__ == "__main__":
    manager = run_full_simulation()
