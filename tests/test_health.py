import pytest
import json


def test_health_endpoint_success(client):
    """Test health endpoint returns 200 when database is accessible."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['database'] == 'ok'
    assert 'timestamp' in data


def test_health_endpoint_json_format(client):
    """Test health endpoint returns proper JSON content type."""
    response = client.get('/health')
    assert response.content_type == 'application/json'


def test_health_endpoint_database_error(client, monkeypatch):
    """Test health endpoint returns 503 when database fails."""
    def mock_failing_engine(*args, **kwargs):
        raise Exception("DB connection failed")
    
    import models
    monkeypatch.setattr(models, 'get_engine', mock_failing_engine)
    
    response = client.get('/health')
    assert response.status_code == 503
    data = json.loads(response.data)
    assert data['status'] == 'unhealthy'
    assert data['database'] == 'error'
