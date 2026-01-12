"""
OpenAPI 3.0 Specification Generator for SURESH AI ORIGIN
Automatically documents all 60+ API endpoints across 15 AI features
"""

OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "SURESH AI ORIGIN API",
        "version": "1.0.0",
        "description": "Comprehensive AI-powered business intelligence platform with 19 integrated features including predictive analytics, automation workflows, real-time analytics, futuristic website generation, A/B testing, and customer journey orchestration.",
        "contact": {
            "name": "SURESH AI ORIGIN",
            "url": "https://suresh-ai-origin.com"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5000",
            "description": "Development server"
        }
    ],
    "tags": [
        {"name": "AI Generator", "description": "AI content generation endpoints"},
        {"name": "Recommendations", "description": "Smart product recommendations"},
        {"name": "Predictive Analytics", "description": "Revenue, churn, and growth forecasting"},
        {"name": "Chatbot", "description": "AI chatbot interactions"},
        {"name": "Email Timing", "description": "Smart email send time optimization"},
        {"name": "Growth Forecast", "description": "Scenario-based growth projections"},
        {"name": "CLV", "description": "Customer lifetime value analysis"},
        {"name": "Dynamic Pricing", "description": "AI-driven pricing optimization"},
        {"name": "Churn Prediction", "description": "Customer churn risk assessment"},
        {"name": "Segments", "description": "Customer segmentation and optimization"},
        {"name": "Campaigns", "description": "AI-powered campaign generation"},
        {"name": "Market Intelligence", "description": "Market trends and signals"},
        {"name": "Payment Intelligence", "description": "Payment health monitoring"},
        {"name": "Social Auto-Share", "description": "Automated social media scheduling"},
        {"name": "Voice Analytics", "description": "Voice transcript sentiment analysis"},
        {"name": "Automation", "description": "Intelligent workflow automation"},
        {"name": "Website Generator", "description": "AI-powered 1% tier website generation"},
        {"name": "Real-time Analytics", "description": "Visitor tracking, conversion funnels, and live KPIs"},
        {"name": "A/B Testing", "description": "Multi-variant experiments with statistical significance testing"},
        {"name": "Journey Orchestration", "description": "Multi-touch customer journey automation with personalization"}
    ],
    "paths": {
        "/api/ai/generate": {
            "post": {
                "tags": ["AI Generator"],
                "summary": "Generate AI content",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "prompt": {"type": "string"},
                                    "type": {"type": "string", "enum": ["email", "product_desc", "social_post"]}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Content generated successfully"}
                }
            }
        },
        "/api/recommendations/generate": {
            "get": {
                "tags": ["Recommendations"],
                "summary": "Get product recommendations",
                "parameters": [
                    {"name": "days", "in": "query", "schema": {"type": "integer", "default": 90}}
                ],
                "responses": {
                    "200": {"description": "Recommendations generated"}
                }
            }
        },
        "/api/predictions/revenue": {
            "get": {
                "tags": ["Predictive Analytics"],
                "summary": "Forecast revenue",
                "parameters": [
                    {"name": "days", "in": "query", "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {"description": "Revenue forecast"}
                }
            }
        },
        "/api/chat": {
            "post": {
                "tags": ["Chatbot"],
                "summary": "Chat with AI bot",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Bot response"}
                }
            }
        },
        "/api/clv/compute": {
            "post": {
                "tags": ["CLV"],
                "summary": "Compute customer lifetime value",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "receipt": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "CLV computed"}
                }
            }
        },
        "/api/pricing/dynamic": {
            "get": {
                "tags": ["Dynamic Pricing"],
                "summary": "Get all dynamic prices",
                "parameters": [
                    {"name": "days", "in": "query", "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {"description": "Dynamic prices"}
                }
            }
        },
        "/api/churn/risk": {
            "post": {
                "tags": ["Churn Prediction"],
                "summary": "Compute churn risk for customer",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "receipt": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Churn risk score"}
                }
            }
        },
        "/api/segments/analyze": {
            "get": {
                "tags": ["Segments"],
                "summary": "Analyze customer segments",
                "parameters": [
                    {"name": "days", "in": "query", "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {"description": "Segment analysis"}
                }
            }
        },
        "/api/campaigns/generate": {
            "post": {
                "tags": ["Campaigns"],
                "summary": "Generate AI campaign",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "audience_segments": {"type": "array", "items": {"type": "string"}},
                                    "objective": {"type": "string", "enum": ["engagement", "revenue", "retention"]}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Campaign generated"}
                }
            }
        },
        "/api/market/insights": {
            "get": {
                "tags": ["Market Intelligence"],
                "summary": "Get market insights",
                "parameters": [
                    {"name": "days", "in": "query", "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {"description": "Market insights"}
                }
            }
        },
        "/api/payments/metrics": {
            "get": {
                "tags": ["Payment Intelligence"],
                "summary": "Get payment health metrics",
                "parameters": [
                    {"name": "days", "in": "query", "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {"description": "Payment metrics"}
                }
            }
        },
        "/api/social/schedule": {
            "get": {
                "tags": ["Social Auto-Share"],
                "summary": "Get social post schedule",
                "parameters": [
                    {"name": "days", "in": "query", "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {"description": "Post schedule"}
                }
            }
        },
        "/api/voice/analyze": {
            "post": {
                "tags": ["Voice Analytics"],
                "summary": "Analyze voice transcript",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "transcript": {"type": "string"},
                                    "receipt": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Voice analysis"}
                }
            }
        },
        "/api/automations/trigger": {
            "post": {
                "tags": ["Automation"],
                "summary": "Trigger automation workflow",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "workflow": {"type": "string", "enum": ["churn_retention", "payment_retry", "segment_campaign", "voice_support", "social_content", "all"]},
                                    "days": {"type": "integer"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Workflow executed"}
                }
            }
        },
        "/api/websites/generate": {
            "post": {
                "tags": ["Website Generator"],
                "summary": "Generate AI-powered 1% tier website",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "product_name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "audience": {"type": "string", "enum": ["B2B SaaS", "Enterprise", "SMB", "Startup", "Consumer"]},
                                    "industry": {"type": "string"},
                                    "count": {"type": "integer", "minimum": 1, "maximum": 10}
                                },
                                "required": ["product_name", "description"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Website(s) generated with tier classification, performance metrics, and AI copy"}
                }
            }
        },
        "/api/websites/tier/{tier}": {
            "get": {
                "tags": ["Website Generator"],
                "summary": "Get tier information and features",
                "parameters": [
                    {"name": "tier", "in": "path", "required": True, "schema": {"type": "string", "enum": ["BREAKTHROUGH", "ELITE", "PREMIUM", "GROWTH"]}}
                ],
                "responses": {
                    "200": {"description": "Tier details with color, conversion lift, and features"}
                }
            }
        },
        "/api/websites/optimize": {
            "post": {
                "tags": ["Website Generator"],
                "summary": "Optimize website performance",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "website": {"type": "object", "description": "Website configuration"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Optimized website with suggested improvements and estimated score gains"}
                }
            }
        },
        "/api/websites/analyze": {
            "post": {
                "tags": ["Website Generator"],
                "summary": "Analyze website portfolio metrics",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "websites": {"type": "array", "items": {"type": "object"}}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Conversion impact analysis, tier distribution, and recommendations"}
                }
            }
        },
        "/api/analytics/visitors": {
            "get": {
                "tags": ["Real-time Analytics"],
                "summary": "Get active visitors and summary",
                "responses": {
                    "200": {
                        "description": "Active visitors and visitor summary statistics",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "active_visitors": {"type": "integer"},
                                        "visitor_summary": {
                                            "type": "object",
                                            "properties": {
                                                "total_visitors": {"type": "integer"},
                                                "total_pageviews": {"type": "integer"},
                                                "traffic_sources": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/analytics/track": {
            "post": {
                "tags": ["Real-time Analytics"],
                "summary": "Track visitor page view or event",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "session_id": {"type": "string"},
                                    "page": {"type": "string"},
                                    "source": {"type": "string"},
                                    "device": {"type": "string", "enum": ["desktop", "mobile", "tablet"]},
                                    "event_type": {"type": "string"},
                                    "event_data": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Visitor tracking recorded successfully"}
                }
            }
        },
        "/api/analytics/funnel": {
            "get": {
                "tags": ["Real-time Analytics"],
                "summary": "Get conversion funnel analysis",
                "responses": {
                    "200": {
                        "description": "Conversion funnel with dropoff rates and segment analysis",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "funnel_name": {"type": "string"},
                                        "steps": {"type": "array"},
                                        "overall_conversion_rate": {"type": "number"},
                                        "dropoff_rates": {"type": "object"},
                                        "segment_analysis": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/analytics/heatmap": {
            "get": {
                "tags": ["Real-time Analytics"],
                "summary": "Get user journey heatmap",
                "responses": {
                    "200": {
                        "description": "User journey transitions and segment distribution",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "heatmap": {"type": "object"},
                                        "total_transitions": {"type": "integer"},
                                        "user_segments": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/analytics/kpis": {
            "get": {
                "tags": ["Real-time Analytics"],
                "summary": "Get real-time KPIs",
                "responses": {
                    "200": {
                        "description": "Real-time key performance indicators",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "active_visitors": {"type": "integer"},
                                        "total_visitors": {"type": "integer"},
                                        "conversion_rate_percentage": {"type": "number"},
                                        "bounce_rate_percentage": {"type": "number"},
                                        "avg_time_on_site_seconds": {"type": "number"},
                                        "revenue_per_visitor": {"type": "number"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/experiments/create": {
            "post": {
                "tags": ["A/B Testing"],
                "summary": "Create new A/B test experiment",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "hypothesis": {"type": "string"},
                                    "primary_metric": {"type": "string", "enum": ["conversion_rate", "revenue_per_visitor", "click_through_rate", "engagement"]},
                                    "confidence_level": {"type": "number", "minimum": 0.90, "maximum": 0.99}
                                },
                                "required": ["name", "hypothesis", "primary_metric"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Experiment created successfully"}
                }
            }
        },
        "/api/experiments/{experiment_id}/start": {
            "post": {
                "tags": ["A/B Testing"],
                "summary": "Start an experiment",
                "parameters": [
                    {"name": "experiment_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {"description": "Experiment started"}
                }
            }
        },
        "/api/experiments/{experiment_id}/variant/add": {
            "post": {
                "tags": ["A/B Testing"],
                "summary": "Add variant to experiment",
                "parameters": [
                    {"name": "experiment_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "variant_id": {"type": "string"},
                                    "variant_name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "traffic_allocation": {"type": "number", "minimum": 0, "maximum": 1}
                                },
                                "required": ["variant_id", "variant_name", "traffic_allocation"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Variant added successfully"}
                }
            }
        },
        "/api/experiments/{experiment_id}/track": {
            "post": {
                "tags": ["A/B Testing"],
                "summary": "Track conversion in experiment",
                "parameters": [
                    {"name": "experiment_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "variant_id": {"type": "string"},
                                    "converted": {"type": "boolean"},
                                    "revenue": {"type": "number"}
                                },
                                "required": ["variant_id", "converted"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Conversion tracked"}
                }
            }
        },
        "/api/experiments/{experiment_id}/results": {
            "get": {
                "tags": ["A/B Testing"],
                "summary": "Get experiment results and statistics",
                "parameters": [
                    {"name": "experiment_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {
                        "description": "Experiment results with statistical significance",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "experiment_id": {"type": "string"},
                                        "status": {"type": "string"},
                                        "total_visitors": {"type": "integer"},
                                        "variants_performance": {"type": "array"},
                                        "winner_analysis": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/experiments/{experiment_id}/end": {
            "post": {
                "tags": ["A/B Testing"],
                "summary": "End experiment and determine winner",
                "parameters": [
                    {"name": "experiment_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {"description": "Experiment ended with winner determination"}
                }
            }
        },
        "/api/journeys/create": {
            "post": {
                "tags": ["Journey Orchestration"],
                "summary": "Create a new customer journey",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "example": "Welcome Series"},
                                    "description": {"type": "string", "example": "Onboarding for new users"},
                                    "trigger": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string", "example": "signup"},
                                            "segment": {"type": "string", "example": "new_users"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {"description": "Journey created successfully"}
                }
            }
        },
        "/api/journeys/{journey_id}/step/add": {
            "post": {
                "tags": ["Journey Orchestration"],
                "summary": "Add a step to a journey",
                "parameters": [
                    {"name": "journey_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "step_type": {"type": "string", "enum": ["email", "sms", "wait", "decision", "push"]},
                                    "config": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {"description": "Step added successfully"}
                }
            }
        },
        "/api/journeys/{journey_id}/publish": {
            "post": {
                "tags": ["Journey Orchestration"],
                "summary": "Publish a journey for enrollment",
                "parameters": [
                    {"name": "journey_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {"description": "Journey published successfully"}
                }
            }
        },
        "/api/journeys/{journey_id}/enroll": {
            "post": {
                "tags": ["Journey Orchestration"],
                "summary": "Enroll a customer in a journey",
                "parameters": [
                    {"name": "journey_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "customer_id": {"type": "string"},
                                    "customer_data": {
                                        "type": "object",
                                        "properties": {
                                            "email": {"type": "string"},
                                            "phone": {"type": "string"},
                                            "segment": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {"description": "Customer enrolled successfully"}
                }
            }
        },
        "/api/journeys/{journey_id}/track-conversion": {
            "post": {
                "tags": ["Journey Orchestration"],
                "summary": "Track conversion for a customer",
                "parameters": [
                    {"name": "journey_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "customer_id": {"type": "string"},
                                    "value": {"type": "number", "example": 99.99}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Conversion tracked successfully"}
                }
            }
        },
        "/api/journeys/{journey_id}/analytics": {
            "get": {
                "tags": ["Journey Orchestration"],
                "summary": "Get journey analytics and metrics",
                "parameters": [
                    {"name": "journey_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {
                        "description": "Journey analytics retrieved",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "journey_id": {"type": "string"},
                                        "completion_rate": {"type": "number"},
                                        "conversion_rate": {"type": "number"},
                                        "active_customers": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "securitySchemes": {
            "AdminAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "Admin session authentication required for all endpoints"
            }
        }
    },
    "security": [{"AdminAuth": []}]
}


def get_postman_collection():
    """Generate Postman collection v2.1"""
    return {
        "info": {
            "name": "SURESH AI ORIGIN API",
            "description": "Complete API collection for all 19 AI features",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            {
                "name": "AI Generator",
                "item": [
                    {
                        "name": "Generate Content",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/ai/generate",
                            "body": {
                                "mode": "raw",
                                "raw": '{"prompt": "Write a product description", "type": "product_desc"}'
                            }
                        }
                    }
                ]
            },
            {
                "name": "Recommendations",
                "item": [
                    {
                        "name": "Get Recommendations",
                        "request": {
                            "method": "GET",
                            "url": "{{base_url}}/api/recommendations/generate?days=90"
                        }
                    }
                ]
            },
            {
                "name": "Automation",
                "item": [
                    {
                        "name": "Trigger Churn Retention",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/automations/trigger",
                            "body": {
                                "mode": "raw",
                                "raw": '{"workflow": "churn_retention", "days": 30}'
                            }
                        }
                    },
                    {
                        "name": "Run All Workflows",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/automations/trigger",
                            "body": {
                                "mode": "raw",
                                "raw": '{"workflow": "all", "days": 30}'
                            }
                        }
                    }
                ]
            },
            {
                "name": "Website Generator",
                "item": [
                    {
                        "name": "Generate Website",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/websites/generate",
                            "body": {
                                "mode": "raw",
                                "raw": '{"product_name": "SuperAI", "description": "AI analytics platform", "audience": "B2B SaaS", "count": 3}'
                            }
                        }
                    },
                    {
                        "name": "Get Tier Info",
                        "request": {
                            "method": "GET",
                            "url": "{{base_url}}/api/websites/tier/BREAKTHROUGH"
                        }
                    },
                    {
                        "name": "Optimize Performance",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/websites/optimize",
                            "body": {
                                "mode": "raw",
                                "raw": '{"website": {}}'
                            }
                        }
                    },
                    {
                        "name": "Analyze Websites",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/websites/analyze",
                            "body": {
                                "mode": "raw",
                                "raw": '{"websites": []}'
                            }
                        }
                    }
                ]
            },
            {
                "name": "Real-time Analytics",
                "item": [
                    {
                        "name": "Get Active Visitors",
                        "request": {
                            "method": "GET",
                            "url": "{{base_url}}/api/analytics/visitors"
                        }
                    },
                    {
                        "name": "Track Visitor",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/analytics/track",
                            "body": {
                                "mode": "raw",
                                "raw": '{"session_id": "session_001", "page": "/home", "source": "google", "device": "desktop"}'
                            }
                        }
                    },
                    {
                        "name": "Get Conversion Funnel",
                        "request": {
                            "method": "GET",
                            "url": "{{base_url}}/api/analytics/funnel"
                        }
                    },
                    {
                        "name": "Get Journey Heatmap",
                        "request": {
                            "method": "GET",
                            "url": "{{base_url}}/api/analytics/heatmap"
                        }
                    },
                    {
                        "name": "Get Real-time KPIs",
                        "request": {
                            "method": "GET",
                            "url": "{{base_url}}/api/analytics/kpis"
                        }
                    }
                ]
            },
            {
                "name": "A/B Testing",
                "item": [
                    {
                        "name": "Create Experiment",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/experiments/create",
                            "body": {
                                "mode": "raw",
                                "raw": '{"name": "CTA Button Test", "hypothesis": "Red button improves conversion", "primary_metric": "conversion_rate", "confidence_level": 0.95}'
                            }
                        }
                    },
                    {
                        "name": "Start Experiment",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/experiments/exp_1/start"
                        }
                    },
                    {
                        "name": "Add Variant",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/experiments/exp_1/variant/add",
                            "body": {
                                "mode": "raw",
                                "raw": '{"variant_id": "control", "variant_name": "Blue Button", "traffic_allocation": 0.5}'
                            }
                        }
                    },
                    {
                        "name": "Track Conversion",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/experiments/exp_1/track",
                            "body": {
                                "mode": "raw",
                                "raw": '{"variant_id": "control", "converted": true, "revenue": 99.99}'
                            }
                        }
                    },
                    {
                        "name": "Get Experiment Results",
                        "request": {
                            "method": "GET",
                            "url": "{{base_url}}/api/experiments/exp_1/results"
                        }
                    },
                    {
                        "name": "End Experiment",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/experiments/exp_1/end"
                        }
                    }
                ]
            },
            {
                "name": "Journey Orchestration",
                "item": [
                    {
                        "name": "Create Journey",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/journeys/create",
                            "body": {
                                "mode": "raw",
                                "raw": '{"name": "Welcome Series", "description": "Onboarding for new users", "trigger": {"type": "signup", "segment": "new_users"}}'
                            }
                        }
                    },
                    {
                        "name": "Add Step",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/journeys/journey_1/step/add",
                            "body": {
                                "mode": "raw",
                                "raw": '{"step_type": "email", "config": {"subject": "Welcome!", "content": "Hello and welcome"}}'
                            }
                        }
                    },
                    {
                        "name": "Publish Journey",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/journeys/journey_1/publish"
                        }
                    },
                    {
                        "name": "Enroll Customer",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/journeys/journey_1/enroll",
                            "body": {
                                "mode": "raw",
                                "raw": '{"customer_id": "cust_123", "customer_data": {"email": "customer@example.com", "segment": "new_users"}}'
                            }
                        }
                    },
                    {
                        "name": "Track Conversion",
                        "request": {
                            "method": "POST",
                            "url": "{{base_url}}/api/journeys/journey_1/track-conversion",
                            "body": {
                                "mode": "raw",
                                "raw": '{"customer_id": "cust_123", "value": 149.99}'
                            }
                        }
                    },
                    {
                        "name": "Get Analytics",
                        "request": {
                            "method": "GET",
                            "url": "{{base_url}}/api/journeys/journey_1/analytics"
                        }
                    }
                ]
            }
        ],
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:5000"
            }
        ]
    }
