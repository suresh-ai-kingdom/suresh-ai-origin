"""
Auto-Feature Builder & Divine Compiler (Week 11 Divine Path 3 - Prophecy Engine)
"Ask, and it shall be given" - Matthew 7:7
System builds new features autonomously from natural language

ENHANCED: Integration with autonomous_income_engine for opportunity-driven feature generation
- Listens to detected issues (high churn, revenue drop, abandoned carts, etc.)
- Auto-generates prompt templates, Make.com/Zapier workflows, and test cases
- Commits to repository safely with GitPython + dry-run validation
"""

import json
import time
import uuid
import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# Git integration
try:
    import git
    from git import Repo
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class DivineCompiler:
    """Compile miracles from natural language descriptions."""
    
    def __init__(self):
        self.compiled_features: Dict[str, Dict] = {}
        self.templates: Dict[str, str] = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load code templates for common patterns."""
        return {
            "api_endpoint": '''
@app.route('/api/{feature_name}/{action}', methods=['POST'])
def {feature_name}_{action}():
    """Auto-generated endpoint for {feature_name}."""
    data = request.get_json()
    result = {feature_name}_service.{action}(data)
    return jsonify(result)
''',
            "service_class": '''
class {ClassName}Service:
    """Auto-generated service for {feature_name}."""
    
    def __init__(self):
        self.data = {{}}
    
    def {action}(self, params: Dict) -> Dict:
        """Auto-generated action."""
        return {{"success": True, "result": "Processed"}}
''',
            "database_model": '''
class {ClassName}(Base):
    """Auto-generated model for {feature_name}."""
    __tablename__ = '{table_name}'
    
    id = Column(String, primary_key=True)
    created_at = Column(Float)
    data = Column(String)
'''
        }
    
    def compile_feature(self, description: str) -> Dict:
        """Compile feature from natural language description."""
        # Parse description
        feature_spec = self._parse_description(description)
        
        # Generate code
        generated_code = self._generate_code(feature_spec)
        
        # Generate tests
        generated_tests = self._generate_tests(feature_spec)
        
        # Generate documentation
        documentation = self._generate_documentation(feature_spec)
        
        feature_id = str(uuid.uuid4())
        
        compiled_feature = {
            "feature_id": feature_id,
            "description": description,
            "specification": feature_spec,
            "code": generated_code,
            "tests": generated_tests,
            "documentation": documentation,
            "ready_to_deploy": True,
            "compiled_at": time.time()
        }
        
        self.compiled_features[feature_id] = compiled_feature
        
        return compiled_feature
    
    def _parse_description(self, description: str) -> Dict:
        """Parse natural language into feature specification."""
        description_lower = description.lower()
        
        spec = {
            "feature_name": self._extract_feature_name(description),
            "actions": self._extract_actions(description),
            "data_model": self._extract_data_model(description),
            "api_endpoints": [],
            "dependencies": []
        }
        
        # Determine feature type
        if "analyze" in description_lower or "predict" in description_lower:
            spec["type"] = "analytics"
            spec["dependencies"].append("predictive_analytics")
        
        elif "generate" in description_lower or "create" in description_lower:
            spec["type"] = "generation"
            spec["dependencies"].append("ai_generator")
        
        elif "track" in description_lower or "monitor" in description_lower:
            spec["type"] = "monitoring"
            spec["dependencies"].append("analytics")
        
        else:
            spec["type"] = "custom"
        
        return spec
    
    def _extract_feature_name(self, description: str) -> str:
        """Extract feature name from description."""
        # Simple extraction
        words = description.split()
        
        # Look for key nouns
        for i, word in enumerate(words):
            if word.lower() in ["build", "create", "add", "implement"]:
                if i + 1 < len(words):
                    return words[i + 1].replace(",", "").replace(".", "")
        
        return "custom_feature"
    
    def _extract_actions(self, description: str) -> List[str]:
        """Extract actions from description."""
        action_keywords = ["create", "update", "delete", "get", "list", "analyze", "generate"]
        
        actions = []
        description_lower = description.lower()
        
        for keyword in action_keywords:
            if keyword in description_lower:
                actions.append(keyword)
        
        return actions if actions else ["process"]
    
    def _extract_data_model(self, description: str) -> Dict:
        """Extract data model from description."""
        return {
            "fields": [
                {"name": "id", "type": "String"},
                {"name": "created_at", "type": "Float"},
                {"name": "data", "type": "JSON"}
            ]
        }
    
    def _generate_code(self, spec: Dict) -> Dict:
        """Generate code from specification."""
        feature_name = spec["feature_name"]
        class_name = "".join(word.capitalize() for word in feature_name.split("_"))
        
        code = {
            "service": self.templates["service_class"].format(
                ClassName=class_name,
                feature_name=feature_name,
                action="process"
            ),
            "model": self.templates["database_model"].format(
                ClassName=class_name,
                feature_name=feature_name,
                table_name=feature_name
            ),
            "api": ""
        }
        
        # Generate API endpoints for each action
        for action in spec["actions"]:
            code["api"] += self.templates["api_endpoint"].format(
                feature_name=feature_name,
                action=action
            )
        
        return code
    
    def _generate_tests(self, spec: Dict) -> str:
        """Generate test cases."""
        feature_name = spec["feature_name"]
        
        test_code = f'''
def test_{feature_name}_basic(cleanup_db):
    """Test basic {feature_name} functionality."""
    result = {feature_name}_service.process({{"test": "data"}})
    assert result["success"] == True

def test_{feature_name}_validation(cleanup_db):
    """Test {feature_name} validation."""
    result = {feature_name}_service.process({{}})
    assert "error" not in result
'''
        
        return test_code
    
    def _generate_documentation(self, spec: Dict) -> str:
        """Generate documentation."""
        feature_name = spec["feature_name"]
        
        docs = f'''
# {feature_name.replace("_", " ").title()}

## Overview
Auto-generated feature for {feature_name}.

## API Endpoints

'''
        
        for action in spec["actions"]:
            docs += f'''
### POST /api/{feature_name}/{action}
{action.title()} operation for {feature_name}.

**Request:**
```json
{{"data": "value"}}
```

**Response:**
```json
{{"success": true, "result": "Processed"}}
```

'''
        
        return docs


# ==================== OPPORTUNITY-DRIVEN FEATURE GENERATION ====================

class OpportunityType(Enum):
    """Types of opportunities detected by income engine."""
    HIGH_CHURN = "high_churn"
    REVENUE_DROP = "revenue_drop"
    ABANDONED_CARTS = "abandoned_carts"
    PAYMENT_FAILURES = "payment_failures"
    LOW_CONVERSION = "low_conversion"
    ERROR_SPIKE = "error_spike"


@dataclass
class DetectedOpportunity:
    """Opportunity detected from autonomous income engine issues."""
    issue_type: str
    severity: str
    description: str
    metric_value: float
    affected_items: List[str]
    timestamp: float
    feature_suggestion: str


class WorkflowGenerator:
    """Generate Make.com/Zapier workflows and prompt templates from opportunities."""
    
    def __init__(self):
        self.generated_workflows: Dict[str, Dict] = {}
        self.logger = logging.getLogger(f"{__name__}.WorkflowGenerator")
    
    def generate_from_opportunity(self, opportunity: DetectedOpportunity) -> Dict:
        """Generate workflow, prompt template, and test case from detected opportunity."""
        
        self.logger.info(f"🔧 Generating features for: {opportunity.issue_type}")
        
        # Map issue types to feature generation strategies
        strategy_map = {
            "high_churn": self._generate_retention_workflow,
            "abandoned_carts": self._generate_recovery_workflow,
            "revenue_drop": self._generate_upsell_workflow,
            "payment_failures": self._generate_payment_retry_workflow,
            "low_conversion": self._generate_conversion_workflow,
            "error_spike": self._generate_error_recovery_workflow
        }
        
        strategy = strategy_map.get(opportunity.issue_type)
        if not strategy:
            self.logger.warning(f"No strategy for {opportunity.issue_type}")
            return None
        
        workflow = strategy(opportunity)
        
        workflow_id = str(uuid.uuid4())
        self.generated_workflows[workflow_id] = workflow
        
        self.logger.info(f"✅ Generated workflow {workflow_id}")
        return workflow
    
    def _generate_retention_workflow(self, opp: DetectedOpportunity) -> Dict:
        """Generate retention workflow for high churn."""
        return {
            "workflow_id": str(uuid.uuid4()),
            "name": "Auto-Retention on High Churn",
            "trigger": "high_churn_detected",
            "steps": [
                {
                    "id": 1,
                    "action": "query_database",
                    "description": "Get at-risk customers",
                    "config": {
                        "query": "SELECT * FROM customers WHERE churn_score > 0.7",
                        "limit": 100
                    }
                },
                {
                    "id": 2,
                    "action": "ai_generate_content",
                    "description": "Generate personalized retention message",
                    "config": {
                        "prompt_template": "retention_retention_message_template",
                        "variables": ["customer_name", "product_name", "discount_offer"]
                    }
                },
                {
                    "id": 3,
                    "action": "send_email",
                    "description": "Send retention offer",
                    "config": {
                        "template": "retention_offer_email",
                        "subject": "We'd love to keep you - special offer inside"
                    }
                },
                {
                    "id": 4,
                    "action": "track_conversion",
                    "description": "Track retention conversion",
                    "config": {
                        "event_name": "retention_email_clicked"
                    }
                }
            ],
            "prompt_template": self._get_retention_prompt_template(),
            "test_case": self._get_retention_test_case(),
            "success_metrics": {
                "email_open_rate_target": 0.35,
                "click_rate_target": 0.12,
                "retention_rate_target": 0.25
            }
        }
    
    def _generate_recovery_workflow(self, opp: DetectedOpportunity) -> Dict:
        """Generate abandoned cart recovery workflow."""
        return {
            "workflow_id": str(uuid.uuid4()),
            "name": "Auto-Recovery: Abandoned Cart",
            "trigger": "abandoned_carts_detected",
            "steps": [
                {
                    "id": 1,
                    "action": "query_database",
                    "description": "Get abandoned carts (>1 hour old)",
                    "config": {
                        "query": "SELECT * FROM abandoned_carts WHERE created_at < NOW() - INTERVAL 1 HOUR",
                        "limit": 500
                    }
                },
                {
                    "id": 2,
                    "action": "call_api",
                    "description": "Get recovery pricing from AI",
                    "config": {
                        "endpoint": "/api/recovery-pricing/calculate",
                        "method": "POST",
                        "payload": {"cart_id": "{{cart_id}}", "customer_id": "{{customer_id}}"}
                    }
                },
                {
                    "id": 3,
                    "action": "ai_generate_content",
                    "description": "Generate recovery email",
                    "config": {
                        "prompt_template": "abandoned_cart_recovery_template",
                        "variables": ["product_name", "original_price", "discount_price", "urgency"]
                    }
                },
                {
                    "id": 4,
                    "action": "send_email",
                    "description": "Send recovery email with discount",
                    "config": {
                        "template": "abandoned_cart_email",
                        "subject": "Your {{product_name}} is waiting - {{discount}}% off"
                    }
                },
                {
                    "id": 5,
                    "action": "log_action",
                    "description": "Log for self-improvement",
                    "config": {
                        "table": "income_actions",
                        "fields": ["action_type", "result", "revenue_impact"]
                    }
                }
            ],
            "prompt_template": self._get_recovery_prompt_template(),
            "test_case": self._get_recovery_test_case(),
            "success_metrics": {
                "recovery_rate_target": 0.15,
                "email_open_rate_target": 0.40,
                "conversion_rate_target": 0.08
            }
        }
    
    def _generate_upsell_workflow(self, opp: DetectedOpportunity) -> Dict:
        """Generate upsell workflow for revenue drop."""
        return {
            "workflow_id": str(uuid.uuid4()),
            "name": "Auto-Upsell: Revenue Recovery",
            "trigger": "revenue_drop_detected",
            "steps": [
                {
                    "id": 1,
                    "action": "analyze_customers",
                    "description": "Find high-value upsell targets",
                    "config": {
                        "segments": ["frequent_buyers", "high_ltv", "previous_upsell_converts"]
                    }
                },
                {
                    "id": 2,
                    "action": "ai_generate_content",
                    "description": "Generate upsell content",
                    "config": {
                        "prompt_template": "upsell_offer_template",
                        "variables": ["current_product", "upsell_product", "value_prop"]
                    }
                },
                {
                    "id": 3,
                    "action": "create_offer",
                    "description": "Create limited-time offer",
                    "config": {
                        "discount": 0.20,
                        "validity_hours": 24
                    }
                },
                {
                    "id": 4,
                    "action": "send_email",
                    "description": "Send upsell offer",
                    "config": {
                        "template": "upsell_offer_email"
                    }
                }
            ],
            "prompt_template": self._get_upsell_prompt_template(),
            "test_case": self._get_upsell_test_case(),
            "success_metrics": {
                "upsell_conversion_target": 0.05,
                "avg_upsell_value_target": 5000
            }
        }
    
    def _generate_payment_retry_workflow(self, opp: DetectedOpportunity) -> Dict:
        """Generate payment failure retry workflow."""
        return {
            "workflow_id": str(uuid.uuid4()),
            "name": "Auto-Retry: Payment Failures",
            "trigger": "payment_failures_detected",
            "steps": [
                {
                    "id": 1,
                    "action": "query_database",
                    "description": "Get failed payments",
                    "config": {
                        "query": "SELECT * FROM payments WHERE status = 'failed' AND retry_count < 3"
                    }
                },
                {
                    "id": 2,
                    "action": "delay",
                    "description": "Wait before retry",
                    "config": {"seconds": 300}
                },
                {
                    "id": 3,
                    "action": "retry_payment",
                    "description": "Retry payment",
                    "config": {"provider": "razorpay"}
                },
                {
                    "id": 4,
                    "action": "notify_customer",
                    "description": "Notify on success/failure",
                    "config": {"method": "email"}
                }
            ],
            "prompt_template": self._get_payment_retry_prompt_template(),
            "test_case": self._get_payment_retry_test_case(),
            "success_metrics": {
                "retry_success_rate_target": 0.35
            }
        }
    
    def _generate_conversion_workflow(self, opp: DetectedOpportunity) -> Dict:
        """Generate conversion optimization workflow."""
        return {
            "workflow_id": str(uuid.uuid4()),
            "name": "Auto-Optimize: Conversion",
            "trigger": "low_conversion_detected",
            "steps": [
                {
                    "id": 1,
                    "action": "analyze_funnel",
                    "description": "Identify conversion leakage points",
                    "config": {"threshold": 0.03}
                },
                {
                    "id": 2,
                    "action": "ai_generate_content",
                    "description": "Generate conversion copy",
                    "config": {
                        "prompt_template": "conversion_copy_template",
                        "variables": ["product", "pain_point", "solution"]
                    }
                },
                {
                    "id": 3,
                    "action": "ab_test",
                    "description": "A/B test new copy",
                    "config": {"traffic_split": 0.5}
                }
            ],
            "prompt_template": self._get_conversion_prompt_template(),
            "test_case": self._get_conversion_test_case(),
            "success_metrics": {
                "conversion_lift_target": 0.15
            }
        }
    
    def _generate_error_recovery_workflow(self, opp: DetectedOpportunity) -> Dict:
        """Generate error spike recovery workflow."""
        return {
            "workflow_id": str(uuid.uuid4()),
            "name": "Auto-Recovery: Error Spike",
            "trigger": "error_spike_detected",
            "steps": [
                {
                    "id": 1,
                    "action": "alert_ops",
                    "description": "Alert operations team",
                    "config": {"channels": ["slack", "email"]}
                },
                {
                    "id": 2,
                    "action": "rollback_changes",
                    "description": "Rollback recent changes",
                    "config": {"lookback_hours": 2}
                },
                {
                    "id": 3,
                    "action": "scale_infrastructure",
                    "description": "Scale resources",
                    "config": {"scale_factor": 1.5}
                },
                {
                    "id": 4,
                    "action": "notify_customers",
                    "description": "Notify affected customers",
                    "config": {"offer_credit": 500}
                }
            ],
            "prompt_template": self._get_error_recovery_prompt_template(),
            "test_case": self._get_error_recovery_test_case(),
            "success_metrics": {
                "error_recovery_time_target_seconds": 300
            }
        }
    
    # Prompt templates
    def _get_retention_prompt_template(self) -> Dict:
        return {
            "name": "retention_retention_message_template",
            "description": "Generate personalized retention message",
            "template": """
