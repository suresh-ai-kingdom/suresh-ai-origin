import pytest


def test_api_documentation_routes(client):
    """Test API documentation endpoints."""
    
    # Main docs page
    rv = client.get('/docs')
    assert rv.status_code == 200
    assert b'API Documentation' in rv.data
    assert b'60+' in rv.data
    
    # OpenAPI spec
    r1 = client.get('/api/docs/openapi.json')
    assert r1.status_code == 200
    spec = r1.get_json()
    assert spec['openapi'] == '3.0.0'
    assert 'paths' in spec
    assert len(spec['tags']) >= 15
    
    # Postman collection
    r2 = client.get('/api/docs/postman.json')
    assert r2.status_code == 200
    collection = r2.get_json()
    assert 'info' in collection
    assert collection['info']['name'] == 'SURESH AI ORIGIN API'


def test_openapi_spec_structure():
    """Test OpenAPI spec has correct structure."""
    from api_documentation import OPENAPI_SPEC
    
    assert OPENAPI_SPEC['openapi'] == '3.0.0'
    assert 'info' in OPENAPI_SPEC
    assert 'paths' in OPENAPI_SPEC
    assert 'tags' in OPENAPI_SPEC
    assert 'components' in OPENAPI_SPEC
    
    # Check key endpoints documented
    paths = OPENAPI_SPEC['paths']
    assert '/api/ai/generate' in paths
    assert '/api/churn/risk' in paths
    assert '/api/automations/trigger' in paths
    assert '/api/voice/analyze' in paths


def test_postman_collection_structure():
    """Test Postman collection has correct structure."""
    from api_documentation import get_postman_collection
    
    collection = get_postman_collection()
    assert 'info' in collection
    assert 'item' in collection
    assert 'variable' in collection
    
    # Check has base_url variable
    vars = {v['key']: v['value'] for v in collection['variable']}
    assert 'base_url' in vars
