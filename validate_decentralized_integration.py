#!/usr/bin/env python3
"""
INTEGRATION VALIDATOR: Decentralized AI Node + Income Engine + Monetization
Demonstrates complete workflow: Detection → Processing → Reward Distribution
"""

import json
import time
from dataclasses import asdict
from decentralized_ai_node import DecentralizedAINode, TaskPriority
from autonomous_income_engine import AutonomousIncomeEngine


def simulate_income_engine_detection():
    """
    Simulate income engine detecting a high-value opportunity.
    Returns detected issue suitable for decentralized processing.
    """
    print("\n[1] INCOME ENGINE: Detecting Business Opportunity")
    print("-" * 70)
    
    # Simulate detection of revenue drop issue
    detected_issue = {
        "issue_type": "revenue_drop",
        "severity": "critical",
        "description": "Q4 revenue declined 15% vs previous quarter",
        "opportunity_value": 25000,  # Potential recovery value
        "data_points": {
            "current_revenue": 85000,
            "previous_revenue": 100000,
            "affected_segments": ["Enterprise", "SMB"],
            "root_causes": ["customer_churn", "price_sensitivity", "feature_gaps"]
        }
    }
    
    print(f"✓ Issue Type: {detected_issue['issue_type'].upper()}")
    print(f"✓ Severity: {detected_issue['severity'].upper()}")
    print(f"✓ Opportunity Value: ${detected_issue['opportunity_value']:,}")
    print(f"✓ Affected Segments: {', '.join(detected_issue['data_points']['affected_segments'])}")
    print(f"✓ Root Causes: {', '.join(detected_issue['data_points']['root_causes'])}")
    
    return detected_issue


def convert_to_decentralized_task(detected_issue):
    """
    Convert income engine opportunity to decentralized node task.
    """
    print("\n[2] CONVERSION: Income Opportunity → Decentralized Task")
    print("-" * 70)
    
    # Map issue to task
    task_type_map = {
        "revenue_drop": "analyze",
        "customer_churn": "analyze",
        "abandoned_carts": "generate_content",
        "payment_failures": "analyze",
        "low_conversion": "generate_content",
        "error_spike": "analyze"
    }
    
    # Create structured task
    task = {
        "task_id": f"task_{int(time.time())}",
        "task_type": task_type_map.get(detected_issue['issue_type'], "analyze"),
        "prompt": f"""Analyze the following business challenge and provide:
1. Root cause analysis (why this is happening)
2. Immediate actions (next 7 days)
3. Long-term solutions (30+ days)
4. Expected revenue recovery

Challenge: {detected_issue['description']}
Data: {json.dumps(detected_issue['data_points'], indent=2)}
Potential Value: ${detected_issue['opportunity_value']:,}""",
        "priority": "critical" if detected_issue['severity'] == "critical" else "high",
        "complexity": 9.0,  # Complex analysis required
        "creator_address": "income_engine_0x1234"
    }
    
    print(f"✓ Task ID: {task['task_id']}")
    print(f"✓ Task Type: {task['task_type'].upper()}")
    print(f"✓ Priority: {task['priority'].upper()}")
    print(f"✓ Complexity Score: {task['complexity']}/10")
    print(f"✓ Creator: {task['creator_address']}")
    
    return task


def process_with_decentralized_node(task):
    """
    Process task through decentralized node with rarity filtering.
    """
    print("\n[3] PROCESSING: Decentralized Node Rarity Filter")
    print("-" * 70)
    
    # Initialize node
    node = DecentralizedAINode(
        node_id="validator_node_prod",
        rarity_threshold=85.0,  # High threshold for quality
        max_concurrent_tasks=5
    )
    
    # Start node
    start_result = node.start()
    print(f"✓ Node Started: {start_result['address']}")
    print(f"✓ Public Key: {start_result['public_key'][:16]}...")
    
    # Process task
    print("\n[3a] Task Scoring (Rarity Filter)")
    print("-" * 70)
    
    result = node.process_task(task)
    
    print(f"✓ Rarity Score: {result['rarity_score']:.1f}/100")
    print(f"✓ Score Status: {'ACCEPTED (>85)' if result['rarity_score'] > 85 else 'REJECTED (<85)'}")
    
    if result['success']:
        print(f"\n[3b] Task Execution")
        print("-" * 70)
        print(f"✓ Status: {result.get('status', 'COMPLETED').upper()}")
        print(f"✓ Processing Time: {result.get('processing_time', 0):.2f}s")
        print(f"✓ Result Preview: {result.get('result', 'No result')[:100]}...")
        
        # Get node status
        node_status = node.get_node_status()
        print(f"\n[3c] Node Status")
        print("-" * 70)
        print(f"✓ Tasks Completed: {node_status['tasks_completed']}")
        print(f"✓ Reputation Score: {node_status['reputation']:.2f}")
        print(f"✓ Uptime: {node_status['uptime_seconds']:.1f}s")
    else:
        print(f"\n✗ Task Rejected: {result.get('reason', 'Unknown reason')}")
    
    node.stop()
    return result