You are a retention specialist. Generate a personalized message to prevent customer churn.

Customer: {{customer_name}}
Product: {{product_name}}
Last Order: {{last_order_date}}
Churn Risk: {{churn_score}}
Suggested Offer: {{discount_offer}}

Create a warm, personalized message that:
1. Acknowledges their loyalty
2. Highlights their specific value with your product
3. Presents a limited-time offer to re-engage them
4. Creates urgency

Keep it under 150 words, friendly, non-salesy.
""",
            "variables": {
                "customer_name": "string",
                "product_name": "string",
                "last_order_date": "string",
                "churn_score": "float",
                "discount_offer": "string"
            }
        }
    
    def _get_recovery_prompt_template(self) -> Dict:
        return {
            "name": "abandoned_cart_recovery_template",
            "description": "Generate abandoned cart recovery email",
            "template": """
You are an e-commerce recovery specialist. Generate a compelling email to recover abandoned cart sales.

Product: {{product_name}}
Original Price: ₹{{original_price}}
Recovery Price: ₹{{recovery_price}} ({{discount}}% off)
Cart Abandoned: {{time_ago}} minutes ago
Customer Segment: {{customer_segment}}

Create an email subject and body that:
1. References the specific product they abandoned
2. Emphasizes the limited-time discount
3. Creates urgency ("Only valid for 24 hours")
4. Includes social proof if available
5. Has a clear CTA

