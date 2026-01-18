"""
Test Suite: Drone Delivery Agent
Tests all lifecycle phases: Order → Route → Dispatch → Track → Confirm
"""

import pytest
import time
import json
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from drone_delivery_agent import (
    DroneDeliveryAgent, Location, Package, Drone,
    DeliveryStatus, DroneType, DeliveryOrder
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def agent():
    """Initialize drone delivery agent for tests"""
    return DroneDeliveryAgent(
        agent_id="test_agent",
        regions=["north_america", "europe", "asia"]
    )


@pytest.fixture
def test_location_nyc():
    """NYC test location"""
    return Location(
        latitude=40.7128,
        longitude=-74.0060,
        address="123 Test St, NYC",
        region="north_america"
    )


@pytest.fixture
def test_location_brooklyn():
    """Brooklyn test location"""
    return Location(
        latitude=40.6501,
        longitude=-73.9496,
        address="456 Test Ave, Brooklyn",
        region="north_america"
    )


@pytest.fixture
def test_location_london():
    """London test location"""
    return Location(
        latitude=51.5074,
        longitude=-0.1278,
        address="789 Test Road, London",
        region="europe"
    )


@pytest.fixture
def test_package_standard():
    """Standard delivery package"""
    return Package(
        package_id="pkg_test_001",
        weight_kg=2.0,
        dimensions={"length": 30, "width": 20, "height": 15},
        contents="Electronics",
        fragile=False,
        temperature_controlled=False,
        value_usd=150,
        priority=2
    )


@pytest.fixture
def test_package_vip():
    """VIP delivery package"""
    return Package(
        package_id="pkg_test_vip",
        weight_kg=1.5,
        dimensions={"length": 20, "width": 15, "height": 10},
        contents="Luxury goods",
        fragile=True,
        temperature_controlled=True,
        value_usd=2500,
        priority=5
    )


@pytest.fixture
def test_package_heavy():
    """Heavy payload package"""
    return Package(
        package_id="pkg_test_heavy",
        weight_kg=8.0,
        dimensions={"length": 50, "width": 40, "height": 30},
        contents="Industrial equipment",
        fragile=False,
        temperature_controlled=False,
        value_usd=5000,
        priority=3
    )


# ============================================================================
# PHASE 1: ORDER PROCESSING TESTS
# ============================================================================

def test_process_order_standard(agent, test_package_standard, test_location_nyc, test_location_brooklyn):
    """Test standard order processing"""
    result = agent.process_order(
        customer_id="cust_001",
        package=test_package_standard,
        pickup_location=test_location_nyc,
        delivery_location=test_location_brooklyn,
        priority=2
    )
    
    assert result["success"] == True
    assert "order_id" in result
    assert result["status"] == "pending"
    assert result["drone_type"] == "economy"
    assert result["base_price_usd"] > 0
    assert result["dynamic_price_usd"] >= result["base_price_usd"]
    assert result["estimated_time_min"] > 0
    
    # Verify order stored
    assert result["order_id"] in agent.active_orders


def test_process_order_vip(agent, test_package_vip, test_location_nyc, test_location_london):
    """Test VIP order processing with elite tier"""
    result = agent.process_order(
        customer_id="cust_vip_001",
        package=test_package_vip,
        pickup_location=test_location_nyc,
        delivery_location=test_location_london,
        priority=5,
        ai_prompt="VIP priority delivery"
    )
    
    assert result["success"] == True
    assert result["rarity_score"] > 90  # Should be elite
    assert result["drone_type"] == "elite"
    assert result["dynamic_price_usd"] > result["base_price_usd"]  # Markup applied
    assert "ai_recommendation" in result


def test_process_order_heavy(agent, test_package_heavy, test_location_nyc, test_location_brooklyn):
    """Test heavy payload order (BVLOS)"""
    result = agent.process_order(
        customer_id="cust_002",
        package=test_package_heavy,
        pickup_location=test_location_nyc,
        delivery_location=test_location_brooklyn,
        priority=3
    )
    
    assert result["success"] == True
    assert result["drone_type"] in ["premium", "bvlos", "elite"]
    assert result["dynamic_price_usd"] > 0


def test_process_order_rarity_scoring(agent, test_location_nyc, test_location_brooklyn):
    """Test rarity score increases with value and priority"""
    low_priority_pkg = Package(
        package_id="low",
        weight_kg=1.0,
        dimensions={"length": 10, "width": 10, "height": 10},
        contents="Low value",
        fragile=False,
        temperature_controlled=False,
        value_usd=50,
        priority=1
    )
    
    high_priority_pkg = Package(
        package_id="high",
        weight_kg=1.0,
        dimensions={"length": 10, "width": 10, "height": 10},
        contents="High value",
        fragile=True,
        temperature_controlled=True,
        value_usd=3000,
        priority=5
    )
    
    low_result = agent.process_order(
        customer_id="cust_low",
        package=low_priority_pkg,
        pickup_location=test_location_nyc,
        delivery_location=test_location_brooklyn,
        priority=1
    )
    
    high_result = agent.process_order(
        customer_id="cust_high",
        package=high_priority_pkg,
        pickup_location=test_location_nyc,
        delivery_location=test_location_brooklyn,
        priority=5
    )
    
    assert high_result["rarity_score"] > low_result["rarity_score"]


def test_process_order_dynamic_pricing(agent, test_location_nyc, test_location_brooklyn):
    """Test dynamic pricing markup calculation"""
    pkg = Package(
        package_id="pricing_test",
        weight_kg=2.0,
        dimensions={"length": 20, "width": 20, "height": 20},
        contents="Test",
        fragile=False,
        temperature_controlled=False,
        value_usd=200,
        priority=3
    )
    
    result = agent.process_order(
        customer_id="cust_pricing",
        package=pkg,
        pickup_location=test_location_nyc,
        delivery_location=test_location_brooklyn,
        priority=3
    )
    
    # Dynamic price should be higher than base with priority 3
    assert result["dynamic_price_usd"] > result["base_price_usd"]
    
    # Calculate expected markup
    priority_markup = (3 / 5) * 0.3  # up to 30% for priority
    rarity_markup = (result["rarity_score"] / 100) * 0.5
    expected_min = result["base_price_usd"] * (1 + priority_markup + rarity_markup - 0.1)
    
    assert result["dynamic_price_usd"] >= expected_min


# ============================================================================
# PHASE 2: ROUTE OPTIMIZATION TESTS
# ============================================================================

def test_optimize_route_short_distance(agent, test_location_nyc, test_location_brooklyn, test_package_standard):
    """Test route optimization for short distance"""
    waypoints = agent.optimize_route(
        pickup=test_location_nyc,
        delivery=test_location_brooklyn,
        package=test_package_standard,
        num_waypoints=2
    )
    
    assert len(waypoints) >= 2
    assert waypoints[0].latitude == test_location_nyc.latitude
    assert waypoints[-1].latitude == test_location_brooklyn.latitude


def test_optimize_route_long_distance(agent, test_location_nyc, test_location_london, test_package_vip):
    """Test route optimization for long distance (international)"""
    waypoints = agent.optimize_route(
        pickup=test_location_nyc,
        delivery=test_location_london,
        package=test_package_vip,
        num_waypoints=3
    )
    
    # Long distance should have multiple waypoints
    assert len(waypoints) > 2
    assert waypoints[0].latitude == test_location_nyc.latitude
    assert waypoints[-1].latitude == test_location_london.latitude


def test_estimate_delivery_time_short(agent, test_location_nyc, test_location_brooklyn):
    """Test delivery time estimation for short route"""
    waypoints = [test_location_nyc, test_location_brooklyn]
    
    economy_time = agent._estimate_delivery_time(waypoints, DroneType.ECONOMY)
    premium_time = agent._estimate_delivery_time(waypoints, DroneType.PREMIUM)
    
    # Premium should be faster than economy
    assert premium_time < economy_time
    assert economy_time > 0
    assert premium_time > 0


def test_haversine_distance_calculation(agent):
    """Test Haversine distance calculation"""
    nyc = (40.7128, -74.0060)
    brooklyn = (40.6501, -73.9496)
    
    distance = agent._haversine_distance(nyc, brooklyn)
    
    # NYC to Brooklyn is approximately 8-9 km
    assert 7 < distance < 10


# ============================================================================
# PHASE 3: DISPATCH TESTS
# ============================================================================

def test_dispatch_drone(agent, test_package_standard, test_location_nyc, test_location_brooklyn):
    """Test drone dispatch"""
    # First create order
    result = agent.process_order(
        customer_id="cust_001",
        package=test_package_standard,
        pickup_location=test_location_nyc,
        delivery_location=test_location_brooklyn,
        priority=2
    )
    order_id = result["order_id"]
    
    # Dispatch drone
    dispatch_result = agent.dispatch_drone(order_id)
    
    assert dispatch_result["success"] == True
    assert "drone_id" in dispatch_result
    assert dispatch_result["dispatch_time"]
    assert dispatch_result["estimated_arrival"]
    assert "node_dispatch" in dispatch_result
    
    # Verify order status updated
    assert agent.active_orders[order_id].status == DeliveryStatus.DISPATCHED


def test_dispatch_nonexistent_order(agent):
    """Test dispatch of non-existent order"""
    result = agent.dispatch_drone("nonexistent_order")
    
    assert result["success"] == False
    assert "error" in result


def test_drone_allocation(agent):
    """Test drone allocation from fleet"""
    agent._initialize_drone_fleet()
    
    pkg = Package(
        package_id="alloc_test",
        weight_kg=2.0,
        dimensions={"length": 20, "width": 20, "height": 20},
        contents="Test",
        fragile=False,
        temperature_controlled=False,
        value_usd=100,
        priority=2
    )
    
    order = DeliveryOrder(
        order_id="test_order",
        customer_id="cust_test",
        package=pkg,
        pickup_location=Location(40.7128, -74.0060, "NYC", "north_america"),
        delivery_location=Location(40.6501, -73.9496, "Brooklyn", "north_america"),
        rarity_score=50,
        drone_type=DroneType.ECONOMY,
        estimated_time_min=15,
        route_waypoints=[],
        status=DeliveryStatus.PENDING,
        price_usd=25.0,
        dynamic_price_usd=25.0,
        created_at=time.time()
    )
    
    drone = agent._allocate_drone(order)
    
    assert drone is not None
    assert drone.status == "assigned"


# ============================================================================
# PHASE 4: TRACKING TESTS
# ============================================================================

def test_track_status_pending(agent, test_package_standard, test_location_nyc, test_location_brooklyn):
    """Test tracking pending order"""
    result = agent.process_order(
        customer_id="cust_001",
        package=test_package_standard,
        pickup_location=test_location_nyc,
        delivery_location=test_location_brooklyn,
        priority=2
    )
    order_id = result["order_id"]
    
    status = agent.track_status(order_id)
    
    assert status["success"] == True
    assert status["order_id"] == order_id
    assert status["status"] == "pending"


def test_track_status_in_flight(agent, test_package_standard, test_location_nyc, test_location_brooklyn):
    """Test tracking in-flight order"""
    result = agent.process_order(
        customer_id="cust_001",
        package=test_package_standard,
        pickup_location=test_location_nyc,
        delivery_location=test_location_brooklyn,
        priority=2
    )
    order_id = result["order_id"]
    
    # Dispatch
    agent.dispatch_drone(order_id)
    
    # Track - should transition to in_flight
    status = agent.track_status(order_id)
    
    assert status["success"] == True
    assert status["status"] == "in_flight"
    assert "current_location" in status


def test_track_status_delivered(agent, test_package_standard, test_location_nyc, test_location_brooklyn):
    """Test tracking completed delivery"""
    result = agent.process_order(
        customer_id="cust_001",
        package=test_package_standard,
        pickup_location=test_location_nyc,
        delivery_location=test_location_brooklyn,
        priority=2
    )
    order_id = result["order_id"]
    
    # Dispatch
    agent.dispatch_drone(order_id)
    
    # Track through all phases
    agent.track_status(order_id)  # dispatched -> in_flight
    agent.track_status(order_id)  # in_flight -> arriving
    status = agent.track_status(order_id)  # arriving -> delivered
    
    assert status["success"] == True
    assert status["status"] == "delivered"
    assert status["delivered_at"] is not None
    assert status["revenue_usd"] > 0


def test_track_nonexistent_order(agent):
    """Test tracking non-existent order"""
    status = agent.track_status("nonexistent_order")
    
    assert status["success"] == False
    assert "error" in status


# ============================================================================
# PHASE 5: METRICS & ANALYTICS
# ============================================================================

def test_performance_metrics_initial(agent):
    """Test initial performance metrics"""
    metrics = agent.get_performance_metrics()
    
    assert metrics["agent_id"] == "test_agent"
    assert metrics["total_deliveries"] == 0
    assert metrics["successful_deliveries"] == 0
    assert metrics["total_revenue_usd"] == 0.0


def test_performance_metrics_after_delivery(agent, test_package_standard, test_location_nyc, test_location_brooklyn):
    """Test metrics after completing delivery"""
    # Process order
    result = agent.process_order(
        customer_id="cust_001",
        package=test_package_standard,
        pickup_location=test_location_nyc,
        delivery_location=test_location_brooklyn,
        priority=2
    )
    order_id = result["order_id"]
    
    # Dispatch and complete
    agent.dispatch_drone(order_id)
    agent.track_status(order_id)  # dispatched -> in_flight
    agent.track_status(order_id)  # in_flight -> arriving
    agent.track_status(order_id)  # arriving -> delivered
    
    metrics = agent.get_performance_metrics()
    
    assert metrics["total_deliveries"] == 1
    assert metrics["successful_deliveries"] == 1
    assert metrics["total_revenue_usd"] > 0.0
    assert metrics["success_rate"] == 100.0


def test_batch_status_check(agent, test_package_standard, test_location_nyc, test_location_brooklyn):
    """Test batch status retrieval"""
    # Create multiple orders
    order_ids = []
    for i in range(3):
        result = agent.process_order(
            customer_id=f"cust_{i}",
            package=test_package_standard,
            pickup_location=test_location_nyc,
            delivery_location=test_location_brooklyn,
            priority=2
        )
        order_ids.append(result["order_id"])
    
    # Get batch status
    batch_status = agent.get_order_status_batch(order_ids)
    
    assert len(batch_status) == 3
    for status in batch_status:
        assert "order_id" in status
        assert "status" in status
        assert "price_usd" in status


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_delivery_lifecycle(agent, test_package_standard, test_location_nyc, test_location_brooklyn):
    """Test complete delivery lifecycle: Request → Route → Dispatch → Track → Confirm"""
    print("\n\n=== FULL LIFECYCLE TEST ===")
    
    # Step 1: Process order
    print("1. Processing order...")
    result = agent.process_order(
        customer_id="cust_lifecycle",
        package=test_package_standard,
        pickup_location=test_location_nyc,
        delivery_location=test_location_brooklyn,
        priority=2
    )
    assert result["success"] == True
    order_id = result["order_id"]
    print(f"   ✓ Order created: {order_id}")
    
    # Step 2: Verify route optimization
    print("2. Route optimization...")
    order = agent.active_orders[order_id]
    assert len(order.route_waypoints) > 0
    print(f"   ✓ Route optimized with {len(order.route_waypoints)} waypoints")
    
    # Step 3: Dispatch drone
    print("3. Dispatching drone...")
    dispatch = agent.dispatch_drone(order_id)
    assert dispatch["success"] == True
    print(f"   ✓ Drone {dispatch['drone_id']} dispatched")
    
    # Step 4: Track progress
    print("4. Tracking delivery...")
    statuses = []
    for i in range(4):
        status = agent.track_status(order_id)
        statuses.append(status["status"])
        print(f"   Step {i+1}: {status['status'].upper()}")
    
    # Verify progression
    assert statuses[0] == "in_flight"
    assert statuses[1] == "arriving"
    assert statuses[2] == "delivered"
    
    # Step 5: Verify completion
    print("5. Verifying completion...")
    final_status = agent.track_status(order_id)
    assert final_status["status"] == "delivered"
    assert final_status["revenue_usd"] > 0
    print(f"   ✓ Revenue: ${final_status['revenue_usd']:.2f}")
    
    # Verify metrics updated
    metrics = agent.get_performance_metrics()
    assert metrics["total_deliveries"] == 1
    assert metrics["successful_deliveries"] == 1
    print(f"   ✓ Metrics: {metrics['successful_deliveries']} successful")
    
    print("=== LIFECYCLE TEST PASSED ✓ ===\n")


def test_multi_order_scenario(agent):
    """Test handling multiple concurrent orders"""
    print("\n\n=== MULTI-ORDER SCENARIO ===")
    
    locations = [
        (40.7128, -74.0060),  # NYC
        (40.6501, -73.9496),  # Brooklyn
        (51.5074, -0.1278),   # London
    ]
    
    orders = []
    for i in range(5):
        pickup_lat, pickup_lon = locations[i % len(locations)]
        delivery_lat, delivery_lon = locations[(i + 1) % len(locations)]
        
        pkg = Package(
            package_id=f"pkg_multi_{i}",
            weight_kg=random.uniform(1, 5),
            dimensions={"length": 20, "width": 20, "height": 20},
            contents=f"Package {i}",
            fragile=random.choice([True, False]),
            temperature_controlled=False,
            value_usd=random.uniform(100, 2000),
            priority=random.randint(1, 5)
        )
        
        result = agent.process_order(
            customer_id=f"cust_multi_{i}",
            package=pkg,
            pickup_location=Location(pickup_lat, pickup_lon, f"Location {i}", "test"),
            delivery_location=Location(delivery_lat, delivery_lon, f"Location {(i+1)%len(locations)}", "test"),
            priority=pkg.priority
        )
        
        if result["success"]:
            orders.append(result["order_id"])
            print(f"Order {i+1}: {result['order_id'][:12]}... | Score: {result['rarity_score']:.1f}")
    
    print(f"✓ Created {len(orders)} orders")
    print(f"✓ Active orders: {len(agent.active_orders)}")
    print("=== MULTI-ORDER TEST PASSED ✓ ===\n")


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    import random
    
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
