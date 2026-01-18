# RARITY ENGINE - Quick Reference

**Status**: 🟢 **PRODUCTION READY** | **Version**: 1.0.0 | **File**: rarity_engine.py

---

## ⚡ 60-Second Start

```python
from rarity_engine import RarityEngine

# Initialize
engine = RarityEngine()

# Score content (0-100)
result = engine.score_item("Your prompt here")
print(f"Score: {result['score']}/100 ({result['level']})")

# Rarify low-score content (auto-generate variants)
rarified = engine.rarify_content("What is AI?")
print(f"Final score: {rarified.final_score} (success: {rarified.success})")

# View statistics
stats = engine.get_rarity_stats()
print(f"Total items: {stats['total_items']}, Mean score: {stats['score_stats']['mean']:.1f}")
```

---

## 📊 Scoring Scale

```
0-30:    LOW         (common, duplicated)
30-50:   MEDIUM      (some uniqueness)
50-70:   HIGH        (distinct, valuable)
70-85:   RARE        (very unique)
85-95:   LEGENDARY   (top tier)
95-100:  MYTHICAL    (1% of content)
```

---

## 🎯 Core Methods

### Scoring
```python
# Score single item
result = engine.score_item(content, source="manual", metadata={})
# Returns: dict with score, level, components

# Score multiple items
results = engine.batch_score(contents, source="batch")
# Returns: list of result dicts
```

### Rarification
```python
# Improve low-rarity content
rarified = engine.rarify_content(content, source="manual", metadata={})
# Returns: RarityResult with original, variants, final_score, success

# Rarify multiple items
results = engine.batch_rarify(contents, source="batch")
# Returns: list of RarityResult objects
```

### Analytics
```python
# Get database statistics
stats = engine.get_rarity_stats()
# Returns: total_items, score_stats, level_distribution

# Get top rare items
top = engine.get_top_rare_items(limit=10)
# Returns: list of highest-scoring items

# Search database
results = engine.search_rare_items("quantum computing", limit=10)
# Returns: matching items sorted by score
```

### Database Management
```python
# Curate database (cleanup + optimize)
stats = engine.curate_db(cleanup=True, optimize=True)
# Returns: removed_count, final_count, processing_time
```

---

## ⚙️ Configuration

```python
from rarity_engine import RarityConfig, RarityEngine

# Create custom config
config = RarityConfig(
    min_score_threshold=95.0,      # Auto-rarify if below
    similarity_threshold=0.75,      # Duplicate detection
    max_variants=5,                 # Variants per attempt
    variant_diversity_level=3,      # 1=conservative, 5=aggressive
    enable_auto_recovery=True,      # Use auto_recovery.py
    recovery_retry_count=3,         # Retry attempts
    max_db_items=10000              # Max database size
)

# Use custom config
engine = RarityEngine(config=config)
```

---

## 📈 Scoring Formula

```
Final Score (0-100) =
    Uniqueness (40%) +
    Complexity (25%) +
    Semantic Depth (20%) +
    Freshness (15%)

Where:
  Uniqueness    = How unique vs. existing database
  Complexity    = Vocabulary diversity & structure
  Semantic Depth = Meaning richness & analysis level
  Freshness     = Recency (new items = 100)
```

---

## 🔄 Variant Strategies

Engine generates 5 types of variants:

1. **Paraphrase**: Reorder tokens
   - "AI transforms business" → "Business is transformed by AI"

2. **Expand**: Add context
   - "Use Python" → "Use Python and install relevant libraries"

3. **Compress**: Simplify
   - "The rapid growth of AI" → "AI growth accelerates"

4. **Reorder**: Rearrange sentences
   - Different narrative structure

5. **Synonym**: Replace words
   - "Create solutions" → "Generate approaches"

---

## 🔗 Integration Examples

### With AI Gateway
```python
if rarity_score < 90:
    rarified = engine.rarify_content(response)
    return rarified.final_score
```

### With Revenue Optimization
```python
revenue_optimizer.log_event({
    'type': 'rarity_improvement',
    'original_score': 45.2,
    'final_score': 96.8,
    'recovery_used': True,
    'revenue_impact': 0.50
})
```

### With Flask API
```python
from flask import Flask, request, jsonify
from rarity_engine import RarityEngine

app = Flask(__name__)
engine = RarityEngine()

@app.route('/api/score', methods=['POST'])
def score():
    result = engine.score_item(request.json['content'])
    return jsonify(result)

@app.route('/api/rarify', methods=['POST'])
def rarify():
    result = engine.rarify_content(request.json['content'])
    return jsonify({
        'original_score': result.original['score'],
        'final_score': result.final_score,
        'success': result.success
    })
```

