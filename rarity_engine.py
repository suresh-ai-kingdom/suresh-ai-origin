"""
RARITY ENGINE - Suresh AI Origin's Content Scoring & Curation System

Scores content/prompts/workflows for uniqueness via NLP similarity analysis.
Auto-generates variants for low-rarity items and maintains curated database.
Integrates with auto_recovery.py for self-healing rarity optimization.

KEY FEATURES:
- NLP-based uniqueness scoring (0-100 scale)
- Automatic variant generation for low-rarity content
- Persistent rare_db.json management
- Auto-recovery integration for self-healing
- Similarity analysis using spaCy/NLTK
- Content metadata tracking
- Batch scoring capability
- Rarity trend analysis

EXAMPLE USAGE:
    engine = RarityEngine()
    
    # Score a prompt
    result = engine.score_item("Your prompt here")
    # Returns: {"score": 92.5, "level": "high", "unique_tokens": 45, ...}
    
    # Rarify content (generate variants if low score)
    rarefied = engine.rarify_content("Original prompt")
    # Returns: {"original": ..., "variants": [...], "final_score": 97.8, ...}
    
    # Manage database
    engine.curate_db()  # Auto-optimize rare_db.json
    
    # Get rarity trends
    stats = engine.get_rarity_stats()
"""

import json
import os
import time
import hashlib
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
import re
from collections import Counter
from abc import ABC, abstractmethod

# NLP imports (with graceful fallback)
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available - using fallback NLP")

try:
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    import nltk
    NLTK_AVAILABLE = True
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available - using fallback tokenization")


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class RarityConfig:
    """Configuration for rarity engine"""
    
    # Scoring
    min_score_threshold: float = 95.0  # Score below this triggers auto-curation
    similarity_threshold: float = 0.75  # Similarity above this counts as duplicate
    
    # Variant generation
    max_variants: int = 5  # Max variants to generate per item
    variant_diversity_level: int = 3  # 1=conservative, 3=moderate, 5=aggressive
    
    # Database
    db_path: str = "rare_db.json"
    max_db_items: int = 10000  # Max items before cleanup
    
    # Auto-recovery
    enable_auto_recovery: bool = True
    recovery_retry_count: int = 3
    recovery_sleep_seconds: float = 0.5
    
    # Scoring weights
    uniqueness_weight: float = 0.40  # How unique vs corpus
    complexity_weight: float = 0.25  # Content complexity
    semantic_weight: float = 0.20   # Semantic depth
    freshness_weight: float = 0.15  # Recency factor
    

@dataclass
class RarityItem:
    """Model for a rarity-scored item"""
    
    id: str  # SHA256 hash
    content: str  # Original content
    score: float  # Rarity score (0-100)
    level: str  # "low", "medium", "high", "rare", "legendary"
    unique_tokens: int  # Count of unique tokens
    complexity: float  # Complexity score
    semantic_depth: float  # Semantic richness
    freshness: float  # Recency factor
    variants: List[str] = field(default_factory=list)  # Generated variants
    timestamp: float = field(default_factory=time.time)  # Creation time
    access_count: int = 0  # Times accessed
    source: str = "manual"  # "manual", "auto_generated", "api"
    metadata: Dict[str, Any] = field(default_factory=dict)  # Custom metadata
    

@dataclass
class RarityResult:
    """Result from rarify_content operation"""
    
    original: Dict[str, Any]  # Original item data
    variants: List[Dict[str, Any]]  # Generated variants
    final_score: float  # Best achieved score
    iterations: int  # Curation iterations
    success: bool  # Whether min threshold achieved
    processing_time: float  # Total time taken
    recovered: bool = False  # Whether recovered from low score


# ============================================================================
# BASE SCORER (Abstract)
# ============================================================================