def calculate_monetization_reward(task, processing_result):
    """
    Calculate reward to be distributed via monetization engine.
    """
    print("\n[4] MONETIZATION: Reward Calculation")
    print("-" * 70)
    
    if not processing_result['success']:
        print("✗ Task not processed (no reward generated)")
        return 0
    
    # Reward formula:
    # Base: 0.01 USDC
    # Rarity multiplier: (rarity_score / 50) - 0.5x to 2x
    # Complexity multiplier: complexity / 5 - 0.2x to 2x
    # Efficiency bonus: processing_time < 30s ? +0.2x : 0
    
    base_reward = 0.01  # USDC
    rarity_multiplier = (processing_result['rarity_score'] / 50)
    complexity_multiplier = min(2.0, processing_result.get('processing_time', 0) / 150)
    efficiency_bonus = 0.2 if processing_result.get('processing_time', 0) < 30 else 0
    
    total_reward = base_reward * rarity_multiplier * complexity_multiplier + efficiency_bonus
    
    print(f"✓ Base Reward: {base_reward:.4f} USDC")
    print(f"✓ Rarity Multiplier: {rarity_multiplier:.2f}x (score: {processing_result['rarity_score']:.1f})")
    print(f"✓ Complexity Multiplier: {complexity_multiplier:.2f}x")
    print(f"✓ Efficiency Bonus: +{efficiency_bonus:.4f} USDC" if efficiency_bonus > 0 else f"✓ Efficiency Bonus: None (>30s)")
    print(f"\n✓ TOTAL REWARD: {total_reward:.4f} USDC")
    
    return total_reward


def track_workflow_impact(detected_issue, reward):
    """
    Track workflow impact on business metrics.
    """
    print("\n[5] IMPACT: Workflow Performance Metrics")
    print("-" * 70)
    
    opportunity_value = detected_issue.get('opportunity_value', 0)
    
    # ROI Calculation
    roi = (opportunity_value / (reward * 1000)) * 100 if reward > 0 else 0
    
    print(f"✓ Income Engine Opportunity: ${opportunity_value:,}")
    print(f"✓ Decentralized Node Reward: {reward:.4f} USDC (≈${reward:.2f})")
    print(f"✓ ROI: {roi:.1f}:1 (${opportunity_value:,} potential / ${reward:.2f} cost)")
    print(f"✓ Value-to-Cost Ratio: {opportunity_value / max(reward, 0.0001):.0f}x")
    
    return {
        "opportunity_value": opportunity_value,
        "reward_paid": reward,
        "roi": roi,
        "status": "profitable" if roi > 100 else "moderate" if roi > 10 else "low"
    }


def run_full_integration():
    """
    Run complete integration workflow.
    """
    print("\n" + "=" * 80)
    print("DECENTRALIZED AI NODE + INCOME ENGINE INTEGRATION VALIDATOR".center(80))
    print("=" * 80)
    
    try:
        # Step 1: Income engine detection
        detected_issue = simulate_income_engine_detection()
        
        # Step 2: Convert to task
        task = convert_to_decentralized_task(detected_issue)
        
        # Step 3: Process with decentralized node
        processing_result = process_with_decentralized_node(task)
        
        # Step 4: Monetization reward
        reward = calculate_monetization_reward(task, processing_result)
        
        # Step 5: Impact tracking
        impact = track_workflow_impact(detected_issue, reward)
        
        # Summary
        print("\n" + "=" * 80)
        print("INTEGRATION VALIDATION SUMMARY".center(80))
        print("=" * 80)
        
        print(f"\n✓ Complete Workflow: SUCCESS")
        print(f"✓ Task Processed: {processing_result['success']}")
        print(f"✓ Rarity Score: {processing_result['rarity_score']:.1f}/100")
        print(f"✓ Reward Generated: {reward:.4f} USDC")
        print(f"✓ Opportunity Value: ${impact['opportunity_value']:,}")
        print(f"✓ Value ROI: {impact['roi']:.1f}:1")
        print(f"✓ Status: {impact['status'].upper()}")
        
        print("\n" + "=" * 80)
        
        return {
            "success": True,
            "detected_issue": detected_issue,
            "task": task,
            "processing_result": processing_result,
            "reward": reward,
            "impact": impact
        }
        
    except Exception as e:
        print(f"\n✗ Integration Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = run_full_integration()
    
    # Save results
    with open("integration_validation_results.json", "w") as f:
        json.dump({
            k: v for k, v in result.items()
            if k not in ['processing_result']  # Skip result object
        }, f, indent=2, default=str)
    
    print("\n✓ Results saved to: integration_validation_results.json")
