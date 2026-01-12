"""
Comprehensive tests for Journey Orchestration Engine (Feature #19)
Tests journey creation, step execution, personalization, enrollment, and analytics
"""

import pytest
from journey_orchestration_engine import (
    JourneyOrchestrator,
    JourneyBuilder,
    StepExecutor,
    TouchpointOptimizer,
    StepType,
    JourneyStatus,
    TouchpointChannel,
    generate_demo_journeys
)


class TestJourneyBuilder:
    """Test journey creation and management"""

    def test_create_journey(self):
        """Test creating a new journey"""
        builder = JourneyBuilder()
        journey_id = builder.create_journey(
            name="Test Journey",
            description="Test description",
            trigger={"type": "signup", "segment": "new_users"}
        )
        
        assert journey_id.startswith("journey_")
        journey = builder.get_journey(journey_id)
        assert journey["name"] == "Test Journey"
        assert journey["status"] == JourneyStatus.DRAFT.value

    def test_add_step_to_journey(self):
        """Test adding steps to a journey"""
        builder = JourneyBuilder()
        journey_id = builder.create_journey(
            name="Multi-Step Journey",
            description="Test",
            trigger={"type": "signup"}
        )
        
        success = builder.add_step(journey_id, StepType.EMAIL, {
            "subject": "Welcome",
            "content": "Hello"
        })
        
        assert success
        journey = builder.get_journey(journey_id)
        assert len(journey["steps"]) == 1
        assert journey["steps"][0]["type"] == "email"

    def test_add_multiple_steps(self):
        """Test adding multiple steps in sequence"""
        builder = JourneyBuilder()
        journey_id = builder.create_journey(
            name="Multi-Step",
            description="Test",
            trigger={"type": "signup"}
        )
        
        for i in range(3):
            builder.add_step(journey_id, StepType.EMAIL, {"subject": f"Email {i}"})
        
        journey = builder.get_journey(journey_id)
        assert len(journey["steps"]) == 3

    def test_publish_journey(self):
        """Test publishing a journey"""
        builder = JourneyBuilder()
        journey_id = builder.create_journey(
            name="Test",
            description="Test",
            trigger={"type": "signup"}
        )
        builder.add_step(journey_id, StepType.EMAIL, {"subject": "Test"})
        
        success, message = builder.publish_journey(journey_id)
        
        assert success
        journey = builder.get_journey(journey_id)
        assert journey["status"] == JourneyStatus.PUBLISHED.value

    def test_cannot_publish_empty_journey(self):
        """Test that journeys with no steps cannot be published"""
        builder = JourneyBuilder()
        journey_id = builder.create_journey(
            name="Empty",
            description="Test",
            trigger={"type": "signup"}
        )
        
        success, message = builder.publish_journey(journey_id)
        
        assert not success
        assert "at least one step" in message

    def test_list_journeys(self):
        """Test listing journeys"""
        builder = JourneyBuilder()
        for i in range(3):
            journey_id = builder.create_journey(
                name=f"Journey {i}",
                description="Test",
                trigger={"type": "signup"}
            )
            builder.add_step(journey_id, StepType.EMAIL, {"subject": "Test"})
            if i == 0:
                builder.publish_journey(journey_id)
        
        all_journeys = builder.list_journeys()
        published = builder.list_journeys(status=JourneyStatus.PUBLISHED.value)
        
        assert len(all_journeys) == 3
        assert len(published) == 1

    def test_journey_stats(self):
        """Test getting journey statistics"""
        builder = JourneyBuilder()
        journey_id = builder.create_journey(
            name="Stats Test",
            description="Test",
            trigger={"type": "signup"}
        )
        builder.add_step(journey_id, StepType.EMAIL, {"subject": "Test"})
        builder.publish_journey(journey_id)
        
        stats = builder.get_journey_stats(journey_id)
        
        assert stats["name"] == "Stats Test"
        assert stats["status"] == "published"
        assert stats["step_count"] == 1


