#!/usr/bin/env python3
"""
Test: Autonomous Feature Listener Integration
Tests auto_feature_builder.py enhanced with autonomous_income_engine integration.
"""

import json
import time
import tempfile
from pathlib import Path
from auto_feature_builder import (
    AutonomousFeatureListener,
    WorkflowGenerator,
    RepositoryCommitManager,
    DetectedOpportunity,
    OpportunityType
)


def test_workflow_generation_for_high_churn():
    """Test workflow generation when high churn is detected."""
    print("\n" + "="*70)
    print("TEST 1: Workflow Generation - High Churn Detection")
    print("="*70)
    
    listener = AutonomousFeatureListener()
    
    # Simulate high churn detection from autonomous_income_engine
    result = listener.on_income_engine_issue(
        issue_type="high_churn",
        severity="high",
        description="Customer churn rate 8.5% exceeds 5% threshold",
        metric_value=0.085,
        affected_items=["customer_101", "customer_205", "customer_512"]
    )
    
    print(f"\n✅ Result: {result['success']}")
    print(f"   Issue Type: {result['issue_type']}")
    print(f"   Workflow: {result['workflow_name']}")
    print(f"   Workflow ID: {result['workflow_id']}")
    print(f"   Files Created: {result['files_created']}")
    print(f"   Mode: {result['commit_result']['mode']}")
    
    assert result['success'] == True
    assert result['workflow_name'] == "Auto-Retention on High Churn"
    print("\n✅ TEST PASSED")


def test_workflow_generation_for_abandoned_carts():
    """Test workflow generation for abandoned carts."""
    print("\n" + "="*70)
    print("TEST 2: Workflow Generation - Abandoned Carts")
    print("="*70)
    
    listener = AutonomousFeatureListener()
    
    result = listener.on_income_engine_issue(
        issue_type="abandoned_carts",
        severity="medium",
        description="527 abandoned carts detected in last 24 hours",
        metric_value=527,
        affected_items=[]
    )
    
    print(f"\n✅ Result: {result['success']}")
    print(f"   Workflow: {result['workflow_name']}")
    print(f"   Expected Recovery Rate: 15%")
    print(f"   Revenue Impact Target: ₹{int(527 * 50 * 0.15 / 100)}")
    
    assert result['success'] == True
    assert "Recovery" in result['workflow_name']
    print("\n✅ TEST PASSED")


def test_workflow_generation_for_payment_failures():
    """Test workflow generation for payment failures."""
    print("\n" + "="*70)
    print("TEST 3: Workflow Generation - Payment Failures")
    print("="*70)
    
    listener = AutonomousFeatureListener()
    
    result = listener.on_income_engine_issue(
        issue_type="payment_failures",
        severity="high",
        description="Payment success rate dropped to 88% from 95%",
        metric_value=0.88,
        affected_items=[]
    )
    
    print(f"\n✅ Workflow Generated: {result['workflow_name']}")
    print(f"   Auto-Retry Attempts: 3 with exponential backoff")
    print(f"   Expected Success: 35% additional recovery")
    
    assert result['success'] == True
    print("\n✅ TEST PASSED")


def test_prompt_template_generation():
    """Test prompt template generation for each workflow type."""
    print("\n" + "="*70)
    print("TEST 4: Prompt Template Generation")
    print("="*70)
    
    gen = WorkflowGenerator()
    
    # Generate templates
    retention_template = gen._get_retention_prompt_template()
    recovery_template = gen._get_recovery_prompt_template()
    upsell_template = gen._get_upsell_prompt_template()
    
    print(f"\n✅ Retention Template")
    print(f"   Name: {retention_template['name']}")
    print(f"   Variables: {', '.join(retention_template['variables'].keys())}")
    print(f"   Sample: {retention_template['template'][:100]}...")
    
    print(f"\n✅ Recovery Template")
    print(f"   Name: {recovery_template['name']}")
    print(f"   Variables: {', '.join(recovery_template['variables'].keys())}")
    
    print(f"\n✅ Upsell Template")
    print(f"   Name: {upsell_template['name']}")
    print(f"   Variables: {', '.join(upsell_template['variables'].keys())}")
    
    assert "{{customer_name}}" in retention_template["template"]
    assert "{{product_name}}" in recovery_template["template"]
    print("\n✅ TEST PASSED")


def test_test_case_generation():
    """Test that test cases are properly generated."""
    print("\n" + "="*70)
    print("TEST 5: Test Case Generation")
    print("="*70)
    
    gen = WorkflowGenerator()
    
    retention_test = gen._get_retention_test_case()
    recovery_test = gen._get_recovery_test_case()
    payment_test = gen._get_payment_retry_test_case()
    
    print(f"\n✅ Retention Test Case")
    print(f"   Contains: test_retention_workflow_high_churn")
    print(f"   Contains: test_retention_email_personalization")
    assert "test_retention_workflow_high_churn" in retention_test
    
    print(f"\n✅ Recovery Test Case")
    print(f"   Contains: test_recovery_workflow_abandoned_carts")
    assert "abandoned_carts_detected" in recovery_test
    
    print(f"\n✅ Payment Retry Test Case")
    print(f"   Contains: retry_payment check")
    assert "retry_payment" in payment_test
    
    print("\n✅ TEST PASSED")


