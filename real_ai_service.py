"""
Real AI Service - SURESH AI ORIGIN
Unified interface for all AI providers (OpenAI, Claude, Gemini, Groq)
"""

import os
import json
import logging
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Provider detection
AI_PROVIDER = os.getenv('AI_PROVIDER', 'claude')  # openai, claude, gemini, groq, demo
AI_MODEL = os.getenv('AI_MODEL', 'claude-opus-4.5')

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')


class RealAI:
    """Unified AI interface supporting multiple providers."""
    
    def __init__(self):
        self.provider = AI_PROVIDER.lower()
        self.model = AI_MODEL
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate AI client based on provider."""
        try:
            if self.provider == 'openai' and OPENAI_API_KEY:
                from openai import OpenAI
                self.client = OpenAI(api_key=OPENAI_API_KEY)
                logging.info(f"✅ OpenAI client initialized: {self.model}")
                
            elif self.provider == 'claude' and ANTHROPIC_API_KEY:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
                logging.info(f"✅ Claude client initialized: {self.model}")
                
            elif self.provider == 'gemini' and GOOGLE_API_KEY:
                import google.generativeai as genai
                genai.configure(api_key=GOOGLE_API_KEY)
                self.client = genai.GenerativeModel(self.model)
                logging.info(f"✅ Gemini client initialized: {self.model}")
                
            elif self.provider == 'groq' and GROQ_API_KEY:
                from groq import Groq
                self.client = Groq(api_key=GROQ_API_KEY)
                logging.info(f"✅ Groq client initialized: {self.model}")
                
            else:
                logging.warning(f"⚠️ AI Provider '{self.provider}' not configured - using DEMO mode")
                self.provider = 'demo'
                
        except ImportError as e:
            logging.error(f"❌ Failed to import AI library: {e}")
            logging.info("💡 Install required package: pip install openai anthropic google-generativeai groq")
            self.provider = 'demo'
        except Exception as e:
            logging.error(f"❌ Failed to initialize AI client: {e}")
            self.provider = 'demo'
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text completion using configured AI provider."""
        
        if self.provider == 'demo':
            return self._demo_response(prompt)
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            
            elif self.provider == 'claude':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif self.provider == 'gemini':
                response = self.client.generate_content(
                    prompt,
                    generation_config={
                        'max_output_tokens': max_tokens,
                        'temperature': temperature
                    }
                )
                return response.text
            
            elif self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"AI generation error: {e}")
            return self._demo_response(prompt)
    
    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 500) -> str:
        """Multi-turn chat conversation."""
        
        if self.provider == 'demo':
            last_msg = messages[-1]['content'] if messages else "Hello"
            return f"🤖 DEMO: I received your message: '{last_msg}'. Configure real AI to enable actual conversations!"
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == 'claude':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=messages
                )
                return response.content[0].text
            
            elif self.provider == 'gemini':
                # Convert to Gemini format
                chat = self.client.start_chat(history=[])
                for msg in messages[:-1]:
                    chat.send_message(msg['content'])
                response = chat.send_message(messages[-1]['content'])
                return response.text
            
            elif self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
                
        except Exception as e:
            logging.error(f"AI chat error: {e}")
            return f"Error: {str(e)}"
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text (positive/negative/neutral)."""
        prompt = f"""Analyze the sentiment of this text and respond ONLY with valid JSON:

Text: "{text}"

Response format:
{{"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0, "emotion": "happy|sad|angry|neutral", "summary": "one sentence"}}"""
        
        response = self.generate(prompt, max_tokens=200, temperature=0.3)
        
        try:
            # Try to parse JSON from response
            return json.loads(response)
        except:
            # Fallback response
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotion": "neutral",
                "summary": "Unable to analyze sentiment"
            }
    
    def generate_content(self, content_type: str, topic: str, tone: str = "professional") -> str:
        """Generate marketing content (email, blog, social post)."""
        
        prompts = {
            "email": f"Write a professional marketing email about {topic}. Tone: {tone}. Include subject line.",
            "blog": f"Write a 500-word blog post about {topic}. Tone: {tone}. Include title and SEO keywords.",
            "social": f"Write 3 social media posts about {topic}. Tone: {tone}. Include hashtags.",
            "ad": f"Write compelling ad copy for {topic}. Tone: {tone}. Include headline and CTA.",
        }
        
        prompt = prompts.get(content_type, f"Write content about {topic}")
        return self.generate(prompt, max_tokens=1500, temperature=0.8)
    
    def predict(self, data: Dict, prediction_type: str) -> Dict:
        """Make predictions based on data (churn, revenue, growth)."""
        
        prompt = f"""You are a data scientist. Analyze this data and predict {prediction_type}:

Data: {json.dumps(data, indent=2)}

Respond with ONLY valid JSON:
{{"prediction": "value", "confidence": 0.0-1.0, "factors": ["factor1", "factor2"], "recommendation": "action to take"}}"""
        
        response = self.generate(prompt, max_tokens=500, temperature=0.3)
        
        try:
            return json.loads(response)
        except:
            return {
                "prediction": "Unable to predict",
                "confidence": 0.0,
                "factors": ["Insufficient data"],
                "recommendation": "Collect more data"
            }
    
    def _demo_response(self, prompt: str) -> str:
        """Demo mode response when no AI provider configured."""
        return f"""🎭 DEMO MODE RESPONSE

Your prompt: "{prompt[:100]}..."

This is a simulated AI response. To enable REAL AI:

1. Get FREE Gemini API key: https://aistudio.google.com/
2. Add to Render environment:
   GOOGLE_API_KEY=your_key_here
   AI_PROVIDER=gemini
   AI_MODEL=gemini-pro

3. Restart service

Then you'll get real AI responses powered by Google Gemini!

Read AI_INTEGRATION_GUIDE.md for full setup.
"""
    
    def is_real(self) -> bool:
        """Check if real AI is configured."""
        return self.provider != 'demo'
    
    def get_status(self) -> Dict:
        """Get AI service status."""
        return {
            "provider": self.provider,
            "model": self.model,
            "is_real": self.is_real(),
            "client_initialized": self.client is not None
        }


# Global AI instance
ai_service = RealAI()


# Convenience functions
def generate_ai_content(prompt: str, **kwargs) -> str:
    """Quick access to AI generation."""
    return ai_service.generate(prompt, **kwargs)


def ai_chat(messages: List[Dict], **kwargs) -> str:
    """Quick access to AI chat."""
    return ai_service.chat(messages, **kwargs)


def analyze_text_sentiment(text: str) -> Dict:
    """Quick access to sentiment analysis."""
    return ai_service.analyze_sentiment(text)


def create_marketing_content(content_type: str, topic: str, tone: str = "professional") -> str:
    """Quick access to content generation."""
    return ai_service.generate_content(content_type, topic, tone)


def predict_with_ai(data: Dict, prediction_type: str) -> Dict:
    """Quick access to predictions."""
    return ai_service.predict(data, prediction_type)


def is_ai_real() -> bool:
    """Check if real AI is configured (not demo mode)."""
    return ai_service.is_real()


def get_ai_status() -> Dict:
    """Get current AI service configuration."""
    return ai_service.get_status()


# Test function
if __name__ == '__main__':
    print("Testing AI Service...")
    print(f"Provider: {ai_service.provider}")
    print(f"Model: {ai_service.model}")
    print(f"Real AI: {ai_service.is_real()}")
    
    test_response = generate_ai_content("Say hello to SURESH AI ORIGIN!")
    print(f"\nTest Response:\n{test_response}")
