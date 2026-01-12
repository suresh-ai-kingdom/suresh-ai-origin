"""AI Content Generator - Auto-generate content using Claude API."""
import time
import os
import json
from datetime import datetime
from models import get_session, AIGeneration
from sqlalchemy import Column, String, Text, Float, Integer
from models import Base


# Configuration
GENERATION_CONFIG = {
    'model': 'claude-3-5-sonnet-20241022',
    'max_tokens': 2000,
    'cost_per_1k_tokens': 3,  # ₹3 per 1000 tokens approximately
    'cache_duration_days': 30,  # Cache generated content for 30 days
    'quality_threshold': 70,  # Minimum quality score to auto-use
}

# Prompt templates for common use cases
PROMPT_TEMPLATES = {
    'email_welcome': """Generate a warm, compelling welcome email for {product} customers.
    Include: warm greeting, what they get, quick win example, CTA.
    Tone: friendly, professional, exciting. Max 150 words.""",
    
    'email_upsell': """Generate an upsell email recommending upgrade from {current_tier} to {target_tier}.
    Highlight benefits, additional features, value increase. 
    Include social proof. Max 120 words.""",
    
    'referral_message': """Generate a WhatsApp/social media message to share {product} referral code.
    Make it casual, exciting, benefit-focused. Include code: {code}
    Max 100 words.""",
    
    'product_description': """Write a compelling product description for {product_name}.
    Target audience: {audience}. Include benefits, features, ideal use cases.
    Professional but engaging. Max 200 words.""",
    
    'blog_title': """Generate 5 catchy blog post titles about {topic}.
    Make them SEO-friendly, engaging, curiosity-inducing.
    Format as numbered list.""",
    
    'social_post': """Create a LinkedIn/Twitter post about {topic} from {persona}.
    Make it professional, insightful, shareable. Include relevant emoji.
    Max 280 characters.""",
    
    'campaign_copy': """Write marketing copy for {campaign_name} campaign.
    Goal: {goal}. Target: {target_audience}. Budget: {budget}.
    Include headline, sub-headline, CTA. Tone: {tone}""",
    
    'faq_answer': """Answer this FAQ question: {question}
    Context: {context}. Be clear, concise, helpful.
    Format as Q&A. Max 150 words.""",
}


