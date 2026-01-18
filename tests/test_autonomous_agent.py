"""
Tests for Autonomous Business Agent.
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from autonomous_business_agent import (
    AutonomousBusinessAgent,
    Metrics,
    Action,
    DATA_DIR
)


@pytest.fixture
def agent():
    """Create test agent instance."""
    return AutonomousBusinessAgent(
        base_url="http://localhost:5000",
        leads_threshold=10,
        revenue_threshold=1000.0,
        error_threshold=0.05
    )


@pytest.fixture
def sample_metrics():
    """Sample metrics for testing."""
    return Metrics(
        timestamp=time.time(),
        revenue_today=500.0,
        leads_today=5,
        error_rate=0.02,
        active_subscriptions=10,
        mrr=50000.0
    )


def test_metrics_dataclass():
    """Test Metrics dataclass."""
    metrics = Metrics(
        timestamp=1234567890.0,
        revenue_today=1500.0,
        leads_today=20,
        error_rate=0.01,
        active_subscriptions=15,
        mrr=75000.0
    )
    
    assert metrics.revenue_today == 1500.0
    assert metrics.leads_today == 20
    assert metrics.error_rate == 0.01
    
    # Test to_dict
    data = metrics.to_dict()
    assert data["revenue_today"] == 1500.0
    assert data["leads_today"] == 20


def test_action_dataclass():
    """Test Action dataclass."""
    action = Action(
        timestamp=time.time(),
        action_type="content_generated",
        details={"reason": "low_leads", "content_length": 250},
        success=True
    )
    
    assert action.action_type == "content_generated"
    assert action.success is True
    assert action.details["reason"] == "low_leads"
    
    # Test to_dict
    data = action.to_dict()
    assert data["action_type"] == "content_generated"


def test_agent_initialization(agent):
    """Test agent initialization with thresholds."""
    assert agent.base_url == "http://localhost:5000"
    assert agent.leads_threshold == 10
    assert agent.revenue_threshold == 1000.0
    assert agent.error_threshold == 0.05


@patch('autonomous_business_agent.requests.get')
def test_fetch_internal_metrics(mock_get, agent):
    """Test fetching metrics from internal API."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "revenue_today": 2500.0,
        "leads_today": 15,
        "error_rate": 0.01,
        "active_subscriptions": 20,
        "mrr": 100000.0
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    result = agent._fetch_internal_metrics()
    
    assert result["revenue_today"] == 2500.0
    assert result["leads_today"] == 15
    mock_get.assert_called_once()


@patch('autonomous_business_agent.requests.get')
def test_fetch_stripe_revenue(mock_get, agent, monkeypatch):
    """Test fetching revenue from Stripe."""
    monkeypatch.setenv("STRIPE_API_KEY", "sk_test_123")
    
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"amount": 199900, "paid": True},  # ₹1999
            {"amount": 99900, "paid": True},   # ₹999
            {"amount": 50000, "paid": False}   # Not paid, skip
        ]
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    revenue = agent._fetch_stripe_revenue()
    
    assert revenue == 2998.0  # (199900 + 99900) / 100
    mock_get.assert_called_once()


@patch('autonomous_business_agent.generate_ai_content')
@patch('autonomous_business_agent.send_email')
def test_generate_content(mock_email, mock_ai, agent, sample_metrics):
    """Test content generation via Claude."""
    mock_ai.return_value = """🚀 Here's why 99% of businesses will fail in 2026...

They're still doing manual work while AI is eating the world.

We built SURESH AI ORIGIN - 48 AI systems that run your business on autopilot.

→ Destiny Blueprint: Your exact path to ₹10L/month
→ Business Consciousness: Multi-industry AI brain
→ Perfect Timing: Never make wrong decisions again

99.95% uptime. Zero manual work.

Join the top 1%: https://sureshaiorigin.com

The future doesn't wait."""
    
    agent.generate_content(reason="low_leads", metrics=sample_metrics)
    
    # Verify AI was called
    mock_ai.assert_called_once()
    prompt = mock_ai.call_args[0][0]
    assert "low_leads" in prompt
    assert "Destiny Blueprint" in prompt
    
    # Verify email sent
    mock_email.assert_called_once()


