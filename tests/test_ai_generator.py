"""Tests for AI Content Generator."""
import pytest
import json
import time
from ai_generator import (
    generate_content, batch_generate, rate_generation,
    increment_usage, get_generation_stats, get_generations,
    PROMPT_TEMPLATES
)
from models import AIGeneration, get_session


def test_generation_templates_exist():
    """Test that all prompt templates are defined."""
    assert len(PROMPT_TEMPLATES) > 0
    assert 'email_welcome' in PROMPT_TEMPLATES
    assert 'blog_title' in PROMPT_TEMPLATES
    assert 'product_description' in PROMPT_TEMPLATES


def test_generate_content_without_claude():
    """Test generate_content when Claude API not available."""
    result = generate_content('email_welcome', {'product': 'test'})
    # Should return error about Claude not available or empty content
    assert 'error' in result or 'content' in result


def test_rate_generation_valid():
    """Test rating a generation."""
    # Create a test generation
    session = get_session()
    gen_id = f'TEST_GEN_{int(time.time())}'
    try:
        gen = AIGeneration(
            id=gen_id,
            content_type='email_welcome',
            prompt='Test prompt',
            generated_content='Test content',
            tokens_used=100,
            cost_cents=30,
            quality_score=85,
            created_at=time.time(),
            created_by='test'
        )
        session.add(gen)
        session.commit()
        
        # Rate it
        success = rate_generation(gen_id, 4)
        assert success is True
        
        # Verify rating was saved
        gen_check = session.query(AIGeneration).filter(AIGeneration.id == gen_id).first()
        assert gen_check.user_rating == 4
    finally:
        session.query(AIGeneration).filter(AIGeneration.id == gen_id).delete()
        session.commit()
        session.close()


def test_rate_generation_invalid_rating():
    """Test rating with invalid score."""
    success = rate_generation('fake_id', 10)  # Rating should be 1-5
    assert success is False
    
    success = rate_generation('fake_id', 0)
    assert success is False


def test_increment_usage():
    """Test incrementing usage counter."""
    session = get_session()
    gen_id = f'TEST_GEN_{int(time.time())}'
    try:
        gen = AIGeneration(
            id=gen_id,
            content_type='email_welcome',
            prompt='Test',
            generated_content='Test content',
            tokens_used=100,
            cost_cents=30,
            quality_score=85,
            used_count=0,
            created_at=time.time(),
            created_by='test'
        )
        session.add(gen)
        session.commit()
        session.close()
        
        # Increment usage
        success = increment_usage(gen_id)
        assert success is True
        
        # Verify increment in fresh session
        check_session = get_session()
        gen_check = check_session.query(AIGeneration).filter(AIGeneration.id == gen_id).first()
        first_count = gen_check.used_count if gen_check else 0
        check_session.close()
        
        # Increment again
        increment_usage(gen_id)
        
        # Verify final count
        check_session2 = get_session()
        gen_check2 = check_session2.query(AIGeneration).filter(AIGeneration.id == gen_id).first()
        final_count = gen_check2.used_count if gen_check2 else 0
        check_session2.close()
        
        assert final_count > first_count
    finally:
        final_session = get_session()
        final_session.query(AIGeneration).filter(AIGeneration.id == gen_id).delete()
        final_session.commit()
        final_session.close()


def test_get_generation_stats():
    """Test retrieving generation statistics."""
    session = get_session()
    
    # Clear existing
    session.query(AIGeneration).delete()
    session.commit()
    
    # Create test generations
    for i in range(3):
        gen = AIGeneration(
            id=f'TEST_STAT_{i}',
            content_type='email_welcome' if i < 2 else 'blog_title',
            prompt='Test prompt',
            generated_content=f'Test content {i}',
            tokens_used=100 + i * 50,
            cost_cents=30 + i * 10,
            quality_score=80 + i,
            user_rating=4 if i == 0 else (5 if i == 1 else None),
            used_count=i,
            created_at=time.time(),
            created_by='test'
        )
        session.add(gen)
    session.commit()
    
    stats = get_generation_stats()
    
    assert stats['total_generations'] >= 3
    assert stats['total_tokens_used'] > 0
    assert stats['total_cost_rupees'] > 0
    assert isinstance(stats['by_type'], dict)
    
    session.query(AIGeneration).filter(AIGeneration.id.like('TEST_STAT_%')).delete()
    session.commit()
    session.close()