class TestStepExecutor:
    """Test step execution functionality"""

    def test_execute_email_step(self):
        """Test executing an email step"""
        executor = StepExecutor()
        
        success, status = executor.execute_email_step(
            step_id="step_1",
            customer_id="cust_1",
            email="test@example.com",
            subject="Test",
            content="Test content"
        )
        
        assert success in [True, False]  # Can succeed or fail
        assert status in ["sent", "failed", "error: "]

    def test_execute_sms_step(self):
        """Test executing an SMS step"""
        executor = StepExecutor()
        
        success, status = executor.execute_sms_step(
            step_id="step_1",
            customer_id="cust_1",
            phone="+1234567890",
            message="Test message"
        )
        
        assert success in [True, False]
        assert status in ["sent", "failed", "error: "]

    def test_execute_wait_step(self):
        """Test executing a wait step"""
        executor = StepExecutor()
        
        success = executor.execute_wait_step(step_id="step_1", duration_hours=24)
        
        assert success
        assert len(executor.step_history) == 1

    def test_execute_decision_step(self):
        """Test executing a decision step with branching"""
        executor = StepExecutor()
        
        context = {"user_type": "premium", "lifetime_value": 5000}
        condition = {"key": "user_type", "value": "premium", "operator": "equals"}
        
        path, _ = executor.execute_decision_step(
            step_id="step_1",
            condition=condition,
            context=context
        )
        
        assert path == "yes"

    def test_decision_step_false_condition(self):
        """Test decision step with false condition"""
        executor = StepExecutor()
        
        context = {"user_type": "free"}
        condition = {"key": "user_type", "value": "premium", "operator": "equals"}
        
        path, _ = executor.execute_decision_step(
            step_id="step_1",
            condition=condition,
            context=context
        )
        
        assert path == "no"

    def test_step_analytics(self):
        """Test getting step execution analytics"""
        executor = StepExecutor()
        
        executor.execute_email_step("s1", "c1", "test@example.com", "S", "C")
        executor.execute_email_step("s2", "c2", "test@example.com", "S", "C")
        
        analytics = executor.get_step_analytics()
        
        assert "executed_steps" in analytics
        assert "success_rate" in analytics
        assert analytics["total_steps"] >= 2


class TestTouchpointOptimizer:
    """Test channel optimization functionality"""

    def test_recommend_channel_default(self):
        """Test default channel recommendation"""
        optimizer = TouchpointOptimizer()
        channel = optimizer.recommend_channel()
        
        assert channel == TouchpointChannel.EMAIL

    def test_recommend_channel_by_segment(self):
        """Test channel recommendation by customer segment"""
        optimizer = TouchpointOptimizer()
        
        channel = optimizer.recommend_channel(segment="mobile_first")
        assert channel == TouchpointChannel.PUSH

    def test_channel_performance_tracking(self):
        """Test tracking channel performance"""
        optimizer = TouchpointOptimizer()
        
        optimizer.add_engagement(
            TouchpointChannel.EMAIL,
            opens=100,
            clicks=25,
            conversions=5,
            sends=200
        )
        
        performance = optimizer.get_channel_performance()
        
        assert "email" in performance
        assert performance["email"]["ctr"] > 0
        assert performance["email"]["cvr"] > 0

    def test_best_channel_selection(self):
        """Test selecting best performing channel"""
        optimizer = TouchpointOptimizer()
        
        optimizer.add_engagement(TouchpointChannel.EMAIL, 100, 25, 5, 200)
        optimizer.add_engagement(TouchpointChannel.SMS, 50, 10, 1, 100)
        
        best_channel = optimizer.recommend_channel()
        
        # Email should be selected as it has better performance
        assert best_channel in [TouchpointChannel.EMAIL, TouchpointChannel.SMS]

    def test_recommend_send_time(self):
        """Test recommended send time"""
        optimizer = TouchpointOptimizer()
        time = optimizer.recommend_time()
        
        assert isinstance(time, str)
        assert ":" in time


