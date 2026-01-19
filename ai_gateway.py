#!/usr/bin/env python3
"""
AI GATEWAY: Central Router for Suresh AI Origin's Rare AI Internet
Routes requests to decentralized nodes, local agents, and AI services
with VIP authentication, rarity enforcement, and revenue optimization.
"""

import os
import jwt
import json
import time
import logging
import hashlib
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from cryptography.fernet import Fernet, InvalidToken

from flask import Flask, request, jsonify, session, render_template_string
from werkzeug.security import check_password_hash, generate_password_hash

# Import existing AI systems
try:
    from decentralized_ai_node import DecentralizedAINode
    from autonomous_business_agent import AutonomousBusinessAgent
    from revenue_optimization_ai import RevenueOptimizationAI
    from real_ai_service import RealAI
    IMPORTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some imports unavailable: {e}. Running in demo mode.")
    IMPORTS_AVAILABLE = False

try:
    from enterprise_layer import EnterpriseLayer
except ImportError:
    EnterpriseLayer = None  # type: ignore

try:
    from analytics_deep_insights import AnalyticsDeepInsights
except ImportError:
    class AnalyticsDeepInsights:  # type: ignore
        def track_usage(self, event: str, data: Dict[str, Any]):
            return True
        def log_event(self, event: str, data: Dict[str, Any]):
            return True


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_gateway.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Configuration
class Config:
    """Gateway configuration."""
    SECRET_KEY = os.getenv('GATEWAY_SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret-key-change-in-production')
    JWT_EXPIRATION_HOURS = 24
    
    # VIP Configuration
    VIP_TIERS = {
        'free': {'rate_limit': 10, 'priority': 1, 'rarity_threshold': 0},
        'basic': {'rate_limit': 50, 'priority': 2, 'rarity_threshold': 50},
        'pro': {'rate_limit': 200, 'priority': 3, 'rarity_threshold': 70},
        'enterprise': {'rate_limit': 1000, 'priority': 4, 'rarity_threshold': 85},
        'elite': {'rate_limit': -1, 'priority': 5, 'rarity_threshold': 90}  # -1 = unlimited
    }
    
    # Routing Configuration
    ROUTE_TO_DECENTRALIZED = True
    ROUTE_TO_LOCAL_AGENT = True
    ENABLE_AI_BROWSE = True
    ENABLE_AUTO_CONTENT = True
    
    # Performance
    MAX_CONCURRENT_REQUESTS = 100
    REQUEST_TIMEOUT = 300
    CACHE_TTL = 3600


enterprise_key_env = os.getenv('ENTERPRISE_FERNET_KEY')
_enterprise_key = enterprise_key_env.encode() if enterprise_key_env else None
enterprise_layer = EnterpriseLayer(_enterprise_key) if EnterpriseLayer else None
analytics_client = AnalyticsDeepInsights()