def test_get_generations_list():
    """Test retrieving generations."""
    session = get_session()
    
    # Create test data
    test_id = f'LIST_TEST_{int(time.time())}'
    gen = AIGeneration(
        id=test_id,
        content_type='email_welcome',
        prompt='Test',
        generated_content='Test content for listing',
        tokens_used=100,
        cost_cents=30,
        quality_score=85,
        user_rating=4,
        used_count=2,
        created_at=time.time(),
        created_by='test'
    )
    session.add(gen)
    session.commit()
    
    try:
        gens = get_generations(limit=10)
        assert isinstance(gens, list)
        assert len(gens) > 0
        
        # Check structure
        if len(gens) > 0:
            assert 'id' in gens[0]
            assert 'type' in gens[0]
            assert 'content' in gens[0]
            assert 'rating' in gens[0]
            assert 'used' in gens[0]
            assert 'cost' in gens[0]
    finally:
        session.query(AIGeneration).filter(AIGeneration.id == test_id).delete()
        session.commit()
        session.close()


def test_get_generations_by_type():
    """Test filtering generations by type."""
    session = get_session()
    
    # Create mixed types
    for i in range(2):
        gen1 = AIGeneration(
            id=f'TYPE_TEST_WELCOME_{i}',
            content_type='email_welcome',
            prompt='Test',
            generated_content='Welcome content',
            tokens_used=100,
            cost_cents=30,
            quality_score=85,
            created_at=time.time(),
            created_by='test'
        )
        gen2 = AIGeneration(
            id=f'TYPE_TEST_BLOG_{i}',
            content_type='blog_title',
            prompt='Test',
            generated_content='Blog content',
            tokens_used=100,
            cost_cents=30,
            quality_score=85,
            created_at=time.time(),
            created_by='test'
        )
        session.add(gen1)
        session.add(gen2)
    session.commit()
    
    try:
        email_gens = get_generations('email_welcome', limit=10)
        blog_gens = get_generations('blog_title', limit=10)
        
        # Check we got some results
        assert len(email_gens) > 0 or len(blog_gens) > 0
        
        # Verify types if we got results
        for gen in email_gens:
            assert gen['type'] == 'email_welcome'
        for gen in blog_gens:
            assert gen['type'] == 'blog_title'
    finally:
        session.query(AIGeneration).filter(
            AIGeneration.id.like('TYPE_TEST_%')
        ).delete()
        session.commit()
        session.close()


def test_batch_generate():
    """Test batch generation."""
    batch_list = [
        {'type': 'email_welcome', 'variables': {'product': 'test'}},
        {'type': 'blog_title', 'variables': {'topic': 'AI'}},
    ]
    
    result = batch_generate(batch_list, 'test_user')
    
    assert 'results' in result
    assert 'count' in result
    assert 'total_cost_rupees' in result
    assert result['count'] == 2


def test_template_variable_filling():
    """Test that templates can be filled with variables."""
    template = PROMPT_TEMPLATES['email_welcome']
    filled = template.format(product='Test Product', tone='friendly')
    
    assert 'Test Product' in filled
    # Check that no unfilled template placeholders remain
    assert '{' not in filled and '}' not in filled


def test_template_missing_variables():
    """Test error handling for missing variables."""
    from ai_generator import generate_content
    
    result = generate_content('email_welcome', {})  # Missing 'product' and 'tone'
    
    # Should return error about missing variables
    assert 'error' in result


@pytest.fixture(scope='session')
def cleanup_test_data():
    """Clean up test data after all tests."""
    yield
    session = get_session()
    session.query(AIGeneration).filter(
        AIGeneration.id.like('TEST_%')
    ).delete()
    session.query(AIGeneration).filter(
        AIGeneration.id.like('LIST_%')
    ).delete()
    session.query(AIGeneration).filter(
        AIGeneration.id.like('TYPE_%')
    ).delete()
    session.commit()
    session.close()
