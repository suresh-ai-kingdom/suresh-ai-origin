"""
Universal API Gateway - Week 12 Final System
Single endpoint for ALL 50+ features with intelligent routing
"I am the way, the truth, and the life" - John 14:6
The way to access all blessings through one gateway
"""

import json
import time
import uuid
import hmac
import hashlib
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class APIKey:
    """API authentication key."""
    key_id: str
    key_secret: str
    user_id: str
    permissions: List[str] = field(default_factory=list)
    rate_limit: int = 1000  # requests per minute
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None


@dataclass
class FeatureEndpoint:
    """Feature endpoint registration."""
    endpoint_id: str
    name: str
    category: str
    description: str
    handler: Callable
    required_params: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    rate_limit_multiplier: float = 1.0


class UniversalAPIGateway:
    """Master gateway for all 50+ features."""
    
    def __init__(self):
        self.features: Dict[str, FeatureEndpoint] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.request_log: List[Dict] = []
        self.rate_limiters: Dict[str, Dict] = {}
    
    def register_feature(self, feature: FeatureEndpoint):
        """Register feature endpoint."""
        self.features[feature.endpoint_id] = feature
    
    def create_api_key(self, user_id: str, permissions: List[str], duration_days: int = 365) -> Dict:
        """Create new API key."""
        key_id = f"key_{uuid.uuid4().hex[:16]}"
        key_secret = hashlib.sha256(f"{key_id}:{time.time()}".encode()).hexdigest()
        
        expires_at = time.time() + (duration_days * 86400)
        
        api_key = APIKey(
            key_id=key_id,
            key_secret=key_secret,
            user_id=user_id,
            permissions=permissions,
            expires_at=expires_at
        )
        
        self.api_keys[key_id] = api_key
        
        return {
            "key_id": key_id,
            "key_secret": key_secret,
            "user_id": user_id,
            "permissions": permissions,
            "expires_at": datetime.fromtimestamp(expires_at).isoformat(),
            "warning": "Store secret securely - never share or commit to git"
        }
    
    def validate_request(self, request: Dict) -> Dict:
        """Validate API request."""
        # Extract auth
        auth_header = request.get("headers", {}).get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return {"valid": False, "error": "Missing bearer token"}
        
        key_id = auth_header[7:]
        
        # Check key exists
        if key_id not in self.api_keys:
            return {"valid": False, "error": "Invalid API key"}
        
        api_key = self.api_keys[key_id]
        
        # Check expiration
        if api_key.expires_at and time.time() > api_key.expires_at:
            return {"valid": False, "error": "API key expired"}
        
        # Check rate limit
        rate_limit_check = self._check_rate_limit(key_id, api_key.rate_limit)
        if not rate_limit_check["allowed"]:
            return {"valid": False, "error": "Rate limit exceeded"}
        
        # Verify signature
        body = json.dumps(request.get("body", {}), sort_keys=True)
        signature = request.get("headers", {}).get("X-Signature")
        
        expected_sig = hmac.new(
            api_key.key_secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if signature and signature != expected_sig:
            return {"valid": False, "error": "Invalid signature"}
        
        return {
            "valid": True,
            "user_id": api_key.user_id,
            "permissions": api_key.permissions,
            "key_id": key_id
        }
    
    def _check_rate_limit(self, key_id: str, limit: int) -> Dict:
        """Check rate limit for key."""
        if key_id not in self.rate_limiters:
            self.rate_limiters[key_id] = {
                "requests": [],
                "limit": limit
            }
        
        limiter = self.rate_limiters[key_id]
        current_minute = int(time.time() / 60)
        
        # Clean old requests
        limiter["requests"] = [
            r for r in limiter["requests"]
            if r > current_minute - 1
        ]
        
        if len(limiter["requests"]) >= limit:
            return {"allowed": False, "retry_after": 60}
        
        limiter["requests"].append(current_minute)
        
        return {"allowed": True}
    
    def handle_request(self, path: str, method: str, body: Dict, auth_header: str) -> Dict:
        """Handle incoming API request."""
        # Validate request
        validation = self.validate_request({
            "headers": {"Authorization": auth_header},
            "body": body
        })
        
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "status": 401
            }
        
        # Parse path: /api/v1/{category}/{feature}/{action}
        parts = path.strip("/").split("/")
        
        if len(parts) < 4:
            return {
                "success": False,
                "error": "Invalid endpoint format",
                "status": 400
            }
        
        category = parts[2]
        feature = parts[3]
        action = parts[4] if len(parts) > 4 else None
        
        # Find matching feature
        feature_key = f"{category}/{feature}"
        
        matching_features = [
            f for f in self.features.values()
            if f.category == category and f.name == feature
        ]
        
        if not matching_features:
            return {
                "success": False,
                "error": f"Feature not found: {feature_key}",
                "status": 404
            }
        
        feature_endpoint = matching_features[0]
        
        # Check permissions
        required_perms = feature_endpoint.permissions
        user_perms = validation.get("permissions", [])
        
        if required_perms and not any(p in user_perms for p in required_perms):
            return {
                "success": False,
                "error": "Insufficient permissions",
                "status": 403
            }
        
        # Execute handler
        try:
            result = feature_endpoint.handler(action, body, validation["user_id"])
            
            # Log request
            self._log_request(validation["user_id"], feature_key, result)
            
            return {
                "success": True,
                "data": result,
                "status": 200
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": 500
            }
    
    def _log_request(self, user_id: str, feature: str, result: Dict):
        """Log API request."""
        self.request_log.append({
            "user_id": user_id,
            "feature": feature,
            "timestamp": time.time(),
            "success": result.get("success", False)
        })
    
    def discover_features(self, category: Optional[str] = None) -> Dict:
        """Discover available features."""
        features = list(self.features.values())
        
        if category:
            features = [f for f in features if f.category == category]
        
        return {
            "total_features": len(features),
            "features": [
                {
                    "id": f.endpoint_id,
                    "name": f.name,
                    "category": f.category,
                    "description": f.description,
                    "required_params": f.required_params,
                    "endpoint": f"/api/v1/{f.category}/{f.name}"
                }
                for f in features
            ],
            "categories": list(set(f.category for f in self.features.values()))
        }
    
    def get_api_stats(self, user_id: str, days: int = 30) -> Dict:
        """Get API usage statistics."""
        cutoff_time = time.time() - (days * 86400)
        
        user_requests = [
            r for r in self.request_log
            if r["user_id"] == user_id and r["timestamp"] > cutoff_time
        ]
        
        total_requests = len(user_requests)
        successful = sum(1 for r in user_requests if r["success"])
        
        # Group by feature
        by_feature = {}
        for req in user_requests:
            feature = req["feature"]
            by_feature[feature] = by_feature.get(feature, 0) + 1
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_requests": total_requests,
            "successful_requests": successful,
            "success_rate": successful / total_requests if total_requests > 0 else 0,
            "requests_by_feature": by_feature,
            "top_feature": max(by_feature.items(), key=lambda x: x[1])[0] if by_feature else None
        }
    
    def generate_sdk(self, language: str) -> Dict:
        """Generate SDK for specific language."""
        sdk_templates = {
            "python": {
                "package": "suresh_ai_sdk",
                "import": "from suresh_ai_sdk import Client",
                "init": "client = Client(api_key='your_key')"
            },
            "javascript": {
                "package": "@suresh-ai/sdk",
                "import": "import { Client } from '@suresh-ai/sdk'",
                "init": "const client = new Client({ apiKey: 'your_key' })"
            },
            "go": {
                "package": "github.com/suresh-ai/sdk-go",
                "import": "import \"github.com/suresh-ai/sdk-go\"",
                "init": "client := sureshai.NewClient(\"your_key\")"
            }
        }
        
        if language not in sdk_templates:
            return {"success": False, "error": f"SDK not available for {language}"}
        
        template = sdk_templates[language]
        
        return {
            "success": True,
            "language": language,
            "sdk": template,
            "documentation_url": f"https://docs.suresh-ai.com/sdks/{language}",
            "github_url": f"https://github.com/suresh-ai/sdk-{language}",
            "npm_url": f"https://npmjs.com/package/{template['package']}" if language == "javascript" else None
        }


