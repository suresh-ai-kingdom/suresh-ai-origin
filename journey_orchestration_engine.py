"""
Customer Journey Orchestration Engine (Feature #19)
Manages multi-touch customer journeys with real-time personalization,
dynamic branching, and attribution tracking across multiple channels.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import random
from collections import defaultdict


class TouchpointChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEB = "web"
    WEBHOOK = "webhook"


class JourneyStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PAUSED = "paused"
    ARCHIVED = "archived"


class StepType(Enum):
    EMAIL = "email"
    SMS = "sms"
    WAIT = "wait"
    DECISION = "decision"
    PUSH = "push"
    WEBHOOK = "webhook"
    ACTION = "action"


class StepStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    FAILED = "failed"
    SKIPPED = "skipped"


class TouchpointOptimizer:
    """Optimizes channel selection and timing for touchpoints"""

    def __init__(self):
        self.channel_performance = defaultdict(lambda: {"opens": 0, "clicks": 0, "conversions": 0, "sends": 0})
        self.time_performance = defaultdict(lambda: {"conversions": 0, "total": 0})
        self.segment_preferences = {}

    def add_engagement(self, channel: TouchpointChannel, opens: int, clicks: int, conversions: int, sends: int):
        """Record channel engagement metrics"""
        perf = self.channel_performance[channel.value]
        perf["opens"] += opens
        perf["clicks"] += clicks
        perf["conversions"] += conversions
        perf["sends"] += sends

    def recommend_channel(self, segment: str = "default", context: Dict = None) -> TouchpointChannel:
        """Recommend best channel for a segment based on performance history"""
        if not self.channel_performance:
            # Default recommendation strategy
            preferences = {
                "high_value": TouchpointChannel.EMAIL,
                "mobile_first": TouchpointChannel.PUSH,
                "budget_conscious": TouchpointChannel.SMS,
                "default": TouchpointChannel.EMAIL
            }
            return preferences.get(segment, preferences["default"])

        # Calculate conversion rate per channel
        channel_scores = {}
        for channel, metrics in self.channel_performance.items():
            if metrics["sends"] == 0:
                channel_scores[channel] = 0
                continue
            click_rate = metrics["clicks"] / max(metrics["sends"], 1)
            conversion_rate = metrics["conversions"] / max(metrics["sends"], 1)
            score = (click_rate * 0.3) + (conversion_rate * 0.7)
            channel_scores[channel] = score

        # Return best performing channel
        if channel_scores:
            best_channel = max(channel_scores, key=channel_scores.get)
            return TouchpointChannel(best_channel)
        return TouchpointChannel.EMAIL

    def recommend_time(self, segment: str = "default") -> str:
        """Recommend best time to send based on conversion history"""
        if not self.time_performance:
            return "09:00"  # Default to 9 AM

        best_hour = max(self.time_performance, key=lambda h: self.time_performance[h]["conversions"])
        return f"{best_hour}:00"

    def get_channel_performance(self) -> Dict:
        """Get performance summary for all channels"""
        summary = {}
        for channel, metrics in self.channel_performance.items():
            if metrics["sends"] == 0:
                summary[channel] = {"ctr": 0, "cvr": 0, "sends": 0}
            else:
                summary[channel] = {
                    "sends": metrics["sends"],
                    "ctr": round(metrics["clicks"] / metrics["sends"], 4),
                    "cvr": round(metrics["conversions"] / metrics["sends"], 4),
                    "opens": metrics["opens"]
                }
        return summary


class StepExecutor:
    """Executes individual journey steps with branch logic"""

    def __init__(self):
        self.step_history = []
        self.executed_steps = 0
        self.failed_steps = 0

    def execute_email_step(self, step_id: str, customer_id: str, email: str, subject: str, content: str) -> Tuple[bool, str]:
        """Execute email step"""
        try:
            # Simulate email sending with 95% success rate
            success = random.random() < 0.95
            status = StepStatus.SENT.value if success else StepStatus.FAILED.value
            
            self.step_history.append({
                "step_id": step_id,
                "customer_id": customer_id,
                "type": "email",
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "recipient": email
            })
            
            if success:
                self.executed_steps += 1
            else:
                self.failed_steps += 1
            
            return success, status
        except Exception as e:
            self.failed_steps += 1
            return False, f"error: {str(e)}"

    def execute_sms_step(self, step_id: str, customer_id: str, phone: str, message: str) -> Tuple[bool, str]:
        """Execute SMS step"""
        try:
            success = random.random() < 0.98
            status = StepStatus.SENT.value if success else StepStatus.FAILED.value
            
            self.step_history.append({
                "step_id": step_id,
                "customer_id": customer_id,
                "type": "sms",
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "recipient": phone
            })
            
            if success:
                self.executed_steps += 1
            else:
                self.failed_steps += 1
            
            return success, status
        except Exception as e:
            self.failed_steps += 1
            return False, f"error: {str(e)}"

    def execute_wait_step(self, step_id: str, duration_hours: int) -> bool:
        """Execute wait step"""
        self.step_history.append({
            "step_id": step_id,
            "type": "wait",
            "duration_hours": duration_hours,
            "status": StepStatus.PENDING.value,
            "scheduled_resume": (datetime.utcnow() + timedelta(hours=duration_hours)).isoformat()
        })
        return True

    def execute_decision_step(self, step_id: str, condition: Dict, context: Dict) -> Tuple[str, str]:
        """Execute conditional decision step with branching"""
        # Evaluate condition against context
        condition_key = condition.get("key")
        condition_value = condition.get("value")
        condition_operator = condition.get("operator", "equals")
        
        context_value = context.get(condition_key)
        
        met = False
        if condition_operator == "equals":
            met = context_value == condition_value
        elif condition_operator == "greater_than":
            met = float(context_value or 0) > float(condition_value)
        elif condition_operator == "less_than":
            met = float(context_value or 0) < float(condition_value)
        elif condition_operator == "contains":
            met = condition_value in str(context_value or "")
        
        path = "yes" if met else "no"
        self.step_history.append({
            "step_id": step_id,
            "type": "decision",
            "status": "evaluated",
            "condition": condition,
            "result": path,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return path, "yes_step_id" if met else "no_step_id"

    def get_step_analytics(self) -> Dict:
        """Get execution analytics"""
        total = self.executed_steps + self.failed_steps
        return {
            "executed_steps": self.executed_steps,
            "failed_steps": self.failed_steps,
            "total_steps": total,
            "success_rate": round(self.executed_steps / max(total, 1), 4),
            "history_count": len(self.step_history)
        }


class JourneyBuilder:
    """Builds and manages journey definitions"""

    def __init__(self):
        self.journeys = {}
        self.journey_counter = 0

    def create_journey(self, name: str, description: str, trigger: Dict) -> str:
        """Create a new journey"""
        journey_id = f"journey_{self.journey_counter}"
        self.journey_counter += 1
        
        self.journeys[journey_id] = {
            "id": journey_id,
            "name": name,
            "description": description,
            "trigger": trigger,
            "steps": [],
            "status": JourneyStatus.DRAFT.value,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "published_at": None,
            "segment": trigger.get("segment", "all"),
            "max_enrollments": trigger.get("max_enrollments"),
            "enrolled_count": 0,
            "completed_count": 0,
            "conversion_value": 0
        }
        return journey_id

    def add_step(self, journey_id: str, step_type: StepType, config: Dict, position: Optional[int] = None) -> bool:
        """Add a step to a journey"""
        if journey_id not in self.journeys:
            return False
        
        journey = self.journeys[journey_id]
        if journey["status"] != JourneyStatus.DRAFT.value:
            return False  # Can't add steps to published journeys
        
        step = {
            "step_id": f"step_{len(journey['steps'])}",
            "type": step_type.value,
            "config": config,
            "position": position if position is not None else len(journey["steps"]),
            "added_at": datetime.utcnow().isoformat()
        }
        
        if position is not None:
            journey["steps"].insert(position, step)
        else:
            journey["steps"].append(step)
        
        journey["updated_at"] = datetime.utcnow().isoformat()
        return True

    def publish_journey(self, journey_id: str) -> Tuple[bool, str]:
        """Publish a journey for enrollment"""
        if journey_id not in self.journeys:
            return False, "Journey not found"
        
        journey = self.journeys[journey_id]
        if len(journey["steps"]) == 0:
            return False, "Journey must have at least one step"
        
        journey["status"] = JourneyStatus.PUBLISHED.value
        journey["published_at"] = datetime.utcnow().isoformat()
        return True, "Journey published successfully"

    def get_journey(self, journey_id: str) -> Optional[Dict]:
        """Get journey details"""
        return self.journeys.get(journey_id)

    def list_journeys(self, status: Optional[str] = None) -> List[Dict]:
        """List journeys, optionally filtered by status"""
        journeys = list(self.journeys.values())
        if status:
            journeys = [j for j in journeys if j["status"] == status]
        return sorted(journeys, key=lambda j: j["created_at"], reverse=True)

    def get_journey_stats(self, journey_id: str) -> Dict:
        """Get journey performance statistics"""
        if journey_id not in self.journeys:
            return {}
        
        journey = self.journeys[journey_id]
        return {
            "journey_id": journey_id,
            "name": journey["name"],
            "status": journey["status"],
            "enrolled": journey["enrolled_count"],
            "completed": journey["completed_count"],
            "completion_rate": round(journey["completed_count"] / max(journey["enrolled_count"], 1), 4),
            "step_count": len(journey["steps"]),
            "total_value": journey["conversion_value"],
            "avg_value": round(journey["conversion_value"] / max(journey["completed_count"], 1), 2)
        }


class JourneyOrchestrator:
    """Main orchestration engine coordinating journey execution"""

    def __init__(self):
        self.builder = JourneyBuilder()
        self.executor = StepExecutor()
        self.optimizer = TouchpointOptimizer()
        self.active_customers = {}  # {customer_id: journey_state}
        self.completed_journeys = []
        self.customer_counter = 0

    def enroll_customer(self, journey_id: str, customer_id: str, customer_data: Dict) -> Tuple[bool, str]:
        """Enroll a customer in a journey"""
        journey = self.builder.get_journey(journey_id)
        if not journey:
            return False, "Journey not found"
        
        if journey["status"] != JourneyStatus.PUBLISHED.value:
            return False, "Journey is not published"
        
        if journey["max_enrollments"] and journey["enrolled_count"] >= journey["max_enrollments"]:
            return False, "Journey enrollment limit reached"
        
        # Check segment eligibility
        segment = customer_data.get("segment", "default")
        if journey["segment"] != "all" and segment != journey["segment"]:
            return False, f"Customer does not match segment {journey['segment']}"
        
        self.active_customers[customer_id] = {
            "journey_id": journey_id,
            "current_step": 0,
            "status": "active",
            "enrolled_at": datetime.utcnow().isoformat(),
            "customer_data": customer_data,
            "step_history": [],
            "conversions": 0,
            "engagement_score": 0
        }
        
        journey["enrolled_count"] += 1
        return True, f"Customer {customer_id} enrolled in journey {journey_id}"

    def process_step(self, customer_id: str) -> Tuple[bool, str]:
        """Process the next step for a customer"""
        if customer_id not in self.active_customers:
            return False, "Customer not found in active journeys"
        
        state = self.active_customers[customer_id]
        journey = self.builder.get_journey(state["journey_id"])
        
        if state["current_step"] >= len(journey["steps"]):
            state["status"] = "completed"
            self.completed_journeys.append({
                "customer_id": customer_id,
                "journey_id": state["journey_id"],
                "completed_at": datetime.utcnow().isoformat(),
                "journey_state": state
            })
            journey["completed_count"] += 1
            del self.active_customers[customer_id]
            return True, "Customer journey completed"
        
        step = journey["steps"][state["current_step"]]
        step_type = StepType(step["type"])
        config = step["config"]
        
        success = False
        message = ""
        
        if step_type == StepType.EMAIL:
            success, message = self.executor.execute_email_step(
                step["step_id"],
                customer_id,
                state["customer_data"].get("email", ""),
                config.get("subject", ""),
                config.get("content", "")
            )
        elif step_type == StepType.SMS:
            success, message = self.executor.execute_sms_step(
                step["step_id"],
                customer_id,
                state["customer_data"].get("phone", ""),
                config.get("message", "")
            )
        elif step_type == StepType.WAIT:
            success = self.executor.execute_wait_step(step["step_id"], config.get("hours", 1))
            message = f"Wait step scheduled for {config.get('hours', 1)} hours"
        elif step_type == StepType.DECISION:
            path, next_step = self.executor.execute_decision_step(step["step_id"], config.get("condition", {}), state["customer_data"])
            success = True
            message = f"Decision path: {path}"
        elif step_type == StepType.ACTION:
            success = True
            message = f"Action executed: {config.get('action_type', 'unknown')}"
        
        if success:
            state["step_history"].append({
                "step_id": step["step_id"],
                "type": step["type"],
                "result": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            state["current_step"] += 1
            state["engagement_score"] += random.uniform(0.5, 2.0)
        
        return success, message

    def track_conversion(self, customer_id: str, value: float = 1.0) -> Tuple[bool, str]:
        """Track a conversion for a customer"""
        # Check completed journeys first
        for completed in self.completed_journeys:
            if completed["customer_id"] == customer_id:
                completed["journey_state"]["conversions"] += 1
                completed["journey_state"]["journey_state"]["conversion_value"] = value
                return True, f"Conversion tracked: ${value}"
        
        if customer_id in self.active_customers:
            self.active_customers[customer_id]["conversions"] += 1
            return True, f"Conversion tracked: ${value}"
        
        return False, "Customer not found"

    def pause_customer_journey(self, customer_id: str) -> Tuple[bool, str]:
        """Pause a customer's journey"""
        if customer_id not in self.active_customers:
            return False, "Customer not found"
        
        self.active_customers[customer_id]["status"] = "paused"
        return True, "Journey paused"

    def resume_customer_journey(self, customer_id: str) -> Tuple[bool, str]:
        """Resume a paused journey"""
        if customer_id not in self.active_customers:
            return False, "Customer not found"
        
        self.active_customers[customer_id]["status"] = "active"
        return True, "Journey resumed"

    def get_journey_analytics(self, journey_id: str) -> Dict:
        """Get analytics for a journey"""
        journey = self.builder.get_journey(journey_id)
        if not journey:
            return {}
        
        # Calculate metrics from completed journeys
        completed_in_journey = [j for j in self.completed_journeys if j["journey_id"] == journey_id]
        
        total_engagement = sum(j["journey_state"]["engagement_score"] for j in completed_in_journey)
        total_conversions = sum(j["journey_state"]["conversions"] for j in completed_in_journey)
        
        return {
            "journey_id": journey_id,
            "total_enrolled": journey["enrolled_count"],
            "total_completed": journey["completed_count"],
            "completion_rate": round(journey["completed_count"] / max(journey["enrolled_count"], 1), 4),
            "total_conversions": total_conversions,
            "conversion_rate": round(total_conversions / max(journey["completed_count"], 1), 4),
            "avg_engagement_score": round(total_engagement / max(len(completed_in_journey), 1), 2),
            "active_customers": len([c for c in self.active_customers.values() if c["journey_id"] == journey_id]),
            "step_executor_stats": self.executor.get_step_analytics()
        }

    def get_orchestrator_stats(self) -> Dict:
        """Get overall orchestrator statistics"""
        total_journeys = len(self.builder.journeys)
        published_journeys = len(self.builder.list_journeys(status=JourneyStatus.PUBLISHED.value))
        
        total_enrolled = sum(j["enrolled_count"] for j in self.builder.journeys.values())
        total_completed = sum(j["completed_count"] for j in self.builder.journeys.values())
        
        return {
            "total_journeys": total_journeys,
            "published_journeys": published_journeys,
            "draft_journeys": len(self.builder.list_journeys(status=JourneyStatus.DRAFT.value)),
            "total_enrolled_customers": total_enrolled,
            "total_completed_customers": total_completed,
            "active_customers": len(self.active_customers),
            "completion_rate": round(total_completed / max(total_enrolled, 1), 4),
            "channel_performance": self.optimizer.get_channel_performance()
        }