def generate_content(content_type, variables, user_receipt=None):
    """Generate content using Claude API.
    
    Args:
        content_type: Type from PROMPT_TEMPLATES keys
        variables: Dict with template variables to fill
        user_receipt: Who requested this generation
        
    Returns:
        dict with generated content and metadata
    """
    try:
        import anthropic
    except ImportError:
        return {
            'error': 'Claude API not available. Install: pip install anthropic',
            'content': None
        }
    
    # Get template
    if content_type not in PROMPT_TEMPLATES:
        return {
            'error': f'Unknown content type. Available: {list(PROMPT_TEMPLATES.keys())}',
            'content': None
        }
    
    template = PROMPT_TEMPLATES[content_type]
    
    # Fill in variables
    try:
        prompt = template.format(**variables)
    except KeyError as e:
        return {
            'error': f'Missing variable: {e}',
            'content': None
        }
    
    # Call Claude
    try:
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        message = client.messages.create(
            model=GENERATION_CONFIG['model'],
            max_tokens=GENERATION_CONFIG['max_tokens'],
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        
        generated_content = message.content[0].text
        tokens_used = message.usage.input_tokens + message.usage.output_tokens
        cost_cents = int((tokens_used / 1000) * GENERATION_CONFIG['cost_per_1k_tokens'] * 100)
        
        # Store in database
        gen_id = f'GEN_{int(time.time())}_{content_type[:10]}'
        session = get_session()
        try:
            generation = AIGeneration(
                id=gen_id,
                content_type=content_type,
                prompt=prompt,
                generated_content=generated_content,
                tokens_used=tokens_used,
                cost_cents=cost_cents,
                quality_score=85,  # Default good score
                used_count=0,
                created_at=time.time(),
                created_by=user_receipt
            )
            session.add(generation)
            session.commit()
        finally:
            session.close()
        
        return {
            'success': True,
            'id': gen_id,
            'content': generated_content,
            'tokens': tokens_used,
            'cost_rupees': cost_cents / 100,
            'type': content_type
        }
    
    except Exception as e:
        return {
            'error': f'Claude API error: {str(e)}',
            'content': None
        }


def batch_generate(generations_list, user_receipt=None):
    """Generate multiple contents at once.
    
    Args:
        generations_list: List of {type, variables} dicts
        user_receipt: Who requested
        
    Returns:
        List of generation results
    """
    results = []
    total_cost = 0
    
    for item in generations_list:
        result = generate_content(item['type'], item['variables'], user_receipt)
        results.append(result)
        if 'cost_rupees' in result:
            total_cost += result['cost_rupees']
    
    return {
        'results': results,
        'count': len(results),
        'total_cost_rupees': total_cost
    }


def rate_generation(generation_id, rating):
    """Rate generated content (1-5 stars).
    
    Args:
        generation_id: ID of generation to rate
        rating: 1-5 score
        
    Returns:
        bool success
    """
    if not 1 <= rating <= 5:
        return False
    
    session = get_session()
    try:
        gen = session.query(AIGeneration).filter(
            AIGeneration.id == generation_id
        ).first()
        
        if gen:
            gen.user_rating = rating
            session.commit()
            return True
        return False
    finally:
        session.close()


def increment_usage(generation_id):
    """Track when content is actually used.
    
    Args:
        generation_id: ID of generation
        
    Returns:
        bool success
    """
    session = get_session()
    try:
        gen = session.query(AIGeneration).filter(
            AIGeneration.id == generation_id
        ).first()
        
        if gen:
            gen.used_count += 1
            session.commit()
            return True
        return False
    finally:
        session.close()


def get_generation_stats():
    """Get AI generation statistics.
    
    Returns:
        dict with stats
    """
    session = get_session()
    try:
        from sqlalchemy import func
        
        total = session.query(func.count(AIGeneration.id)).scalar() or 0
        total_tokens = session.query(func.sum(AIGeneration.tokens_used)).scalar() or 0
        total_cost = session.query(func.sum(AIGeneration.cost_cents)).scalar() or 0
        avg_rating = session.query(func.avg(AIGeneration.user_rating)).scalar() or 0
        
        # By type
        by_type = {}
        types = session.query(AIGeneration.content_type).distinct().all()
        for t in types:
            type_name = t[0]
            count = session.query(func.count(AIGeneration.id)).filter(
                AIGeneration.content_type == type_name
            ).scalar() or 0
            by_type[type_name] = count
        
        return {
            'total_generations': total,
            'total_tokens_used': total_tokens,
            'total_cost_rupees': total_cost / 100,
            'average_rating': round(avg_rating, 1),
            'by_type': by_type
        }
    finally:
        session.close()


def get_generations(content_type=None, limit=20):
    """Get recent generations.
    
    Args:
        content_type: Filter by type (optional)
        limit: Max results
        
    Returns:
        list of generations
    """
    session = get_session()
    try:
        query = session.query(AIGeneration)
        
        if content_type:
            query = query.filter(AIGeneration.content_type == content_type)
        
        gens = query.order_by(AIGeneration.created_at.desc()).limit(limit).all()
        
        result = []
        for g in gens:
            result.append({
                'id': g.id,
                'type': g.content_type,
                'content': g.generated_content[:100] + '...',  # Preview
                'rating': g.user_rating,
                'used': g.used_count,
                'cost': g.cost_cents / 100,
                'created': datetime.fromtimestamp(g.created_at).strftime('%Y-%m-%d %H:%M')
            })
        
        return result
    finally:
        session.close()


def regenerate_content(generation_id):
    """Regenerate content for a previous generation.
    
    Args:
        generation_id: ID to regenerate
        
    Returns:
        New generation result
    """
    session = get_session()
    try:
        gen = session.query(AIGeneration).filter(
            AIGeneration.id == generation_id
        ).first()
        
        if not gen:
            return {'error': 'Generation not found'}
        
        # Parse content type and variables from original prompt
        # Try to extract variables - this is best-effort
        return generate_content(gen.content_type, {}, gen.created_by)
    finally:
        session.close()