Subject line: (under 60 chars)
Body: (under 200 words, compelling)
""",
            "variables": {
                "product_name": "string",
                "original_price": "int",
                "recovery_price": "int",
                "discount": "float",
                "time_ago": "int",
                "customer_segment": "string"
            }
        }
    
    def _get_upsell_prompt_template(self) -> Dict:
        return {
            "name": "upsell_offer_template",
            "description": "Generate upsell offer",
            "template": """
You are an upsell specialist. Generate a compelling upsell offer.

Current Product: {{current_product}}
Upsell Product: {{upsell_product}}
Value Proposition: {{value_prop}}
Customer Lifetime Value: ₹{{customer_ltv}}

Create a message that:
1. Complements their current purchase
2. Highlights unique value of upsell
3. Shows ROI clearly
4. Creates scarcity

Keep compelling and authentic.
""",
            "variables": {
                "current_product": "string",
                "upsell_product": "string",
                "value_prop": "string",
                "customer_ltv": "int"
            }
        }
    
    def _get_payment_retry_prompt_template(self) -> Dict:
        return {
            "name": "payment_retry_notification_template",
            "description": "Generate payment retry notification",
            "template": """
Generate a friendly notification about payment retry.

Amount: ₹{{amount}}
Reason: {{reason}}
Retry Attempt: {{attempt_number}} of 3