# Demo data generator
def generate_demo_journeys() -> JourneyOrchestrator:
    """Generate demo journeys with realistic data"""
    orchestrator = JourneyOrchestrator()
    
    # Journey 1: Welcome Series
    welcome_id = orchestrator.builder.create_journey(
        name="Welcome Series",
        description="Onboarding series for new users",
        trigger={"type": "signup", "segment": "new_users"}
    )
    orchestrator.builder.add_step(welcome_id, StepType.EMAIL, {
        "subject": "Welcome to our platform!",
        "content": "Get started with our powerful features"
    })
    orchestrator.builder.add_step(welcome_id, StepType.WAIT, {"hours": 24})
    orchestrator.builder.add_step(welcome_id, StepType.EMAIL, {
        "subject": "Here's what you can do next",
        "content": "Feature highlights to maximize your success"
    })
    orchestrator.builder.publish_journey(welcome_id)
    
    # Journey 2: Abandoned Cart Recovery
    cart_id = orchestrator.builder.create_journey(
        name="Abandoned Cart Recovery",
        description="Win back customers with abandoned carts",
        trigger={"type": "cart_abandoned", "segment": "all"}
    )
    orchestrator.builder.add_step(cart_id, StepType.EMAIL, {
        "subject": "You left something behind",
        "content": "Complete your purchase"
    })
    orchestrator.builder.add_step(cart_id, StepType.WAIT, {"hours": 12})
    orchestrator.builder.add_step(cart_id, StepType.SMS, {"message": "Ready to checkout? Use code SAVE10"})
    orchestrator.builder.publish_journey(cart_id)
    
    # Journey 3: VIP Engagement
    vip_id = orchestrator.builder.create_journey(
        name="VIP Engagement Journey",
        description="Premium experience for high-value customers",
        trigger={"type": "high_lifetime_value", "segment": "vip"}
    )
    orchestrator.builder.add_step(vip_id, StepType.EMAIL, {
        "subject": "Exclusive VIP offer",
        "content": "Premium benefits await you"
    })
    orchestrator.builder.publish_journey(vip_id)
    
    # Simulate enrollments and completions
    for i in range(25):
        customer_data = {
            "customer_id": f"cust_{i}",
            "email": f"customer{i}@example.com",
            "phone": f"+1234567{i:04d}",
            "segment": "new_users" if i % 3 == 0 else "default"
        }
        orchestrator.enroll_customer(welcome_id, f"cust_{i}", customer_data)
    
    # Process some steps to show activity
    for customer_id in list(orchestrator.active_customers.keys())[:15]:
        for _ in range(2):
            orchestrator.process_step(customer_id)
    
    # Record some conversions
    for completed_journey in orchestrator.completed_journeys[:10]:
        orchestrator.track_conversion(completed_journey["customer_id"], random.uniform(10, 500))
    
    # Add channel performance data
    orchestrator.optimizer.add_engagement(
        TouchpointChannel.EMAIL, opens=450, clicks=180, conversions=45, sends=500
    )
    orchestrator.optimizer.add_engagement(
        TouchpointChannel.SMS, opens=200, clicks=95, conversions=30, sends=220
    )
    orchestrator.optimizer.add_engagement(
        TouchpointChannel.PUSH, opens=320, clicks=110, conversions=25, sends=400
    )
    
    return orchestrator
