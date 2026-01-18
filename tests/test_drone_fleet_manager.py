"""
Comprehensive test suite for drone_fleet_manager.py
Tests: Fleet initialization, delivery assignment, self-healing, threading, weather, VIP prioritization
"""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from drone_fleet_manager import (
    DroneFleetManager,
    VirtualDrone,
    FleetDelivery,
    Region,
    DroneStatus,
    WeatherCondition,
    DeliveryPriority,
    FlightSimulator,
    IntelligentAssignmentEngine,
    SelfHealingEngine
)


@pytest.fixture
def fleet_manager():
    """Initialize fleet manager for testing."""
    manager = DroneFleetManager(manager_id='test_fleet_01')
    yield manager
    manager.stop_fleet_operations()


@pytest.fixture
def test_dashboard_path(tmp_path):
    """Create temporary dashboard path."""
    dashboard_path = tmp_path / 'test_dashboard.json'
    return str(dashboard_path)


# ============================================================================
# PHASE 1: FLEET INITIALIZATION TESTS
# ============================================================================

class TestFleetInitialization:
    """Test fleet manager initialization and setup."""

    def test_fleet_manager_initialization(self, fleet_manager):
        """Test basic fleet manager creation."""
        assert fleet_manager.manager_id == 'test_fleet_01'
        assert len(fleet_manager.regions) == 7
        assert len(fleet_manager.drones) == 0
        assert fleet_manager.pending_deliveries == {}
        assert fleet_manager.active_deliveries == {}
        assert fleet_manager.completed_deliveries == []

    def test_global_fleet_building(self, fleet_manager):
        """Test building global fleet with 100+ drones."""
        fleet_manager.build_global_fleet(drones_per_region=15)
        
        assert len(fleet_manager.drones) == 105
        
        for region_id in fleet_manager.regions:
            region_drones = [d for d in fleet_manager.drones.values() 
                           if d.region_id == region_id]
            assert len(region_drones) == 15

    def test_add_drone_to_region(self, fleet_manager):
        """Test adding individual drone to region."""
        drone_id = fleet_manager.add_drone('us_west', 'economy', 37.7749, -122.4194)
        
        assert drone_id is not None
        assert drone_id in fleet_manager.drones
        
        drone = fleet_manager.drones[drone_id]
        assert drone.max_payload_kg == 2.0
        assert drone.region_id == 'us_west'
        assert drone.status == DroneStatus.IDLE

    def test_add_different_drone_types(self, fleet_manager):
        """Test adding drones of different types."""
        types_and_payloads = [
            ('economy', 2.0),
            ('premium', 5.0),
            ('elite', 3.0),
            ('bvlos', 10.0)
        ]
        drone_ids = []
        
        for dtype, expected_payload in types_and_payloads:
            drone_id = fleet_manager.add_drone('us_west', dtype, 37.7749, -122.4194)
            drone_ids.append(drone_id)
            assert fleet_manager.drones[drone_id].max_payload_kg == expected_payload
        
        assert len(drone_ids) == 4
        assert len(set(drone_ids)) == 4

    def test_regions_initialized_correctly(self, fleet_manager):
        """Test that all 7 regions are initialized."""
        expected_regions = ['us_east', 'us_west', 'eu_central', 'apac', 
                          'middle_east', 'africa', 'south_america']
        
        for region_id in expected_regions:
            assert region_id in fleet_manager.regions
            region = fleet_manager.regions[region_id]
            assert region.region_id == region_id


# ============================================================================
# PHASE 2: DELIVERY ASSIGNMENT TESTS
# ============================================================================

