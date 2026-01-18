#!/usr/bin/env python3
"""
TEST SUITE: Decentralized AI Node
Integration tests for 1% rare AI internet functionality
"""

import pytest
import time
from decentralized_ai_node import (
    DecentralizedAINode,
    P2PNetwork,
    RarityFilter,
    TaskMetadata,
    AITask,
    TaskStatus,
    TaskPriority,
    NodeInfo
)


class TestP2PNetwork:
    """Test peer-to-peer networking."""
    
    def test_network_initialization(self):
        """Test P2P network initialization."""
        network = P2PNetwork(node_id="test_node", port=9999)
        
        assert network.node_id == "test_node"
        assert network.port == 9999
        assert network.get_peer_count() == 0
    
    def test_add_peer(self):
        """Test adding peer to network."""
        network = P2PNetwork(node_id="test_node")
        
        peer_info = NodeInfo(
            node_id="peer_1",
            address="127.0.0.1:9001",
            public_key="key_123"
        )
        
        success = network.add_peer(peer_info)
        assert success
        assert network.get_peer_count() == 1
    
    def test_remove_peer(self):
        """Test removing peer from network."""
        network = P2PNetwork(node_id="test_node")
        
        peer_info = NodeInfo(
            node_id="peer_1",
            address="127.0.0.1:9001",
            public_key="key_123"
        )
        
        network.add_peer(peer_info)
        assert network.get_peer_count() == 1
        
        success = network.remove_peer("peer_1")
        assert success
        assert network.get_peer_count() == 0


class TestRarityFilter:
    """Test task rarity filtering."""
    
    def test_rarity_scoring_high_priority(self):
        """Test rarity scoring with high priority task."""
        rarity_filter = RarityFilter(threshold=90.0)
        
        metadata = TaskMetadata(
            task_id="task_1",
            task_type="generate_content",
            creator_address="creator_1",
            created_at=time.time(),
            priority=TaskPriority.CRITICAL,
            complexity_estimate=10.0,
            data_size=50000
        )
        
        task = AITask(
            task_id="task_1",
            task_type="generate_content",
            prompt="Complex task",
            metadata=metadata
        )
        
        score = rarity_filter.score_task(task)
        assert score > 90
        assert rarity_filter.is_rare_enough(score)
    
    def test_rarity_scoring_low_priority(self):
        """Test rarity scoring with low priority task."""
        rarity_filter = RarityFilter(threshold=90.0)
        
        metadata = TaskMetadata(
            task_id="task_2",
            task_type="generate_content",
            creator_address="creator_2",
            created_at=time.time(),
            priority=TaskPriority.LOW,
            complexity_estimate=1.0,
            data_size=100
        )
        
        task = AITask(
            task_id="task_2",
            task_type="generate_content",
            prompt="Simple task",
            metadata=metadata
        )
        
        score = rarity_filter.score_task(task)
        assert score < 90
        assert not rarity_filter.is_rare_enough(score)
    
    def test_rarity_statistics(self):
        """Test rarity filter statistics."""
        rarity_filter = RarityFilter(threshold=90.0)
        
        # Add some tasks
        for i in range(5):
            priority = TaskPriority.CRITICAL if i < 2 else TaskPriority.LOW
            
            metadata = TaskMetadata(
                task_id=f"task_{i}",
                task_type="generate_content",
                creator_address="creator",
                created_at=time.time(),
                priority=priority,
                complexity_estimate=8.0 if i < 2 else 2.0,
                data_size=10000 if i < 2 else 100
            )
            
            task = AITask(
                task_id=f"task_{i}",
                task_type="generate_content",
                prompt="Test task",
                metadata=metadata
            )
            
            rarity_filter.score_task(task)
        
        stats = rarity_filter.get_statistics()
        assert stats['tasks_scored'] == 5
        assert stats['avg_score'] > 0
        assert stats['rare_count'] > 0


