"""
Week 2 Integration Tests: Executor + Outcome Logger

Tests for:
- Executor page rendering
- Outcome logger page rendering  
- E2E flow: create profile → start execution → update progress → log outcome
"""

import pytest
import json
from uuid import uuid4
from models import get_engine, get_session, Base, UserProfile, WorkflowExecution, Outcome
import time
import tempfile
import os


@pytest.fixture(scope="function")
def client():
    """Test client with isolated DB."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    os.environ['DATA_DB'] = db_path
    
    engine = get_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    
    from app import app
    app.config['TESTING'] = True
    
    with app.test_client() as test_client:
        yield test_client
    
    if 'DATA_DB' in os.environ:
        del os.environ['DATA_DB']


class TestExecutorRendering:
    """Test Executor page rendering."""
    
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
    
    def test_executor_page_renders(self, client):
        """Executor page renders successfully."""
        user_id, execution_id = self._create_execution(client)
        
        response = client.get(f'/executor/{execution_id}')
        
        assert response.status_code == 200
        assert b'executor' in response.data.lower() or b'step' in response.data.lower()
    
    def test_executor_includes_workflow_data(self, client):
        """Executor page includes workflow data."""
        user_id, execution_id = self._create_execution(client)
        
        response = client.get(f'/executor/{execution_id}')
        
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        # Check for workflow-related content
        assert 'resume' in html.lower() or 'workflow' in html.lower() or 'step' in html.lower()
    
    def test_executor_nonexistent_execution(self, client):
        """Executor returns 404 for nonexistent execution."""
        response = client.get('/executor/nonexistent-id')
        
        assert response.status_code == 404


class TestOutcomeLoggerRendering:
    """Test Outcome Logger page rendering."""
    
    def _create_execution(self, client):
        """Helper to create execution."""
        user_resp = client.post('/api/profile', json={
            'email': f'user{uuid4()}@example.com',
            'goal': 'earn_money',
            'market': 'freelancer',
            'skill_level': 'intermediate',
            'country': 'IN'
        })
        user_id = user_resp.get_json()['user_id']
        
        exec_resp = client.post('/api/execution', json={
            'user_id': user_id,
            'workflow_name': 'prompt_selling',
            'total_steps': 3
        })
        execution_id = exec_resp.get_json()['execution_id']
        
        return user_id, execution_id
    
    def test_outcome_logger_page_renders(self, client):
        """Outcome logger page renders successfully."""
        user_id, execution_id = self._create_execution(client)
        
        response = client.get(f'/outcome/{execution_id}')
        
        assert response.status_code == 200
        assert b'outcome' in response.data.lower() or b'result' in response.data.lower()
    
    def test_outcome_logger_nonexistent_execution(self, client):
        """Outcome logger returns 404 for nonexistent execution."""
        response = client.get('/outcome/nonexistent-id')
        
        assert response.status_code == 404


class TestE2EFlow:
    """End-to-end flow: profile → execution → progress → outcome."""
    
    def test_complete_workflow_flow(self, client):
        """Full flow from profile creation to outcome logging."""
        # Step 1: Create profile
        profile_resp = client.post('/api/profile', json={
            'email': 'e2e_test@example.com',
            'goal': 'earn_money',
            'market': 'freelancer',
            'skill_level': 'intermediate',
            'country': 'IN'
        })
        assert profile_resp.status_code == 201
        user_id = profile_resp.get_json()['user_id']
        
        # Step 2: Start execution
        exec_resp = client.post('/api/execution', json={
            'user_id': user_id,
            'workflow_name': 'whatsapp_bot',
            'total_steps': 4
        })
        assert exec_resp.status_code == 201
        execution_id = exec_resp.get_json()['execution_id']
        
        # Step 3: Update progress
        progress_resp = client.put(f'/api/execution/{execution_id}/progress', json={
            'steps_completed': 2,
            'notes': 'Halfway through'
        })
        assert progress_resp.status_code == 200
        assert progress_resp.get_json()['progress'] == '2/4'
        
        # Step 4: Complete execution
        complete_resp = client.put(f'/api/execution/{execution_id}/progress', json={
            'steps_completed': 4
        })
        assert complete_resp.status_code == 200
        assert complete_resp.get_json()['status'] == 'completed'
        
        # Step 5: Log outcome
        outcome_resp = client.post('/api/outcome', json={
            'execution_id': execution_id,
            'user_id': user_id,
            'metric_type': 'revenue',
            'value': 5000,
            'currency': 'INR',
            'proof_type': 'screenshot'
        })
        assert outcome_resp.status_code == 201
        assert outcome_resp.get_json()['metric_type'] == 'revenue'
        assert outcome_resp.get_json()['value'] == 5000
    
    def test_view_executor_page_during_flow(self, client):
        """Can view executor page during workflow."""
        # Create execution
        profile_resp = client.post('/api/profile', json={
            'email': f'user{uuid4()}@example.com',
            'goal': 'save_time',
            'market': 'content_creator',
            'skill_level': 'advanced',
            'country': 'US'
        })
        user_id = profile_resp.get_json()['user_id']
        
        exec_resp = client.post('/api/execution', json={
            'user_id': user_id,
            'workflow_name': 'resume_generator',
            'total_steps': 5
        })
        execution_id = exec_resp.get_json()['execution_id']
        
        # View executor page
        executor_resp = client.get(f'/executor/{execution_id}')
        assert executor_resp.status_code == 200
        
        # Continue to outcome logger
        outcome_resp = client.get(f'/outcome/{execution_id}')
        assert outcome_resp.status_code == 200
    
    def test_multiple_outcomes_per_execution(self, client):
        """Can log multiple metrics for same execution."""
        # Create execution
        profile_resp = client.post('/api/profile', json={
            'email': f'user{uuid4()}@example.com',
            'goal': 'scale_business',
            'market': 'shop_owner',
            'skill_level': 'beginner',
            'country': 'IN'
        })
        user_id = profile_resp.get_json()['user_id']
        
        exec_resp = client.post('/api/execution', json={
            'user_id': user_id,
            'workflow_name': 'prompt_selling',
            'total_steps': 2
        })
        execution_id = exec_resp.get_json()['execution_id']
        
        # Log revenue outcome
        outcome1 = client.post('/api/outcome', json={
            'execution_id': execution_id,
            'user_id': user_id,
            'metric_type': 'revenue',
            'value': 2000,
            'currency': 'INR'
        })
        assert outcome1.status_code == 201
        
        # Log time saved outcome
        outcome2 = client.post('/api/outcome', json={
            'execution_id': execution_id,
            'user_id': user_id,
            'metric_type': 'time_saved',
            'value': 5
        })
        assert outcome2.status_code == 201
        
        # Both should be stored
        assert outcome1.get_json()['outcome_id'] != outcome2.get_json()['outcome_id']


class TestWorkflowMetadata:
    """Test workflow definitions are loaded correctly."""
    
    def test_workflows_json_exists(self):
        """workflows.json file exists and is valid."""
        import json
        with open('workflows.json', 'r') as f:
            data = json.load(f)
        
        assert 'workflows' in data
        assert len(data['workflows']) > 0
    
    def test_workflow_has_required_fields(self):
        """Each workflow has required fields."""
        import json
        with open('workflows.json', 'r') as f:
            data = json.load(f)
        
        for wf_name, wf_data in data['workflows'].items():
            assert 'title' in wf_data
            assert 'description' in wf_data
            assert 'total_steps' in wf_data
            assert 'steps' in wf_data
            assert len(wf_data['steps']) > 0
    
    def test_each_step_has_content(self):
        """Each step has title, description, tips."""
        import json
        with open('workflows.json', 'r') as f:
            data = json.load(f)
        
        for wf_name, wf_data in data['workflows'].items():
            for step in wf_data['steps']:
                assert 'number' in step
                assert 'title' in step
                assert 'description' in step
                assert 'tips' in step
                assert 'estimated_time' in step


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
