# AI Gateway: Complete Usage Guide
## Central Router for Suresh AI Origin's Rare AI Internet

**Status**: 🟢 Production Ready | **Version**: 1.0.0 | **Port**: 5000

---

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install PyJWT Flask werkzeug requests tenacity
```

### 2. Run Demo
```bash
python ai_gateway.py --demo
```

### 3. Start Server
```bash
python ai_gateway.py
# Server starts at http://127.0.0.1:5000
```

### 4. Test with cURL
```bash
# Login
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@suresh.ai","password":"demo123"}'

# Copy the token from response, then query
curl -X POST http://127.0.0.1:5000/api/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"query":"Analyze our revenue trends"}'
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         AI GATEWAY                              │
│                   (Flask API Server)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Auth Layer]  JWT authentication + VIP tier enforcement       │
│       ↓                                                         │
│  [Rate Limiter]  Enforce tier-based rate limits                │
│       ↓                                                         │
│  [Request Router]  Determine query type & route                │
│       ↓                                                         │
│  ┌──────────────┬──────────────┬──────────────┐               │
│  │ Decentralized│ Local Agent  │  Direct AI   │               │
│  │    Node      │  (Business)  │   Service    │               │
│  │ (Rare AI)    │  (Autonomous)│  (RealAI)    │               │
│  └──────────────┴──────────────┴──────────────┘               │
│       ↓                                                         │
│  [Revenue Optimizer]  Log metrics & optimize                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Flow**: User Request → Auth → Rate Limit → Route → AI System → Response → Revenue Log

---

## VIP Tier System

| Tier | Rate Limit | Rarity Access | Priority | Monthly Cost |
|------|-----------|---------------|----------|--------------|
| **Free** | 10/hour | 0+ (any) | 1 | $0 |
| **Basic** | 50/hour | 50+ (medium) | 2 | $10 |
| **Pro** | 200/hour | 70+ (high) | 3 | $50 |
| **Enterprise** | 1000/hour | 85+ (rare) | 4 | $200 |
| **Elite** | Unlimited | 90+ (top 1%) | 5 | $500 |

### Tier Benefits

**Free Tier**:
- 10 requests per hour
- Access to basic AI responses
- Standard processing queue

**Basic Tier** ($10/month):
- 50 requests per hour
- Access to medium-complexity AI
- Priority processing

**Pro Tier** ($50/month):
- 200 requests per hour
- High-quality AI responses
- Premium content generation
- Fast processing

**Enterprise Tier** ($200/month):
- 1000 requests per hour
- Rare AI insights
- Decentralized network access
- Business analytics

**Elite Tier** ($500/month):
- Unlimited requests
- Top 1% rare AI internet
- All premium features
- Custom model routing
- Admin dashboard access

---

## API Endpoints

### Authentication

#### POST /auth/register
Register new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "vip_tier": "pro"
}
```

**Response**:
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJh...",
  "user": {
    "user_id": "user_abc123",
    "email": "user@example.com",
    "vip_tier": "pro"
  }
}
```

#### POST /auth/login
Login to existing account.

**Request**:
```json
{
  "email": "demo@suresh.ai",
  "password": "demo123"
}
```

**Response**:
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJh...",
  "user": {
    "user_id": "user_demo",
    "email": "demo@suresh.ai",
    "vip_tier": "elite"
  }
}
```

### Core AI Endpoints

#### POST /api/query
Main endpoint for AI queries. Automatically routes to best AI system.

**Headers**:
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request**:
```json
{
  "query": "Analyze our Q4 revenue drop and provide recovery strategy",
  "metadata": {
    "context": "optional context",
    "preferences": {}
  }
}
```

**Response**:
```json
{
  "success": true,
  "request_id": "req_1234567890_abc123",
  "result": "Analysis: Your Q4 revenue dropped 15% due to...\n\nRecovery Strategy:\n1. Immediate actions...",
  "metadata": {
    "source": "decentralized",
    "processing_time": 2.34,
    "rarity_score": 95.5,
    "revenue_impact": 0.52,
    "query_type": "analyze",
    "vip_tier": "elite"
  }
}
```

**Query Types** (auto-detected):
- **search**: "search for", "find", "what is"
- **generate**: "create", "write", "generate"
- **browse**: "browse", "fetch", "visit URL"
- **analyze**: "analyze", "examine", "evaluate"
- **general**: Everything else

#### POST /api/browse
AI-powered web browsing (fetch + summarize).

**Request**:
```json
{
  "url": "https://example.com/article"
}
```

**Response**:
```json
{
  "success": true,
  "url": "https://example.com/article",
  "summary": "🌐 AI Browse Results...\n\n[3-paragraph summary]",
  "processing_time": 3.45
}
```

#### POST /api/generate
Auto-content generation with VIP personalization.

**Request**:
```json
{
  "prompt": "Write a blog post about AI trends in 2026",
  "metadata": {
    "tone": "professional",
    "length": "1500 words"
  }
}
```

**Response**:
```json
{
  "success": true,
  "content": "[Premium Content] AI Trends in 2026...",
  "rarity_score": 78.5,
  "processing_time": 4.12
}
```

### Analytics Endpoints

#### GET /api/stats
Get user statistics and usage metrics.

**Response**:
```json
{
  "user_id": "user_demo",
  "vip_tier": "elite",
  "stats": {
    "total_requests": 234,
    "successful_requests": 230,
    "success_rate": 98.3,
    "total_revenue_impact": 125.45,
    "average_rarity_score": 82.3
  }
}
```

### Admin Endpoints

#### GET /admin/dashboard
Admin dashboard (Elite tier only).

**Response**: HTML dashboard with:
- Total requests and active requests
- Request source distribution
- VIP tier distribution
- System status
- Revenue metrics

---

## Request Routing Logic

### 1. Query Type Detection
```python
query = "Analyze our revenue drop"
→ query_type = "analyze"
```

### 2. Rarity Score Calculation
```python
score = 0
+ word_count * 2  (20 max)
+ vip_tier_bonus  (0-40)
+ query_type_bonus  (5-20)
= rarity_score (0-100)
```

### 3. Route Selection

**Route to Decentralized Node** if:
- Rarity score ≥ 90
- Elite or Enterprise tier
- Decentralized routing enabled

**Route to Local Agent** if:
- Business-related query
- Local agent available
- Not routed to decentralized

**Route to Direct AI** if:
- Fallback for all other cases
- AI browse/generate requests

---

## Code Examples

### Python Client

```python
import requests