class SimilarityScorer(ABC):
    """Abstract base for similarity scoring"""
    
    @abstractmethod
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0-1)"""
        pass
    
    @abstractmethod
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        pass


# ============================================================================
# SPACY-BASED SCORER
# ============================================================================

class SpacySimilarityScorer(SimilarityScorer):
    """NLP scoring using spaCy"""
    
    def __init__(self, model: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
            self.available = True
        except OSError:
            logging.warning(f"spaCy model {model} not found, trying to download...")
            os.system(f"python -m spacy download {model}")
            try:
                self.nlp = spacy.load(model)
                self.available = True
            except:
                self.available = False
                logging.warning("Failed to load spaCy model")
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using spaCy vectors"""
        if not self.available or not text1 or not text2:
            return 0.0
        
        try:
            doc1 = self.nlp(text1[:1000])  # Limit to 1000 chars for performance
            doc2 = self.nlp(text2[:1000])
            
            if doc1.vector_norm == 0 or doc2.vector_norm == 0:
                return 0.0
            
            return doc1.similarity(doc2)
        except Exception as e:
            logging.error(f"spaCy similarity error: {e}")
            return 0.0
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize using spaCy"""
        if not self.available:
            return text.lower().split()
        
        try:
            doc = self.nlp(text[:1000])
            return [token.text for token in doc]
        except:
            return text.lower().split()


# ============================================================================
# NLTK-BASED SCORER (Fallback)
# ============================================================================

class NLTKSimilarityScorer(SimilarityScorer):
    """NLP scoring using NLTK (fallback)"""
    
    def __init__(self):
        self.stopwords_set = set(stopwords.words('english')) if NLTK_AVAILABLE else set()
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using token overlap"""
        if not text1 or not text2:
            return 0.0
        
        tokens1 = set(self.tokenize(text1))
        tokens2 = set(self.tokenize(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize using NLTK"""
        text = text.lower()
        
        if NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(text)
            except:
                tokens = re.findall(r'\w+', text)
        else:
            tokens = re.findall(r'\w+', text)
        
        # Filter stopwords
        return [t for t in tokens if t not in self.stopwords_set and len(t) > 2]


# ============================================================================
# SIMPLE SCORER (Pure Python fallback)
# ============================================================================

class SimpleSimilarityScorer(SimilarityScorer):
    """Pure Python similarity scorer (fallback)"""
    
    def similarity(self, text1: str, text2: str) -> float:
        """Simple token-based similarity"""
        if not text1 or not text2:
            return 0.0
        
        tokens1 = set(self.tokenize(text1))
        tokens2 = set(self.tokenize(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0
    
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return [t for t in tokens if len(t) > 2]


# ============================================================================
# MAIN RARITY ENGINE
# ============================================================================

class RarityEngine:
    """
    Main rarity scoring and curation engine.
    
    Scores content for uniqueness, auto-generates variants for low scores,
    and maintains a curated database of rare content.
    """
    
    def __init__(self, config: Optional[RarityConfig] = None):
        """Initialize rarity engine"""
        
        self.config = config or RarityConfig()
        self.logger = self._setup_logging()
        
        # Initialize similarity scorer
        self.scorer = self._init_scorer()
        
        # Load or create database
        self.db_path = Path(self.config.db_path)
        self.rare_db = self._load_database()
        
        # Variant generators
        self.variant_generators = [
            self._paraphrase_variant,
            self._expand_variant,
            self._compress_variant,
            self._reorder_variant,
            self._synonym_variant,
        ]
        
        # Auto-recovery client (lazy loaded)
        self._auto_recovery_client = None
        
        self.logger.info(f"RarityEngine initialized with scorer: {type(self.scorer).__name__}")
    
    # ========================================================================
    # SETUP & INITIALIZATION
    # ========================================================================
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("RarityEngine")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - RarityEngine - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _init_scorer(self) -> SimilarityScorer:
        """Initialize best available similarity scorer"""
        
        if SPACY_AVAILABLE:
            self.logger.info("Using spaCy scorer")
            return SpacySimilarityScorer()
        elif NLTK_AVAILABLE:
            self.logger.info("Using NLTK scorer")
            return NLTKSimilarityScorer()
        else:
            self.logger.info("Using simple fallback scorer")
            return SimpleSimilarityScorer()
    
    def _load_database(self) -> Dict[str, Dict[str, Any]]:
        """Load rare_db.json or create new"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.logger.info(f"Loaded database with {len(data)} items")
                    return data
            except Exception as e:
                self.logger.error(f"Failed to load database: {e}")
                return {}
        return {}
    
    def _save_database(self):
        """Save database to rare_db.json"""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.rare_db, f, indent=2)
            self.logger.debug(f"Saved database with {len(self.rare_db)} items")
        except Exception as e:
            self.logger.error(f"Failed to save database: {e}")
    
    # ========================================================================
    # CORE SCORING METHODS
    # ========================================================================
    
    def score_item(self, content: str, source: str = "manual", 
                   metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Score content for rarity/uniqueness.
        
        Args:
            content: Content to score
            source: Source of content
            metadata: Optional metadata
            
        Returns:
            Dictionary with score, level, and analysis
        """
        
        if not content or not isinstance(content, str):
            self.logger.warning("Invalid content provided")
            return {"score": 0, "level": "invalid", "error": "Invalid content"}
        
        start_time = time.time()
        
        try:
            # Generate item ID
            item_id = self._hash_content(content)
            
            # Calculate component scores
            uniqueness = self._score_uniqueness(content)
            complexity = self._score_complexity(content)
            semantic_depth = self._score_semantic_depth(content)
            freshness = self._score_freshness(item_id)
            
            # Weighted combination
            score = (
                uniqueness * self.config.uniqueness_weight +
                complexity * self.config.complexity_weight +
                semantic_depth * self.config.semantic_weight +
                freshness * self.config.freshness_weight
            )
            
            # Normalize to 0-100
            score = min(100, max(0, score))
            
            # Determine level
            level = self._score_to_level(score)
            
            # Tokenize for unique token count
            tokens = self.scorer.tokenize(content)
            unique_tokens = len(set(tokens))
            
            result = {
                "id": item_id,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "score": round(score, 2),
                "level": level,
                "unique_tokens": unique_tokens,
                "complexity": round(complexity, 2),
                "semantic_depth": round(semantic_depth, 2),
                "freshness": round(freshness, 2),
                "source": source,
                "timestamp": time.time(),
                "processing_time": round(time.time() - start_time, 4),
                "components": {
                    "uniqueness": round(uniqueness, 2),
                    "complexity": round(complexity, 2),
                    "semantic_depth": round(semantic_depth, 2),
                    "freshness": round(freshness, 2),
                }
            }
            
            # Add to database with metadata
            if item_id not in self.rare_db:
                item = RarityItem(
                    id=item_id,
                    content=content,
                    score=score,
                    level=level,
                    unique_tokens=unique_tokens,
                    complexity=complexity,
                    semantic_depth=semantic_depth,
                    freshness=freshness,
                    source=source,
                    metadata=metadata or {}
                )
                self.rare_db[item_id] = asdict(item)
                self._save_database()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error scoring item: {e}")
            return {"score": 0, "level": "error", "error": str(e)}
    
    def _score_uniqueness(self, content: str) -> float:
        """Score uniqueness against existing database (0-100)"""
        
        if not self.rare_db:
            return 100.0  # First item is maximally unique
        
        # Sample comparison (for performance, don't compare all)
        sample_size = min(100, len(self.rare_db))
        sample_items = list(self.rare_db.values())[:sample_size]
        
        similarities = []
        for item in sample_items:
            sim = self.scorer.similarity(content, item.get("content", ""))
            similarities.append(sim)
        
        if not similarities:
            return 100.0
        
        # Average similarity
        avg_similarity = sum(similarities) / len(similarities)
        
        # Convert to uniqueness (100 = unique, 0 = duplicate)
        uniqueness = max(0, (1 - avg_similarity) * 100)
        
        return uniqueness
    
    def _score_complexity(self, content: str) -> float:
        """Score content complexity (0-100)"""
        
        tokens = self.scorer.tokenize(content)
        if not tokens:
            return 0.0
        
        # Metrics
        unique_ratio = len(set(tokens)) / len(tokens)  # Vocab diversity
        avg_word_length = sum(len(t) for t in tokens) / len(tokens)
        sentence_count = len(re.split(r'[.!?]+', content))
        sentences_with_tokens = sentence_count if sentence_count > 0 else 1
        avg_sentence_length = len(tokens) / sentences_with_tokens
        
        # Scoring
        complexity_score = (
            (unique_ratio * 30) +  # Diversity bonus
            (min(avg_word_length / 10, 1.0) * 30) +  # Word length bonus
            (min(avg_sentence_length / 20, 1.0) * 40)  # Sentence complexity bonus
        )
        
        return min(100, complexity_score)
    
    def _score_semantic_depth(self, content: str) -> float:
        """Score semantic richness and depth (0-100)"""
        
        # Heuristics for semantic depth
        depth_indicators = {
            r'\b(because|therefore|however|furthermore|moreover)\b': 10,
            r'\b(analyze|consider|evaluate|examine|investigate)\b': 8,
            r'\b(question|problem|solution|approach|method)\b': 7,
            r'\b(relationship|connection|pattern|correlation)\b': 6,
            r'[,;:]': 2,  # Punctuation for complexity
        }
        
        score = 0.0
        for pattern, points in depth_indicators.items():
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            score += matches * points
        
        # Normalize
        tokens = self.scorer.tokenize(content)
        if tokens:
            score = (score / len(tokens)) * 100
        
        return min(100, score)
    
    def _score_freshness(self, item_id: str) -> float:
        """Score freshness based on recency (0-100)"""
        
        if item_id in self.rare_db:
            item = self.rare_db[item_id]
            timestamp = item.get("timestamp", time.time())
            age_seconds = time.time() - timestamp
            age_days = age_seconds / 86400
            
            # Decay over 30 days
            freshness = max(0, 100 - (age_days / 30 * 100))
            return freshness
        
        return 100.0  # New items are fresh
    
    def _score_to_level(self, score: float) -> str:
        """Convert score to level"""
        if score >= 95:
            return "legendary"
        elif score >= 85:
            return "rare"
        elif score >= 70:
            return "high"
        elif score >= 50:
            return "medium"
        else:
            return "low"
    
    # ========================================================================
    # VARIANT GENERATION
    # ========================================================================
    
    def _paraphrase_variant(self, content: str) -> str:
        """Generate paraphrase variant"""
        tokens = self.scorer.tokenize(content)
        if len(tokens) < 5:
            return content
        
        # Reorder some tokens
        import random
        reordered_tokens = tokens[:]
        shuffle_indices = random.sample(range(len(reordered_tokens)), 
                                       min(3, len(reordered_tokens) // 3))
        for i in shuffle_indices:
            if i + 1 < len(reordered_tokens):
                reordered_tokens[i], reordered_tokens[i + 1] = reordered_tokens[i + 1], reordered_tokens[i]
        
        return " ".join(reordered_tokens)
    
    def _expand_variant(self, content: str) -> str:
        """Generate expanded variant"""
        
        expansions = {
            r'\b(and|or)\b': lambda m: {' and ': ' and additionally ', ' or ': ' or alternatively '}[m.group(0)],
            r'([.!?])$': r'\1 This is important.',
        }
        
        expanded = content
        for pattern, replacement in expansions.items():
            if callable(replacement):
                expanded = re.sub(pattern, replacement, expanded)
            else:
                expanded = re.sub(pattern, replacement, expanded)
        
        return expanded
    
    def _compress_variant(self, content: str) -> str:
        """Generate compressed variant"""
        
        # Remove redundant words
        tokens = self.scorer.tokenize(content)
        compressed = []
        prev_token = None
        
        for token in tokens:
            if token != prev_token:
                compressed.append(token)
                prev_token = token
        
        return " ".join(compressed)
    
    def _reorder_variant(self, content: str) -> str:
        """Generate reordered variant"""
        
        sentences = re.split(r'(?<=[.!?])\s+', content)
        if len(sentences) <= 1:
            return content
        
        import random
        reordered = sentences[:]
        random.shuffle(reordered)
        
        return " ".join(reordered)
    
    def _synonym_variant(self, content: str) -> str:
        """Generate synonym variant"""
        
        # Simple synonym replacements
        synonyms = {
            'important': 'significant',
            'good': 'excellent',
            'bad': 'poor',
            'helpful': 'beneficial',
            'problem': 'issue',
            'solution': 'approach',
            'create': 'generate',
            'make': 'produce',
            'use': 'utilize',
            'help': 'assist',
        }
        
        result = content
        for original, synonym in synonyms.items():
            pattern = r'\b' + original + r'\b'
            result = re.sub(pattern, synonym, result, flags=re.IGNORECASE)
        
        return result
    
    def _generate_variants(self, content: str) -> List[str]:
        """Generate multiple variants of content"""
        
        variants = []
        
        for generator in self.variant_generators[:self.config.max_variants]:
            try:
                variant = generator(content)
                if variant != content:
                    variants.append(variant)
            except Exception as e:
                self.logger.warning(f"Failed to generate variant: {e}")
        
        return variants
    
    # ========================================================================
    # MAIN RARIFY OPERATION
    # ========================================================================
    
    def rarify_content(self, content: str, source: str = "manual",
                      metadata: Optional[Dict] = None) -> RarityResult:
        """
        Rarify content: score, auto-generate variants if needed, curate.
        
        Args:
            content: Content to rarify
            source: Content source
            metadata: Optional metadata
            
        Returns:
            RarityResult with original, variants, final score
        """
        
        start_time = time.time()
        iterations = 0
        recovered = False
        
        try:
            # Initial score
            original_result = self.score_item(content, source, metadata)
            original_score = original_result.get("score", 0)
            
            # Check if meets threshold
            if original_score >= self.config.min_score_threshold:
                self.logger.info(f"Content already rare: {original_score}")
                return RarityResult(
                    original=original_result,
                    variants=[],
                    final_score=original_score,
                    iterations=1,
                    success=True,
                    processing_time=time.time() - start_time,
                    recovered=False
                )
            
            # Need to rarify
            self.logger.info(f"Content score low ({original_score}), generating variants...")
            
            best_variant = None
            best_score = original_score
            all_variants = []
            
            # Generate and score variants
            max_iterations = self.config.recovery_retry_count if self.config.enable_auto_recovery else 1
            
            for iteration in range(max_iterations):
                iterations += 1
                
                variants = self._generate_variants(content)
                
                for variant in variants:
                    variant_result = self.score_item(variant, f"{source}_variant", metadata)
                    variant_score = variant_result.get("score", 0)
                    
                    all_variants.append({
                        "variant": variant,
                        "result": variant_result,
                        "score": variant_score
                    })
                    
                    if variant_score > best_score:
                        best_variant = variant
                        best_score = variant_score
                        self.logger.info(f"Better variant found: {variant_score}")
                    
                    # Stop if threshold reached
                    if variant_score >= self.config.min_score_threshold:
                        self.logger.info(f"Threshold reached: {variant_score}")
                        recovered = True
                        break
                
                if recovered:
                    break
                
                # Sleep before retry
                if iteration < max_iterations - 1:
                    time.sleep(self.config.recovery_sleep_seconds)
            
            # Try auto-recovery if enabled and still below threshold
            if (not recovered and self.config.enable_auto_recovery and 
                best_score < self.config.min_score_threshold):
                
                self.logger.info("Attempting auto-recovery...")
                recovered_score = self._attempt_auto_recovery(content, source, metadata)
                
                if recovered_score and recovered_score > best_score:
                    best_score = recovered_score
                    recovered = True
                    self.logger.info(f"Auto-recovery succeeded: {best_score}")
            
            # Final result
            variant_dicts = [v["result"] for v in all_variants]
            
            return RarityResult(
                original=original_result,
                variants=variant_dicts,
                final_score=best_score,
                iterations=iterations,
                success=best_score >= self.config.min_score_threshold,
                processing_time=time.time() - start_time,
                recovered=recovered
            )
            
        except Exception as e:
            self.logger.error(f"Error rarifying content: {e}")
            return RarityResult(
                original={},
                variants=[],
                final_score=0,
                iterations=0,
                success=False,
                processing_time=time.time() - start_time,
                recovered=False
            )
    
    # ========================================================================
    # AUTO-RECOVERY INTEGRATION
    # ========================================================================
    
    def _attempt_auto_recovery(self, content: str, source: str,
                               metadata: Optional[Dict]) -> Optional[float]:
        """Attempt auto-recovery via auto_recovery.py integration"""
        
        if not self.config.enable_auto_recovery:
            return None
        
        try:
            # Lazy-load auto_recovery client
            if self._auto_recovery_client is None:
                try:
                    from auto_recovery import AutoRecoverySystem
                    self._auto_recovery_client = AutoRecoverySystem()
                except ImportError:
                    self.logger.warning("auto_recovery.py not available")
                    return None
            
            # Call recovery system
            if self._auto_recovery_client:
                recovery_result = self._auto_recovery_client.recover_quality(
                    content=content,
                    quality_type="rarity",
                    target_score=self.config.min_score_threshold
                )
                
                if recovery_result and recovery_result.get("success"):
                    recovered_content = recovery_result.get("recovered_content", content)
                    score_result = self.score_item(recovered_content, f"{source}_recovered", metadata)
                    return score_result.get("score")
        
        except Exception as e:
            self.logger.warning(f"Auto-recovery failed: {e}")
        
        return None
    
    # ========================================================================
    # DATABASE CURATION
    # ========================================================================
    
    def curate_db(self, cleanup: bool = True, optimize: bool = True) -> Dict[str, Any]:
        """
        Curate rare_db.json: cleanup, optimize, maintain integrity.
        
        Args:
            cleanup: Remove low-scoring items
            optimize: Optimize structure
            
        Returns:
            Curation statistics
        """
        
        start_time = time.time()
        stats = {
            "initial_count": len(self.rare_db),
            "removed_count": 0,
            "optimized_count": 0,
            "duplicate_count": 0,
        }
        
        try:
            # Cleanup low-scoring items
            if cleanup:
                items_to_remove = []
                for item_id, item_data in self.rare_db.items():
                    score = item_data.get("score", 0)
                    
                    # Remove very low scoring items or accessed only once
                    if (score < 30 and item_data.get("access_count", 0) <= 1):
                        items_to_remove.append(item_id)
                
                for item_id in items_to_remove:
                    del self.rare_db[item_id]
                    stats["removed_count"] += 1
            
            # Optimize structure
            if optimize:
                optimized_db = {}
                seen_contents = set()
                
                for item_id, item_data in self.rare_db.items():
                    content = item_data.get("content", "")
                    
                    # Check for duplicates
                    content_hash = self._hash_content(content)
                    if content_hash in seen_contents:
                        stats["duplicate_count"] += 1
                        continue
                    
                    seen_contents.add(content_hash)
                    optimized_db[item_id] = item_data
                    stats["optimized_count"] += 1
                
                self.rare_db = optimized_db
            
            # Enforce max items limit
            if len(self.rare_db) > self.config.max_db_items:
                sorted_items = sorted(
                    self.rare_db.items(),
                    key=lambda x: x[1].get("score", 0) * x[1].get("access_count", 1),
                    reverse=True
                )
                self.rare_db = dict(sorted_items[:self.config.max_db_items])
            
            self._save_database()
            
            stats["final_count"] = len(self.rare_db)
            stats["processing_time"] = time.time() - start_time
            
            self.logger.info(f"Curation complete: {stats}")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Curation failed: {e}")
            return stats
    
    # ========================================================================
    # DATABASE ANALYTICS
    # ========================================================================
    
    def get_rarity_stats(self) -> Dict[str, Any]:
        """Get statistics about database and rarity distribution"""
        
        if not self.rare_db:
            return {"total_items": 0, "error": "Empty database"}
        
        scores = [item.get("score", 0) for item in self.rare_db.values()]
        levels = [item.get("level", "unknown") for item in self.rare_db.values()]
        access_counts = [item.get("access_count", 0) for item in self.rare_db.values()]
        
        return {
            "total_items": len(self.rare_db),
            "score_stats": {
                "min": min(scores),
                "max": max(scores),
                "mean": sum(scores) / len(scores),
                "median": sorted(scores)[len(scores) // 2],
            },
            "level_distribution": dict(Counter(levels)),
            "total_accesses": sum(access_counts),
            "avg_access_count": sum(access_counts) / len(access_counts),
            "db_size_bytes": os.path.getsize(self.config.db_path) if self.db_path.exists() else 0,
            "timestamp": datetime.now().isoformat(),
        }
    
    def get_top_rare_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top rarest items from database"""
        
        sorted_items = sorted(
            self.rare_db.items(),
            key=lambda x: x[1].get("score", 0),
            reverse=True
        )
        
        return [item[1] for item in sorted_items[:limit]]
    
    def search_rare_items(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search database for items matching query"""
        
        query_lower = query.lower()
        results = []
        
        for item in self.rare_db.values():
            content = item.get("content", "").lower()
            if query_lower in content:
                results.append(item)
        
        # Sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return results[:limit]
    
    # ========================================================================
    # UTILITIES
    # ========================================================================
    
    def _hash_content(self, content: str) -> str:
        """Generate SHA256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def batch_score(self, contents: List[str], source: str = "batch") -> List[Dict[str, Any]]:
        """Score multiple items at once"""
        
        results = []
        for content in contents:
            try:
                result = self.score_item(content, source)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Batch score error: {e}")
                results.append({"error": str(e)})
        
        return results
    
    def batch_rarify(self, contents: List[str], source: str = "batch") -> List[RarityResult]:
        """Rarify multiple items at once"""
        
        results = []
        for content in contents:
            try:
                result = self.rarify_content(content, source)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Batch rarify error: {e}")
        
        return results


# ============================================================================
# EXAMPLE USAGE & DEMONSTRATION
# ============================================================================

def demo_rarity_engine():
    """Demonstrate rarity engine capabilities"""
    
    print("\n" + "=" * 80)
    print("RARITY ENGINE DEMONSTRATION")
    print("=" * 80 + "\n")
    
    # Initialize engine
    engine = RarityEngine()
    
    # Example 1: Score a prompt
    print("1. SCORING A PROMPT")
    print("-" * 80)
    prompt = "Analyze the relationship between artificial intelligence and human creativity"
    result = engine.score_item(prompt, source="example")
    print(f"Prompt: {prompt}")
    print(f"Score: {result['score']}/100")
    print(f"Level: {result['level']}")
    print(f"Components: {result.get('components', {})}\n")
    
    # Example 2: Rarify content
    print("2. RARIFYING CONTENT (Score < 95 → Auto-generate variants)")
    print("-" * 80)
    low_rarity_prompt = "What is machine learning"
    rarified = engine.rarify_content(low_rarity_prompt, source="example")
    print(f"Original: {low_rarity_prompt}")
    print(f"Original Score: {rarified.original['score']}")
    print(f"Final Score: {rarified.final_score} (after {rarified.iterations} iterations)")
    print(f"Success: {rarified.success}")
    print(f"Recovered: {rarified.recovered}")
    print(f"Processing Time: {rarified.processing_time}s")
    if rarified.variants:
        print(f"Variants Generated: {len(rarified.variants)}")
    print()
    
    # Example 3: Batch scoring
    print("3. BATCH SCORING")
    print("-" * 80)
    batch_prompts = [
        "Create an innovative solution for renewable energy storage",
        "Explain quantum computing basics",
        "Design a sustainable city",
    ]
    batch_results = engine.batch_score(batch_prompts, source="batch_example")
    for i, result in enumerate(batch_results, 1):
        print(f"{i}. Score: {result.get('score')}/100, Level: {result.get('level')}")
    print()
    
    # Example 4: Database statistics
    print("4. DATABASE STATISTICS")
    print("-" * 80)
    stats = engine.get_rarity_stats()
    print(f"Total Items: {stats['total_items']}")
    print(f"Score Range: {stats['score_stats']['min']:.1f}-{stats['score_stats']['max']:.1f}")
    print(f"Mean Score: {stats['score_stats']['mean']:.1f}")
    print(f"Median Score: {stats['score_stats']['median']:.1f}")
    print(f"Level Distribution: {stats['level_distribution']}")
    print()
    
    # Example 5: Curation
    print("5. DATABASE CURATION")
    print("-" * 80)
    curation_stats = engine.curate_db()
    print(f"Items Before: {curation_stats['initial_count']}")
    print(f"Items Removed: {curation_stats['removed_count']}")
    print(f"Items After: {curation_stats['final_count']}")
    print(f"Processing Time: {curation_stats['processing_time']:.4f}s")
    print()
    
    # Example 6: Top rare items
    print("6. TOP RARE ITEMS")
    print("-" * 80)
    top_items = engine.get_top_rare_items(limit=5)
    for i, item in enumerate(top_items, 1):
        print(f"{i}. Score: {item['score']} | Level: {item['level']} | Content: {item['content'][:50]}...")
    print()
    
    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    demo_rarity_engine()
