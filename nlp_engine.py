"""
NLP Engine - Natural Language Processing for text analysis, sentiment analysis, and understanding
Powers chatbot, support ticket analysis, and user feedback processing
"""

import re
from typing import Dict, List, Tuple, Optional
from collections import Counter
from real_ai_service import get_ai_response

class NLPEngine:
    def __init__(self):
        self.stop_words = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'and', 'or', 'but', 'in',
            'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'if',
            'that', 'this', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
            'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'
        }
        self.sentiment_words = {
            'positive': ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                        'awesome', 'perfect', 'love', 'best', 'happy', 'satisfied'],
            'negative': ['bad', 'terrible', 'awful', 'horrible', 'poor', 'hate', 'worst',
                        'angry', 'frustrated', 'disappointed', 'unhappy', 'broken']
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of text
        Returns: {sentiment: 'positive'|'negative'|'neutral', score: 0-1, confidence: 0-1}
        """
        try:
            prompt = f"""
            Analyze sentiment of this text: "{text}"
            Return JSON: {{"sentiment": "positive/negative/neutral", "score": 0.8, "confidence": 0.95}}
            """
            
            response = get_ai_response(prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {'sentiment': 'neutral', 'score': 0.5, 'confidence': 0.5}
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities (people, places, organizations, etc.)"""
        try:
            prompt = f"""
            Extract named entities from: "{text}"
            Return JSON with keys: persons, places, organizations, products, dates
            """
            
            response = get_ai_response(prompt)
            entities = self._parse_json_response(response)
            return entities or {'persons': [], 'places': [], 'organizations': [], 'products': [], 'dates': []}
            
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {'persons': [], 'places': [], 'organizations': [], 'products': [], 'dates': []}
    
    def classify_text(self, text: str, categories: List[str]) -> Dict[str, float]:
        """Classify text into predefined categories"""
        try:
            categories_str = ', '.join(categories)
            prompt = f"""
            Classify this text into categories: {categories_str}
            Text: "{text}"
            Return JSON with scores for each category (0-1)
            """
            
            response = get_ai_response(prompt)
            return self._parse_json_response(response) or {cat: 0.5 for cat in categories}
            
        except Exception as e:
            print(f"Error classifying text: {e}")
            return {cat: 0.5 for cat in categories}
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """Extract top N keywords from text"""
        try:
            # Remove stop words
            words = re.findall(r'\w+', text.lower())
            keywords = [w for w in words if w not in self.stop_words and len(w) > 2]
            
            # Count frequency
            word_freq = Counter(keywords)
            
            # Ask AI for importance
            prompt = f"""
            Rank these keywords by importance: {list(word_freq.keys())[:20]}
            For text about: "{text[:200]}"
            Return JSON with keyword: score pairs
            """
            
            ai_scores = self._parse_json_response(get_ai_response(prompt))
            if ai_scores:
                return sorted(ai_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
            else:
                return word_freq.most_common(top_n)
                
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def summarize_text(self, text: str, max_length: int = 100) -> str:
        """Generate summary of text"""
        try:
            prompt = f"Summarize this text in maximum {max_length} characters: {text}"
            return get_ai_response(prompt)
        except Exception as e:
            print(f"Error summarizing: {e}")
            return text[:max_length]
    
    def answer_question(self, question: str, context: str = "") -> str:
        """Answer question based on context"""
        try:
            if context:
                prompt = f"Based on: {context}\nAnswer: {question}"
            else:
                prompt = question
            
            return get_ai_response(prompt)
        except Exception as e:
            print(f"Error answering question: {e}")
            return "Unable to answer question"
    
    def detect_language(self, text: str) -> Dict[str, any]:
        """Detect language of text"""
        try:
            prompt = f'Detect language of: "{text}". Return: {{"language": "english", "confidence": 0.95}}'
            return self._parse_json_response(get_ai_response(prompt))
        except Exception as e:
            print(f"Error detecting language: {e}")
            return {'language': 'unknown', 'confidence': 0.0}
    
    def correct_grammar(self, text: str) -> str:
        """Correct grammar and spelling"""
        try:
            prompt = f'Correct grammar and spelling: "{text}". Return only corrected text.'
            return get_ai_response(prompt)
        except Exception as e:
            print(f"Error correcting grammar: {e}")
            return text
    
    def generate_response(self, user_input: str, context: str = "") -> str:
        """Generate contextual response to user input"""
        try:
            if context:
                prompt = f"Context: {context}\nUser: {user_input}\nRespond:"
            else:
                prompt = f"User: {user_input}\nRespond:"
            
            return get_ai_response(prompt)
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm unable to respond at the moment"
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from AI response"""
        try:
            if "{" in response and "}" in response:
                import json
                json_str = response[response.find("{"):response.rfind("}")+1]
                return json.loads(json_str)
            return None
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return None

# Initialize globally
nlp_engine = NLPEngine()

# Wrapper functions
def analyze_sentiment(text: str) -> Dict:
    return nlp_engine.analyze_sentiment(text)

def extract_entities(text: str) -> Dict:
    return nlp_engine.extract_entities(text)

def classify_text(text: str, categories: List[str]) -> Dict:
    return nlp_engine.classify_text(text, categories)

def extract_keywords(text: str, top_n: int = 5) -> List[Tuple[str, float]]:
    return nlp_engine.extract_keywords(text, top_n)

def summarize_text(text: str, max_length: int = 100) -> str:
    return nlp_engine.summarize_text(text, max_length)

def answer_question(question: str, context: str = "") -> str:
    return nlp_engine.answer_question(question, context)