class IntelligentRouter:
    """Route requests to optimal feature handlers."""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.performance_metrics: Dict[str, Dict] = {}
    
    def register_handler(self, feature_id: str, handler: Callable):
        """Register feature handler."""
        self.handlers[feature_id] = handler
        self.performance_metrics[feature_id] = {
            "calls": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "errors": 0
        }
    
    def route(self, feature_id: str, request: Dict) -> Dict:
        """Route request to best handler."""
        if feature_id not in self.handlers:
            return {
                "success": False,
                "error": f"Handler not found: {feature_id}"
            }
        
        handler = self.handlers[feature_id]
        
        # Time execution
        start = time.time()
        
        try:
            result = handler(request)
            elapsed = time.time() - start
            
            # Update metrics
            metrics = self.performance_metrics[feature_id]
            metrics["calls"] += 1
            metrics["total_time"] += elapsed
            metrics["avg_time"] = metrics["total_time"] / metrics["calls"]
            
            return {
                "success": True,
                "data": result,
                "execution_time_ms": elapsed * 1000
            }
        
        except Exception as e:
            metrics = self.performance_metrics[feature_id]
            metrics["errors"] += 1
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_routing_stats(self) -> Dict:
        """Get routing performance statistics."""
        total_calls = sum(m["calls"] for m in self.performance_metrics.values())
        total_errors = sum(m["errors"] for m in self.performance_metrics.values())
        
        return {
            "total_handlers": len(self.handlers),
            "total_calls": total_calls,
            "total_errors": total_errors,
            "error_rate": total_errors / total_calls if total_calls > 0 else 0,
            "handlers": [
                {
                    "feature_id": fid,
                    "calls": m["calls"],
                    "avg_time_ms": m["avg_time"] * 1000,
                    "errors": m["errors"]
                }
                for fid, m in self.performance_metrics.items()
            ]
        }


