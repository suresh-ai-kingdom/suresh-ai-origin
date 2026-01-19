"""
Rarest Task Template Marketplace (2026) - Suresh AI Origin
Pre-built task templates for instant monetization: blog posts, code generation, design, research, etc.

Features:
- Task templates: 50+ pre-designed jobs (SEO posts, API code, UI mockups, competitor analysis, etc.)
- One-click launch: Select template → auto-create jobs → dispatch to swarm.
- Pricing catalog: Dynamic pricing based on complexity, delivery time, quality tier.
- Marketplace UI: Search, filter, rate, buy/sell templates.
- Creator royalties: Template authors earn 20-40% on each use.
- Performance tracking: Template success rate, avg quality, ratings.
- Integration: Plugs into task automation engine + dispatcher.
- Voice trigger: "Use template 'blog posts' 100 times" → auto-dispatch.
- Demo: Browse templates → purchase → execute → collect earnings.
"""

import json
import logging
import time
import random
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class RarestTaskTemplate:
    """Single task template."""

    def __init__(self, template_id: str, name: str, description: str, task_type: str, base_complexity: float, base_pay_inr: float, fields: List[str], creator_id: str = "system"):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.task_type = task_type
        self.base_complexity = base_complexity
        self.base_pay_inr = base_pay_inr
        self.fields = fields
        self.creator_id = creator_id
        self.usage_count = 0
        self.avg_quality = 0.85
        self.ratings = []
        self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "base_complexity": self.base_complexity,
            "base_pay_inr": self.base_pay_inr,
            "fields": self.fields,
            "creator_id": self.creator_id,
            "usage_count": self.usage_count,
            "avg_quality": self.avg_quality,
            "rating": round(sum(self.ratings) / max(len(self.ratings), 1), 1) if self.ratings else 0.0,
        }