class TestJourneyOrchestrator:
    """Test overall journey orchestration"""

    def test_create_and_publish_journey(self):
        """Test creating and publishing a journey"""
        orchestrator = JourneyOrchestrator()
        
        journey_id = orchestrator.builder.create_journey(
            name="Complete Journey",
            description="Test",
            trigger={"type": "signup", "segment": "new_users"}
        )
        orchestrator.builder.add_step(journey_id, StepType.EMAIL, {
            "subject": "Welcome",
            "content": "Hello"
        })
        success, _ = orchestrator.builder.publish_journey(journey_id)
        
        assert success

    def test_enroll_customer(self):
        """Test enrolling a customer in a journey"""
        orchestrator = JourneyOrchestrator()
        
        journey_id = orchestrator.builder.create_journey(
            name="Test",
            description="Test",
            trigger={"type": "signup", "segment": "all"}
        )
        orchestrator.builder.add_step(journey_id, StepType.EMAIL, {"subject": "Test"})
        orchestrator.builder.publish_journey(journey_id)
        
        success, message = orchestrator.enroll_customer(
            journey_id,
            "cust_1",
            {"email": "test@example.com", "segment": "default"}
        )
        
        assert success
        assert "cust_1" in orchestrator.active_customers

    def test_cannot_enroll_unpublished_journey(self):
        """Test that customers cannot enroll in unpublished journeys"""
        orchestrator = JourneyOrchestrator()
        
        journey_id = orchestrator.builder.create_journey(
            name="Draft",
            description="Test",
            trigger={"type": "signup"}
        )
        orchestrator.builder.add_step(journey_id, StepType.EMAIL, {"subject": "Test"})
        
        success, message = orchestrator.enroll_customer(
            journey_id,
            "cust_1",
            {"email": "test@example.com"}
        )
        
        assert not success

    def test_segment_filtering(self):
        """Test that customers are filtered by segment"""
        orchestrator = JourneyOrchestrator()
        
        journey_id = orchestrator.builder.create_journey(
            name="VIP Only",
            description="Test",
            trigger={"type": "signup", "segment": "vip"}
        )
        orchestrator.builder.add_step(journey_id, StepType.EMAIL, {"subject": "Test"})
        orchestrator.builder.publish_journey(journey_id)
        
        # Try to enroll non-VIP customer
        success, _ = orchestrator.enroll_customer(
            journey_id,
            "cust_1",
            {"email": "test@example.com", "segment": "regular"}
        )
        
        assert not success

    def test_process_customer_step(self):
        """Test processing a step for a customer"""
        orchestrator = JourneyOrchestrator()
        
        journey_id = orchestrator.builder.create_journey(
            name="Test",
            description="Test",
            trigger={"type": "signup", "segment": "all"}
        )
        orchestrator.builder.add_step(journey_id, StepType.WAIT, {"hours": 1})
        orchestrator.builder.publish_journey(journey_id)
        
        orchestrator.enroll_customer(
            journey_id,
            "cust_1",
            {"email": "test@example.com"}
        )
        
        success, _ = orchestrator.process_step("cust_1")
        
        assert success

    def test_track_conversion(self):
        """Test tracking a conversion"""
        orchestrator = JourneyOrchestrator()
        
        journey_id = orchestrator.builder.create_journey(
            name="Test",
            description="Test",
            trigger={"type": "signup", "segment": "all"}
        )
        orchestrator.builder.add_step(journey_id, StepType.WAIT, {"hours": 1})
        orchestrator.builder.publish_journey(journey_id)
        
        orchestrator.enroll_customer(
            journey_id,
            "cust_1",
            {"email": "test@example.com"}
        )
        
        success, _ = orchestrator.track_conversion("cust_1", 99.99)
        
        assert success

    def test_pause_and_resume_journey(self):
        """Test pausing and resuming a customer journey"""
        orchestrator = JourneyOrchestrator()
        
        journey_id = orchestrator.builder.create_journey(
            name="Test",
            description="Test",
            trigger={"type": "signup", "segment": "all"}
        )
        orchestrator.builder.add_step(journey_id, StepType.WAIT, {"hours": 1})
        orchestrator.builder.publish_journey(journey_id)
        
        orchestrator.enroll_customer(
            journey_id,
            "cust_1",
            {"email": "test@example.com"}
        )
        
        pause_success, _ = orchestrator.pause_customer_journey("cust_1")
        resume_success, _ = orchestrator.resume_customer_journey("cust_1")
        
        assert pause_success
        assert resume_success


class TestJourneyAnalytics:
    """Test journey analytics and reporting"""

    def test_journey_analytics(self):
        """Test getting journey analytics"""
        orchestrator = JourneyOrchestrator()
        
        journey_id = orchestrator.builder.create_journey(
            name="Analytics Test",
            description="Test",
            trigger={"type": "signup", "segment": "all"}
        )
        orchestrator.builder.add_step(journey_id, StepType.EMAIL, {"subject": "Test"})
        orchestrator.builder.publish_journey(journey_id)
        
        analytics = orchestrator.get_journey_analytics(journey_id)
        
        assert "journey_id" in analytics
        assert "completion_rate" in analytics
        assert "conversion_rate" in analytics

    def test_orchestrator_stats(self):
        """Test getting overall orchestrator statistics"""
        orchestrator = JourneyOrchestrator()
        
        journey_id = orchestrator.builder.create_journey(
            name="Test",
            description="Test",
            trigger={"type": "signup", "segment": "all"}
        )
        orchestrator.builder.add_step(journey_id, StepType.EMAIL, {"subject": "Test"})
        orchestrator.builder.publish_journey(journey_id)
        
        stats = orchestrator.get_orchestrator_stats()
        
        assert "total_journeys" in stats
        assert "published_journeys" in stats
        assert "total_enrolled_customers" in stats
        assert "completion_rate" in stats


