"""
Recommendations Engine - AI-Powered Product/Service Suggestions
Provides personalized recommendations based on user behavior, preferences, and collaborative filtering
"""

from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from real_ai_service import get_ai_response

class RecommendationsEngine:
    def __init__(self):
        self.cache = {}
        self.recommendation_timeout = 3600  # 1 hour cache
        
    def get_personalized_recommendations(self, user_id: str, context: Dict[str, Any]) -> List[Dict]:
        """
        Generate personalized recommendations for a user
        
        Args:
            user_id: User ID
            context: User context (browsing history, purchases, preferences)
            
        Returns:
            List of recommended items with scores
        """
        try:
            # Build recommendation prompt for AI
            prompt = f"""
            Based on user behavior:
            - Purchase history: {context.get('purchase_history', [])}
            - Browsing history: {context.get('browsing_history', [])}
            - Preferences: {context.get('preferences', {})}
            
            Generate 5 personalized product recommendations with scores 0-1.
            Return JSON: [{{"product_id": "...", "score": 0.9, "reason": "..."}}]
            """
            
            recommendations = get_ai_response(prompt)
            return self._parse_recommendations(recommendations)
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
    
    def get_trending_recommendations(self, category: str = None) -> List[Dict]:
        """Get trending items recommendations"""
        try:
            prompt = f"What are trending products in {category or 'all categories'}?"
            response = get_ai_response(prompt)
            return self._parse_recommendations(response)
        except Exception as e:
            print(f"Error getting trending: {e}")
            return []
    
    def get_collaborative_recommendations(self, user_id: str, similar_users: List[str]) -> List[Dict]:
        """Get recommendations from similar users (collaborative filtering)"""
        try:
            prompt = f"""
            Based on what similar users bought:
            {similar_users}
            
            Recommend products this user might like.
            Return JSON list of recommendations.
            """
            
            recommendations = get_ai_response(prompt)
            return self._parse_recommendations(recommendations)
            
        except Exception as e:
            print(f"Error in collaborative filtering: {e}")
            return []
    
    def get_crosssell_recommendations(self, product_id: str) -> List[Dict]:
        """Get cross-sell recommendations based on product"""
        try:
            prompt = f"What products would cross-sell well with product {product_id}?"
            response = get_ai_response(prompt)
            return self._parse_recommendations(response)
        except Exception as e:
            print(f"Error getting cross-sell: {e}")
            return []
    
    def get_upsell_recommendations(self, current_purchase: Dict) -> List[Dict]:
        """Get upsell recommendations (premium alternatives)"""
        try:
            prompt = f"""
            User just purchased: {current_purchase}
            Suggest premium upgrades or higher-tier alternatives.
            Return JSON recommendations.
            """
            
            response = get_ai_response(prompt)
            return self._parse_recommendations(response)
            
        except Exception as e:
            print(f"Error getting upsell: {e}")
            return []
    
    def _parse_recommendations(self, response: str) -> List[Dict]:
        """Parse AI response into recommendation list"""
        try:
            # Extract JSON from response
            if "[" in response and "]" in response:
                json_str = response[response.find("["):response.rfind("]")+1]
                return json.loads(json_str)
            return []
        except Exception as e:
            print(f"Error parsing recommendations: {e}")
            return []
    
    def score_recommendation(self, user_id: str, product_id: str, 
                           features: Dict[str, Any]) -> float:
        """Calculate recommendation score (0-1) for a product"""
        try:
            score = 0.5  # Base score
            
            # Boost based on features
            if features.get('in_wishlist'):
                score += 0.2
            if features.get('price_range_match'):
                score += 0.15
            if features.get('similar_to_purchased'):
                score += 0.15
            
            return min(score, 1.0)
            
        except Exception as e:
            print(f"Error scoring recommendation: {e}")
            return 0.5

# Initialize globally
recommendations_engine = RecommendationsEngine()

def get_recommendations(user_id: str, rec_type: str = "personalized", **kwargs) -> List[Dict]:
    """Wrapper function for getting recommendations"""
    
    if rec_type == "personalized":
        return recommendations_engine.get_personalized_recommendations(
            user_id, kwargs.get('context', {})
        )
    elif rec_type == "trending":
        return recommendations_engine.get_trending_recommendations(
            kwargs.get('category')
        )
    elif rec_type == "collaborative":
        return recommendations_engine.get_collaborative_recommendations(
            user_id, kwargs.get('similar_users', [])
        )
    elif rec_type == "crosssell":
        return recommendations_engine.get_crosssell_recommendations(
            kwargs.get('product_id')
        )
    elif rec_type == "upsell":
        return recommendations_engine.get_upsell_recommendations(
            kwargs.get('current_purchase', {})
        )
    else:
        return recommendations_engine.get_personalized_recommendations(
            user_id, kwargs.get('context', {})
        )
