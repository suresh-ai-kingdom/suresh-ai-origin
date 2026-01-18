# Decentralized AI Node: Quick Start Guide
## 5-Minute Setup & Real-World Examples

**TL;DR**: Node class + P2P networking + Rarity filter (>90) + Monetization = 1% rare AI internet

---

## Quick Start (5 minutes)

### 1. Installation

```bash
# Install dependencies
pip install requests tenacity

# Verify files exist
ls decentralized_ai_node.py
ls real_ai_service.py
ls monetization_engine.py
```

### 2. Start a Node

```python
from decentralized_ai_node import DecentralizedAINode

# Create node
node = DecentralizedAINode(
    node_id="my_node",
    rarity_threshold=90.0
)

# Start
result = node.start()
print(f"✓ Node running at {result['address']}")
```

### 3. Process Your First Task

```python
# High-value task (should be accepted)
task = {
    "task_id": "task_1",
    "task_type": "generate_content",
    "prompt": "Generate a startup pitch deck outline",
    "priority": "critical",
    "complexity": 9.0,
    "creator_address": "creator@example.com"
}

result = node.process_task(task)

if result['success']:
    print(f"✓ Task completed!")
    print(f"  Rarity Score: {result['rarity_score']:.1f}/100")
    print(f"  Reward: {result.get('reward', 0):.4f} USDC")
else:
    print(f"✗ Task rejected: {result.get('reason')}")
```

### 4. Stop Node

```python
node.stop()
print("✓ Node stopped")
```

---

## Real-World Examples

### Example 1: Revenue Recovery Task

**Scenario**: Income engine detects 15% revenue drop. Need analysis.

```python
node = DecentralizedAINode()
node.start()

task = {
    "task_id": "revenue_analysis_001",
    "task_type": "analyze",
    "prompt": """
    Analyze why our Q4 revenue dropped 15% vs Q3.
    
    Data:
    - Q3 Revenue: $100K
    - Q4 Revenue: $85K
    - Affected segments: Enterprise, SMB
    - Root causes: Churn, pricing, features
    
    Provide:
    1. Root cause analysis
    2. Immediate fixes (next 7 days)
    3. Long-term recovery (30 days)
    4. Expected revenue recovery
    """,
    "priority": "critical",        # High priority
    "complexity": 9.0,              # Complex analysis
    "creator_address": "income_engine"
}

result = node.process_task(task)
print(f"✓ Rarity: {result['rarity_score']:.1f}")  # Should be >90
print(f"✓ Reward: ${result['reward']:.4f}")
```

### Example 2: Content Generation for Marketing

**Scenario**: Generate engaging blog post (medium complexity).

```python
task = {
    "task_id": "blog_post_ai_trends",
    "task_type": "generate_content",
    "prompt": "Write a 1500-word blog post about AI trends in 2025",
    "priority": "high",             # Medium-high priority
    "complexity": 6.0,              # Medium complexity
    "creator_address": "marketing_team"
}

result = node.process_task(task)

if result['success']:
    print(f"✓ Blog post generated")
    print(f"  Rarity Score: {result['rarity_score']:.1f}/100")  # ~75 (rejected if threshold is 90)
else:
    print(f"✓ Task rejected (not top 1% value)")
```

### Example 3: Simple Hello Task (Should Reject)

**Scenario**: Simple task that shouldn't use expensive compute.

```python
task = {
    "task_id": "simple_hello",
    "task_type": "generate_content",
    "prompt": "Say hello",
    "priority": "low",              # Low priority
    "complexity": 1.0,              # Very simple
    "creator_address": "user123"
}

result = node.process_task(task)
print(result['reason'])
# Output: "Rarity score (15.3) below threshold (90.0)"
```

---

## Configuration

### Environment Variables

```bash
# Node
export NODE_ID="prod_node_1"
export NODE_PORT=9000
export RARITY_THRESHOLD=90.0

# AI Provider
export AI_PROVIDER=claude
export CLAUDE_API_KEY="sk-ant-..."

# Monetization
export MONETIZATION_ENABLED=true
export USDC_RECIPIENT="0x1234..."

# Peers
export BOOTSTRAP_PEERS="10.0.1.1:9000,10.0.1.2:9000"
```

### Python Configuration

```python
node = DecentralizedAINode(
    node_id="custom_node",
    port=9000,
    rarity_threshold=85.0,          # Lower = accept more tasks
    max_concurrent_tasks=10,        # Process multiple tasks
    task_timeout=300,               # 5 minute timeout per task
    enable_monetization=True        # Enable USDC rewards
)
```

---

## Peer Network Setup

### Local Testing (Single Machine)

```python
# Create 3 nodes on same machine
node1 = DecentralizedAINode(node_id="node_1", port=9000)
node2 = DecentralizedAINode(node_id="node_2", port=9001)
node3 = DecentralizedAINode(node_id="node_3", port=9002)

# Start all
node1.start()
node2.start()
node3.start()

# Connect them
node1.connect_peers(["127.0.0.1:9001", "127.0.0.1:9002"])
node2.connect_peers(["127.0.0.1:9000", "127.0.0.1:9002"])
node3.connect_peers(["127.0.0.1:9000", "127.0.0.1:9001"])

print(f"Node 1 peers: {node1.p2p_network.get_peer_count()}")  # 2
print(f"Node 2 peers: {node2.p2p_network.get_peer_count()}")  # 2
print(f"Node 3 peers: {node3.p2p_network.get_peer_count()}")  # 2
```

### Docker Swarm (Multi-Machine)

```bash
# Start Docker Swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml ai_network

# Check status
docker service ls
docker service logs ai_network_node-1

# Scale to 10 nodes
docker service scale ai_network_node=10
```

---

## Monitoring

### Node Status