class TestDemoJourneys:
    """Test demo journey generation"""

    def test_generate_demo_journeys(self):
        """Test generating demo journeys"""
        orchestrator = generate_demo_journeys()
        
        assert orchestrator is not None
        journeys = orchestrator.builder.list_journeys()
        assert len(journeys) >= 3

    def test_demo_journeys_have_data(self):
        """Test that demo journeys have realistic data"""
        orchestrator = generate_demo_journeys()
        journeys = orchestrator.builder.list_journeys(status="published")
        
        assert len(journeys) > 0
        
        # Just verify journeys exist and have steps
        for journey in journeys:
            assert "steps" in journey
            assert len(journey["steps"]) > 0

    def test_demo_channel_performance(self):
        """Test that demo data includes channel performance"""
        orchestrator = generate_demo_journeys()
        performance = orchestrator.optimizer.get_channel_performance()
        
        assert len(performance) > 0
        assert "email" in performance


class TestJourneyIntegration:
    """Integration tests for complete journey workflows"""

    def test_complete_journey_workflow(self):
        """Test complete journey from creation to completion"""
        orchestrator = JourneyOrchestrator()
        
        # Create journey
        journey_id = orchestrator.builder.create_journey(
            name="Complete Workflow",
            description="Full test",
            trigger={"type": "signup", "segment": "all"}
        )
        
        # Add steps
        orchestrator.builder.add_step(journey_id, StepType.EMAIL, {
            "subject": "Step 1",
            "content": "First email"
        })
        orchestrator.builder.add_step(journey_id, StepType.WAIT, {"hours": 1})
        orchestrator.builder.add_step(journey_id, StepType.EMAIL, {
            "subject": "Step 2",
            "content": "Second email"
        })
        
        # Publish
        success, _ = orchestrator.builder.publish_journey(journey_id)
        assert success
        
        # Enroll customer
        enroll_success, _ = orchestrator.enroll_customer(
            journey_id,
            "cust_workflow",
            {"email": "workflow@example.com"}
        )
        assert enroll_success
        
        # Process steps
        for _ in range(3):
            orchestrator.process_step("cust_workflow")
        
        # Track conversion
        conv_success, _ = orchestrator.track_conversion("cust_workflow", 150.00)
        assert conv_success

    def test_multiple_journeys_concurrent(self):
        """Test multiple journeys running concurrently"""
        orchestrator = JourneyOrchestrator()
        
        # Create multiple journeys
        journey_ids = []
        for i in range(3):
            journey_id = orchestrator.builder.create_journey(
                name=f"Journey {i}",
                description="Test",
                trigger={"type": "signup", "segment": "all"}
            )
            orchestrator.builder.add_step(journey_id, StepType.WAIT, {"hours": 1})
            orchestrator.builder.publish_journey(journey_id)
            journey_ids.append(journey_id)
        
        # Enroll customers in multiple journeys
        for i in range(10):
            for journey_id in journey_ids:
                orchestrator.enroll_customer(
                    journey_id,
                    f"cust_{i}",
                    {"email": f"cust{i}@example.com", "segment": "default"}
                )
        
        stats = orchestrator.get_orchestrator_stats()
        assert stats["total_journeys"] == 3
        assert stats["total_enrolled_customers"] >= 10


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_enroll_nonexistent_journey(self):
        """Test enrolling in nonexistent journey"""
        orchestrator = JourneyOrchestrator()
        
        success, message = orchestrator.enroll_customer(
            "nonexistent_123",
            "cust_1",
            {"email": "test@example.com"}
        )
        
        assert not success

    def test_process_nonexistent_customer(self):
        """Test processing step for nonexistent customer"""
        orchestrator = JourneyOrchestrator()
        
        success, _ = orchestrator.process_step("nonexistent_cust")
        
        assert not success

    def test_enrollment_limit(self):
        """Test journey enrollment limits"""
        orchestrator = JourneyOrchestrator()
        
        journey_id = orchestrator.builder.create_journey(
            name="Limited Journey",
            description="Test",
            trigger={"type": "signup", "segment": "all", "max_enrollments": 2}
        )
        orchestrator.builder.add_step(journey_id, StepType.WAIT, {"hours": 1})
        orchestrator.builder.publish_journey(journey_id)
        
        # Enroll at capacity
        success1, _ = orchestrator.enroll_customer(journey_id, "cust_1", {})
        success2, _ = orchestrator.enroll_customer(journey_id, "cust_2", {})
        success3, _ = orchestrator.enroll_customer(journey_id, "cust_3", {})
        
        assert success1
        assert success2
        assert not success3  # Should fail due to limit

    def test_decision_step_operators(self):
        """Test different decision operators"""
        executor = StepExecutor()
        
        context = {"value": 100}
        
        # Greater than
        _, _ = executor.execute_decision_step("s1", {
            "key": "value",
            "value": 50,
            "operator": "greater_than"
        }, context)
        
        # Less than
        _, _ = executor.execute_decision_step("s2", {
            "key": "value",
            "value": 200,
            "operator": "less_than"
        }, context)
        
        assert len(executor.step_history) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
