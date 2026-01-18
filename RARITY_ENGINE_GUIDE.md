# RARITY ENGINE - Complete Guide

**Status**: 🟢 **PRODUCTION READY** | **Version**: 1.0.0 | **Type**: Content Scoring & Curation System  
**Purpose**: Score content for uniqueness, auto-generate rare variants, maintain curated database  
**Built for**: Suresh AI Origin's 1% Rare AI Internet

---

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Architecture](#architecture)
4. [API Reference](#api-reference)
5. [Configuration](#configuration)
6. [Scoring System](#scoring-system)
7. [Variant Generation](#variant-generation)
8. [Auto-Recovery Integration](#auto-recovery-integration)
9. [Database Management](#database-management)
10. [Code Examples](#code-examples)
11. [Integration Points](#integration-points)
12. [Deployment](#deployment)
13. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

```bash
# Install dependencies
pip install nltk spacy

# Download spaCy model (optional, for better NLP)
python -m spacy download en_core_web_sm
```

### Basic Usage (5 minutes)

```python
from rarity_engine import RarityEngine

# Initialize
engine = RarityEngine()

# Score content
result = engine.score_item("Your prompt here")
print(f"Score: {result['score']}/100")
print(f"Level: {result['level']}")

# Rarify content (auto-generate variants if low score)
rarified = engine.rarify_content("Original prompt")
print(f"Final Score: {rarified.final_score}")
print(f"Success: {rarified.success}")

# View database stats
stats = engine.get_rarity_stats()
print(f"Total items: {stats['total_items']}")
```

### Run Demo

```bash
python rarity_engine.py
```

Output shows:
- Scoring example
- Rarification with variants
- Batch processing
- Database statistics
- Top rare items

---

## Core Concepts

### What is "Rarity"?

**Rarity Score**: 0-100 scale measuring content uniqueness & quality
- **0-30**: Low (common, duplicated)
- **30-50**: Medium (some uniqueness)
- **50-70**: High (distinct, valuable)
- **70-85**: Rare (very unique)
- **85-95**: Legendary (top tier)
- **95-100**: Mythical (1% of content)

### What is "Rarification"?

**Rarification**: Process of automatically improving low-rarity content by:
1. Generating variants through multiple strategies
2. Scoring each variant
3. Selecting the best variant
4. Attempting auto-recovery if still below threshold

### Why Does It Matter?

In the 1% rare AI internet:
- **Scarcity = Value**: Rare content commands higher prices
- **Quality Filter**: Separates exceptional from ordinary
- **Differentiation**: Ensures unique outputs per user
- **Revenue Optimization**: Rare content generates more revenue

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│ RarityEngine                                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Scoring Module                                   │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ - Uniqueness Score (vs. corpus)      [40% weight] │  │
│  │ - Complexity Score (vocab diversity)  [25% weight] │  │
│  │ - Semantic Depth (meaning richness)  [20% weight] │  │
│  │ - Freshness Score (recency)          [15% weight] │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │ NLP Backend (Pluggable)                          │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ 1. spaCy (preferred - semantic vectors)         │  │
│  │ 2. NLTK (fallback - token-based)                │  │
│  │ 3. Simple (pure Python - no dependencies)       │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Variant Generation Module                        │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ - Paraphrase Variant                            │  │
│  │ - Expand Variant (add context)                  │  │
│  │ - Compress Variant (simplify)                   │  │
│  │ - Reorder Variant (rearrange)                   │  │
│  │ - Synonym Variant (replace words)               │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Auto-Recovery Module                            │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ - Retries generation up to N times              │  │
│  │ - Calls auto_recovery.py if available           │  │
│  │ - Validates against min_threshold               │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Database Module (rare_db.json)                   │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ - Store all scored items                        │  │
│  │ - Track metadata & history                      │  │
│  │ - Enable search & analytics                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
Input Content
     ↓
[Hash/ID Generation]
     ↓
[Uniqueness Scoring] → Compare vs. existing items
     ↓
[Complexity Scoring] → Analyze vocabulary & structure
     ↓
[Semantic Scoring]   → Evaluate meaning depth
     ↓
[Freshness Scoring]  → Check recency
     ↓
[Weighted Combination] → (40% + 25% + 20% + 15%)
     ↓
[Final Score 0-100]
     ↓
Check: Score >= 95?
     ├─ YES → Store & Return ✓
     └─ NO  → Generate Variants
              ↓
         Score Each Variant
              ↓
         Best > 95?
              ├─ YES → Rarify Complete ✓
              └─ NO  → Attempt Auto-Recovery
                       ↓
                   Success?
                   ├─ YES → Rarify Complete ✓
                   └─ NO  → Return with recovered=false
```

---

## API Reference

### Main Classes

#### RarityEngine

Central orchestrator for all rarity operations.

```python
engine = RarityEngine(config=None)
```

**Parameters**:
- `config` (RarityConfig, optional): Configuration object

**Key Methods**:
- `score_item(content, source, metadata)` → dict
- `rarify_content(content, source, metadata)` → RarityResult
- `curate_db(cleanup, optimize)` → dict
- `get_rarity_stats()` → dict
- `get_top_rare_items(limit)` → list
- `search_rare_items(query, limit)` → list
- `batch_score(contents, source)` → list
- `batch_rarify(contents, source)` → list

#### RarityConfig

Configuration dataclass for engine behavior.

```python
config = RarityConfig(
    min_score_threshold=95.0,      # Auto-rarify if below
    similarity_threshold=0.75,      # Duplicate detection
    max_variants=5,                 # Variants per item
    variant_diversity_level=3,      # 1-5 aggression
    db_path="rare_db.json",         # Database location
    max_db_items=10000,             # Max capacity
    enable_auto_recovery=True,      # Use auto_recovery.py
    recovery_retry_count=3,         # Retry attempts
    recovery_sleep_seconds=0.5      # Wait between retries
)
```

#### RarityItem

Data model for stored items.

```python
@dataclass
class RarityItem:
    id: str                         # SHA256 hash
    content: str                    # Original content
    score: float                    # 0-100
    level: str                      # low|medium|high|rare|legendary
    unique_tokens: int              # Token diversity
    complexity: float               # Complexity metric
    semantic_depth: float           # Meaning richness
    freshness: float                # Recency score
    variants: List[str]             # Generated variants
    timestamp: float                # Creation time
    access_count: int               # Usage count
    source: str                     # "manual"|"api"|"auto_generated"
    metadata: Dict                  # Custom data
```

#### RarityResult

Result from rarify_content operation.

```python
@dataclass
class RarityResult:
    original: Dict                  # Original item data
    variants: List[Dict]            # Generated variants
    final_score: float              # Best achieved score
    iterations: int                 # Curation iterations
    success: bool                   # Threshold achieved?
    processing_time: float          # Execution time (seconds)
    recovered: bool                 # Auto-recovery used?
```

---

### Method Documentation

#### `score_item(content, source="manual", metadata=None)`

Score content for rarity/uniqueness.

```python
result = engine.score_item(
    content="Your prompt here",
    source="api",  # "manual", "api", "batch"
    metadata={"user_id": "user123", "language": "en"}
)

# Returns:
{
    "id": "abc123...",              # SHA256 hash
    "content": "Your prompt...",    # Truncated to 100 chars
    "score": 87.5,                  # 0-100
    "level": "rare",                # low|medium|high|rare|legendary
    "unique_tokens": 45,            # Unique vocabulary
    "complexity": 72.3,             # Complexity metric
    "semantic_depth": 68.5,         # Meaning richness
    "freshness": 100.0,             # Recency (new = 100)
    "source": "api",
    "timestamp": 1705691234.567,
    "processing_time": 0.0234,
    "components": {
        "uniqueness": 85.2,
        "complexity": 72.3,
        "semantic_depth": 68.5,
        "freshness": 100.0
    }
}
```

#### `rarify_content(content, source="manual", metadata=None)`

Improve low-rarity content by generating variants.

```python
result = engine.rarify_content(
    content="What is AI",
    source="user_query",
    metadata={"category": "tech"}
)

# Returns:
RarityResult(
    original={...},                 # Original scoring result
    variants=[
        {"variant": "...", "result": {...}, "score": 78.5},
        {"variant": "...", "result": {...}, "score": 82.1},
        # ... up to max_variants
    ],
    final_score=96.3,               # Best achieved
    iterations=3,                   # Curation attempts
    success=True,                   # Threshold achieved
    processing_time=2.342,          # Seconds
    recovered=False                 # Auto-recovery used?
)
```

#### `curate_db(cleanup=True, optimize=True)`

Maintain database: cleanup, optimize, enforce limits.

```python
stats = engine.curate_db()

# Returns:
{
    "initial_count": 1234,          # Before curation
    "removed_count": 45,            # Deleted items
    "optimized_count": 1189,        # Kept items
    "duplicate_count": 12,          # Merged duplicates
    "final_count": 1189,            # After curation
    "processing_time": 0.456
}
```

#### `get_rarity_stats()`

Get database statistics and distribution.

```python
stats = engine.get_rarity_stats()

# Returns:
{
    "total_items": 1234,
    "score_stats": {
        "min": 15.3,
        "max": 99.8,
        "mean": 72.5,
        "median": 75.2
    },
    "level_distribution": {
        "low": 123,
        "medium": 245,
        "high": 456,
        "rare": 321,
        "legendary": 89
    },
    "total_accesses": 5432,
    "avg_access_count": 4.4,
    "db_size_bytes": 2345678,
    "timestamp": "2026-01-19T15:30:45.123"
}
```

#### `get_top_rare_items(limit=10)`

Retrieve highest-scoring items.

```python
top_items = engine.get_top_rare_items(limit=5)

# Returns: List of top 5 RarityItem dicts sorted by score descending
```

#### `search_rare_items(query, limit=10)`

Search database by content text.

```python
results = engine.search_rare_items("quantum computing", limit=10)

# Returns: List of items matching query, sorted by relevance
```

#### `batch_score(contents, source="batch")`

Score multiple items efficiently.

```python
results = engine.batch_score([
    "Prompt 1",
    "Prompt 2",
    "Prompt 3"
])

# Returns: List of score results
```

#### `batch_rarify(contents, source="batch")`

Rarify multiple items at once.

```python
results = engine.batch_rarify([
    "Prompt 1",
    "Prompt 2"
])

# Returns: List of RarityResult objects
```

---

## Configuration

### Default Configuration

```python
from rarity_engine import RarityConfig, RarityEngine

config = RarityConfig()
engine = RarityEngine(config=config)
```

### Custom Configuration Examples

**Conservative (high threshold)**:
```python
config = RarityConfig(
    min_score_threshold=97.0,       # Stricter
    variant_diversity_level=1,      # Less aggressive
    max_variants=3                  # Fewer attempts
)
```

**Aggressive (quick processing)**:
```python
config = RarityConfig(
    min_score_threshold=85.0,       # More lenient
    variant_diversity_level=5,      # More aggressive
    max_variants=10,                # More attempts
    recovery_retry_count=5          # More retries
)
```

**Production (balanced)**:
```python
config = RarityConfig(
    min_score_threshold=95.0,
    similarity_threshold=0.75,
    max_variants=5,
    max_db_items=50000,             # Large capacity
    enable_auto_recovery=True,
    recovery_retry_count=3
)
```

### Environment Variables (Future)

```bash
# Not yet implemented, but planned:
RARITY_MIN_SCORE=95.0
RARITY_DB_PATH=./rare_db.json
RARITY_AUTO_RECOVERY=true
RARITY_MAX_VARIANTS=5
```

---

## Scoring System

### Scoring Formula

```
Final Score = 
    (Uniqueness × 0.40) +
    (Complexity × 0.25) +
    (Semantic Depth × 0.20) +
    (Freshness × 0.15)
```

### Score Components

#### Uniqueness (40% weight)

Measures how unique content is compared to database.

```python
# Algorithm:
# 1. Sample up to 100 items from database
# 2. Calculate similarity to each sample
# 3. Average similarities
# 4. Convert to uniqueness (100 - avg_similarity)

# Example:
# - Average similarity: 0.3 → Uniqueness: 70 points
# - Average similarity: 0.05 → Uniqueness: 95 points
```

**High Uniqueness**:
- Novel topics
- Original phrasing
- Unique combinations

**Low Uniqueness**:
- Common topics ("What is AI?")
- Clichéd language
- Repeated content

#### Complexity (25% weight)

Measures content depth and sophistication.

```python
# Metrics:
# 1. Vocabulary diversity (unique_words / total_words)
# 2. Average word length (favor longer, technical words)
# 3. Sentence complexity (words per sentence)

# Scoring:
# - Diversity: 30 points max
# - Word length: 30 points max
# - Sentence complexity: 40 points max
```

**High Complexity**:
- Technical vocabulary
- Varied sentence structure
- Advanced concepts

**Low Complexity**:
- Simple words
- Repetitive structure
- Basic concepts

#### Semantic Depth (20% weight)

Measures meaning richness and conceptual depth.

```python
# Heuristics:
# - Academic/analytical words: "analyze", "investigate"
# - Reasoning words: "because", "therefore"
# - Relationship words: "correlation", "relationship"
# - Punctuation (complexity indicator): commas, semicolons

# Algorithm:
# 1. Count depth indicators
# 2. Weight by importance
# 3. Normalize by content length
```

**High Semantic Depth**:
- Multiple perspectives
- Causal relationships
- Technical depth

**Low Semantic Depth**:
- Surface-level statements
- Simple facts
- No analysis

#### Freshness (15% weight)

Measures recency of content.

```python
# Algorithm:
# 1. Calculate age in days: (now - creation_time) / 86400
# 2. Decay over 30 days: max(0, 100 - (age / 30 * 100))
# 3. New items = 100 points
# 4. 30-day-old items = 0 points
```

**High Freshness**:
- Newly created
- Recently updated

**Low Freshness**:
- Older content
- Potentially outdated

### Score Levels

| Score | Level | Meaning | Rarity |
|-------|-------|---------|--------|
| 0-30 | Low | Common, duplicated | Very Common |
| 30-50 | Medium | Some uniqueness | Common |
| 50-70 | High | Distinct, valuable | Less Common |
| 70-85 | Rare | Very unique | Rare |
| 85-95 | Legendary | Top tier | Very Rare |
| 95-100 | Mythical | 1% of content | Extreme |

---

## Variant Generation

### Variant Strategies

Engine generates variants using 5 different strategies:

#### 1. Paraphrase Variant

Reorder tokens while preserving meaning.

```python
Original: "Artificial intelligence transforms business"
Variant:  "Business transforms through artificial intelligence"
```

**Use Case**: Create different phrasings of same concept

#### 2. Expand Variant

Add context, examples, or elaboration.

```python
Original: "Use Python for AI"
Variant:  "Use Python and additionally install relevant libraries for AI development"
```

**Use Case**: Increase depth and complexity

#### 3. Compress Variant

Simplify while retaining meaning.

```python
Original: "The rapid growth of AI and machine learning..."
Variant:  "AI growth accelerates"
```

**Use Case**: Create concise version

#### 4. Reorder Variant

Rearrange sentence or clause order.

```python
Original: "While AI grows, costs rise. Solutions emerge."
Variant:  "Solutions emerge. AI grows while costs rise."
```

**Use Case**: Different narrative structure

#### 5. Synonym Variant

Replace words with synonyms.

```python
Original: "Create good solutions for problems"
Variant:  "Generate excellent approaches for issues"
```

**Use Case**: Vocabulary variation

### Variant Generation Process

```
Input Content
     ↓
Generate all 5 variant types
     ↓
Score each variant
     ↓
Select highest-scoring variant
     ↓
Compare to threshold
     ├─ Above 95? → Success! Return variant
     └─ Below 95? → Try again (up to N retries)
```

### Configuration

```python
config = RarityConfig(
    max_variants=5,           # Generate up to 5 per attempt
    variant_diversity_level=3 # 1=conservative, 5=aggressive
    # Diversity level affects:
    # - How much variants differ from original
    # - Token reordering extent
    # - Compression aggressiveness
)
```

---

## Auto-Recovery Integration

### What is Auto-Recovery?

Auto-recovery is a self-healing mechanism that attempts to improve low-scoring content by:

1. Retrying variant generation
2. Calling `auto_recovery.py` if available
3. Validating against minimum threshold
4. Returning best attempt

### Integration Points

#### Optional Dependency

Auto-recovery is **optional**. Engine works without it.

```python
# If auto_recovery.py exists:
from auto_recovery import AutoRecoverySystem

# If not available:
# Engine logs warning and continues
```

#### Recovery Attempt

```python
# In rarify_content():
if (not recovered and 
    self.config.enable_auto_recovery and 
    best_score < min_threshold):
    
    recovered_score = self._attempt_auto_recovery(
        content, source, metadata
    )
    
    if recovered_score > best_score:
        best_score = recovered_score
        recovered = True
```

#### Configuration

```python
config = RarityConfig(
    enable_auto_recovery=True,      # Enable/disable
    recovery_retry_count=3,         # Retry attempts
    recovery_sleep_seconds=0.5      # Sleep between retries
)
```

### Expected Behavior

**With Auto-Recovery Available**:
- Rarity engine attempts variants (up to N times)
- If still below threshold, calls `AutoRecoverySystem.recover_quality()`
- Recovery system applies domain-specific fixes
- Returns improved content with new score

**Without Auto-Recovery**:
- Rarity engine attempts variants only
- Returns best variant achieved
- `recovered=False` in result

### Example Integration

```python
from rarity_engine import RarityEngine
from auto_recovery import AutoRecoverySystem

engine = RarityEngine()

# This automatically uses auto-recovery if available
result = engine.rarify_content("Low quality prompt")

# Check if auto-recovery was used
if result.recovered:
    print(f"Auto-recovery improved score to {result.final_score}")
else:
    print(f"No auto-recovery needed, score is {result.final_score}")
```

---

## Database Management

### Database Format

File: `rare_db.json`

```json
{
  "abc123...": {
    "id": "abc123...",
    "content": "Full content text",
    "score": 87.5,
    "level": "rare",
    "unique_tokens": 45,
    "complexity": 72.3,
    "semantic_depth": 68.5,
    "freshness": 100.0,
    "variants": ["variant1", "variant2"],
    "timestamp": 1705691234.567,
    "access_count": 5,
    "source": "api",
    "metadata": {
      "user_id": "user123",
      "category": "technology"
    }
  }
}
```

### Database Operations

#### Automatic Saving

Database auto-saves on:
- New item scored
- Content rarified
- Metadata updated

#### Manual Curation

```python
# Cleanup low-scoring items
stats = engine.curate_db(cleanup=True, optimize=True)

# Actions:
# - Remove items with score < 30 and access_count <= 1
# - Remove duplicate content (by hash)
# - Enforce max_db_items limit (keep highest scoring)
# - Optimize JSON structure
```

#### Search & Retrieval

```python
# Get top rare items
top = engine.get_top_rare_items(limit=10)

# Search by content
results = engine.search_rare_items("quantum computing", limit=10)

# Get statistics
stats = engine.get_rarity_stats()
```

### Database Limits

| Setting | Default | Purpose |
|---------|---------|---------|
| `max_db_items` | 10,000 | Maximum items before cleanup |
| Auto-cleanup | Enabled | Runs when limit exceeded |
| Retention | Highest scoring | Keep best items when pruning |

### Backup & Recovery

```bash
# Manual backup
cp rare_db.json rare_db.backup.json

# Restore
cp rare_db.backup.json rare_db.json
```

---

## Code Examples

### Example 1: Score a Single Prompt

```python
from rarity_engine import RarityEngine

engine = RarityEngine()

prompt = "Create an innovative approach to renewable energy storage"
result = engine.score_item(prompt)

print(f"Score: {result['score']}/100")
print(f"Level: {result['level']}")
print(f"Uniqueness: {result['components']['uniqueness']}")
print(f"Complexity: {result['components']['complexity']}")
```

### Example 2: Rarify Content with Variants

```python
result = engine.rarify_content("What is AI?")

print(f"Original Score: {result.original['score']}")
print(f"Final Score: {result.final_score}")
print(f"Variants Generated: {len(result.variants)}")
print(f"Success: {result.success}")

if result.variants:
    for i, variant in enumerate(result.variants, 1):
        print(f"  Variant {i}: {variant['score']}")
```

### Example 3: Batch Processing

```python
prompts = [
    "Explain machine learning",
    "How does quantum computing work?",
    "Design a sustainable city"
]

# Score all
results = engine.batch_score(prompts)

for prompt, result in zip(prompts, results):
    print(f"{prompt[:30]}... → {result['score']}")

# Or rarify all
rarified = engine.batch_rarify(prompts)

for prompt, result in zip(prompts, rarified):
    print(f"{prompt[:30]}... → {result.final_score} (success: {result.success})")
```

### Example 4: Analytics and Insights

```python
# Overall statistics
stats = engine.get_rarity_stats()

print(f"Total Items: {stats['total_items']}")
print(f"Average Score: {stats['score_stats']['mean']:.1f}")
print(f"Score Range: {stats['score_stats']['min']:.1f}-{stats['score_stats']['max']:.1f}")

# Distribution
print("\nLevel Distribution:")
for level, count in stats['level_distribution'].items():
    pct = (count / stats['total_items']) * 100
    print(f"  {level}: {count} ({pct:.1f}%)")

# Top rare items
top = engine.get_top_rare_items(limit=5)
print(f"\nTop {len(top)} Rarest Items:")
for item in top:
    print(f"  Score {item['score']}: {item['content'][:50]}")
```

### Example 5: API Integration

```python
from flask import Flask, request, jsonify
from rarity_engine import RarityEngine

app = Flask(__name__)
engine = RarityEngine()

@app.route('/api/score', methods=['POST'])
def score_api():
    data = request.json
    result = engine.score_item(
        content=data['content'],
        source='api',
        metadata={'user_id': data.get('user_id')}
    )
    return jsonify(result)

@app.route('/api/rarify', methods=['POST'])
def rarify_api():
    data = request.json
    result = engine.rarify_content(
        content=data['content'],
        source='api'
    )
    return jsonify({
        'original_score': result.original['score'],
        'final_score': result.final_score,
        'success': result.success,
        'variants_count': len(result.variants)
    })

@app.route('/api/stats', methods=['GET'])
def stats_api():
    return jsonify(engine.get_rarity_stats())

if __name__ == '__main__':
    app.run(port=5001)
```

### Example 6: Custom Configuration

```python
from rarity_engine import RarityEngine, RarityConfig

# Create custom config
config = RarityConfig(
    min_score_threshold=90.0,        # Lower threshold
    max_variants=10,                  # More variants
    variant_diversity_level=5,        # More aggressive
    enable_auto_recovery=True,
    recovery_retry_count=5            # More retries
)

engine = RarityEngine(config=config)

# Use with custom config
result = engine.rarify_content("Your content")
```

---

## Integration Points

### With AI Gateway (ai_gateway.py)

```python
# In AI Gateway request routing
if rarity_score < 90:
    # Rarify before returning to user
    rarified = rarity_engine.rarify_content(response)
    return rarified.final_score
```

### With Auto-Recovery (auto_recovery.py)

```python
# Optional integration point
from auto_recovery import AutoRecoverySystem

recovery = AutoRecoverySystem()
improved = recovery.recover_quality(
    content=low_rarity_content,
    quality_type="rarity",
    target_score=95.0
)
```

### With Revenue Optimization (revenue_optimization_ai.py)

```python
# Log rarity events for revenue calculation
revenue_optimizer.log_event({
    'type': 'rarity_improvement',
    'original_score': 45.2,
    'final_score': 96.8,
    'variants_count': 5,
    'recovery_used': True,
    'revenue_impact': 0.50  # Higher rarity = higher price
})
```

### With Decentralized Node (decentralized_ai_node.py)

```python
# Only send highest rarity to P2P network
result = engine.score_item(content)
if result['score'] >= 90:
    # This is "rare enough" for decentralized processing
    decentralized_node.process_task(content)
```

---

## Deployment

### Local Development

```bash
# 1. Install dependencies
pip install nltk spacy
python -m spacy download en_core_web_sm

# 2. Run tests/demo
python rarity_engine.py

# 3. Integrate into your app
from rarity_engine import RarityEngine
engine = RarityEngine()
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install nltk spacy
RUN python -m spacy download en_core_web_sm

# Copy files
COPY rarity_engine.py .
COPY rare_db.json .

# Volume for database
VOLUME ["/app/data"]

# Run
CMD ["python", "-c", "from rarity_engine import RarityEngine; engine = RarityEngine()"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rarity-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rarity-engine
  template:
    metadata:
      labels:
        app: rarity-engine
    spec:
      containers:
      - name: rarity-engine
        image: suresh-ai/rarity-engine:1.0.0
        ports:
        - containerPort: 5001
        volumeMounts:
        - name: rare-db
          mountPath: /app/data
      volumes:
      - name: rare-db
        persistentVolumeClaim:
          claimName: rare-db-pvc
```

---

## Troubleshooting

### Issue: "spaCy model not found"

**Solution**:
```bash
python -m spacy download en_core_web_sm
```

**Fallback**: Engine automatically falls back to NLTK or simple scorer.

### Issue: "Memory usage growing"

**Solution**:
```python
# Run periodic curation
engine.curate_db(cleanup=True, optimize=True)

# Reduce max_db_items
config = RarityConfig(max_db_items=5000)
```

### Issue: "Slow scoring"

**Solution**:
```python
# Use simpler NLP (less accurate but faster)
# Engine auto-selects best available:
# 1. spaCy (slow, most accurate)
# 2. NLTK (medium)
# 3. Simple (fast, basic)

# Or batch score instead of individual
results = engine.batch_score(contents)  # More efficient
```

### Issue: "Low rarity even after variants"

**Solution**:
```python
# Increase diversity level
config = RarityConfig(variant_diversity_level=5)

# Or lower threshold temporarily
config.min_score_threshold = 90.0

# Or enable auto-recovery
config.enable_auto_recovery = True
config.recovery_retry_count = 5
```

### Issue: "rare_db.json corrupted"

**Solution**:
```bash
# Restore from backup
cp rare_db.backup.json rare_db.json

# Or start fresh (loses all data)
rm rare_db.json
# Next run will create new empty database
```

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Score item | 50-200ms | Depends on NLP backend |
| Rarify content | 1-5 seconds | Includes variant generation |
| Batch score (100 items) | 5-20 seconds | Efficient processing |
| Curate database | Varies | Proportional to DB size |
| Search (10k items) | 100-500ms | Linear search |
| Load database | 50-500ms | On-disk I/O |

**Optimization Tips**:
- Use batch operations when possible
- Schedule curation during off-peak hours
- Consider caching frequently accessed items
- Use simpler NLP scorer for speed if accuracy not critical

---

## Next Steps

1. **Run the demo**: `python rarity_engine.py`
2. **Integrate with API**: Use examples in "Code Examples" section
3. **Configure for your use case**: Adjust RarityConfig values
4. **Monitor performance**: Use `get_rarity_stats()` for insights
5. **Deploy**: Choose Docker or Kubernetes option

---

**Status**: ✅ **PRODUCTION READY**  
**Built for**: Suresh AI Origin's 1% Rare AI Internet  
**Last Updated**: January 19, 2026