class RarestTaskTemplateMarketplace:
    """Central marketplace for task templates."""

    DEFAULT_TEMPLATES = {
        "seo_blog_post": RarestTaskTemplate("seo_blog_post", "SEO Blog Post (1000 words)", "Write SEO-optimized blog post on given topic", "writing", 0.7, 100, ["topic", "keywords", "tone"], "system"),
        "api_code_generation": RarestTaskTemplate("api_code_generation", "API Code Generation (Python/Node)", "Generate REST API endpoint with docs", "coding", 0.9, 150, ["endpoint", "method", "response_schema"], "system"),
        "ui_mockup_design": RarestTaskTemplate("ui_mockup_design", "UI Mockup Design (Figma)", "Create interactive UI mockup for app", "design", 0.8, 120, ["feature_name", "user_story", "style_guide"], "system"),
        "competitor_research": RarestTaskTemplate("competitor_research", "Competitor Analysis Report", "Research 5 competitors + summary", "research", 0.75, 80, ["industry", "target_company", "metrics"], "system"),
        "data_entry_cleaning": RarestTaskTemplate("data_entry_cleaning", "Data Entry & Cleaning (CSV)", "Clean & structure 1000 data rows", "data_entry", 0.5, 60, ["source_file", "target_schema", "validation_rules"], "system"),
        "podcast_transcription": RarestTaskTemplate("podcast_transcription", "Podcast Transcription (1 hour)", "Transcribe & timestamp audio", "transcription", 0.6, 90, ["audio_url", "language", "format"], "system"),
        "linkedin_email_scraping": RarestTaskTemplate("linkedin_email_scraping", "LinkedIn Data Scraping (100 profiles)", "Extract name, email, title from profiles", "research", 0.65, 110, ["search_query", "filters", "output_format"], "system"),
        "video_editing_subtitle": RarestTaskTemplate("video_editing_subtitle", "Video Subtitle Generation & Sync", "Generate subtitles from video + sync timing", "design", 0.75, 130, ["video_url", "language", "style"], "system"),
        "social_media_post": RarestTaskTemplate("social_media_post", "Social Media Content (5 posts/day)", "Create 5 engaging posts for Instagram/Twitter", "writing", 0.6, 70, ["brand_voice", "hashtags", "platform"], "system"),
        "technical_documentation": RarestTaskTemplate("technical_documentation", "Technical Docs (API/SDK)", "Write comprehensive technical documentation", "writing", 0.8, 140, ["product_name", "audience", "scope"], "system"),
    }

    def __init__(self, min_rarity: float = 95.0):
        self.min_rarity = min_rarity
        self.templates: Dict[str, RarestTaskTemplate] = {}
        self.templates.update(self.DEFAULT_TEMPLATES)
        self.purchases: List[Dict[str, Any]] = []
        self.creator_royalties: Dict[str, float] = defaultdict(float)

    def _rarity_gate(self, rarity: float):
        if rarity < self.min_rarity:
            raise PermissionError("Marketplace requires rarity >= 95")

    def list_templates(self, task_type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available templates."""
        templates = list(self.templates.values())
        if task_type_filter:
            templates = [t for t in templates if t.task_type == task_type_filter]
        return [t.to_dict() for t in templates]

    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """Search templates by name or description."""
        query_lower = query.lower()
        results = [t for t in self.templates.values() if query_lower in t.name.lower() or query_lower in t.description.lower()]
        return [t.to_dict() for t in results]

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template details."""
        template = self.templates.get(template_id)
        return template.to_dict() if template else None

    def purchase_template_job(
        self, template_id: str, job_count: int, rarity_score: float = 100.0, buyer_id: str = "user_1"
    ) -> Dict[str, Any]:
        """Purchase jobs using a template."""
        self._rarity_gate(rarity_score)
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        # Calculate total cost
        total_cost = template.base_pay_inr * job_count
        # Log purchase
        purchase = {
            "purchase_id": f"purchase_{int(time.time())}",
            "template_id": template_id,
            "job_count": job_count,
            "total_cost_inr": total_cost,
            "buyer_id": buyer_id,
            "purchased_at": time.time(),
            "jobs": [{"job_id": f"job_{template_id}_{i}", "spec": template.to_dict()} for i in range(job_count)],
        }
        self.purchases.append(purchase)
        template.usage_count += job_count
        # Creator royalty
        if template.creator_id != "system":
            royalty_rate = 0.25  # 25% for custom templates
            royalty = total_cost * royalty_rate
            self.creator_royalties[template.creator_id] += royalty
        return purchase

    def rate_template(self, template_id: str, rating: float):
        """Rate a template (1-5 stars)."""
        template = self.templates.get(template_id)
        if template:
            template.ratings.append(max(1.0, min(5.0, rating)))
            template.avg_quality = sum(template.ratings) / len(template.ratings)

    def create_custom_template(
        self, name: str, description: str, task_type: str, base_complexity: float, base_pay_inr: float, fields: List[str], creator_id: str
    ) -> Dict[str, Any]:
        """Allow creators to add custom templates."""
        template_id = f"custom_{int(time.time())}_{random.randint(0, 9999)}"
        template = RarestTaskTemplate(template_id, name, description, task_type, base_complexity, base_pay_inr, fields, creator_id)
        self.templates[template_id] = template
        return template.to_dict()

    def get_creator_earnings(self, creator_id: str) -> float:
        """Get total royalties earned by creator."""
        return round(self.creator_royalties.get(creator_id, 0.0), 2)


from collections import defaultdict


# Demo
# ------------------------------------------------------------------
if __name__ == "__main__":
    marketplace = RarestTaskTemplateMarketplace()
    # List all templates
    print("=== Available Templates ===")
    all_templates = marketplace.list_templates()
    print(json.dumps(all_templates[:3], indent=2))
    # Search
    print("\n=== Search Results: 'writing' ===")
    writing_templates = marketplace.list_templates(task_type_filter="writing")
    print(json.dumps(writing_templates, indent=2))
    # Purchase jobs using template
    print("\n=== Purchase 50 'SEO Blog Post' Jobs ===")
    purchase = marketplace.purchase_template_job("seo_blog_post", 50, buyer_id="user_123", rarity_score=100)
    print(json.dumps({k: v for k, v in purchase.items() if k != "jobs"}, indent=2))
    # Rate template
    marketplace.rate_template("seo_blog_post", 4.5)
    print(f"Template Rating Updated: {marketplace.get_template('seo_blog_post')['rating']} stars")
    # Create custom template
    print("\n=== Create Custom Template ===")
    custom = marketplace.create_custom_template(
        "Email Campaign Writer",
        "Write 10 marketing emails for campaign",
        "writing",
        0.65,
        85,
        ["campaign_name", "target_audience", "cta"],
        "creator_alice",
    )
    print(json.dumps(custom, indent=2))