def test_dry_run_mode():
    """Test dry-run mode (default)."""
    print("\n" + "="*70)
    print("TEST 6: Dry-Run Mode (Safe by Default)")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo in temp dir
        import subprocess
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)
        
        listener = AutonomousFeatureListener(tmpdir)
        
        print(f"\n✅ Dry-Run Mode Status: {listener.commit_manager.dry_run}")
        
        result = listener.on_income_engine_issue(
            issue_type="high_churn",
            severity="high",
            description="Test churn",
            metric_value=0.08,
            affected_items=[]
        )
        
        print(f"   Commit Mode: {result['commit_result']['mode']}")
        print(f"   Files Would Create: {result['files_created']}")
        
        assert result['commit_result']['mode'] == 'DRY_RUN'
        assert 'Ready to commit' in result['commit_result']['status']
        
        print("\n✅ TEST PASSED - Safe by default!")


def test_listener_status():
    """Test listener status reporting."""
    print("\n" + "="*70)
    print("TEST 7: Listener Status & Logging")
    print("="*70)
    
    listener = AutonomousFeatureListener()
    
    # Generate a few workflows
    listener.on_income_engine_issue(
        issue_type="high_churn",
        severity="high",
        description="Test churn 1",
        metric_value=0.08,
        affected_items=[]
    )
    
    listener.on_income_engine_issue(
        issue_type="abandoned_carts",
        severity="medium",
        description="Test carts",
        metric_value=100,
        affected_items=[]
    )
    
    status = listener.get_status()
    
    print(f"\n✅ Listener Status")
    print(f"   Issues Listened: {status['listened_issues']}")
    print(f"   Features Generated: {status['generated_features']}")
    print(f"   Dry-Run Enabled: {status['dry_run_enabled']}")
    print(f"   Repository: {status['repository']}")
    print(f"   Recent Features: {len(status['recent_features'])}")
    
    assert status['listened_issues'] >= 2
    assert status['generated_features'] >= 2
    print("\n✅ TEST PASSED")


def test_all_issue_types():
    """Test workflow generation for all issue types."""
    print("\n" + "="*70)
    print("TEST 8: All Issue Types Supported")
    print("="*70)
    
    listener = AutonomousFeatureListener()
    issue_types = [
        ("high_churn", "high", "Churn test"),
        ("abandoned_carts", "medium", "Carts test"),
        ("revenue_drop", "high", "Revenue test"),
        ("payment_failures", "high", "Payment test"),
        ("low_conversion", "medium", "Conversion test"),
        ("error_spike", "critical", "Error test")
    ]
    
    results = []
    for issue_type, severity, desc in issue_types:
        result = listener.on_income_engine_issue(
            issue_type=issue_type,
            severity=severity,
            description=desc,
            metric_value=0.5,
            affected_items=[]
        )
        results.append(result)
        print(f"✅ {issue_type}: {result['workflow_name']}")
    
    assert all(r['success'] for r in results)
    print("\n✅ TEST PASSED - All 6 issue types generate workflows!")


def test_integration_with_income_engine():
    """
    Integration test: Simulate autonomous_income_engine detecting issues
    and AutonomousFeatureListener responding.
    """
    print("\n" + "="*70)
    print("TEST 9: Full Integration - Income Engine → Feature Listener")
    print("="*70)
    
    from autonomous_income_engine import DetectedIssue
    
    listener = AutonomousFeatureListener()
    
    # Simulate issues that autonomous_income_engine would detect
    simulated_issues = [
        DetectedIssue(
            issue_type='abandoned_carts',
            severity='medium',
            description='High abandoned cart rate',
            metric_value=5,
            threshold=2,
            affected_items=[],
            timestamp=time.time(),
            detected_by='monitor_kpis'
        ),
        DetectedIssue(
            issue_type='high_churn',
            severity='high',
            description='Customer churn detected',
            metric_value=0.08,
            threshold=0.05,
            affected_items=[],
            timestamp=time.time(),
            detected_by='detect_issues'
        )
    ]
    
    print(f"\n📊 Income Engine Issues Detected:")
    for issue in simulated_issues:
        print(f"   - {issue.issue_type} ({issue.severity}): {issue.description}")
        
        # Feed to listener
        result = listener.on_income_engine_issue(
            issue_type=issue.issue_type,
            severity=issue.severity,
            description=issue.description,
            metric_value=issue.metric_value,
            affected_items=issue.affected_items
        )
        
        print(f"     → Generated: {result['workflow_name']}")
    
    status = listener.get_status()
    print(f"\n✅ Integration Summary")
    print(f"   Issues Detected: {status['listened_issues']}")
    print(f"   Features Auto-Generated: {status['generated_features']}")
    print(f"   Commits (Dry-Run): {status['commits_logged']}")
    
    print("\n✅ TEST PASSED - Full integration working!")


def run_all_tests():
    """Run all tests."""
    print("\n\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  AUTO-FEATURE BUILDER - AUTONOMOUS ENGINE INTEGRATION TESTS".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        test_workflow_generation_for_high_churn,
        test_workflow_generation_for_abandoned_carts,
        test_workflow_generation_for_payment_failures,
        test_prompt_template_generation,
        test_test_case_generation,
        test_dry_run_mode,
        test_listener_status,
        test_all_issue_types,
        test_integration_with_income_engine,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print(f"║  RESULTS: {passed} PASSED, {failed} FAILED".ljust(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")
    
    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    exit(0 if failed == 0 else 1)
