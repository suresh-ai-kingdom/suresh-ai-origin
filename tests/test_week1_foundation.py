"""
Week 1 Foundation Tests: Execution Intelligence Platform

Tests for:
- UserProfile CRUD
- WorkflowExecution creation and progress tracking
- Outcome logging
- Performance metrics (aggregation logic)
- Recommendation generation
"""

import pytest
import json
import time
import os
import tempfile
import subprocess
from uuid import uuid4
from models import get_engine, get_session, Base, UserProfile, WorkflowExecution, Outcome, WorkflowPerformance, Recommendation


@pytest.fixture(scope="function")
def client():
    """Test client with isolated DB."""
    
    # Create temp DB for this test
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Set env var to use test DB
    os.environ['DATA_DB'] = db_path
    
    # Create engine and all tables
    engine = get_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    
    # Import and create test client
    from app import app
    app.config['TESTING'] = True
    
    with app.test_client() as test_client:
        yield test_client
    
    # Cleanup
    if 'DATA_DB' in os.environ:
        del os.environ['DATA_DB']
    
    # Close all connections before deleting
    import gc
    gc.collect()
    
    try:
        os.unlink(db_path)
    except:
        pass  # File might still be locked, that's okay


class TestUserProfile:
    """Test UserProfile creation and retrieval."""
    
    def test_create_profile(self, client):
        """Create a new user profile."""
        response = client.post('/api/profile', json={
            'email': 'test@example.com',
            'goal': 'earn_money',
            'market': 'freelancer',
            'skill_level': 'intermediate',
            'country': 'IN'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['user_id'] is not None
        assert data['email'] == 'test@example.com'
    
    def test_get_profile(self, client):
        """Retrieve a user profile by ID."""
        # Create first
        create_resp = client.post('/api/profile', json={
            'email': 'test2@example.com',
            'goal': 'save_time',
            'market': 'shop_owner',
            'skill_level': 'beginner',
            'country': 'US'
        })
        user_id = create_resp.get_json()['user_id']
        
        # Retrieve
        get_resp = client.get(f'/api/profile/{user_id}')
        assert get_resp.status_code == 200
        data = get_resp.get_json()
        assert data['success'] is True
        assert data['email'] == 'test2@example.com'
        assert data['goal'] == 'save_time'
        assert data['skill_level'] == 'beginner'
    
    def test_duplicate_email_rejected(self, client):
        """Reject duplicate emails."""
        client.post('/api/profile', json={
            'email': 'dup@example.com',
            'goal': 'earn_money',
            'market': 'freelancer',
            'skill_level': 'intermediate',
            'country': 'IN'
        })
        
        # Try to create again with same email
        response = client.post('/api/profile', json={
            'email': 'dup@example.com',
            'goal': 'save_time',
            'market': 'content_creator',
            'skill_level': 'advanced',
            'country': 'IN'
        })
        
        assert response.status_code == 409
        assert response.get_json()['success'] is False
    
    def test_missing_required_fields(self, client):
        """Reject profile with missing required fields."""
        response = client.post('/api/profile', json={
            'email': 'test@example.com',
            'goal': 'earn_money'
            # Missing market, skill_level
        })
        
        assert response.status_code == 400


class TestWorkflowExecution:
    """Test WorkflowExecution creation and progress tracking."""
    
    def _create_user(self, client):
        """Helper to create a user."""
        resp = client.post('/api/profile', json={
            'email': f'user{uuid4()}@example.com',
            'goal': 'earn_money',
            'market': 'freelancer',
            'skill_level': 'intermediate',
            'country': 'IN'
        })
        return resp.get_json()['user_id']
    
    def test_start_execution(self, client):
        """Start a workflow execution."""
        user_id = self._create_user(client)
        
        response = client.post('/api/execution', json={
            'user_id': user_id,
            'workflow_name': 'resume_generator',
            'total_steps': 5
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['execution_id'] is not None
        assert data['status'] == 'started'
        assert data['workflow_name'] == 'resume_generator'
    
    def test_update_progress(self, client):
        """Update execution progress."""
        user_id = self._create_user(client)
        
        # Start execution
        start_resp = client.post('/api/execution', json={
            'user_id': user_id,
            'workflow_name': 'whatsapp_bot',
            'total_steps': 5
        })
        execution_id = start_resp.get_json()['execution_id']
        
        # Update progress
        update_resp = client.put(f'/api/execution/{execution_id}/progress', json={
            'steps_completed': 3,
            'notes': 'Completed first 3 steps'
        })
        
        assert update_resp.status_code == 200
        data = update_resp.get_json()
        assert data['success'] is True
        assert data['status'] == 'in_progress'
        assert data['progress'] == '3/5'
    
    def test_execution_completion(self, client):
        """Mark execution as completed."""
        user_id = self._create_user(client)
        
        # Start
        start_resp = client.post('/api/execution', json={
            'user_id': user_id,
            'workflow_name': 'prompt_selling',
            'total_steps': 5
        })
        execution_id = start_resp.get_json()['execution_id']
        
        # Complete all steps
        complete_resp = client.put(f'/api/execution/{execution_id}/progress', json={
            'steps_completed': 5
        })
        
        assert complete_resp.status_code == 200
        data = complete_resp.get_json()
        assert data['status'] == 'completed'
        assert data['progress'] == '5/5'
    
    def test_nonexistent_user_rejected(self, client):
        """Reject execution for nonexistent user."""
        response = client.post('/api/execution', json={
            'user_id': 'nonexistent-id',
            'workflow_name': 'test_workflow',
            'total_steps': 5
        })
        
        assert response.status_code == 404


class TestOutcomeLogging:
    """Test Outcome capture from workflow execution."""
    
    def _create_execution(self, client):
        """Helper to create user and execution."""
        # Create user
        user_resp = client.post('/api/profile', json={
            'email': f'user{uuid4()}@example.com',
            'goal': 'earn_money',
            'market': 'freelancer',
            'skill_level': 'intermediate',
            'country': 'IN'
        })
        user_id = user_resp.get_json()['user_id']
        
        # Create execution
        exec_resp = client.post('/api/execution', json={
            'user_id': user_id,
            'workflow_name': 'resume_generator',
            'total_steps': 5
        })
        execution_id = exec_resp.get_json()['execution_id']
        
        return user_id, execution_id
    
    def test_log_revenue_outcome(self, client):
        """Log revenue outcome."""
        user_id, execution_id = self._create_execution(client)
        
        response = client.post('/api/outcome', json={
            'execution_id': execution_id,
            'user_id': user_id,
            'metric_type': 'revenue',
            'value': 5000,
            'currency': 'INR',
            'proof_type': 'screenshot',
            'proof_url': 'https://example.com/proof.png'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['outcome_id'] is not None
        assert data['metric_type'] == 'revenue'
        assert data['value'] == 5000
    
    def test_log_time_saved_outcome(self, client):
        """Log time saved outcome."""
        user_id, execution_id = self._create_execution(client)
        
        response = client.post('/api/outcome', json={
            'execution_id': execution_id,
            'user_id': user_id,
            'metric_type': 'time_saved',
            'value': 10,
            'currency': 'hours'
        })
        
        assert response.status_code == 201
        assert response.get_json()['metric_type'] == 'time_saved'
    
    def test_log_customers_outcome(self, client):
        """Log customers acquired outcome."""
        user_id, execution_id = self._create_execution(client)
        
        response = client.post('/api/outcome', json={
            'execution_id': execution_id,
            'user_id': user_id,
            'metric_type': 'customers',
            'value': 3,
            'currency': 'count'
        })
        
        assert response.status_code == 201
        assert response.get_json()['metric_type'] == 'customers'
    
    def test_missing_outcome_fields(self, client):
        """Reject outcome with missing fields."""
        user_id, execution_id = self._create_execution(client)
        
        response = client.post('/api/outcome', json={
            'execution_id': execution_id,
            'user_id': user_id,
            'metric_type': 'revenue'
            # Missing value
        })
        
        assert response.status_code == 400


class TestPerformanceMetrics:
    """Test WorkflowPerformance aggregation."""
    
    def test_get_performance_for_workflow(self, client):
        """Get performance metrics for a workflow."""
        # Create performance data in DB
        engine = get_engine()
        session_db = get_session(engine)
        
        perf = WorkflowPerformance(
            id=str(uuid4()),
            workflow_name='resume_generator',
            market='freelancer',
            skill_level='intermediate',
            success_rate=73.5,
            avg_outcome_value=5000,
            completion_time_hours=8,
            data_points=50,
            updated_at=time.time()
        )
        session_db.add(perf)
        session_db.commit()
        session_db.close()
        
        # Query via API
        response = client.get('/api/performance/resume_generator?market=freelancer&skill_level=intermediate')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['performance']) > 0
        perf_data = data['performance'][0]
        assert perf_data['success_rate'] == 73.5
        assert perf_data['avg_outcome_value'] == 5000
    
    def test_get_performance_nonexistent_workflow(self, client):
        """Get performance for nonexistent workflow returns empty."""
        response = client.get('/api/performance/nonexistent_workflow')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['performance']) == 0


class TestRecommendations:
    """Test Recommendation generation and retrieval."""
    
    def test_get_recommendations_for_user(self, client):
        """Get recommendations for a user."""
        # Create user
        user_resp = client.post('/api/profile', json={
            'email': f'user{uuid4()}@example.com',
            'goal': 'earn_money',
            'market': 'freelancer',
            'skill_level': 'beginner',
            'country': 'IN'
        })
        user_id = user_resp.get_json()['user_id']
        
        # Create recommendations in DB
        engine = get_engine()
        session_db = get_session(engine)
        
        for i in range(3):
            rec = Recommendation(
                id=str(uuid4()),
                user_id=user_id,
                workflow_name=f'workflow_{i}',
                reason=f'Recommended for your market',
                rank=i+1,
                created_at=time.time(),
                clicked=0
            )
            session_db.add(rec)
        session_db.commit()
        session_db.close()
        
        # Query via API
        response = client.get(f'/api/recommendations/{user_id}?limit=5')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['recommendations']) == 3
        assert data['recommendations'][0]['rank'] == 1
    
    def test_recommendations_for_nonexistent_user(self, client):
        """Get recommendations for nonexistent user fails."""
        response = client.get('/api/recommendations/nonexistent-id')
        
        assert response.status_code == 404


class TestNoRegressions:
    """Ensure Week 1 changes don't break existing functionality."""
    
    def test_old_download_route_still_works(self, client):
        """Verify old /download route still accessible (even if returns 404)."""
        response = client.get('/download/nonexistent')
        # Should be 404 (product not found), not 500 (server error)
        assert response.status_code in [404, 400, 200]  # Depends on product existence
    
    def test_old_home_route_still_works(self, client):
        """Verify home route still works."""
        response = client.get('/')
        # Should succeed or redirect, not crash
        assert response.status_code in [200, 302]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
