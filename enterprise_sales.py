"""
Enterprise Sales System - Week 12 Final System
B2B lead generation, sales pipeline, deal management
"The harvest is plentiful but laborers are few" - Matthew 9:37
"""

import json
import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Enterprise Lead:
    """Enterprise sales lead."""
    lead_id: str
    company_name: str
    contact_email: str
    company_size: str
    industry: str
    estimated_value: float
    stage: str  # prospect, qualified, contacted, demo, negotiating, won
    created_date: float


class EnterpriseSalesSystem:
    """B2B enterprise sales automation."""
    
    def __init__(self):
        self.leads: Dict[str, Enterprise Lead] = {}
        self.deals: List[Dict] = []
    
    def create_lead(self, company_info: Dict) -> Dict:
        """Create new enterprise lead."""
        lead_id = f"lead_{uuid.uuid4().hex[:12]}"
        
        lead = Enterprise Lead(
            lead_id=lead_id,
            company_name=company_info["company_name"],
            contact_email=company_info["contact_email"],
            company_size=company_info.get("company_size", "unknown"),
            industry=company_info.get("industry", "unknown"),
            estimated_value=company_info.get("estimated_value", 50000),
            stage="prospect",
            created_date=time.time()
        )
        
        self.leads[lead_id] = lead
        
        return {
            "success": True,
            "lead_id": lead_id,
            "company": lead.company_name,
            "stage": lead.stage
        }
    
    def score_lead(self, lead_id: str) -> Dict:
        """Score lead for qualification."""
        if lead_id not in self.leads:
            return {"error": "Lead not found"}
        
        lead = self.leads[lead_id]
        
        # Simple scoring
        score = 0
        
        if lead.company_size in ["large", "enterprise"]:
            score += 40
        elif lead.company_size == "mid-market":
            score += 20
        
        if lead.estimated_value > 100000:
            score += 40
        elif lead.estimated_value > 50000:
            score += 20
        
        if lead.industry in ["tech", "finance", "healthcare"]:
            score += 20
        
        qualification = "qualified" if score > 60 else "prospect"
        
        return {
            "lead_id": lead_id,
            "score": score,
            "recommendation": qualification
        }
    
    def update_deal_stage(self, lead_id: str, stage: str) -> Dict:
        """Update deal stage in sales pipeline."""
        if lead_id not in self.leads:
            return {"error": "Lead not found"}
        
        lead = self.leads[lead_id]
        old_stage = lead.stage
        lead.stage = stage
        
        return {
            "success": True,
            "lead_id": lead_id,
            "old_stage": old_stage,
            "new_stage": stage
        }