class EnterpriseGatewayLayer:
    def __init__(self, layer: Optional[EnterpriseLayer], analytics: Optional[AnalyticsDeepInsights]):
        self.layer = layer
        self.analytics = analytics
        self.top_user_projection = 600_000_000

    def auth_enterprise(self, user: Dict[str, Any], cui_payload: Dict[str, Any]) -> Dict[str, Any]:
        vip = user.get('vip_tier')
        allowed = vip in ['elite', 'enterprise', 'one_percent']
        encrypted = None
        if allowed and self.layer:
            encrypted = self.layer.encrypt_payload({'cui': cui_payload, 'ts': time.time()})
        return {
            'allowed': allowed,
            'encrypted_cui': encrypted,
            'vip_tier': vip,
            'projection_users': self.top_user_projection,
        }

    def layer_insights(self, query: str, signals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.layer:
            return {'query': query, 'insights': [], 'timestamp': time.time()}
        insights = self.layer.semantic_insights(query, signals)
        if self.analytics:
            self.analytics.track_usage('enterprise_layer_insights', {'query': query, 'score': insights['insights'][0]['score'] if insights.get('insights') else 0})
        return insights

    def enforce_rarity(self, vip_tier: str, rarity_score: float) -> bool:
        if rarity_score >= 95:
            return vip_tier in ['elite', 'enterprise', 'one_percent']
        tier_cfg = Config.VIP_TIERS.get(vip_tier, Config.VIP_TIERS['free'])
        threshold = tier_cfg['rarity_threshold']
        return rarity_score >= threshold or threshold >= 85

    def worldwide_deploy(self, payload: Dict[str, Any], regions: List[str]) -> Dict[str, Any]:
        if not self.layer:
            return {'partners': [], 'calls': []}
        partners = self.layer.worldwide_partners(regions)
        calls = [self.layer.partner_call(p['partner'], payload) for p in partners]
        return {'partners': partners, 'calls': calls}


enterprise_gateway_layer = EnterpriseGatewayLayer(enterprise_layer, analytics_client)


# Data Models
@dataclass
class User:
    """User with VIP tier."""
    user_id: str
    email: str
    password_hash: str
    vip_tier: str
    created_at: float
    request_count: int = 0
    last_request_time: float = 0.0


@dataclass
class AIRequest:
    """Incoming AI request."""
    request_id: str
    user_id: str
    query: str
    query_type: str  # search, generate, browse, analyze
    vip_tier: str
    timestamp: float
    metadata: Dict[str, Any]


@dataclass
class AIResponse:
    """AI response with routing info."""
    request_id: str
    success: bool
    result: str
    source: str  # decentralized, local_agent, direct_ai
    processing_time: float
    rarity_score: float
    revenue_impact: float
    metadata: Dict[str, Any]


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['JSON_SORT_KEYS'] = False


# In-memory storage (replace with database in production)
users_db = {
    'demo@suresh.ai': User(
        user_id='user_demo',
        email='demo@suresh.ai',
        password_hash=generate_password_hash('demo123'),
        vip_tier='elite',
        created_at=time.time()
    )
}
request_history = []
active_requests = {}


# Initialize AI systems
class AISystemManager:
    """Manages all AI system instances."""
    
    def __init__(self):
        self.decentralized_node = None
        self.business_agent = None
        self.revenue_optimizer = None
        self.real_ai = None
        self.initialized = False
    
    def initialize(self):
        """Initialize all AI systems."""
        if self.initialized:
            return
        
        try:
            if IMPORTS_AVAILABLE:
                # Decentralized node
                if Config.ROUTE_TO_DECENTRALIZED:
                    self.decentralized_node = DecentralizedAINode(
                        node_id="gateway_node",
                        rarity_threshold=90.0
                    )
                    self.decentralized_node.start()
                    logger.info("✓ Decentralized node initialized")
                
                # Business agent
                if Config.ROUTE_TO_LOCAL_AGENT:
                    self.business_agent = AutonomousBusinessAgent()
                    logger.info("✓ Business agent initialized")
                
                # Revenue optimizer
                self.revenue_optimizer = RevenueOptimizationAI()
                logger.info("✓ Revenue optimizer initialized")
                
                # Real AI service
                self.real_ai = RealAI()
                logger.info("✓ Real AI service initialized")
            
            self.initialized = True
            logger.info("✓ AI Gateway systems initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize AI systems: {e}")
            # Continue with limited functionality
    
    def shutdown(self):
        """Shutdown all AI systems."""
        try:
            if self.decentralized_node:
                self.decentralized_node.stop()
            logger.info("✓ AI systems shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global AI system manager
ai_systems = AISystemManager()


# Authentication & Authorization
def generate_jwt(user: User) -> str:
    """Generate JWT token for user."""
    payload = {
        'user_id': user.user_id,
        'email': user.email,
        'vip_tier': user.vip_tier,
        'exp': datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')


def verify_jwt(token: str) -> Optional[Dict]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token")
        return None


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
            payload = verify_jwt(token)
            
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Attach user info to request
            request.user = payload
            return f(*args, **kwargs)
        
        except Exception as e:
            logger.error(f"Auth error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function


def enforce_rate_limit(user_id: str, vip_tier: str) -> bool:
    """Enforce rate limiting based on VIP tier."""
    tier_config = Config.VIP_TIERS.get(vip_tier, Config.VIP_TIERS['free'])
    rate_limit = tier_config['rate_limit']
    
    if rate_limit == -1:  # Unlimited
        return True
    
    # Get user
    user = next((u for u in users_db.values() if u.user_id == user_id), None)
    if not user:
        return False
    
    # Check rate limit (requests per hour)
    current_time = time.time()
    time_window = 3600  # 1 hour
    
    if current_time - user.last_request_time > time_window:
        user.request_count = 0
        user.last_request_time = current_time
    
    if user.request_count >= rate_limit:
        logger.warning(f"Rate limit exceeded for user {user_id}")
        return False
    
    user.request_count += 1
    return True


def check_rarity_access(vip_tier: str, rarity_score: float) -> bool:
    """Check if user's VIP tier can access content with given rarity score."""
    if enterprise_gateway_layer:
        return enterprise_gateway_layer.enforce_rarity(vip_tier, rarity_score)
    tier_config = Config.VIP_TIERS.get(vip_tier, Config.VIP_TIERS['free'])
    threshold = tier_config['rarity_threshold']
    return threshold >= 85 or rarity_score >= threshold


# Request Router
class RequestRouter:
    """Routes requests to appropriate AI system."""
    
    @staticmethod
    def determine_query_type(query: str) -> str:
        """Determine query type from user input."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['search', 'find', 'lookup', 'what is']):
            return 'search'
        elif any(word in query_lower for word in ['generate', 'create', 'write', 'make']):
            return 'generate'
        elif any(word in query_lower for word in ['browse', 'visit', 'fetch', 'url', 'website']):
            return 'browse'
        elif any(word in query_lower for word in ['analyze', 'examine', 'review', 'evaluate']):
            return 'analyze'
        else:
            return 'general'
    
    @staticmethod
    def calculate_rarity_score(query: str, vip_tier: str) -> float:
        """Calculate rarity score for query."""
        score = 0.0
        
        # Base score from query complexity
        word_count = len(query.split())
        score += min(20, word_count * 2)
        
        # VIP tier bonus
        tier_bonuses = {
            'free': 0,
            'basic': 10,
            'pro': 20,
            'enterprise': 30,
            'elite': 40
        }
        score += tier_bonuses.get(vip_tier, 0)
        
        # Query type bonus
        query_type = RequestRouter.determine_query_type(query)
        type_bonuses = {
            'search': 5,
            'generate': 15,
            'browse': 10,
            'analyze': 20,
            'general': 5
        }
        score += type_bonuses.get(query_type, 0)
        
        return min(100, score)
    
    @staticmethod
    def route_request(ai_request: AIRequest) -> AIResponse:
        """Route request to appropriate AI system."""
        start_time = time.time()
        
        try:
            # Calculate rarity
            rarity_score = RequestRouter.calculate_rarity_score(
                ai_request.query,
                ai_request.vip_tier
            )
            
            # Check access
            if not check_rarity_access(ai_request.vip_tier, rarity_score):
                return AIResponse(
                    request_id=ai_request.request_id,
                    success=False,
                    result=f"Access denied. Your VIP tier ({ai_request.vip_tier}) cannot access content with rarity {rarity_score:.1f}. Upgrade to access rare AI content.",
                    source='gateway',
                    processing_time=time.time() - start_time,
                    rarity_score=rarity_score,
                    revenue_impact=0.0,
                    metadata={'access_denied': True}
                )
            
            # Route based on query type and rarity
            if ai_request.query_type == 'browse' and Config.ENABLE_AI_BROWSE:
                result = RequestRouter._handle_browse(ai_request)
                source = 'ai_browse'
            
            elif ai_request.query_type == 'generate' and Config.ENABLE_AUTO_CONTENT:
                result = RequestRouter._handle_generate(ai_request)
                source = 'auto_content'
            
            elif rarity_score >= 90 and Config.ROUTE_TO_DECENTRALIZED:
                result = RequestRouter._handle_decentralized(ai_request)
                source = 'decentralized'
            
            elif Config.ROUTE_TO_LOCAL_AGENT:
                result = RequestRouter._handle_local_agent(ai_request)
                source = 'local_agent'
            
            else:
                result = RequestRouter._handle_direct_ai(ai_request)
                source = 'direct_ai'
            
            processing_time = time.time() - start_time
            
            # Calculate revenue impact
            revenue_impact = RequestRouter._calculate_revenue_impact(
                ai_request.vip_tier,
                rarity_score,
                processing_time
            )
            
            # Log to revenue optimizer
            if ai_systems.revenue_optimizer:
                try:
                    ai_systems.revenue_optimizer.log_request(
                        user_id=ai_request.user_id,
                        vip_tier=ai_request.vip_tier,
                        rarity_score=rarity_score,
                        revenue=revenue_impact
                    )
                except Exception as e:
                    logger.warning(f"Failed to log to revenue optimizer: {e}")
            
            return AIResponse(
                request_id=ai_request.request_id,
                success=True,
                result=result,
                source=source,
                processing_time=processing_time,
                rarity_score=rarity_score,
                revenue_impact=revenue_impact,
                metadata={
                    'query_type': ai_request.query_type,
                    'vip_tier': ai_request.vip_tier
                }
            )
        
        except Exception as e:
            logger.error(f"Request routing failed: {e}")
            return AIResponse(
                request_id=ai_request.request_id,
                success=False,
                result=f"Request failed: {str(e)}",
                source='error',
                processing_time=time.time() - start_time,
                rarity_score=0.0,
                revenue_impact=0.0,
                metadata={'error': str(e)}
            )
    
    @staticmethod
    def _handle_browse(ai_request: AIRequest) -> str:
        """Handle AI browse request (mock fetch + summarize)."""
        logger.info(f"AI Browse: {ai_request.query}")
        
        # Extract URL from query
        import re
        url_match = re.search(r'https?://[^\s]+', ai_request.query)
        url = url_match.group(0) if url_match else None
        
        if not url:
            return "No URL found in query. Please provide a URL to browse."
        
        # Mock fetch content
        mock_content = f"""
        [AI-Fetched Content from {url}]
        
        This is a simulated fetch of web content. In production, this would:
        1. Fetch the actual webpage content
        2. Extract relevant text and metadata
        3. Filter ads and irrelevant content
        4. Structure the information
        
        For now, returning mock summary.
        """
        
        # Summarize with AI
        if ai_systems.real_ai:
            try:
                summary_prompt = f"Summarize the following content from {url}:\n\n{mock_content}\n\nProvide a concise 3-paragraph summary."
                summary = ai_systems.real_ai.generate(summary_prompt)
                return f"🌐 AI Browse Results for {url}\n\n{summary}\n\n[Source: AI-powered fetch & summarization]"
            except Exception as e:
                logger.error(f"AI summarization failed: {e}")
        
        return mock_content
    
    @staticmethod
    def _handle_generate(ai_request: AIRequest) -> str:
        """Handle auto-content generation."""
        logger.info(f"Auto-Generate: {ai_request.query}")
        
        if ai_systems.real_ai:
            try:
                # Add personalization based on VIP tier
                vip_prefix = ""
                if ai_request.vip_tier in ['pro', 'enterprise', 'elite']:
                    vip_prefix = "[Premium Content] "
                
                result = ai_systems.real_ai.generate(ai_request.query)
                return f"{vip_prefix}{result}"
            
            except Exception as e:
                logger.error(f"Content generation failed: {e}")
                return f"Content generation failed: {str(e)}"
        
        return "AI content generation not available. Please configure real_ai_service."
    
    @staticmethod
    def _handle_decentralized(ai_request: AIRequest) -> str:
        """Route to decentralized AI node."""
        logger.info(f"Routing to decentralized node: {ai_request.query}")
        
        if ai_systems.decentralized_node:
            try:
                task = {
                    'task_id': ai_request.request_id,
                    'task_type': ai_request.query_type,
                    'prompt': ai_request.query,
                    'priority': 'critical' if ai_request.vip_tier in ['enterprise', 'elite'] else 'high',
                    'complexity': 9.0,
                    'creator_address': ai_request.user_id
                }
                
                result = ai_systems.decentralized_node.process_task(task)
                
                if result['success']:
                    return f"🌐 [Decentralized AI Network]\n\n{result.get('result', 'Processing complete')}\n\n[Rarity Score: {result.get('rarity_score', 0):.1f}/100]"
                else:
                    # Fall back to local processing
                    return RequestRouter._handle_direct_ai(ai_request)
            
            except Exception as e:
                logger.error(f"Decentralized routing failed: {e}")
        
        return RequestRouter._handle_direct_ai(ai_request)
    
    @staticmethod
    def _handle_local_agent(ai_request: AIRequest) -> str:
        """Route to local business agent."""
        logger.info(f"Routing to local agent: {ai_request.query}")
        
        if ai_systems.business_agent:
            try:
                result = ai_systems.business_agent.process_query(ai_request.query)
                return f"🤖 [Autonomous Business Agent]\n\n{result}"
            
            except Exception as e:
                logger.error(f"Local agent routing failed: {e}")
        
        return RequestRouter._handle_direct_ai(ai_request)
    
    @staticmethod
    def _handle_direct_ai(ai_request: AIRequest) -> str:
        """Direct AI processing (fallback)."""
        logger.info(f"Direct AI processing: {ai_request.query}")
        
        if ai_systems.real_ai:
            try:
                return ai_systems.real_ai.generate(ai_request.query)
            except Exception as e:
                logger.error(f"Direct AI failed: {e}")
        
        return f"Processed query: {ai_request.query}\n\n[Demo Mode: Real AI systems not available]"
    
    @staticmethod
    def _calculate_revenue_impact(vip_tier: str, rarity_score: float, processing_time: float) -> float:
        """Calculate revenue impact of request."""
        tier_values = {
            'free': 0.0,
            'basic': 0.01,
            'pro': 0.05,
            'enterprise': 0.20,
            'elite': 0.50
        }
        
        base_value = tier_values.get(vip_tier, 0.0)
        rarity_multiplier = rarity_score / 50  # 0.5x to 2.0x
        efficiency_bonus = 0.1 if processing_time < 5 else 0
        
        return base_value * rarity_multiplier + efficiency_bonus


# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'systems': {
            'decentralized_node': ai_systems.decentralized_node is not None,
            'business_agent': ai_systems.business_agent is not None,
            'revenue_optimizer': ai_systems.revenue_optimizer is not None,
            'real_ai': ai_systems.real_ai is not None
        }
    })


@app.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = users_db.get(email)
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = generate_jwt(user)
    
    logger.info(f"User logged in: {email}")
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'user_id': user.user_id,
            'email': user.email,
            'vip_tier': user.vip_tier
        }
    })


@app.route('/auth/register', methods=['POST'])
def register():
    """User registration endpoint."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    vip_tier = data.get('vip_tier', 'free')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    if email in users_db:
        return jsonify({'error': 'Email already registered'}), 400
    
    if vip_tier not in Config.VIP_TIERS:
        return jsonify({'error': f'Invalid VIP tier. Options: {list(Config.VIP_TIERS.keys())}'}), 400
    
    user = User(
        user_id=f"user_{hashlib.md5(email.encode()).hexdigest()[:8]}",
        email=email,
        password_hash=generate_password_hash(password),
        vip_tier=vip_tier,
        created_at=time.time()
    )
    
    users_db[email] = user
    token = generate_jwt(user)
    
    logger.info(f"New user registered: {email} ({vip_tier})")
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'user_id': user.user_id,
            'email': user.email,
            'vip_tier': user.vip_tier
        }
    }), 201


@app.route('/api/query', methods=['POST'])
@require_auth
def process_query():
    """Main API endpoint for AI queries."""
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    user_info = request.user
    user_id = user_info['user_id']
    vip_tier = user_info['vip_tier']
    
    # Rate limiting
    if not enforce_rate_limit(user_id, vip_tier):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': f'Your {vip_tier} tier allows {Config.VIP_TIERS[vip_tier]["rate_limit"]} requests per hour'
        }), 429
    
    # Create request
    request_id = f"req_{int(time.time())}_{hashlib.md5(query.encode()).hexdigest()[:8]}"
    query_type = RequestRouter.determine_query_type(query)
    
    ai_request = AIRequest(
        request_id=request_id,
        user_id=user_id,
        query=query,
        query_type=query_type,
        vip_tier=vip_tier,
        timestamp=time.time(),
        metadata=data.get('metadata', {})
    )
    
    # Track active request
    active_requests[request_id] = ai_request
    
    response = RequestRouter.route_request(ai_request)

    enterprise_meta = None
    if response.rarity_score >= 90 and enterprise_gateway_layer:
        enterprise_meta = {
            'auth': enterprise_gateway_layer.auth_enterprise(user_info, {'request_id': request_id, 'cui': True}),
            'insights': enterprise_gateway_layer.layer_insights(query, data.get('signals')),
            'deploy': enterprise_gateway_layer.worldwide_deploy(
                {'rarity_score': response.rarity_score, 'gpus': data.get('gpus', 512)},
                regions=data.get('regions', ['us', 'eu', 'in'])
            ),
        }
    
    # Save to history
    request_history.append({
        'request': asdict(ai_request),
        'response': asdict(response),
        'enterprise': enterprise_meta,
        'timestamp': time.time()
    })

    if analytics_client:
        try:
            analytics_client.track_usage('ai_gateway_request', {
                'user_id': user_id,
                'vip_tier': vip_tier,
                'rarity_score': response.rarity_score,
                'source': response.source,
                'enterprise': bool(enterprise_meta),
            })
        except Exception as exc:
            logger.warning(f"Analytics tracking failed: {exc}")
    
    # Remove from active
    active_requests.pop(request_id, None)
    
    logger.info(f"Query processed: {query[:50]}... | User: {user_id} | Source: {response.source}")
    
    return jsonify({
        'success': response.success,
        'request_id': response.request_id,
        'result': response.result,
        'metadata': {
            'source': response.source,
            'processing_time': response.processing_time,
            'rarity_score': response.rarity_score,
            'revenue_impact': response.revenue_impact,
            'query_type': query_type,
            'vip_tier': vip_tier,
            'enterprise': enterprise_meta
        }
    })