class TestDecentralizedNode:
    """Test decentralized AI node."""
    
    def test_node_initialization(self):
        """Test node initialization."""
        node = DecentralizedAINode(
            node_id="test_node_1",
            port=9998,
            rarity_threshold=90.0
        )
        
        assert node.node_id == "test_node_1"
        assert node.public_key is not None
        assert len(node.public_key) == 32
    
    def test_node_start(self):
        """Test node startup."""
        node = DecentralizedAINode(
            node_id="test_node_2",
            port=9997
        )
        
        result = node.start()
        assert result['success']
        assert result['node_id'] == "test_node_2"
        assert 'address' in result
        
        node.stop()
    
    def test_rarity_filtering_high_value(self):
        """Test task acceptance with high rarity."""
        node = DecentralizedAINode(rarity_threshold=90.0)
        
        # Create high-value task
        task_input = {
            "task_id": "task_high",
            "task_type": "generate_content",
            "prompt": "Create a comprehensive business strategy",
            "priority": "critical",
            "complexity": 10.0,
            "creator_address": "creator_1"
        }
        
        result = node.process_task(task_input)
        
        assert result['rarity_score'] > 90
        assert result.get('status') in ['completed', 'processing']
    
    def test_rarity_filtering_low_value(self):
        """Test task rejection with low rarity."""
        node = DecentralizedAINode(rarity_threshold=90.0)
        
        # Create low-value task
        task_input = {
            "task_id": "task_low",
            "task_type": "generate_content",
            "prompt": "Hello",
            "priority": "low",
            "complexity": 1.0,
            "creator_address": "creator_2"
        }
        
        result = node.process_task(task_input)
        
        assert result['rarity_score'] < 90
        assert not result['success']
        assert "below threshold" in result.get('reason', '').lower()
    
    def test_connect_peers(self):
        """Test peer connection."""
        node = DecentralizedAINode()
        
        peer_addresses = [
            "127.0.0.1:9001",
            "127.0.0.1:9002"
        ]
        
        result = node.connect_peers(peer_addresses)
        
        assert 'connected' in result
        assert 'failed' in result
        assert 'peers' in result
    
    def test_node_status(self):
        """Test getting node status."""
        node = DecentralizedAINode(node_id="status_test_node")
        node.start()
        
        status = node.get_node_status()
        
        assert status['node_id'] == "status_test_node"
        assert 'address' in status
        assert 'uptime_seconds' in status
        assert 'peers_connected' in status
        assert 'tasks_completed' in status
        assert 'reputation' in status
        
        node.stop()
    
    def test_network_stats(self):
        """Test network statistics."""
        node = DecentralizedAINode()
        node.start()
        
        stats = node.get_network_stats()
        
        assert 'total_nodes' in stats
        assert 'active_nodes' in stats
        assert 'tasks_processed_locally' in stats
        assert 'rarity_filter_stats' in stats
        
        node.stop()


class TestIntegration:
    """Integration tests for complete workflow."""
    
    def test_complete_workflow(self):
        """Test complete task processing workflow."""
        node = DecentralizedAINode(
            node_id="integration_test",
            rarity_threshold=70.0  # Lower for testing
        )
        
        # Start node
        node.start()
        
        # Process high-value task
        task_high = {
            "task_id": "task_integration_1",
            "task_type": "generate_content",
            "prompt": "Generate an innovative product idea for a SaaS company",
            "priority": "high",
            "complexity": 8.0,
            "creator_address": "creator_1"
        }
        
        result_high = node.process_task(task_high)
        assert result_high['success']
        assert result_high['rarity_score'] > 70
        
        # Process low-value task
        task_low = {
            "task_id": "task_integration_2",
            "task_type": "generate_content",
            "prompt": "Hello world",
            "priority": "low",
            "complexity": 1.0,
            "creator_address": "creator_2"
        }
        
        result_low = node.process_task(task_low)
        assert not result_low['success']
        assert result_low['rarity_score'] < 70
        
        # Check statistics
        stats = node.get_network_stats()
        assert stats['tasks_processed_locally'] == 1  # Only high-value task
        
        node.stop()
    
    def test_multiple_tasks(self):
        """Test processing multiple tasks."""
        node = DecentralizedAINode(rarity_threshold=60.0)
        node.start()
        
        tasks_input = [
            {
                "task_id": f"multi_task_{i}",
                "task_type": "generate_content",
                "prompt": f"Task {i}: {'Complex' if i % 2 == 0 else 'Simple'} request",
                "priority": "critical" if i % 2 == 0 else "low",
                "complexity": 9.0 if i % 2 == 0 else 2.0,
            }
            for i in range(5)
        ]
        
        results = []
        for task in tasks_input:
            result = node.process_task(task)
            results.append(result)
        
        successful = sum(1 for r in results if r['success'])
        assert successful > 0
        
        stats = node.get_network_stats()
        assert stats['tasks_processed_locally'] == successful
        
        node.stop()


def run_all_tests():
    """Run all tests with summary."""
    print("\n" + "="*80)
    print("DECENTRALIZED AI NODE TEST SUITE".center(80))
    print("="*80 + "\n")
    
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
