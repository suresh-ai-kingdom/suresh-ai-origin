# Feature #20: Advanced Attribution Modeling API

## Overview
Multi-touch attribution system with ROI optimization, supporting 4 attribution models (first-touch, last-touch, linear, time-decay) and AI-driven budget recommendations.

## Authentication
Bearer token via `X-Admin-Token` header or session-based admin login for dashboard access.

---

## Endpoints

### 1. Track Customer Journey
**POST** `/api/attribution/track-journey`

Track a customer's multi-channel conversion path with automatic attribution across all models.

**Request Body:**
```json
{
  "customer_id": "cust_123",
  "order_id": "ORD_001",
  "conversion_value": 199.99,
  "touchpoints": [
    {
      "channel": "paid_search",
      "timestamp": "2024-01-01T10:00:00"
    },
    {
      "channel": "email",
      "timestamp": "2024-01-02T14:00:00"
    },
    {
      "channel": "direct",
      "timestamp": "2024-01-03T16:00:00"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "customer_id": "cust_123",
  "order_id": "ORD_001",
  "conversion_value": 199.99,
  "path_length": 3,
  "attributions": {
    "first_touch": {
      "channel": "paid_search",
      "attributed_value": 199.99,
      "credit_percentage": 100
    },
    "last_touch": {
      "channel": "direct",
      "attributed_value": 199.99,
      "credit_percentage": 100
    },
    "linear": [
      {"channel": "paid_search", "attributed_value": 66.66, "credit_percentage": 33.33},
      {"channel": "email", "attributed_value": 66.66, "credit_percentage": 33.33},
      {"channel": "direct", "attributed_value": 66.67, "credit_percentage": 33.34}
    ],
    "time_decay": [
      {"channel": "paid_search", "attributed_value": 23.89, "credit_percentage": 11.98},
      {"channel": "email", "attributed_value": 60.13, "credit_percentage": 30.13},
      {"channel": "direct", "attributed_value": 115.97, "credit_percentage": 57.99}
    ]
  }
}
```

---

### 2. Get Full Attribution Report
**GET** `/api/attribution/report`

Comprehensive attribution analysis with all models, channel ROI, patterns, and statistics.