@app.route('/api/browse', methods=['POST'])
@require_auth
def ai_browse():
    """AI-powered web browsing endpoint."""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    user_info = request.user
    
    query = f"Browse and summarize: {url}"
    ai_request = AIRequest(
        request_id=f"browse_{int(time.time())}",
        user_id=user_info['user_id'],
        query=query,
        query_type='browse',
        vip_tier=user_info['vip_tier'],
        timestamp=time.time(),
        metadata={'url': url}
    )
    
    response = RequestRouter.route_request(ai_request)
    
    return jsonify({
        'success': response.success,
        'url': url,
        'summary': response.result,
        'processing_time': response.processing_time
    })


@app.route('/api/generate', methods=['POST'])
@require_auth
def auto_generate():
    """Auto-content generation endpoint."""
    data = request.get_json()
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({'error': 'Prompt required'}), 400
    
    user_info = request.user
    
    ai_request = AIRequest(
        request_id=f"gen_{int(time.time())}",
        user_id=user_info['user_id'],
        query=prompt,
        query_type='generate',
        vip_tier=user_info['vip_tier'],
        timestamp=time.time(),
        metadata=data.get('metadata', {})
    )
    
    response = RequestRouter.route_request(ai_request)
    
    return jsonify({
        'success': response.success,
        'content': response.result,
        'rarity_score': response.rarity_score,
        'processing_time': response.processing_time
    })