---

## 📊 Result Objects

### score_item() returns:
```python
{
    'id': 'abc123...',              # SHA256 hash
    'score': 87.5,                  # 0-100
    'level': 'rare',                # low|medium|high|rare|legendary
    'unique_tokens': 45,
    'complexity': 72.3,
    'semantic_depth': 68.5,
    'freshness': 100.0,
    'components': {
        'uniqueness': 85.2,
        'complexity': 72.3,
        'semantic_depth': 68.5,
        'freshness': 100.0
    },
    'processing_time': 0.0234
}
```

### rarify_content() returns:
```python
RarityResult(
    original={...},                 # Original score
    variants=[{...}, {...}],        # Generated variants
    final_score=96.3,               # Best achieved
    iterations=3,                   # Curation attempts
    success=True,                   # Threshold achieved?
    processing_time=2.342,
    recovered=False                 # Auto-recovery used?
)
```

### get_rarity_stats() returns:
```python
{
    'total_items': 1234,
    'score_stats': {
        'min': 15.3,
        'max': 99.8,
        'mean': 72.5,
        'median': 75.2
    },
    'level_distribution': {
        'low': 123,
        'medium': 245,
        'high': 456,
        'rare': 321,
        'legendary': 89
    }
}
```

---

## 🚀 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Score item | 50-200ms | Depends on NLP |
| Rarify content | 1-5s | Includes variants |
| Batch score (100) | 5-20s | Efficient |
| Database search | 100-500ms | Linear |
| Curate database | Fast | Cleanup + optimize |

---

## 🔧 Common Commands

```bash
# Run demo
python rarity_engine.py

# Install NLP libraries (optional)
pip install nltk spacy
python -m spacy download en_core_web_sm

# Use in Python
from rarity_engine import RarityEngine
engine = RarityEngine()
result = engine.score_item("Your prompt")
```

---

## 📁 Database

**File**: `rare_db.json`

**Stored Data**:
- All scored items
- Generated variants
- Metadata & source
- Access counts
- Timestamps

**Operations**:
- Auto-save on changes
- Manual backup: `cp rare_db.json rare_db.backup.json`
- Restore backup: `cp rare_db.backup.json rare_db.json`

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "spaCy not found" | Auto-falls back to NLTK or simple scorer |
| "Memory growing" | Run `engine.curate_db()` periodically |
| "Slow scoring" | Use batch operations or simpler scorer |
| "Low scores" | Increase `variant_diversity_level` to 5 |
| "DB corrupted" | Restore from backup or delete & recreate |

---

## 🎯 Best Practices

1. **Use custom config** for your use case
   - Conservative (97 threshold) for strict quality
   - Aggressive (85 threshold) for speed

2. **Batch when possible**
   - 10-20% faster than individual scoring

3. **Periodic curation**
   - Run `curate_db()` daily for large databases
   - Removes low-score items with few accesses

4. **Monitor statistics**
   - Use `get_rarity_stats()` for insights
   - Track score distribution changes

5. **Enable auto-recovery**
   - If `auto_recovery.py` available, enable it
   - Gracefully falls back if not available

---

## 📖 Documentation

| File | Content |
|------|---------|
| **rarity_engine.py** | Main implementation (1,200+ lines) |
| **RARITY_ENGINE_GUIDE.md** | Complete guide (800+ lines) |
| **RARITY_ENGINE_SUMMARY.md** | Delivery summary |
| **RARITY_ENGINE_QUICK_REF.md** | This file |

---

## 🔗 Related Systems

- **ai_gateway.py** - Routes requests based on rarity scores
- **auto_recovery.py** - Self-healing for low-rarity content
- **revenue_optimization_ai.py** - Monetizes based on rarity
- **decentralized_ai_node.py** - Handles rare content processing

---

## ✅ Checklist

- [ ] Run `python rarity_engine.py` to see demo
- [ ] Read RARITY_ENGINE_GUIDE.md for deep dive
- [ ] Create RarityConfig for your use case
- [ ] Integrate with your application
- [ ] Test scoring and rarification
- [ ] Set up periodic curation
- [ ] Monitor statistics
- [ ] Deploy to production

---

**Status**: 🟢 **PRODUCTION READY** | **Version**: 1.0.0 | **Built for**: Suresh AI Origin's 1% Rare AI Internet