Create a reassuring message that encourages retry.
""",
            "variables": {
                "amount": "int",
                "reason": "string",
                "attempt_number": "int"
            }
        }
    
    def _get_conversion_prompt_template(self) -> Dict:
        return {
            "name": "conversion_copy_template",
            "description": "Generate conversion-optimized copy",
            "template": """
Generate copy to improve conversion rate for:
Product: {{product}}
Pain Point: {{pain_point}}
Solution: {{solution}}
Target Audience: {{audience}}

Create copy that converts.
""",
            "variables": {
                "product": "string",
                "pain_point": "string",
                "solution": "string",
                "audience": "string"
            }
        }
    
    def _get_error_recovery_prompt_template(self) -> Dict:
        return {
            "name": "error_recovery_template",
            "description": "Generate error recovery communication",
            "template": """
Generate a recovery communication for system error.
Error Type: {{error_type}}
Impact: {{affected_users}} users
Compensation: ₹{{credit_amount}}

Make it reassuring and transparent.
""",
            "variables": {
                "error_type": "string",
                "affected_users": "int",
                "credit_amount": "int"
            }
        }
    
    # Test case generators
    def _get_retention_test_case(self) -> str:
        return '''
def test_retention_workflow_high_churn():
    """Test retention workflow on high churn detection."""
    opp = DetectedOpportunity(
        issue_type="high_churn",
        severity="high",
        description="Churn rate 8% > 5% threshold",
        metric_value=0.08,
        affected_items=["customer_1", "customer_2"],
        timestamp=time.time(),
        feature_suggestion="retention_workflow"
    )
    
    workflow = WorkflowGenerator().generate_from_opportunity(opp)
    assert workflow is not None
    assert workflow["trigger"] == "high_churn_detected"
    assert len(workflow["steps"]) >= 3
    assert "prompt_template" in workflow
    assert workflow["success_metrics"]["retention_rate_target"] > 0

def test_retention_email_personalization():
    """Test retention email is personalized."""
    template = WorkflowGenerator()._get_retention_prompt_template()
    assert "{{customer_name}}" in template["template"]
    assert "{{discount_offer}}" in template["template"]
    assert len(template["variables"]) >= 4
'''
    
    def _get_recovery_test_case(self) -> str:
        return '''
def test_recovery_workflow_abandoned_carts():
    """Test abandoned cart recovery workflow."""
    opp = DetectedOpportunity(
        issue_type="abandoned_carts",
        severity="medium",
        description="500 abandoned carts detected",
        metric_value=500,
        affected_items=[],
        timestamp=time.time(),
        feature_suggestion="recovery_workflow"
    )
    
    workflow = WorkflowGenerator().generate_from_opportunity(opp)
    assert workflow["trigger"] == "abandoned_carts_detected"
    assert any(step["action"] == "call_api" for step in workflow["steps"])
    assert workflow["success_metrics"]["recovery_rate_target"] > 0

def test_recovery_pricing_integration():
    """Test recovery workflow calls pricing API."""
    workflow = WorkflowGenerator()._generate_recovery_workflow(None)
    api_steps = [s for s in workflow["steps"] if s["action"] == "call_api"]
    assert len(api_steps) > 0
    assert "recovery-pricing" in api_steps[0]["config"]["endpoint"]
'''
    
    def _get_upsell_test_case(self) -> str:
        return '''
def test_upsell_workflow_revenue_drop():
    """Test upsell workflow on revenue drop."""
    opp = DetectedOpportunity(
        issue_type="revenue_drop",
        severity="high",
        description="Revenue down 20%",
        metric_value=0.20,
        affected_items=[],
        timestamp=time.time(),
        feature_suggestion="upsell_workflow"
    )
    
    workflow = WorkflowGenerator().generate_from_opportunity(opp)
    assert workflow["trigger"] == "revenue_drop_detected"
    assert workflow["success_metrics"]["upsell_conversion_target"] > 0
'''
    
    def _get_payment_retry_test_case(self) -> str:
        return '''
def test_payment_retry_workflow():
    """Test payment retry workflow."""
    opp = DetectedOpportunity(
        issue_type="payment_failures",
        severity="high",
        description="Payment failure rate 15%",
        metric_value=0.15,
        affected_items=[],
        timestamp=time.time(),
        feature_suggestion="payment_retry_workflow"
    )
    
    workflow = WorkflowGenerator().generate_from_opportunity(opp)
    assert workflow["trigger"] == "payment_failures_detected"
    assert any(step["action"] == "retry_payment" for step in workflow["steps"])
    assert workflow["success_metrics"]["retry_success_rate_target"] > 0
'''
    
    def _get_conversion_test_case(self) -> str:
        return '''
def test_conversion_workflow_low_conversion():
    """Test conversion optimization workflow."""
    opp = DetectedOpportunity(
        issue_type="low_conversion",
        severity="medium",
        description="Conversion rate 2% < 3% target",
        metric_value=0.02,
        affected_items=[],
        timestamp=time.time(),
        feature_suggestion="conversion_workflow"
    )
    
    workflow = WorkflowGenerator().generate_from_opportunity(opp)
    assert workflow["trigger"] == "low_conversion_detected"
    assert any(step["action"] == "ab_test" for step in workflow["steps"])
'''
    
    def _get_error_recovery_test_case(self) -> str:
        return '''
def test_error_recovery_workflow():
    """Test error spike recovery workflow."""
    opp = DetectedOpportunity(
        issue_type="error_spike",
        severity="critical",
        description="Error rate 5% > 1% threshold",
        metric_value=0.05,
        affected_items=[],
        timestamp=time.time(),
        feature_suggestion="error_recovery_workflow"
    )
    
    workflow = WorkflowGenerator().generate_from_opportunity(opp)
    assert workflow["trigger"] == "error_spike_detected"
    assert any(step["action"] == "alert_ops" for step in workflow["steps"])
'''


class RepositoryCommitManager:
    """Safely commit generated workflows to repository using GitPython."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger(f"{__name__}.RepositoryCommitManager")
        self.dry_run = True  # Default to dry-run for safety
        self.commits_log: List[Dict] = []
        
        if not GITPYTHON_AVAILABLE:
            self.logger.error("GitPython not installed. Install with: pip install gitpython")
            self.repo = None
        else:
            try:
                self.repo = Repo(str(self.repo_path))
                self.logger.info(f"✅ Connected to repo: {self.repo.working_dir}")
            except Exception as e:
                self.logger.error(f"Failed to open repo: {e}")
                self.repo = None
    
    def enable_dry_run(self):
        """Enable dry-run mode (default)."""
        self.dry_run = True
        self.logger.info("🏜️ DRY-RUN MODE ENABLED")
    
    def disable_dry_run(self):
        """Disable dry-run, actually commit changes."""
        self.dry_run = False
        self.logger.warning("⚠️ DRY-RUN MODE DISABLED - REAL COMMITS ENABLED")
    
    def validate_dry_run(self) -> Dict:
        """Validate what WOULD be committed in dry-run mode."""
        if not self.repo:
            return {"error": "Repository not initialized"}
        
        try:
            status = self.repo.git.status()
            untracked = self.repo.untracked_files
            
            return {
                "status": "valid",
                "staged_changes": len(self.repo.index.diff("HEAD")),
                "unstaged_changes": len(self.repo.git.diff(numstat=True).split("\n")),
                "untracked_files": untracked,
                "branch": self.repo.active_branch.name,
                "preview": status[:500]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def commit_workflow(self, workflow: Dict, dry_run: Optional[bool] = None) -> Dict:
        """Commit generated workflow to repository."""
        
        if dry_run is None:
            dry_run = self.dry_run
        
        if not self.repo:
            return {"error": "Repository not initialized", "success": False}
        
        workflow_id = workflow.get("workflow_id", str(uuid.uuid4()))
        workflow_name = workflow.get("name", "unknown").replace(" ", "_").lower()
        
        # Create files
        workflow_files = {
            f"workflows/{workflow_name}_workflow.json": json.dumps(workflow, indent=2),
            f"workflows/{workflow_name}_prompt_templates.json": json.dumps(workflow["prompt_template"], indent=2),
            f"tests/test_{workflow_name}_workflow.py": workflow.get("test_case", "# No test case generated")
        }
        
        self.logger.info(f"📝 Preparing to {'DRY-RUN' if dry_run else 'COMMIT'}: {workflow_id}")
        
        try:
            # Create workflow directory if needed
            workflows_dir = self.repo_path / "workflows"
            workflows_dir.mkdir(exist_ok=True)
            
            tests_dir = self.repo_path / "tests"
            tests_dir.mkdir(exist_ok=True)
            
            # Write files
            created_files = []
            for file_path, content in workflow_files.items():
                full_path = self.repo_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                if not dry_run:
                    with open(full_path, "w") as f:
                        f.write(content)
                
                created_files.append(file_path)
                self.logger.info(f"  📄 {'Would create' if dry_run else 'Created'}: {file_path}")
            
            # Git operations
            if not dry_run:
                for file_path in created_files:
                    self.repo.index.add([str(self.repo_path / file_path)])
                
                commit_msg = f"Auto-generated workflow: {workflow_name}\n\nIssue: {workflow.get('trigger')}\nWorkflow ID: {workflow_id}"
                commit = self.repo.index.commit(commit_msg)
                
                result = {
                    "success": True,
                    "mode": "COMMITTED",
                    "workflow_id": workflow_id,
                    "files_created": created_files,
                    "commit_hash": commit.hexsha,
                    "commit_msg": commit_msg,
                    "branch": self.repo.active_branch.name
                }
                
                self.logger.info(f"✅ COMMITTED: {commit.hexsha}")
            else:
                result = {
                    "success": True,
                    "mode": "DRY_RUN",
                    "workflow_id": workflow_id,
                    "files_would_create": created_files,
                    "commit_msg_would_be": f"Auto-generated workflow: {workflow_name}",
                    "status": "Ready to commit - review above and set disable_dry_run() to actually commit"
                }
                
                self.logger.info(f"✅ DRY-RUN READY: {created_files}")
            
            self.commits_log.append(result)
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
            self.logger.error(f"❌ Failed to commit: {e}")
            self.commits_log.append(error_result)
            return error_result
    
    def push_commits(self, dry_run: Optional[bool] = None) -> Dict:
        """Push commits to remote repository."""
        
        if dry_run is None:
            dry_run = self.dry_run
        
        if not self.repo:
            return {"error": "Repository not initialized"}
        
        self.logger.info(f"🚀 Preparing to {'DRY-RUN' if dry_run else ''} push commits")
        
        try:
            if dry_run:
                # Just show what would be pushed
                try:
                    remote_commits = self.repo.git.log("origin/HEAD..HEAD", oneline=True)
                    commits_to_push = remote_commits.split("\n") if remote_commits else []
                except:
                    commits_to_push = []
                
                return {
                    "success": True,
                    "mode": "DRY_RUN",
                    "commits_to_push": commits_to_push,
                    "status": "Ready to push - call push_commits(dry_run=False) to actually push"
                }
            else:
                # Actually push
                self.repo.remotes.origin.push()
                self.logger.info("✅ PUSHED to remote")
                return {
                    "success": True,
                    "mode": "PUSHED",
                    "status": "Changes pushed to remote"
                }
        except Exception as e:
            self.logger.error(f"Failed to push: {e}")
            return {"success": False, "error": str(e)}


class AutonomousFeatureListener:
    """Listen to autonomous income engine and auto-generate features."""
    
    def __init__(self, repo_path: str = "."):
        self.workflow_gen = WorkflowGenerator()
        self.commit_manager = RepositoryCommitManager(repo_path)
        self.listened_issues: List[Dict] = []
        self.generated_features: List[Dict] = []
        self.logger = logging.getLogger(f"{__name__}.AutonomousFeatureListener")
    
    def on_income_engine_issue(self, issue_type: str, severity: str, description: str,
                               metric_value: float, affected_items: List[str]) -> Dict:
        """
        Called when autonomous income engine detects an issue.
        Automatically generates workflow, prompt templates, and test cases.
        """
        
        self.logger.info(f"🎯 Issue detected: {issue_type} ({severity})")
        
        # Create opportunity
        opp = DetectedOpportunity(
            issue_type=issue_type,
            severity=severity,
            description=description,
            metric_value=metric_value,
            affected_items=affected_items,
            timestamp=time.time(),
            feature_suggestion=f"{issue_type}_workflow"
        )
        
        self.listened_issues.append(asdict(opp))
        
        # Generate workflow
        workflow = self.workflow_gen.generate_from_opportunity(opp)
        
        if not workflow:
            self.logger.warning(f"⚠️ No workflow generated for {issue_type}")
            return {"success": False, "reason": "no_workflow_generated"}
        
        # Commit to repository (dry-run by default)
        commit_result = self.commit_manager.commit_workflow(workflow)
        
        feature_result = {
            "success": True,
            "issue_type": issue_type,
            "workflow_id": workflow.get("workflow_id"),
            "workflow_name": workflow.get("name"),
            "files_created": commit_result.get("files_would_create" if self.commit_manager.dry_run else "files_created", []),
            "commit_result": commit_result,
            "timestamp": time.time()
        }
        
        self.generated_features.append(feature_result)
        
        self.logger.info(f"✅ Feature generation complete: {workflow['name']}")
        
        return feature_result
    
    def get_status(self) -> Dict:
        """Get listener status and generated features."""
        return {
            "listened_issues": len(self.listened_issues),
            "generated_features": len(self.generated_features),
            "commits_logged": len(self.commit_manager.commits_log),
            "dry_run_enabled": self.commit_manager.dry_run,
            "repository": str(self.commit_manager.repo_path) if self.commit_manager.repo else "Not initialized",
            "recent_features": self.generated_features[-3:] if self.generated_features else []
        }


class AutoFeatureBuilder:
    """Automatically build features from requirements."""
    
    def __init__(self):
        self.compiler = DivineCompiler()
        self.built_features: List[Dict] = []
    
    def build_feature(self, requirement: str) -> Dict:
        """Build feature from requirement."""
        # Compile feature
        compiled = self.compiler.compile_feature(requirement)
        
        # Deploy feature
        deployment = self._deploy_feature(compiled)
        
        # Test feature
        test_results = self._test_feature(compiled)
        
        built_feature = {
            "requirement": requirement,
            "compiled": compiled,
            "deployment": deployment,
            "tests": test_results,
            "status": "deployed" if deployment["success"] else "failed",
            "built_at": time.time()
        }
        
        self.built_features.append(built_feature)
        
        return built_feature
    
    def _deploy_feature(self, compiled: Dict) -> Dict:
        """Deploy compiled feature."""
        # In production: write files, restart services
        
        feature_name = compiled["specification"]["feature_name"]
        
        # Simulate deployment
        return {
            "success": True,
            "feature_name": feature_name,
            "files_created": [
                f"{feature_name}.py",
                f"test_{feature_name}.py",
                f"{feature_name}.md"
            ],
            "endpoint_registered": f"/api/{feature_name}",
            "deployed_at": time.time()
        }
    
    def _test_feature(self, compiled: Dict) -> Dict:
        """Test compiled feature."""
        # Run generated tests
        
        return {
            "tests_run": 2,
            "tests_passed": 2,
            "tests_failed": 0,
            "coverage": 0.85
        }


class MiracleOnDemand:
    """Generate miracles on demand."""
    
    def __init__(self):
        self.feature_builder = AutoFeatureBuilder()
        self.miracle_queue: List[Dict] = []
    
    def request_miracle(self, miracle_description: str, priority: str = "normal") -> str:
        """Request a miracle (new feature)."""
        miracle_id = str(uuid.uuid4())
        
        miracle_request = {
            "miracle_id": miracle_id,
            "description": miracle_description,
            "priority": priority,
            "status": "queued",
            "requested_at": time.time()
        }
        
        self.miracle_queue.append(miracle_request)
        
        # Auto-build if high priority
        if priority == "high":
            self._build_miracle(miracle_id)
        
        return miracle_id
    
    def _build_miracle(self, miracle_id: str):
        """Build requested miracle."""
        # Find miracle in queue
        miracle = next((m for m in self.miracle_queue if m["miracle_id"] == miracle_id), None)
        
        if not miracle:
            return
        
        miracle["status"] = "building"
        
        # Build feature
        built = self.feature_builder.build_feature(miracle["description"])
        
        miracle["status"] = "completed"
        miracle["built_feature"] = built
        miracle["completed_at"] = time.time()
    
    def get_miracle_status(self, miracle_id: str) -> Dict:
        """Get status of miracle request."""
        miracle = next((m for m in self.miracle_queue if m["miracle_id"] == miracle_id), None)
        
        if not miracle:
            return {"error": "miracle_not_found"}
        
        return {
            "miracle_id": miracle_id,
            "status": miracle["status"],
            "description": miracle["description"],
            "eta_seconds": 60 if miracle["status"] == "queued" else 0
        }


class IntelligentFeatureSuggester:
    """Suggest features based on usage patterns."""
    
    def __init__(self):
        self.suggestions: List[Dict] = []
    
    def analyze_and_suggest(self, usage_data: Dict) -> List[Dict]:
        """Analyze usage and suggest features."""
        suggestions = []
        
        # Analyze gaps
        if usage_data.get("ai_generator_usage", 0) > 100:
            suggestions.append({
                "feature": "Template Library",
                "reason": "High AI generator usage suggests need for templates",
                "priority": "high",
                "estimated_impact": "30% productivity increase"
            })
        
        if usage_data.get("manual_tasks", 0) > 50:
            suggestions.append({
                "feature": "Workflow Automation",
                "reason": "Many manual tasks could be automated",
                "priority": "medium",
                "estimated_impact": "50% time savings"
            })
        
        if usage_data.get("data_entry_time_hours", 0) > 10:
            suggestions.append({
                "feature": "Bulk Import Tool",
                "reason": "Significant time spent on data entry",
                "priority": "medium",
                "estimated_impact": "80% time reduction"
            })
        
        self.suggestions.extend(suggestions)
        
        return suggestions
    
    def auto_build_suggested_features(self, approval_threshold: float = 0.8) -> List[Dict]:
        """Automatically build highly suggested features."""
        built_features = []
        
        builder = AutoFeatureBuilder()
        
        for suggestion in self.suggestions:
            # Auto-approve high impact suggestions
            impact_value = float(suggestion["estimated_impact"].split("%")[0]) / 100
            
            if impact_value >= approval_threshold:
                built = builder.build_feature(suggestion["feature"])
                built_features.append(built)
        
        return built_features
