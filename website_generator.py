"""
AI Website Generator - Feature #16
Generates futuristic, 1% tier landing pages with AI copy and performance optimization
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import random

# ============================================================================
# WEBSITE TIER CLASSIFICATION
# ============================================================================

WEBSITE_TIERS = {
    "BREAKTHROUGH": {
        "score_range": (90, 100),
        "color": "#FF006E",  # Neon Pink
        "description": "Top 1% - Exceptional Performance",
        "conversion_lift": 45,  # 45% conversion lift vs average
        "features": ["AI Copy", "Mobile Optimized", "Micro-interactions", "3D Elements", "Progressive Web App"]
    },
    "ELITE": {
        "score_range": (75, 89),
        "color": "#8338EC",  # Neon Purple
        "description": "Top 5% - Excellent Performance",
        "conversion_lift": 35,  # 35% conversion lift
        "features": ["AI Copy", "Mobile Optimized", "Animations", "Fast Load Time"]
    },
    "PREMIUM": {
        "score_range": (60, 74),
        "color": "#3A86FF",  # Bright Blue
        "description": "Top 25% - Strong Performance",
        "conversion_lift": 20,
        "features": ["Professional Copy", "Mobile Responsive", "Clean Design"]
    },
    "GROWTH": {
        "score_range": (40, 59),
        "color": "#06D6A0",  # Teal
        "description": "Top 50% - Good Performance",
        "conversion_lift": 10,
        "features": ["Basic Copy", "Mobile Friendly", "Standard Design"]
    }
}

# ============================================================================
# FUTURISTIC TEMPLATES
# ============================================================================

FUTURISTIC_TEMPLATES = {
    "neo_glassmorphism": {
        "name": "Neo Glassmorphism",
        "tier": "BREAKTHROUGH",
        "hero": {
            "bg": "linear-gradient(135deg, #000 0%, #1a0033 50%, #000 100%)",
            "text_color": "#00FF9F",
            "accent": "#FF006E",
            "layout": "split_hero_with_animation"
        },
        "sections": [
            "animated_hero",
            "feature_cards_3d",
            "testimonials_carousel",
            "pricing_table_animated",
            "cta_section"
        ],
        "animations": ["parallax", "scroll_reveal", "hover_3d"],
        "performance_score": 95
    },
    
    "quantum_grid": {
        "name": "Quantum Grid",
        "tier": "ELITE",
        "hero": {
            "bg": "linear-gradient(90deg, #0a0a0a 0%, #1a0a3f 50%, #0a0a0a 100%)",
            "text_color": "#00D9FF",
            "accent": "#8338EC",
            "layout": "centered_with_grid_bg"
        },
        "sections": [
            "hero_section",
            "benefits_grid",
            "case_studies",
            "faq_accordion",
            "newsletter_signup"
        ],
        "animations": ["fade_in", "slide_up", "scale"],
        "performance_score": 88
    },
    
    "cyberpunk_minimal": {
        "name": "Cyberpunk Minimal",
        "tier": "ELITE",
        "hero": {
            "bg": "linear-gradient(45deg, #000 0%, #0f0f0f 50%, #000 100%)",
            "text_color": "#FFD700",
            "accent": "#FF006E",
            "layout": "left_aligned_bold"
        },
        "sections": [
            "minimal_hero",
            "feature_list",
            "metrics_display",
            "integration_showcase",
            "cta_footer"
        ],
        "animations": ["typewriter", "counter", "fade"],
        "performance_score": 82
    },
    
    "aurora_flow": {
        "name": "Aurora Flow",
        "tier": "PREMIUM",
        "hero": {
            "bg": "linear-gradient(120deg, #001a4d 0%, #1a0033 50%, #001a4d 100%)",
            "text_color": "#00E5FF",
            "accent": "#00D6FF",
            "layout": "centered_with_animation"
        },
        "sections": [
            "hero_with_video",
            "features_list",
            "social_proof",
            "pricing",
            "contact_form"
        ],
        "animations": ["fade_in", "bounce", "pulse"],
        "performance_score": 75
    },
    
    "tech_standard": {
        "name": "Tech Standard",
        "tier": "GROWTH",
        "hero": {
            "bg": "linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)",
            "text_color": "#000",
            "accent": "#0066ff",
            "layout": "simple_centered"
        },
        "sections": [
            "simple_hero",
            "features",
            "testimonials",
            "pricing",
            "footer"
        ],
        "animations": [],
        "performance_score": 65
    }
}

# ============================================================================
# AI COPY TEMPLATES
# ============================================================================

AI_COPY_LIBRARY = {
    "hero_headlines": {
        "BREAKTHROUGH": [
            "The Future Is Now - Meet {product}",
            "Experience {product} - Top 1% Performance",
            "{product}: Where Innovation Meets Excellence",
            "Breakthrough Results Start Here",
            "Join the 1% - {product} Elite Platform"
        ],
        "ELITE": [
            "Level Up Your Business with {product}",
            "{product} - Exceptional Results Guaranteed",
            "Premium Solutions, Elite Performance",
            "Your Success Story Starts Today"
        ]
    },
    "subheaders": {
        "BREAKTHROUGH": [
            "AI-powered. Lightning-fast. Game-changing.",
            "Performance optimization that breaks limits.",
            "Join 10,000+ companies crushing their goals."
        ],
        "ELITE": [
            "Smart solutions for ambitious teams.",
            "Get results 10x faster than competitors.",
            "Enterprise-grade power, user-friendly design."
        ]
    },
    "cta_buttons": {
        "BREAKTHROUGH": ["Start Your Breakthrough", "Join the Elite", "Access Now - Limited Spots"],
        "ELITE": ["Get Started Free", "See Live Demo", "Try Premium"]
    }
}

# ============================================================================
# PERFORMANCE METRICS CALCULATION
# ============================================================================

def calculate_performance_score(
    page_speed: int = 80,
    mobile_score: int = 85,
    seo_score: int = 90,
    accessibility: int = 88,
    conversion_factors: Dict = None
) -> Tuple[int, str]:
    """
    Calculate overall website performance score (0-100)
    
    Args:
        page_speed: 0-100 (Lighthouse)
        mobile_score: 0-100 (Mobile optimization)
        seo_score: 0-100 (SEO readiness)
        accessibility: 0-100 (WCAG compliance)
        conversion_factors: Additional metrics
    
    Returns:
        (score: int, tier: str)
    """
    
    if conversion_factors is None:
        conversion_factors = {
            "form_optimization": 8,
            "design_quality": 10,
            "copy_quality": 7,
            "trust_signals": 5
        }
    
    # Weighted scoring
    weights = {
        "page_speed": 0.25,
        "mobile": 0.25,
        "seo": 0.20,
        "accessibility": 0.15,
        "conversion": 0.15
    }
    
    conversion_score = sum(conversion_factors.values())
    conversion_score = min(conversion_score, 100)
    
    final_score = int(
        (page_speed * weights["page_speed"]) +
        (mobile_score * weights["mobile"]) +
        (seo_score * weights["seo"]) +
        (accessibility * weights["accessibility"]) +
        (conversion_score * weights["conversion"])
    )
    
    # Determine tier
    tier = "GROWTH"
    for tier_name, tier_data in WEBSITE_TIERS.items():
        if tier_data["score_range"][0] <= final_score <= tier_data["score_range"][1]:
            tier = tier_name
            break
    
    return final_score, tier


def generate_performance_metrics(template_tier: str) -> Dict:
    """Generate realistic performance metrics for a website tier"""
    
    tier_baselines = {
        "BREAKTHROUGH": {"base_speed": 95, "var": 3},
        "ELITE": {"base_speed": 85, "var": 5},
        "PREMIUM": {"base_speed": 75, "var": 8},
        "GROWTH": {"base_speed": 60, "var": 15}
    }
    
    baseline = tier_baselines.get(template_tier, tier_baselines["GROWTH"])
    base = baseline["base_speed"]
    variance = baseline["var"]
    
    # Generate metrics with bounds (0-100)
    page_speed = min(100, max(0, base + random.randint(-variance, variance)))
    mobile_score = min(100, max(0, base + 5 + random.randint(-variance, variance)))
    seo_score = min(100, max(0, base + 2 + random.randint(-variance, variance)))
    accessibility = min(100, max(0, base + random.randint(-variance, variance)))
    
    return {
        "page_speed": page_speed,
        "mobile_score": mobile_score,
        "seo_score": seo_score,
        "accessibility": accessibility,
        "conversion_factors": {
            "form_optimization": random.randint(6, 10),
            "design_quality": random.randint(8, 10),
            "copy_quality": random.randint(7, 10),
            "trust_signals": random.randint(3, 5)
        }
    }

# ============================================================================
# WEBSITE GENERATION
# ============================================================================

def generate_website(
    product_name: str,
    product_description: str,
    target_audience: str = "B2B SaaS",
    industry: str = "Technology",
    template: Optional[str] = None,
    tier: Optional[str] = None
) -> Dict:
    """
    Generate a complete futuristic website
    
    Args:
        product_name: Name of product
        product_description: Product description
        target_audience: Who is this for
        industry: Industry vertical
        template: Optional template name
        tier: Optional tier override
    
    Returns:
        Complete website configuration
    """
    
    # Select template
    if template and template in FUTURISTIC_TEMPLATES:
        selected_template = FUTURISTIC_TEMPLATES[template]
    else:
        selected_template = random.choice(list(FUTURISTIC_TEMPLATES.values()))
        template = list(FUTURISTIC_TEMPLATES.keys())[
            list(FUTURISTIC_TEMPLATES.values()).index(selected_template)
        ]
    
    # Determine tier
    website_tier = tier or selected_template["tier"]
    tier_config = WEBSITE_TIERS[website_tier]
    
    # Generate AI copy
    headline = random.choice(
        AI_COPY_LIBRARY["hero_headlines"].get(website_tier, 
        AI_COPY_LIBRARY["hero_headlines"]["ELITE"])
    ).format(product=product_name)
    
    subheader = random.choice(
        AI_COPY_LIBRARY["subheaders"].get(website_tier, 
        AI_COPY_LIBRARY["subheaders"]["ELITE"])
    )
    
    cta_text = random.choice(
        AI_COPY_LIBRARY["cta_buttons"].get(website_tier, 
        AI_COPY_LIBRARY["cta_buttons"]["ELITE"])
    )
    
    # Generate performance metrics
    perf_metrics = generate_performance_metrics(website_tier)
    performance_score, assigned_tier = calculate_performance_score(**perf_metrics)
    
    # Create website configuration
    website_config = {
        "id": hashlib.md5(f"{product_name}{datetime.now()}".encode()).hexdigest()[:16],
        "product_name": product_name,
        "product_description": product_description,
        "target_audience": target_audience,
        "industry": industry,
        "template": template,
        "template_config": selected_template,
        "tier": website_tier,
        "tier_color": tier_config["color"],
        "tier_description": tier_config["description"],
        "conversion_lift": tier_config["conversion_lift"],
        "features": tier_config["features"],
        "copy": {
            "headline": headline,
            "subheader": subheader,
            "cta_button": cta_text,
            "description": product_description
        },
        "performance": {
            "score": performance_score,
            "metrics": perf_metrics,
            "page_speed": perf_metrics["page_speed"],
            "mobile_score": perf_metrics["mobile_score"],
            "seo_score": perf_metrics["seo_score"],
            "accessibility": perf_metrics["accessibility"]
        },
        "design": {
            "hero_bg": selected_template["hero"]["bg"],
            "text_color": selected_template["hero"]["text_color"],
            "accent_color": selected_template["hero"]["accent"],
            "animations": selected_template["animations"]
        },
        "estimated_conversion_rate": 0.08 + (tier_config["conversion_lift"] / 1000),
        "created_at": datetime.now().isoformat(),
        "estimated_revenue_impact": f"${random.randint(50, 500)}k/month"
    }
    
    return website_config


def batch_generate_websites(
    product_name: str,
    product_description: str,
    count: int = 5,
    target_audience: str = "B2B SaaS"
) -> List[Dict]:
    """Generate multiple website variations"""
    
    websites = []
    for _ in range(count):
        website = generate_website(
            product_name=product_name,
            product_description=product_description,
            target_audience=target_audience
        )
        websites.append(website)
    
    # Sort by performance score
    return sorted(websites, key=lambda x: x["performance"]["score"], reverse=True)


def optimize_website_performance(website_config: Dict) -> Dict:
    """
    Optimize website for better performance
    Simulates performance improvements through optimization strategies
    """
    
    optimizations = {
        "enable_lazy_loading": 5,
        "compress_images": 8,
        "minify_css_js": 4,
        "enable_caching": 10,
        "cdn_implementation": 6,
        "reduce_third_party": 3,
        "optimize_fonts": 2
    }
    
    current_score = website_config["performance"]["score"]
    
    # Calculate improvement potential
    max_possible = 100
    improvement_potential = max_possible - current_score
    
    optimizations_applied = []
    score_increase = 0
    
    for optimization, potential_gain in optimizations.items():
        if improvement_potential > 0 and random.random() > 0.3:
            gain = min(potential_gain, improvement_potential)
            optimizations_applied.append({
                "optimization": optimization,
                "estimated_gain": gain,
                "implementation_effort": f"{random.randint(1, 4)} days"
            })
            score_increase += gain
            improvement_potential -= gain
    
    optimized_config = website_config.copy()
    optimized_config["performance"]["score"] = min(100, current_score + score_increase)
    optimized_config["performance"]["optimizations"] = optimizations_applied
    optimized_config["performance"]["estimated_score_improvement"] = score_increase
    
    return optimized_config


def analyze_website_tier_distribution(websites: List[Dict]) -> Dict:
    """Analyze distribution of websites across tiers"""
    
    tier_counts = {tier: 0 for tier in WEBSITE_TIERS.keys()}
    tier_scores = {tier: [] for tier in WEBSITE_TIERS.keys()}
    
    for website in websites:
        tier = website["tier"]
        tier_counts[tier] += 1
        tier_scores[tier].append(website["performance"]["score"])
    
    analysis = {
        "total_websites": len(websites),
        "tier_distribution": tier_counts,
        "tier_percentages": {
            tier: (count / len(websites) * 100) if len(websites) > 0 else 0
            for tier, count in tier_counts.items()
        },
        "avg_scores_by_tier": {
            tier: sum(scores) / len(scores) if scores else 0
            for tier, scores in tier_scores.items()
        },
        "top_1_percent": tier_counts.get("BREAKTHROUGH", 0),
        "top_5_percent": tier_counts.get("BREAKTHROUGH", 0) + tier_counts.get("ELITE", 0),
        "recommendations": generate_optimization_recommendations(tier_counts)
    }
    
    return analysis


def generate_optimization_recommendations(tier_distribution: Dict) -> List[str]:
    """Generate recommendations based on tier distribution"""
    
    recommendations = []
    total = sum(tier_distribution.values())
    
    if total == 0:
        return recommendations
    
    breakthrough_pct = (tier_distribution.get("BREAKTHROUGH", 0) / total) * 100
    
    if breakthrough_pct < 10:
        recommendations.append("Focus on futuristic design elements to reach BREAKTHROUGH tier")
    
    if tier_distribution.get("GROWTH", 0) > total * 0.5:
        recommendations.append("Implement advanced animations and micro-interactions to improve scores")
    
    recommendations.append("Optimize Core Web Vitals for better performance scores")
    recommendations.append("Add AI-powered copy to increase conversion rates")
    recommendations.append("Implement progressive enhancement for mobile users")
    
    return recommendations


def get_website_by_tier(websites: List[Dict], tier: str) -> List[Dict]:
    """Filter websites by tier"""
    return [w for w in websites if w["tier"] == tier]


def simulate_conversion_impact(website_config: Dict, baseline_conversion: float = 0.02) -> Dict:
    """Simulate conversion impact of website tier"""
    
    tier = website_config["tier"]
    tier_config = WEBSITE_TIERS[tier]
    
    conversion_lift_pct = tier_config["conversion_lift"] / 100
    new_conversion_rate = baseline_conversion * (1 + conversion_lift_pct)
    
    # Simulate revenue impact for 10k monthly visitors
    monthly_visitors = 10000
    avg_order_value = 99.99
    
    baseline_revenue = monthly_visitors * baseline_conversion * avg_order_value
    new_revenue = monthly_visitors * new_conversion_rate * avg_order_value
    revenue_increase = new_revenue - baseline_revenue
    
    return {
        "baseline_conversion_rate": f"{baseline_conversion * 100:.2f}%",
        "optimized_conversion_rate": f"{new_conversion_rate * 100:.2f}%",
        "lift_percentage": f"{conversion_lift_pct * 100:.1f}%",
        "baseline_monthly_revenue": f"${baseline_revenue:,.2f}",
        "optimized_monthly_revenue": f"${new_revenue:,.2f}",
        "monthly_revenue_increase": f"${revenue_increase:,.2f}",
        "annual_revenue_increase": f"${revenue_increase * 12:,.2f}",
        "payback_period": "< 30 days"
    }


# ============================================================================
# HTML GENERATION (ULTRA-PREMIUM GLOW WEBSITES)
# ============================================================================

def generate_glow_html(website_config: Dict, include_animations: bool = True) -> str:
    """
    Generate ultra-premium HTML with glowing effects, animations, and stunning visuals
    
    Args:
        website_config: Website configuration from generate_website()
        include_animations: Include advanced animations (default: True)
    
    Returns:
        Complete HTML string ready to save/deploy
    """
    
    design = website_config['design']
    copy = website_config['copy']
    product_name = website_config['product_name']
    tier = website_config['tier']
    tier_color = website_config['tier_color']
    
    # Advanced animations based on tier
    animations_css = ""
    if include_animations and tier in ['BREAKTHROUGH', 'ELITE']:
        animations_css = """
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        
        @keyframes pulse-glow {
            0%, 100% { 
                box-shadow: 0 0 20px """ + tier_color + """, 
                            0 0 40px """ + tier_color + """; 
            }
            50% { 
                box-shadow: 0 0 40px """ + tier_color + """, 
                            0 0 60px """ + tier_color + """,
                            0 0 80px """ + tier_color + """; 
            }
        }
        
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        @keyframes slide-up {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-float { animation: float 3s ease-in-out infinite; }
        .animate-on-scroll { animation: slide-up 0.8s ease-out; }
        """
    
    # Glassmorphism intensity based on tier
    glass_opacity = {
        'BREAKTHROUGH': 0.05,
        'ELITE': 0.08,
        'PREMIUM': 0.12,
        'GROWTH': 0.15
    }.get(tier, 0.1)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{copy['description'][:160]}">
    <title>{product_name} - {website_config['tier_description']}</title>
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', sans-serif;
            background: {design['hero_bg']};
            background-size: 400% 400%;
            animation: gradient-shift 15s ease infinite;
            color: {design['text_color']};
            min-height: 100vh;
            overflow-x: hidden;
        }}
        
        .hero {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 2rem;
            position: relative;
        }}
        
        /* Glow particle effect background */
        .hero::before {{
            content: '';
            position: absolute;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, {tier_color}33 0%, transparent 70%);
            border-radius: 50%;
            top: -250px;
            right: -250px;
            animation: float 6s ease-in-out infinite;
            z-index: 0;
        }}
        
        .hero::after {{
            content: '';
            position: absolute;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, {design['accent_color']}22 0%, transparent 70%);
            border-radius: 50%;
            bottom: -200px;
            left: -200px;
            animation: float 8s ease-in-out infinite reverse;
            z-index: 0;
        }}
        
        .hero-content {{
            position: relative;
            z-index: 1;
        }}
        
        .glassmorphism {{
            background: rgba(255, 255, 255, {glass_opacity});
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.125);
            border-radius: 24px;
            padding: 4rem 3rem;
            max-width: 900px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            animation: pulse-glow 3s ease-in-out infinite;
        }}
        
        h1 {{
            font-size: clamp(2.5rem, 6vw, 5rem);
            font-weight: 900;
            margin-bottom: 1.5rem;
            line-height: 1.1;
            text-shadow: 0 0 20px {tier_color}, 
                         0 0 40px {tier_color},
                         0 0 60px {tier_color}88;
            letter-spacing: -0.02em;
        }}
        
        .tier-badge {{
            display: inline-block;
            padding: 0.5rem 1.5rem;
            background: {tier_color};
            color: #000;
            font-size: 0.875rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-radius: 50px;
            margin-bottom: 2rem;
            box-shadow: 0 0 30px {tier_color};
        }}
        
        p {{
            font-size: clamp(1.1rem, 2vw, 1.5rem);
            margin-bottom: 2.5rem;
            opacity: 0.95;
            line-height: 1.6;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .cta {{
            display: inline-block;
            padding: 1.25rem 3.5rem;
            background: {design['accent_color']};
            color: #000;
            font-size: 1.25rem;
            font-weight: 700;
            text-decoration: none;
            border-radius: 50px;
            box-shadow: 0 0 40px {design['accent_color']};
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .cta::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }}
        
        .cta:hover {{
            transform: scale(1.05) translateY(-2px);
            box-shadow: 0 0 60px {design['accent_color']},
                        0 10px 40px rgba(0, 0, 0, 0.3);
        }}
        
        .cta:hover::before {{
            width: 300px;
            height: 300px;
        }}
        
        .features {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 3rem;
        }}
        
        .feature-pill {{
            padding: 0.75rem 1.5rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 50px;
            font-size: 0.95rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }}
        
        .feature-pill:hover {{
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-top: 4rem;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(135deg, {tier_color}, {design['accent_color']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}
        
        .stat-label {{
            font-size: 0.95rem;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .glassmorphism {{
                padding: 2.5rem 1.5rem;
            }}
            
            .hero {{
                padding: 1rem;
            }}
            
            h1 {{
                font-size: 2.5rem;
            }}
            
            .cta {{
                padding: 1rem 2.5rem;
                font-size: 1.1rem;
            }}
            
            .stats {{
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }}
        }}
        
        {animations_css}
    </style>
</head>
<body>
    <div class="hero">
        <div class="hero-content">
            <div class="glassmorphism animate-on-scroll">
                <div class="tier-badge">{website_config['tier_description']}</div>
                <h1>{copy['headline']}</h1>
                <p>{copy['subheader']}</p>
                <a href="#signup" class="cta">{copy['cta_button']}</a>
                
                <div class="features">
                    {''.join(f'<div class="feature-pill">✨ {feature}</div>' for feature in website_config['features'])}
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{website_config['performance']['score']}</div>
                        <div class="stat-label">Performance Score</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">+{website_config['conversion_lift']}%</div>
                        <div class="stat-label">Conversion Lift</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{website_config['performance']['page_speed']}</div>
                        <div class="stat-label">Page Speed</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Smooth scroll for CTA
        document.querySelector('.cta').addEventListener('click', (e) => {{
            e.preventDefault();
            // Add your signup logic here
            console.log('CTA clicked!');
        }});
        
        // Animate elements on scroll
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('animate-on-scroll');
                }}
            }});
        }});
        
        document.querySelectorAll('.glassmorphism').forEach(el => observer.observe(el));
    </script>
</body>
</html>"""
    
    return html


def save_website_html(website_config: Dict, filename: Optional[str] = None) -> str:
    """
    Generate and save ultra-premium glow website HTML to file
    
    Args:
        website_config: Website configuration from generate_website()
        filename: Optional filename (auto-generated if not provided)
    
    Returns:
        Path to saved HTML file
    """
    
    html = generate_glow_html(website_config)
    
    if not filename:
        safe_name = website_config['product_name'].lower().replace(' ', '_').replace('-', '_')
        filename = f"{safe_name}_glow_website.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filename


def generate_and_save_best_website(
    product_name: str,
    product_description: str,
    target_audience: str = "B2B SaaS",
    count: int = 5,
    output_dir: str = "."
) -> Dict:
    """
    Generate multiple websites, pick the best, and save as HTML
    
    Args:
        product_name: Product name
        product_description: Product description
        target_audience: Target audience
        count: Number of variations to generate
        output_dir: Directory to save HTML file
    
    Returns:
        Dict with website config and saved file path
    """
    
    import os
    
    # Generate multiple variations
    websites = batch_generate_websites(
        product_name=product_name,
        product_description=product_description,
        target_audience=target_audience,
        count=count
    )
    
    # Pick the best (already sorted by performance)
    best_website = websites[0]
    
    # Generate filename
    safe_name = product_name.lower().replace(' ', '_').replace('-', '_')
    filename = f"{safe_name}_glow_website.html"
    filepath = os.path.join(output_dir, filename)
    
    # Generate and save HTML
    html = generate_glow_html(best_website)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return {
        'website_config': best_website,
        'html_file': filepath,
        'tier': best_website['tier'],
        'performance_score': best_website['performance']['score'],
        'conversion_lift': best_website['conversion_lift'],
        'estimated_revenue_impact': best_website['estimated_revenue_impact'],
        'alternatives_generated': len(websites),
        'template': best_website['template']
    }