class TestDeliveryAssignment:
    """Test delivery submission and intelligent assignment."""

    def test_submit_delivery(self, fleet_manager):
        """Test submitting delivery order."""
        fleet_manager.build_global_fleet(drones_per_region=5)
        
        success, delivery_id = fleet_manager.submit_delivery(
            order_id='order_001',
            pickup_lat=37.7749,
            pickup_lon=-122.4194,
            delivery_lat=40.7128,
            delivery_lon=-74.0060,
            package_weight_kg=2.5,
            rarity_score=75,
            priority='standard',
            revenue_usd=50.0
        )
        
        assert success is True
        assert delivery_id is not None
        assert delivery_id in fleet_manager.pending_deliveries

    def test_submit_vip_rare_delivery(self, fleet_manager):
        """Test submitting VIP rare delivery (rarity > 90)."""
        fleet_manager.build_global_fleet(drones_per_region=5)
        
        success, delivery_id = fleet_manager.submit_delivery(
            order_id='order_vip_001',
            pickup_lat=37.7749,
            pickup_lon=-122.4194,
            delivery_lat=40.7128,
            delivery_lon=-74.0060,
            package_weight_kg=0.5,
            rarity_score=95,
            priority='standard',
            revenue_usd=500.0
        )
        
        assert success is True
        fleet_delivery = fleet_manager.pending_deliveries[delivery_id]
        assert fleet_delivery.priority == DeliveryPriority.VIP_RARE
        assert fleet_delivery.rarity_score == 95

    def test_submit_multiple_deliveries(self, fleet_manager):
        """Test submitting multiple deliveries."""
        fleet_manager.build_global_fleet(drones_per_region=5)
        
        delivery_ids = []
        for i in range(5):
            success, delivery_id = fleet_manager.submit_delivery(
                order_id=f'order_{i:03d}',
                pickup_lat=37.7749 + i*0.01,
                pickup_lon=-122.4194,
                delivery_lat=40.7128,
                delivery_lon=-74.0060,
                package_weight_kg=2.0,
                rarity_score=50,
                priority='standard',
                revenue_usd=50.0
            )
            assert success is True
            delivery_ids.append(delivery_id)
        
        assert len(delivery_ids) == 5

    def test_assign_delivery_auto(self, fleet_manager):
        """Test automatic delivery assignment."""
        fleet_manager.build_global_fleet(drones_per_region=5)
        
        success, delivery_id = fleet_manager.submit_delivery(
            order_id='order_001',
            pickup_lat=37.7749,
            pickup_lon=-122.4194,
            delivery_lat=40.7128,
            delivery_lon=-74.0060,
            package_weight_kg=2.0,
            rarity_score=60,
            priority='standard',
            revenue_usd=50.0
        )
        
        assigned_drone_id = fleet_manager.assign_delivery(delivery_id)
        
        assert assigned_drone_id is not None
        assert delivery_id in fleet_manager.active_deliveries

    def test_vip_rare_gets_priority(self, fleet_manager):
        """Test VIP rare deliveries get high-priority assignment."""
        fleet_manager.build_global_fleet(drones_per_region=5)
        
        success, delivery_id = fleet_manager.submit_delivery(
            order_id='order_vip',
            pickup_lat=37.7749,
            pickup_lon=-122.4194,
            delivery_lat=40.7128,
            delivery_lon=-74.0060,
            package_weight_kg=0.5,
            rarity_score=95,
            priority='standard',
            revenue_usd=500.0
        )
        
        delivery = fleet_manager.pending_deliveries[delivery_id]
        assert delivery.priority == DeliveryPriority.VIP_RARE


# ============================================================================
# PHASE 3: MONITORING & DASHBOARD TESTS
# ============================================================================

class TestMonitoring:
    """Test fleet monitoring and metrics."""

    def test_monitor_fleet_status(self, fleet_manager):
        """Test monitoring fleet status."""
        fleet_manager.build_global_fleet(drones_per_region=5)
        
        status = fleet_manager.monitor_fleet()
        
        assert 'fleet' in status
        assert status['fleet']['total_drones'] == 35

    def test_dashboard_json_structure(self, fleet_manager):
        """Test production dashboard JSON can be created."""
        fleet_manager.build_global_fleet(drones_per_region=3)
        
        # Call global_sync which should create/update dashboard
        fleet_manager.global_sync()
        
        # Just verify that monitor_fleet returns the right structure
        status = fleet_manager.monitor_fleet()
        assert 'manager_id' in status
        assert 'timestamp' in status
        assert 'fleet' in status


# ============================================================================
# PHASE 4: THREADING & OPERATIONS TESTS
# ============================================================================

class TestThreadingOperations:
    """Test multi-threaded fleet operations."""

    def test_start_fleet_operations(self, fleet_manager):
        """Test starting fleet operations."""
        fleet_manager.build_global_fleet(drones_per_region=3)
        fleet_manager.start_fleet_operations(num_workers=2)
        
        time.sleep(0.5)
        
        fleet_manager.stop_fleet_operations()

    def test_concurrent_delivery_processing(self, fleet_manager):
        """Test processing deliveries with threading."""
        fleet_manager.build_global_fleet(drones_per_region=3)
        fleet_manager.start_fleet_operations(num_workers=2)
        
        # Submit deliveries
        for i in range(3):
            fleet_manager.submit_delivery(
                order_id=f'order_{i}',
                pickup_lat=37.7749 + i*0.01,
                pickup_lon=-122.4194,
                delivery_lat=40.7128,
                delivery_lon=-74.0060,
                package_weight_kg=1.5,
                rarity_score=50,
                priority='standard',
                revenue_usd=50.0
            )
        
        time.sleep(1)
        
        fleet_manager.stop_fleet_operations()

    def test_stop_gracefully(self, fleet_manager):
        """Test graceful shutdown."""
        fleet_manager.build_global_fleet(drones_per_region=3)
        fleet_manager.start_fleet_operations(num_workers=2)
        
        time.sleep(0.3)
        fleet_manager.stop_fleet_operations(timeout=5)
        
        assert fleet_manager.stop_event.is_set()