**Query Parameters:**
- `start_date` (optional): ISO format start date for filtering
- `end_date` (optional): ISO format end date for filtering

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_conversions": 150,
    "total_revenue": 29847.50,
    "avg_order_value": 198.98
  },
  "channel_roi": {
    "paid_search": {
      "spend": 5000.00,
      "revenue": 20000.00,
      "roi_percent": 300.00,
      "roas": 4.00,
      "conversions": 75,
      "cost_per_conversion": 66.67,
      "ctr": 0.30
    },
    "email": {
      "spend": 800.00,
      "revenue": 5994.75,
      "roi_percent": 649.34,
      "roas": 7.49,
      "conversions": 35,
      "cost_per_conversion": 22.86,
      "ctr": 0.44
    }
  },
  "best_channel": ["email", {...metrics...}],
  "path_statistics": {
    "total_paths_analyzed": 150,
    "avg_path_length": 2.47,
    "max_path_length": 6,
    "min_path_length": 1,
    "avg_unique_channels": 1.89,
    "avg_hours_between_touches": 24.3,
    "most_common_pattern": "paid_search → direct"
  },
  "common_patterns": [
    ["paid_search → direct", 32],
    ["email → direct", 28],
    ["organic → direct", 22]
  ],
  "model_comparison": {
    "first_touch": {
      "paid_search": 10000.00,
      "email": 3000.00,
      "organic": 2847.50
    },
    "last_touch": {...},
    "linear": {...},
    "time_decay": {...}
  },
  "model_variance": {
    "paid_search": {
      "variance": 2847.50,
      "std_dev": 53.36,
      "avg_attributed": 8500.00
    }
  }
}
```

---

### 3. Get Channel ROI Analysis
**GET** `/api/attribution/channel-roi`

Detailed ROI metrics for all marketing channels.

**Response:**
```json
{
  "success": true,
  "channels": {
    "paid_search": {
      "spend": 5000.00,
      "revenue": 20000.00,
      "roi_percent": 300.00,
      "roas": 4.00,
      "conversions": 75,
      "impressions": 25000,
      "cost_per_conversion": 66.67,
      "ctr": 0.30
    },
    "email": {...},
    "social": {...}
  },
  "best_performing": ["email", {...metrics...}]
}
```

---

### 4. Compare Attribution Models
**GET** `/api/attribution/model-comparison`

Side-by-side attribution comparison across all 4 models with variance analysis.

**Response:**
```json
{
  "success": true,
  "comparison": {
    "first_touch": {
      "paid_search": 10000.00,
      "email": 3000.00,
      "organic": 2847.50
    },
    "last_touch": {
      "paid_search": 5000.00,
      "email": 6847.50,
      "organic": 4000.00
    },
    "linear": {
      "paid_search": 7950.00,
      "email": 4950.00,
      "organic": 4947.50
    },
    "time_decay": {
      "paid_search": 6000.00,
      "email": 7500.00,
      "organic": 3347.50
    }
  },
  "variance": {
    "paid_search": {
      "variance": 2847.50,
      "std_dev": 53.36,
      "avg_attributed": 8500.00
    }
  }
}
```

**Model Descriptions:**
- **First-touch**: 100% credit to first touchpoint (awareness metric)
- **Last-touch**: 100% credit to last touchpoint (conversion metric)
- **Linear**: Equal credit distributed to all touchpoints
- **Time-decay**: Credit increases closer to conversion (exponential decay)

---

### 5. Get Budget Optimization Recommendations
**POST** `/api/attribution/budget-optimization`

AI-driven budget allocation recommendations based on historical ROI.

**Request Body:**
```json
{
  "total_budget": 10000.00
}
```

**Response:**
```json
{
  "success": true,
  "total_budget": 10000.00,
  "recommendations": {
    "email": 4200.00,
    "paid_search": 3500.00,
    "social": 1800.00,
    "organic": 500.00
  },
  "reasoning": {
    "email": "Highest ROI (649%), allocate 42% of budget",
    "paid_search": "Strong ROI (300%), allocate 35% of budget",
    "social": "Lower ROI (20%), allocate 18% of budget",
    "organic": "Free channel, maintain baseline"
  }
}
```

---

### 6. Get Conversion Path Analysis
**GET** `/api/attribution/conversion-paths`

Analyze customer journey patterns and path statistics.

**Query Parameters:**
- `limit` (optional): Max number of patterns to return (default: 10)

**Response:**
```json
{
  "success": true,
  "paths": {
    "patterns": [
      {"pattern": "paid_search → direct", "conversions": 32, "pct": 21.3},
      {"pattern": "email → direct", "conversions": 28, "pct": 18.7},
      {"pattern": "organic → direct", "conversions": 22, "pct": 14.7}
    ],
    "statistics": {
      "total_paths": 150,
      "avg_length": 2.47,
      "max_length": 6,
      "avg_time_between_touches_hours": 24.3
    }
  }
}
```

---

### 7. Admin Dashboard
**GET** `/admin/attribution`

Interactive dashboard with ROI cards, model comparison, budget optimizer, and journey tracker.

**Features:**
- Executive summary (total revenue, conversions, avg order value, path length)
- Channel ROI performance grid
- Attribution model comparison (4 models side-by-side)
- Model variance analysis (consensus indicators)
- Top conversion path patterns
- Path statistics
- Budget allocation calculator
- Journey tracker form

---

## Error Responses

All endpoints return error responses in the format:

```json
{
  "success": false,
  "error": "Error description"
}
```

**Common HTTP Status Codes:**
- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing/invalid authentication
- `500 Internal Server Error`: Server error

---

## Rate Limiting
No rate limiting implemented (development). For production, recommend:
- 100 requests/minute per user
- 1000 requests/minute per API key

---

## Webhook Integration
Coming in Feature #21: Real-time attribution webhooks for marketing platform integrations.

---

## Example Workflows

### Workflow 1: Track Sale and Get Attribution
```python
# Track customer conversion
POST /api/attribution/track-journey
{
  "customer_id": "user_456",
  "order_id": "ORD_2024_001",
  "conversion_value": 299.99,
  "touchpoints": [...]
}

# Get full report
GET /api/attribution/report

# Get budget recommendation
POST /api/attribution/budget-optimization
{"total_budget": 5000}
```

### Workflow 2: Optimize Marketing Spend
```python
# Get current channel ROI
GET /api/attribution/channel-roi

# Compare how different models value channels
GET /api/attribution/model-comparison

# Get AI budget recommendation
POST /api/attribution/budget-optimization
{"total_budget": 10000}

# Implement recommended allocation
```

### Workflow 3: Analyze Customer Journeys
```python
# Get conversion patterns
GET /api/attribution/conversion-paths

# Identify most valuable channels
GET /api/attribution/channel-roi

# View on admin dashboard
GET /admin/attribution
```

---

## Technical Specs

**Attribution Models:** First-touch, Last-touch, Linear, Time-decay
**Path Analysis:** Pattern detection, time-between-touches calculation
**ROI Metrics:** ROAS, CPC, CTR, cost-per-conversion
**Database:** SQLite (development), PostgreSQL recommended (production)
**Performance:** <100ms for most queries with proper indexing

---

**Last Updated:** Feature #20 Complete
**API Version:** 1.0
**Status:** Production Ready