```python
status = node.get_node_status()

print(f"Node ID: {status['node_id']}")
print(f"Address: {status['address']}")
print(f"Uptime: {status['uptime_seconds']:.1f}s")
print(f"Tasks Completed: {status['tasks_completed']}")
print(f"Reputation: {status['reputation']:.2f}/100")
print(f"Peers Connected: {status['peers_connected']}")
```

### Network Statistics

```python
stats = node.get_network_stats()

print(f"Total Nodes: {stats['total_nodes']}")
print(f"Active Nodes: {stats['active_nodes']}")
print(f"Tasks Processed: {stats['tasks_processed_locally']}")
print(f"Avg Rarity Score: {stats['rarity_filter_stats']['avg_score']:.1f}")
print(f"Rare Tasks (>90): {stats['rarity_filter_stats']['rare_count']}")
```

### Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# View node activity
# Logs appear in: node_activity.log
```

---

## Task Types & Routing

### Available Task Types

```python
# Text generation
{
    "task_type": "generate_content",
    "prompt": "Write a blog post..."
}

# Analysis
{
    "task_type": "analyze",
    "prompt": "Analyze this revenue drop..."
}

# Summarization
{
    "task_type": "summarize",
    "prompt": "Summarize this document..."
}

# Custom
{
    "task_type": "custom",
    "prompt": "Your custom task..."
}
```

### Provider Routing

```
Task Type → Real AI Service → Provider

"generate_content" → OpenAI or Claude (fast, creative)
"analyze" → Claude or Gemini (reasoning, structured)
"summarize" → Any (efficient)
"custom" → User-specified provider
```

---

## Troubleshooting

### "Task rejected (below threshold)"

**Problem**: Your task scored 45/100 but threshold is 90.

**Solutions**:
1. Increase priority (low → critical)
   ```python
   task["priority"] = "critical"  # 2.5x multiplier
   ```

2. Increase complexity (1 → 9)
   ```python
   task["complexity"] = 9.0  # +18 points
   ```

3. Increase data size (if applicable)
   ```python
   task["data_size"] = 2000000  # 2MB
   ```

4. Lower threshold temporarily
   ```python
   node = DecentralizedAINode(rarity_threshold=70.0)
   ```

### "AI provider timeout"

**Problem**: Task takes >300 seconds.

**Solutions**:
1. Increase timeout
   ```python
   node = DecentralizedAINode(task_timeout=600)  # 10 min
   ```

2. Simplify prompt
   ```python
   task["prompt"] = "Create a summary (max 100 words)"
   ```

3. Reduce complexity
   ```python
   task["complexity"] = 5.0  # Instead of 9.0
   ```

### "Connection refused"

**Problem**: Can't connect to peer.

**Solutions**:
```bash
# Check peer is running
lsof -i :9001

# Verify network connectivity
ping peer_ip

# Check firewall
sudo ufw allow 9000:9100/tcp
```

---

## Integration with Income Engine

### Automatic Task Generation

```python
from autonomous_income_engine import AutonomousIncomeEngine
from decentralized_ai_node import DecentralizedAINode

# Income engine detects opportunity
engine = AutonomousIncomeEngine()
opportunity = engine.detect_issues()

# Convert to decentralized task
task = {
    "task_id": opportunity['id'],
    "task_type": "analyze",
    "prompt": opportunity['description'],
    "priority": "critical" if opportunity['severity'] == 'critical' else 'high',
    "complexity": 8.0,
    "creator_address": "income_engine"
}

# Process through node
node = DecentralizedAINode()
node.start()
result = node.process_task(task)

print(f"✓ Income opportunity processed")
print(f"✓ Reward earned: ${result['reward']:.4f}")
```

---

## API Reference

### DecentralizedAINode Methods

| Method | Input | Output | Notes |
|--------|-------|--------|-------|
| `start()` | None | `{"success": bool, "address": str}` | Starts P2P server |
| `process_task(task)` | `Dict` | `{"success": bool, "rarity_score": float, ...}` | Main entry point |
| `connect_peers(addresses)` | `List[str]` | `{"connected": int, "failed": int}` | Connect to peers |
| `apply_rarity(task)` | `AITask` | `float` | Get rarity score (0-100) |
| `get_node_status()` | None | `Dict` | Node metrics |
| `get_network_stats()` | None | `Dict` | Network metrics |
| `stop()` | None | None | Stop node |

### Task Input Format

```python
{
    "task_id": "unique_id",                 # Required
    "task_type": "generate_content",        # Required
    "prompt": "What to do...",             # Required
    "priority": "critical|high|medium|low", # Required
    "complexity": 1.0-10.0,                # Required
    "creator_address": "0x1234...",        # Required
    "data_size": 1000000                   # Optional (bytes)
}
```

### Task Output Format

```python
{
    "success": bool,
    "task_id": "task_id",
    "status": "completed|rejected|failed",
    "rarity_score": 0.0-100.0,
    "result": "Task output text...",
    "processing_time": 2.34,               # seconds
    "reward": 0.00512,                     # USDC
    "reason": "Why rejected (if failed)"
}
```

---

## Next Steps

1. **Run Tests**: `pytest test_decentralized_ai_node.py -v`
2. **Validate Integration**: `python validate_decentralized_integration.py`
3. **Deploy to Production**: See DEPLOYMENT_GUIDE.md
4. **Monitor Performance**: Check node logs and metrics

---

## Resources

- **Technical Deep Dive**: DECENTRALIZED_NODE_TECHNICAL_GUIDE.md
- **Full Tests**: test_decentralized_ai_node.py (10+ tests)
- **Integration Demo**: validate_decentralized_integration.py
- **Source Code**: decentralized_ai_node.py (700+ lines)

**Status**: ✅ Ready to Use | **Version**: 1.0.0