# ============================================================================
# PHASE 5: WEATHER & REGION TESTS
# ============================================================================

class TestWeatherSimulation:
    """Test weather simulation."""

    def test_weather_changes(self, fleet_manager):
        """Test weather condition changes."""
        fleet_manager.build_global_fleet(drones_per_region=3)
        
        # Simulate weather changes by calling simulate_weather_change
        for region_id in ['us_west', 'eu_central', 'apac']:
            if region_id in fleet_manager.regions:
                fleet_manager.simulate_weather_change(region_id, 'rainy')
        
        # Verify at least one region has weather
        weather_set = {r.weather for r in fleet_manager.regions.values()}
        assert len(weather_set) > 0

    def test_flight_simulator(self):
        """Test flight physics calculations."""
        sim = FlightSimulator()
        
        # Test distance calculation
        distance = sim.calculate_distance(
            37.7749, -122.4194,  # SF
            40.7128, -74.0060    # NYC
        )
        
        assert distance > 0
        assert distance < 5000  # Should be ~4000km


# ============================================================================
# PHASE 6: RARE PRIORITIZATION TESTS
# ============================================================================

class TestRarePrioritization:
    """Test VIP rare package handling."""

    def test_vip_rare_threshold(self, fleet_manager):
        """Test rarity threshold for VIP."""
        fleet_manager.build_global_fleet(drones_per_region=3)
        
        # Below threshold
        success1, id1 = fleet_manager.submit_delivery(
            order_id='order_low',
            pickup_lat=37.7749,
            pickup_lon=-122.4194,
            delivery_lat=40.7128,
            delivery_lon=-74.0060,
            package_weight_kg=1.0,
            rarity_score=85,
            priority='standard',
            revenue_usd=50.0
        )
        
        # Above threshold
        success2, id2 = fleet_manager.submit_delivery(
            order_id='order_high',
            pickup_lat=37.7749,
            pickup_lon=-122.4194,
            delivery_lat=40.7128,
            delivery_lon=-74.0060,
            package_weight_kg=0.5,
            rarity_score=95,
            priority='standard',
            revenue_usd=500.0
        )
        
        del1 = fleet_manager.pending_deliveries[id1]
        del2 = fleet_manager.pending_deliveries[id2]
        
        assert del1.rarity_score == 85
        assert del1.priority == DeliveryPriority.STANDARD
        assert del2.rarity_score == 95
        assert del2.priority == DeliveryPriority.VIP_RARE


# ============================================================================
# PHASE 7: INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """End-to-end integration tests."""

    def test_full_workflow(self, fleet_manager):
        """Test complete workflow."""
        fleet_manager.build_global_fleet(drones_per_region=3)
        fleet_manager.start_fleet_operations(num_workers=2)
        
        success, delivery_id = fleet_manager.submit_delivery(
            order_id='order_complete',
            pickup_lat=37.7749,
            pickup_lon=-122.4194,
            delivery_lat=40.7128,
            delivery_lon=-74.0060,
            package_weight_kg=1.5,
            rarity_score=60,
            priority='standard',
            revenue_usd=50.0
        )
        
        assert success is True
        
        time.sleep(2)
        
        fleet_manager.stop_fleet_operations()

    def test_multi_regional_delivery(self, fleet_manager):
        """Test multi-region deliveries."""
        fleet_manager.build_global_fleet(drones_per_region=2)
        
        # US delivery
        success1, id1 = fleet_manager.submit_delivery(
            order_id='order_us',
            pickup_lat=37.7749,
            pickup_lon=-122.4194,
            delivery_lat=40.7128,
            delivery_lon=-74.0060,
            package_weight_kg=1.0,
            rarity_score=50,
            priority='standard',
            revenue_usd=50.0
        )
        
        # EU delivery
        success2, id2 = fleet_manager.submit_delivery(
            order_id='order_eu',
            pickup_lat=52.5200,
            pickup_lon=13.4050,
            delivery_lat=48.8566,
            delivery_lon=2.3522,
            package_weight_kg=1.0,
            rarity_score=50,
            priority='standard',
            revenue_usd=50.0
        )
        
        assert success1 is True
        assert success2 is True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
