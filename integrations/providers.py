"""
Unified wrappers for Claude and OpenAI API providers.

Exposes:
  - ClaudeProvider(api_key: str, model: str)
  - OpenAIProvider(api_key: str, model: str)
  - Both implement invoke(messages: list[dict]) -> str

Usage:
    claude = ClaudeProvider(os.getenv("ANTHROPIC_API_KEY"))
    resp = claude.invoke([{"role": "user", "content": "Hi"}])
"""

from __future__ import annotations

import os
import logging
from typing import Dict, List, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base for AI providers."""

    @abstractmethod
    def invoke(self, messages: List[Dict[str, str]]) -> str:
        """Send messages and return text response."""
        pass


class ClaudeProvider(AIProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        if not self.api_key:
            logger.warning("ClaudeProvider: No API key provided")

    def invoke(self, messages: List[Dict[str, str]]) -> str:
        try:
            import anthropic
        except ImportError:
            logger.error("anthropic package not installed. Run: pip install anthropic")
            raise

        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=messages,
            )
            return response.content[0].text
        except Exception as e:
            logger.exception("Claude invoke failed: %s", e)
            raise


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        if not self.api_key:
            logger.warning("OpenAIProvider: No API key provided")

    def invoke(self, messages: List[Dict[str, str]]) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")
            raise

        try:
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2048,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.exception("OpenAI invoke failed: %s", e)
            raise