@app.route('/api/stats', methods=['GET'])
@require_auth
def get_stats():
    """Get user statistics."""
    user_info = request.user
    user_id = user_info['user_id']
    
    # Count user requests
    user_requests = [
        r for r in request_history
        if r['request']['user_id'] == user_id
    ]
    
    total_requests = len(user_requests)
    successful_requests = sum(1 for r in user_requests if r['response']['success'])
    total_revenue = sum(r['response']['revenue_impact'] for r in user_requests)
    avg_rarity = sum(r['response']['rarity_score'] for r in user_requests) / max(total_requests, 1)
    
    return jsonify({
        'user_id': user_id,
        'vip_tier': user_info['vip_tier'],
        'stats': {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / max(total_requests, 1) * 100,
            'total_revenue_impact': total_revenue,
            'average_rarity_score': avg_rarity
        }
    })


@app.route('/admin/dashboard', methods=['GET'])
@require_auth
def admin_dashboard():
    """Admin dashboard (requires elite tier)."""
    user_info = request.user
    
    if user_info['vip_tier'] != 'elite':
        return jsonify({'error': 'Elite tier required'}), 403
    
    # Aggregate stats
    total_requests = len(request_history)
    active_count = len(active_requests)
    
    sources = {}
    for r in request_history:
        source = r['response']['source']
        sources[source] = sources.get(source, 0) + 1
    
    vip_distribution = {}
    for r in request_history:
        tier = r['request']['vip_tier']
        vip_distribution[tier] = vip_distribution.get(tier, 0) + 1
    
    total_revenue = sum(r['response']['revenue_impact'] for r in request_history)
    
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Gateway Admin Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
            .metric {{ display: inline-block; margin: 20px; padding: 20px; background: #f0f0f0; border-radius: 8px; min-width: 150px; }}
            .metric h3 {{ margin: 0; color: #666; font-size: 14px; }}
            .metric p {{ margin: 10px 0 0 0; font-size: 32px; font-weight: bold; color: #4CAF50; }}
            .section {{ margin: 30px 0; }}
            .section h2 {{ color: #555; border-left: 4px solid #4CAF50; padding-left: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #4CAF50; color: white; }}
            .status-healthy {{ color: #4CAF50; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 AI Gateway Admin Dashboard</h1>
            
            <div class="section">
                <div class="metric">
                    <h3>Total Requests</h3>
                    <p>{total_requests}</p>
                </div>
                <div class="metric">
                    <h3>Active Requests</h3>
                    <p>{active_count}</p>
                </div>
                <div class="metric">
                    <h3>Total Revenue</h3>
                    <p>${total_revenue:.2f}</p>
                </div>
                <div class="metric">
                    <h3>Total Users</h3>
                    <p>{len(users_db)}</p>
                </div>
            </div>
            
            <div class="section">
                <h2>Request Sources</h2>
                <table>
                    <tr><th>Source</th><th>Count</th><th>Percentage</th></tr>
                    {''.join(f'<tr><td>{source}</td><td>{count}</td><td>{count/max(total_requests,1)*100:.1f}%</td></tr>' for source, count in sources.items())}
                </table>
            </div>
            
            <div class="section">
                <h2>VIP Tier Distribution</h2>
                <table>
                    <tr><th>Tier</th><th>Requests</th><th>Percentage</th></tr>
                    {''.join(f'<tr><td>{tier}</td><td>{count}</td><td>{count/max(total_requests,1)*100:.1f}%</td></tr>' for tier, count in vip_distribution.items())}
                </table>
            </div>
            
            <div class="section">
                <h2>System Status</h2>
                <table>
                    <tr><th>Component</th><th>Status</th></tr>
                    <tr><td>Decentralized Node</td><td class="status-healthy">{'✓ Active' if ai_systems.decentralized_node else '✗ Inactive'}</td></tr>
                    <tr><td>Business Agent</td><td class="status-healthy">{'✓ Active' if ai_systems.business_agent else '✗ Inactive'}</td></tr>
                    <tr><td>Revenue Optimizer</td><td class="status-healthy">{'✓ Active' if ai_systems.revenue_optimizer else '✗ Inactive'}</td></tr>
                    <tr><td>Real AI Service</td><td class="status-healthy">{'✓ Active' if ai_systems.real_ai else '✗ Inactive'}</td></tr>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return dashboard_html


# Demo function
def demo_gateway():
    """Demonstrate AI Gateway functionality."""
    print("\n" + "="*80)
    print("AI GATEWAY DEMO".center(80))
    print("="*80 + "\n")
    
    # Initialize systems
    print("Initializing AI systems...")
    ai_systems.initialize()
    print()
    
    # Demo scenarios
    scenarios = [
        {
            'name': 'VIP Elite User - Complex Analysis',
            'user': users_db['demo@suresh.ai'],
            'query': 'Analyze our Q4 revenue drop and provide a detailed recovery strategy'
        },
        {
            'name': 'Free User - Simple Query',
            'user': User(
                user_id='user_free',
                email='free@example.com',
                password_hash='',
                vip_tier='free',
                created_at=time.time()
            ),
            'query': 'What is machine learning?'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{'─'*80}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"{'─'*80}")
        
        user = scenario['user']
        query = scenario['query']
        
        print(f"User: {user.email} ({user.vip_tier})")
        print(f"Query: {query}\n")
        
        # Create request
        request_id = f"demo_{int(time.time())}"
        query_type = RequestRouter.determine_query_type(query)
        
        ai_request = AIRequest(
            request_id=request_id,
            user_id=user.user_id,
            query=query,
            query_type=query_type,
            vip_tier=user.vip_tier,
            timestamp=time.time(),
            metadata={}
        )
        
        # Process
        response = RequestRouter.route_request(ai_request)
        
        print(f"✓ Query Type: {query_type}")
        print(f"✓ Rarity Score: {response.rarity_score:.1f}/100")
        print(f"✓ Source: {response.source}")
        print(f"✓ Processing Time: {response.processing_time:.3f}s")
        print(f"✓ Revenue Impact: ${response.revenue_impact:.4f}")
        print(f"\nResult Preview:")
        print(response.result[:200] + "..." if len(response.result) > 200 else response.result)
    
    print("\n" + "="*80)
    print("DEMO COMPLETE".center(80))
    print("="*80 + "\n")
    
    # Shutdown
    ai_systems.shutdown()


if __name__ == '__main__':
    import sys
    
    if '--demo' in sys.argv:
        demo_gateway()
    else:
        # Initialize systems
        ai_systems.initialize()
        
        # Run Flask server
        print("\n" + "="*80)
        print("AI GATEWAY SERVER STARTING".center(80))
        print("="*80)
        print(f"\nListening on: http://127.0.0.1:5000")
        print(f"Health Check: http://127.0.0.1:5000/health")
        print(f"\nDemo Credentials:")
        print(f"  Email: demo@suresh.ai")
        print(f"  Password: demo123")
        print(f"  VIP Tier: elite")
        print(f"\nTo run demo: python ai_gateway.py --demo")
        print("="*80 + "\n")
        
        try:
            app.run(host='0.0.0.0', port=5000, debug=False)
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            ai_systems.shutdown()
        except Exception as e:
            logger.error(f"Server error: {e}")
            ai_systems.shutdown()
