"""
Real-time Analytics Engine - Feature #17
Tracks visitors, analyzes conversion funnels, builds user journeys, and provides live KPIs
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque

# ============================================================================
# VISITOR TRACKING
# ============================================================================

class VisitorTracker:
    """Track real-time visitor activity"""
    
    def __init__(self, max_history: int = 1000):
        self.visitors = {}  # session_id -> visitor data
        self.events_queue = deque(maxlen=max_history)  # Last N events
        self.page_views = defaultdict(int)
        self.source_attribution = defaultdict(int)
    
    def track_visitor(
        self,
        session_id: str,
        page: str,
        source: str = "direct",
        referrer: str = None,
        device: str = "desktop"
    ) -> Dict:
        """Track a visitor page view"""
        
        visitor = self.visitors.get(session_id, {
            "session_id": session_id,
            "first_page": page,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "pages_visited": [],
            "source": source,
            "referrer": referrer,
            "device": device,
            "duration_seconds": 0,
            "events": [],
            "is_active": True
        })
        
        # Add page view
        visitor["pages_visited"].append({
            "page": page,
            "timestamp": datetime.now().isoformat(),
            "duration_on_page": random.randint(10, 600)
        })
        visitor["last_seen"] = datetime.now().isoformat()
        
        # Track event
        event = {
            "session_id": session_id,
            "type": "page_view",
            "page": page,
            "timestamp": datetime.now().isoformat(),
            "device": device,
            "source": source
        }
        self.events_queue.append(event)
        self.page_views[page] += 1
        self.source_attribution[source] += 1
        
        # Store visitor
        self.visitors[session_id] = visitor
        
        return {
            "session_id": session_id,
            "status": "tracked",
            "pages_visited": len(visitor["pages_visited"]),
            "current_page": page
        }
    
    def track_event(
        self,
        session_id: str,
        event_type: str,
        event_data: Dict = None
    ) -> Dict:
        """Track custom events (click, form submit, add to cart, etc.)"""
        
        if session_id not in self.visitors:
            return {"status": "error", "message": "Session not found"}
        
        event = {
            "session_id": session_id,
            "type": event_type,
            "data": event_data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.events_queue.append(event)
        self.visitors[session_id]["events"].append(event)
        
        return {
            "session_id": session_id,
            "event_type": event_type,
            "status": "tracked"
        }
    
    def get_active_visitors(self, minutes: int = 5) -> List[Dict]:
        """Get currently active visitors"""
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        active = []
        
        for session_id, visitor in self.visitors.items():
            last_seen = datetime.fromisoformat(visitor["last_seen"])
            if last_seen > cutoff_time:
                active.append({
                    "session_id": session_id,
                    "current_page": visitor["pages_visited"][-1]["page"] if visitor["pages_visited"] else "unknown",
                    "duration_seconds": visitor["duration_seconds"],
                    "pages_visited": len(visitor["pages_visited"]),
                    "source": visitor["source"],
                    "device": visitor["device"],
                    "last_seen": visitor["last_seen"]
                })
        
        return sorted(active, key=lambda x: x["last_seen"], reverse=True)
    
    def get_visitor_summary(self) -> Dict:
        """Get visitor summary statistics"""
        
        total_visitors = len(self.visitors)
        active_visitors = len(self.get_active_visitors())
        total_pageviews = sum(self.page_views.values())
        
        sources = dict(self.source_attribution)
        top_pages = sorted(self.page_views.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_visitors": total_visitors,
            "active_visitors": active_visitors,
            "total_pageviews": total_pageviews,
            "avg_pages_per_visitor": round(total_pageviews / max(total_visitors, 1), 2),
            "traffic_sources": sources,
            "top_pages": dict(top_pages),
            "unique_sessions": total_visitors
        }


# ============================================================================
# CONVERSION FUNNEL ANALYSIS
# ============================================================================

class ConversionFunnelAnalyzer:
    """Analyze conversion funnels"""
    
    # Standard e-commerce funnel
    STANDARD_FUNNEL = [
        "landing",
        "product_view",
        "add_to_cart",
        "checkout_start",
        "payment",
        "confirmation"
    ]
    
    def __init__(self):
        self.funnel_steps = {}
    
    def build_funnel(
        self,
        visitors: Dict,
        funnel_steps: List[str] = None
    ) -> Dict:
        """Build conversion funnel from visitor events"""
        
        if funnel_steps is None:
            funnel_steps = self.STANDARD_FUNNEL
        
        step_counts = {step: 0 for step in funnel_steps}
        dropoff = {}
        
        # Count visitors at each step
        for session_id, visitor in visitors.items():
            visitor_events = set(e["type"] for e in visitor["events"])
            
            for i, step in enumerate(funnel_steps):
                if step in visitor_events or step == funnel_steps[0]:
                    step_counts[step] += 1
        
        # Calculate dropoff
        for i in range(len(funnel_steps) - 1):
            current_step = funnel_steps[i]
            next_step = funnel_steps[i + 1]
            
            current_count = step_counts[current_step]
            next_count = step_counts[next_step]
            
            if current_count > 0:
                dropoff_rate = ((current_count - next_count) / current_count) * 100
                dropoff[f"{current_step}→{next_step}"] = round(dropoff_rate, 2)
        
        # Calculate conversion rates
        conversion_rate = (step_counts[funnel_steps[-1]] / max(step_counts[funnel_steps[0]], 1)) * 100
        
        return {
            "funnel_name": "Standard Conversion Funnel",
            "steps": funnel_steps,
            "visitor_counts": step_counts,
            "dropoff_rates": dropoff,
            "overall_conversion_rate": round(conversion_rate, 2),
            "critical_dropoff": max(dropoff.values()) if dropoff else 0,
            "recommendations": generate_funnel_recommendations(dropoff, conversion_rate)
        }
    
    def analyze_by_segment(
        self,
        visitors: Dict,
        segment_key: str = "device"
    ) -> Dict:
        """Analyze funnel by segment (device, source, etc.)"""
        
        segments = defaultdict(dict)
        
        for session_id, visitor in visitors.items():
            segment = visitor.get(segment_key, "unknown")
            
            if segment not in segments:
                segments[segment] = {"count": 0, "conversions": 0}
            
            segments[segment]["count"] += 1
            
            # Check if converted (has payment event)
            has_payment = any(e["type"] == "payment" for e in visitor["events"])
            if has_payment:
                segments[segment]["conversions"] += 1
        
        analysis = {}
        for segment, data in segments.items():
            conv_rate = (data["conversions"] / max(data["count"], 1)) * 100
            analysis[segment] = {
                "visitors": data["count"],
                "conversions": data["conversions"],
                "conversion_rate": round(conv_rate, 2)
            }
        
        return {
            "segment_type": segment_key,
            "analysis": analysis,
            "best_performing": max(analysis.items(), key=lambda x: x[1]["conversion_rate"], default=("N/A", {}))
        }


def generate_funnel_recommendations(dropoff: Dict, conversion_rate: float) -> List[str]:
    """Generate optimization recommendations based on funnel analysis"""
    
    recommendations = []
    
    # Check for critical dropoff points
    for step, rate in dropoff.items():
        if rate > 50:
            recommendations.append(f"⚠️ CRITICAL: {rate:.1f}% dropoff at {step} - requires immediate attention")
        elif rate > 30:
            recommendations.append(f"🔴 High dropoff at {step} ({rate:.1f}%) - optimize this step")
    
    if conversion_rate < 1:
        recommendations.append("📊 Conversion rate below 1% - consider A/B testing landing page")
    elif conversion_rate < 3:
        recommendations.append("📈 Room for improvement - optimize checkout process")
    
    if not recommendations:
        recommendations.append("✅ Funnel performing well - focus on traffic growth")
    
    return recommendations


# ============================================================================
# USER JOURNEY HEATMAPS
# ============================================================================

class UserJourneyAnalyzer:
    """Analyze user journeys and generate heatmaps"""
    
    def __init__(self):
        self.transitions = defaultdict(lambda: defaultdict(int))
    
    def build_journey_heatmap(self, visitors: Dict) -> Dict:
        """Build transition heatmap from page to page"""
        
        for session_id, visitor in visitors.items():
            pages = visitor.get("pages_visited", [])
            
            # Track transitions
            for i in range(len(pages) - 1):
                from_page = pages[i]["page"]
                to_page = pages[i + 1]["page"]
                self.transitions[from_page][to_page] += 1
        
        # Convert to heatmap format
        heatmap = {}
        for from_page, transitions in self.transitions.items():
            total_transitions = sum(transitions.values())
            heatmap[from_page] = {
                "total_exits": total_transitions,
                "destinations": dict(transitions),
                "bounce_rate": 0 if total_transitions > 0 else 100  # Would need single-page visitors
            }
        
        return {
            "heatmap": heatmap,
            "total_transitions": sum(len(trans) for trans in self.transitions.values()),
            "unique_pages": len(self.transitions),
            "most_visited_entry": max(
                self.transitions.items(),
                key=lambda x: sum(x[1].values()),
                default=("N/A", {})
            )[0],
            "exit_pages": [
                page for page, trans in self.transitions.items()
                if sum(trans.values()) == 0
            ]
        }
    
    def get_user_segments(self, visitors: Dict) -> Dict:
        """Segment users by journey characteristics"""
        
        segments = {
            "bounces": [],  # Single page visitors
            "browsers": [],  # Multiple pages, no purchase
            "converters": [],  # Completed purchase
            "high_value": []  # High engagement + purchase
        }
        
        for session_id, visitor in visitors.items():
            pages = len(visitor.get("pages_visited", []))
            events = visitor.get("events", [])
            has_purchase = any(e["type"] == "payment" for e in events)
            
            if pages == 1:
                segments["bounces"].append(session_id)
            elif has_purchase:
                if pages > 5:
                    segments["high_value"].append(session_id)
                else:
                    segments["converters"].append(session_id)
            else:
                segments["browsers"].append(session_id)
        
        return {
            "segment_distribution": {
                k: len(v) for k, v in segments.items()
            },
            "segment_percentages": {
                k: round((len(v) / len(visitors)) * 100, 2) if visitors else 0
                for k, v in segments.items()
            },
            "high_value_visitors": len(segments["high_value"]),
            "conversion_segments": len(segments["converters"]) + len(segments["high_value"])
        }


# ============================================================================
# REAL-TIME KPI AGGREGATION
# ============================================================================

def calculate_real_time_kpis(
    visitors: Dict,
    events_queue,
    time_window_minutes: int = 60
) -> Dict:
    """Calculate real-time KPIs for the dashboard"""
    
    # Active visitors
    tracker = VisitorTracker()
    tracker.visitors = visitors
    tracker.events_queue = events_queue
    active = len(tracker.get_active_visitors(minutes=5))
    
    # Total metrics
    total_visitors = len(visitors)
    total_events = len(events_queue)
    
    # Engagement metrics
    total_time_on_site = 0
    pages_viewed = 0
    
    for visitor in visitors.values():
        for page in visitor.get("pages_visited", []):
            pages_viewed += 1
            total_time_on_site += page.get("duration_on_page", 0)
    
    avg_time = total_time_on_site / max(pages_viewed, 1)
    bounce_rate = sum(1 for v in visitors.values() if len(v.get("pages_visited", [])) == 1) / max(total_visitors, 1) * 100
    
    # Conversion metrics
    conversions = sum(1 for v in visitors.values() if any(e["type"] == "payment" for e in v.get("events", [])))
    conversion_rate = (conversions / max(total_visitors, 1)) * 100
    
    # Traffic sources
    sources = defaultdict(int)
    for visitor in visitors.values():
        sources[visitor.get("source", "unknown")] += 1
    
    top_source = max(sources.items(), key=lambda x: x[1], default=("direct", 0))[0]
    
    # Device distribution
    devices = defaultdict(int)
    for visitor in visitors.values():
        devices[visitor.get("device", "unknown")] += 1
    
    return {
        "timestamp": datetime.now().isoformat(),
        "active_visitors": active,
        "total_visitors": total_visitors,
        "total_pageviews": pages_viewed,
        "avg_time_on_site_seconds": round(avg_time, 2),
        "bounce_rate_percentage": round(bounce_rate, 2),
        "total_conversions": conversions,
        "conversion_rate_percentage": round(conversion_rate, 2),
        "revenue_per_visitor": round(conversions * 99.99 / max(total_visitors, 1), 2),
        "top_traffic_source": top_source,
        "traffic_sources": dict(sources),
        "device_distribution": dict(devices),
        "events_last_window": total_events,
        "avg_events_per_visitor": round(total_events / max(total_visitors, 1), 2)
    }


def generate_analytics_summary(visitors: Dict, events_queue) -> Dict:
    """Generate comprehensive analytics summary"""
    
    # Get KPIs
    kpis = calculate_real_time_kpis(visitors, events_queue)
    
    # Get funnel
    analyzer = ConversionFunnelAnalyzer()
    funnel = analyzer.build_funnel(visitors)
    
    # Get segments
    journey_analyzer = UserJourneyAnalyzer()
    segments = journey_analyzer.get_user_segments(visitors)
    
    # Get heatmap
    heatmap = journey_analyzer.build_journey_heatmap(visitors)
    
    return {
        "summary_timestamp": datetime.now().isoformat(),
        "kpis": kpis,
        "funnel": funnel,
        "user_segments": segments,
        "journey_heatmap": heatmap,
        "critical_alerts": generate_critical_alerts(kpis, funnel, segments)
    }


def generate_critical_alerts(kpis: Dict, funnel: Dict, segments: Dict) -> List[Dict]:
    """Generate critical alerts based on analytics"""
    
    alerts = []
    
    # High bounce rate
    if kpis["bounce_rate_percentage"] > 50:
        alerts.append({
            "priority": "HIGH",
            "category": "Engagement",
            "message": f"High bounce rate: {kpis['bounce_rate_percentage']:.1f}%",
            "action": "Review landing page optimization"
        })
    
    # Low conversion
    if kpis["conversion_rate_percentage"] < 1:
        alerts.append({
            "priority": "MEDIUM",
            "category": "Conversion",
            "message": f"Low conversion rate: {kpis['conversion_rate_percentage']:.1f}%",
            "action": "A/B test checkout process"
        })
    
    # Critical funnel dropoff
    if funnel["critical_dropoff"] > 50:
        alerts.append({
            "priority": "HIGH",
            "category": "Funnel",
            "message": f"Critical funnel dropoff detected: {funnel['critical_dropoff']:.1f}%",
            "action": "Investigate step with highest dropoff"
        })
    
    # Low active visitors
    if kpis["active_visitors"] < 5:
        alerts.append({
            "priority": "LOW",
            "category": "Traffic",
            "message": f"Low active visitors: {kpis['active_visitors']}",
            "action": "Consider increasing marketing spend"
        })
    
    return alerts


# ============================================================================
# DEMO DATA GENERATOR
# ============================================================================

def generate_demo_analytics_data(visitor_count: int = 50) -> Tuple[Dict, List]:
    """Generate demo analytics data for testing"""
    
    tracker = VisitorTracker()
    pages = ["landing", "product_view", "pricing", "checkout_start", "payment", "confirmation"]
    sources = ["google", "facebook", "direct", "email", "referral"]
    devices = ["desktop", "mobile", "tablet"]
    
    for i in range(visitor_count):
        session_id = f"session_{i:04d}"
        source = random.choice(sources)
        device = random.choice(devices)
        
        # Simulate user journey
        journey_length = random.randint(1, 6)
        selected_pages = pages[:journey_length]
        
        for page in selected_pages:
            tracker.track_visitor(session_id, page, source=source, device=device)
        
        # Add some conversion events
        if random.random() > 0.85:  # 15% conversion rate
            tracker.track_event(session_id, "payment", {"amount": 99.99})
    
    return tracker.visitors, list(tracker.events_queue)