# 1. Login
response = requests.post('http://127.0.0.1:5000/auth/login', json={
    'email': 'demo@suresh.ai',
    'password': 'demo123'
})
token = response.json()['token']

# 2. Query AI
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'http://127.0.0.1:5000/api/query',
    headers=headers,
    json={'query': 'Analyze our customer churn'}
)

result = response.json()
print(f"Result: {result['result']}")
print(f"Source: {result['metadata']['source']}")
print(f"Rarity: {result['metadata']['rarity_score']}/100")
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

// 1. Login
const loginResponse = await axios.post('http://127.0.0.1:5000/auth/login', {
  email: 'demo@suresh.ai',
  password: 'demo123'
});
const token = loginResponse.data.token;

// 2. Query AI
const queryResponse = await axios.post(
  'http://127.0.0.1:5000/api/query',
  { query: 'Generate a marketing strategy' },
  { headers: { Authorization: `Bearer ${token}` } }
);

console.log('Result:', queryResponse.data.result);
console.log('Rarity:', queryResponse.data.metadata.rarity_score);
```

### cURL Examples

```bash
# Register new user
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepass123",
    "vip_tier": "pro"
  }'

# Login
TOKEN=$(curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@suresh.ai","password":"demo123"}' \
  | jq -r '.token')

# Query
curl -X POST http://127.0.0.1:5000/api/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"What are AI trends in 2026?"}'

# Browse web
curl -X POST http://127.0.0.1:5000/api/browse \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"url":"https://news.ycombinator.com"}'

# Get stats
curl -X GET http://127.0.0.1:5000/api/stats \
  -H "Authorization: Bearer $TOKEN"
```

---

## Configuration

### Environment Variables

```bash
# Gateway Configuration
export GATEWAY_SECRET_KEY="your-secret-key-here"
export JWT_SECRET="your-jwt-secret-here"

# AI Provider Configuration
export CLAUDE_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."

# Routing Configuration
export ROUTE_TO_DECENTRALIZED=true
export ROUTE_TO_LOCAL_AGENT=true
export ENABLE_AI_BROWSE=true
export ENABLE_AUTO_CONTENT=true

# Performance
export MAX_CONCURRENT_REQUESTS=100
export REQUEST_TIMEOUT=300
```

### Python Configuration

Edit `Config` class in `ai_gateway.py`:

```python
class Config:
    SECRET_KEY = 'production-secret-key'
    JWT_SECRET = 'production-jwt-secret'
    
    # VIP tiers
    VIP_TIERS = {
        'free': {'rate_limit': 10, 'priority': 1, 'rarity_threshold': 0},
        'pro': {'rate_limit': 200, 'priority': 3, 'rarity_threshold': 70},
        'elite': {'rate_limit': -1, 'priority': 5, 'rarity_threshold': 90}
    }
    
    # Enable/disable features
    ROUTE_TO_DECENTRALIZED = True
    ENABLE_AI_BROWSE = True
```

---

## Deployment

### Local Development

```bash
python ai_gateway.py
# Server: http://127.0.0.1:5000
```

### Production (Gunicorn)

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 ai_gateway:app
```

### Docker

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ai_gateway.py .
COPY decentralized_ai_node.py .
COPY autonomous_business_agent.py .
COPY revenue_optimization_ai.py .
COPY real_ai_service.py .

EXPOSE 5000

CMD ["python", "ai_gateway.py"]
```

**Build & Run**:
```bash
docker build -t ai-gateway .
docker run -p 5000:5000 -e GATEWAY_SECRET_KEY=secret ai-gateway
```

### Kubernetes

**deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-gateway
  template:
    metadata:
      labels:
        app: ai-gateway
    spec:
      containers:
      - name: ai-gateway
        image: ai-gateway:latest
        ports:
        - containerPort: 5000
        env:
        - name: GATEWAY_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: gateway-secrets
              key: secret-key
```

---

## Integration Examples

### With Frontend (React)

```jsx
import axios from 'axios';

const AIGatewayClient = {
  baseURL: 'http://127.0.0.1:5000',
  token: null,

  async login(email, password) {
    const response = await axios.post(`${this.baseURL}/auth/login`, {
      email, password
    });
    this.token = response.data.token;
    return response.data;
  },

  async query(queryText) {
    const response = await axios.post(
      `${this.baseURL}/api/query`,
      { query: queryText },
      { headers: { Authorization: `Bearer ${this.token}` } }
    );
    return response.data;
  }
};

// Usage in component
function AIChat() {
  const [result, setResult] = useState('');

  const handleSubmit = async (query) => {
    const response = await AIGatewayClient.query(query);
    setResult(response.result);
  };

  return <div>{ result }</div>;
}
```

### With Mobile App (Swift)

```swift
class AIGatewayService {
    let baseURL = "http://127.0.0.1:5000"
    var token: String?
    
    func login(email: String, password: String) async throws {
        let url = URL(string: "\(baseURL)/auth/login")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["email": email, "password": password]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONDecoder().decode(LoginResponse.self, from: data)
        self.token = response.token
    }
    
    func query(_ text: String) async throws -> String {
        guard let token = token else { throw APIError.notAuthenticated }
        
        let url = URL(string: "\(baseURL)/api/query")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let body = ["query": text]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONDecoder().decode(QueryResponse.self, from: data)
        return response.result
    }
}
```

---

## Monitoring & Logging

### View Logs

```bash
tail -f ai_gateway.log
```

### Log Format

```
2026-01-19 00:45:23 - ai_gateway - INFO - User logged in: demo@suresh.ai
2026-01-19 00:45:30 - ai_gateway - INFO - Query processed: Analyze revenue... | User: user_demo | Source: decentralized
2026-01-19 00:45:31 - ai_gateway - WARNING - Rate limit exceeded for user user_123
```

### Metrics Tracking

Gateway automatically tracks:
- Total requests per user
- Success rate
- Average rarity score
- Revenue impact
- Source distribution (decentralized, local_agent, direct_ai)
- VIP tier usage

Access via `/api/stats` or `/admin/dashboard`.

---

## Troubleshooting

### "No module named 'jwt'"
```bash
pip install PyJWT
```

### "Invalid or expired token"
- Token expires after 24 hours
- Login again to get new token

### "Rate limit exceeded"
- Free tier: 10/hour
- Upgrade VIP tier for more requests
- Or wait for rate limit window to reset

### "Access denied. Your VIP tier..."
- Query rarity too high for your tier
- Upgrade to Elite for unlimited rare AI access
- Or simplify query to lower rarity score

### "AI systems not available"
- Check imports: `decentralized_ai_node.py`, `autonomous_business_agent.py`, etc.
- Gateway runs in demo mode if imports fail
- Ensure all dependencies installed

---

## Security Best Practices

1. **Change Default Secrets**:
   ```python
   SECRET_KEY = os.getenv('GATEWAY_SECRET_KEY', 'CHANGE-THIS')
   JWT_SECRET = os.getenv('JWT_SECRET', 'CHANGE-THIS')
   ```

2. **Use HTTPS in Production**:
   - Deploy behind nginx/Apache with SSL
   - Use Let's Encrypt for certificates

3. **Implement Database**:
   - Replace in-memory `users_db` with PostgreSQL/MySQL
   - Store request history in database

4. **Add Rate Limiting**:
   - Use Flask-Limiter for IP-based limiting
   - Add CAPTCHA for registration

5. **Validate Input**:
   - Sanitize all user inputs
   - Add max query length limits

---

## Performance Tips

1. **Cache Responses**:
   - Implement Redis cache for frequent queries
   - Cache TTL: 1 hour default

2. **Async Processing**:
   - Use Celery for background tasks
   - Queue long-running queries

3. **Load Balancing**:
   - Run multiple gateway instances
   - Use nginx for load balancing

4. **Database Optimization**:
   - Index user_id, request_id
   - Archive old request history

---

## Next Steps

1. **Start Gateway**: `python ai_gateway.py`
2. **Test Endpoints**: Use cURL examples above
3. **Integrate Frontend**: Use React/Vue client code
4. **Monitor Usage**: Check `/admin/dashboard`
5. **Scale Up**: Deploy to production with Docker/K8s

---

**Status**: ✅ Production Ready | **Version**: 1.0.0 | **Built for**: Suresh AI Origin