class FeatureDiscovery:
    """Intelligent feature discovery and recommendation."""
    
    def __init__(self):
        self.usage_patterns: Dict[str, List[str]] = {}
        self.feature_relationships: Dict[str, List[str]] = {}
    
    def recommend_features(self, user_id: str, context: Dict) -> Dict:
        """Recommend features based on user context."""
        # Get user history
        history = self.usage_patterns.get(user_id, [])
        
        # Find related features
        recommendations = []
        
        for feature in history[-5:]:  # Recent features
            related = self.feature_relationships.get(feature, [])
            recommendations.extend(related)
        
        # Remove duplicates, rank by frequency
        from collections import Counter
        ranked = Counter(recommendations).most_common(5)
        
        return {
            "user_id": user_id,
            "recommendations": [
                {
                    "feature": feature,
                    "relevance_score": count / len(recommendations) if recommendations else 0
                }
                for feature, count in ranked
            ],
            "personalization_score": min(1.0, len(history) / 20)
        }
    
    def learn_relationships(self, feature_a: str, feature_b: str):
        """Learn relationship between features."""
        if feature_a not in self.feature_relationships:
            self.feature_relationships[feature_a] = []
        
        if feature_b not in self.feature_relationships[feature_a]:
            self.feature_relationships[feature_a].append(feature_b)
    
    def track_usage(self, user_id: str, feature: str):
        """Track feature usage."""
        if user_id not in self.usage_patterns:
            self.usage_patterns[user_id] = []
        
        self.usage_patterns[user_id].append(feature)