@patch('autonomous_business_agent.requests.post')
def test_deploy_update(mock_post, agent, sample_metrics, monkeypatch):
    """Test deployment trigger via GitHub Actions."""
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test123")
    
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    agent.deploy_update(reason="high_error_rate", metrics=sample_metrics)
    
    # Verify GitHub API called
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "github.com" in call_args[0][0]
    assert call_args[1]["json"]["inputs"]["reason"] == "high_error_rate"


def test_build_content_prompt(agent, sample_metrics):
    """Test content prompt building."""
    prompt = agent._build_content_prompt("low_leads", sample_metrics)
    
    assert "low_leads" in prompt
    assert "5 leads today" in prompt
    assert "₹500.00 revenue" in prompt
    assert "Destiny Blueprint" in prompt
    assert "https://sureshaiorigin.com" in prompt


@patch('autonomous_business_agent.send_email')
def test_send_alert(mock_email, agent, sample_metrics):
    """Test alert sending."""
    agent._send_alert(
        title="Low Revenue Alert",
        message="Revenue below threshold",
        metrics=sample_metrics
    )
    
    mock_email.assert_called_once()
    call_args = mock_email.call_args
    assert "Low Revenue Alert" in call_args[1]["subject"]
    assert "Revenue below threshold" in call_args[1]["body"]


def test_log_metrics(agent, sample_metrics):
    """Test metrics logging to JSONL."""
    agent._log_metrics(sample_metrics)
    
    # Verify file exists and contains data
    assert (DATA_DIR / "agent_metrics.jsonl").exists()
    
    with open(DATA_DIR / "agent_metrics.jsonl", 'r') as f:
        lines = f.readlines()
        last_line = json.loads(lines[-1])
        assert last_line["revenue_today"] == 500.0
        assert last_line["leads_today"] == 5


def test_log_action(agent):
    """Test action logging to JSONL."""
    action = Action(
        timestamp=time.time(),
        action_type="content_generated",
        details={"test": "data"},
        success=True
    )
    
    agent._log_action(action)
    
    # Verify file exists and contains data
    assert (DATA_DIR / "agent_actions.jsonl").exists()
    
    with open(DATA_DIR / "agent_actions.jsonl", 'r') as f:
        lines = f.readlines()
        last_line = json.loads(lines[-1])
        assert last_line["action_type"] == "content_generated"
        assert last_line["success"] is True


@patch('autonomous_business_agent.AutonomousBusinessAgent.monitor_metrics')
@patch('autonomous_business_agent.AutonomousBusinessAgent.generate_content')
def test_check_and_act_low_leads(mock_generate, mock_monitor, agent):
    """Test monitoring cycle triggers content generation on low leads."""
    mock_monitor.return_value = Metrics(
        timestamp=time.time(),
        revenue_today=2000.0,
        leads_today=3,  # Below threshold of 10
        error_rate=0.01,
        active_subscriptions=10,
        mrr=50000.0
    )
    
    agent._check_and_act()
    
    # Verify content generation triggered
    mock_generate.assert_called_once()
    assert mock_generate.call_args[1]["reason"] == "low_leads"


@patch('autonomous_business_agent.AutonomousBusinessAgent.monitor_metrics')
@patch('autonomous_business_agent.AutonomousBusinessAgent.deploy_update')
def test_check_and_act_high_errors(mock_deploy, mock_monitor, agent):
    """Test monitoring cycle triggers deployment on high error rate."""
    mock_monitor.return_value = Metrics(
        timestamp=time.time(),
        revenue_today=2000.0,
        leads_today=20,
        error_rate=0.10,  # Above threshold of 0.05
        active_subscriptions=10,
        mrr=50000.0
    )
    
    agent._check_and_act()
    
    # Verify deployment triggered
    mock_deploy.assert_called_once()
    assert mock_deploy.call_args[1]["reason"] == "high_error_rate"


@patch('autonomous_business_agent.AutonomousBusinessAgent.monitor_metrics')
@patch('autonomous_business_agent.AutonomousBusinessAgent._send_alert')
def test_check_and_act_low_revenue(mock_alert, mock_monitor, agent):
    """Test monitoring cycle sends alert on low revenue."""
    mock_monitor.return_value = Metrics(
        timestamp=time.time(),
        revenue_today=500.0,  # Below threshold of 1000
        leads_today=20,
        error_rate=0.01,
        active_subscriptions=10,
        mrr=50000.0
    )
    
    agent._check_and_act()
    
    # Verify alert sent
    mock_alert.assert_called()
    call_args = mock_alert.call_args
    assert "Low Revenue Alert" in call_args[1]["title"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
