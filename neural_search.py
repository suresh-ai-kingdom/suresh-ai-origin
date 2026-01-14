"""
Neural Search & Knowledge Graphs - Week 8 Elite Tier
Vector embeddings, semantic search, knowledge graphs, conversational search
"""

import hashlib
import json
import time
import uuid
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class DocumentEmbedding:
    """Document with vector embedding."""
    doc_id: str
    content: str
    embedding: List[float]
    metadata: Dict
    created_at: float


class VectorEmbeddingService:
    """Generate and manage vector embeddings for semantic search."""
    
    def __init__(self, model: str = "text-embedding-3-large"):
        self.model = model
        self.embeddings: Dict[str, DocumentEmbedding] = {}
        self.dimension = 1536  # OpenAI embedding dimension
    
    def embed_text(self, text: str, metadata: Dict = None) -> DocumentEmbedding:
        """Generate vector embedding for text."""
        doc_id = str(uuid.uuid4())
        
        # Generate embedding (mock - in production use OpenAI/Cohere/etc)
        embedding = self._generate_embedding(text)
        
        doc_embedding = DocumentEmbedding(
            doc_id=doc_id,
            content=text,
            embedding=embedding,
            metadata=metadata or {},
            created_at=time.time()
        )
        
        self.embeddings[doc_id] = doc_embedding
        
        return doc_embedding
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding."""
        # In production: use OpenAI API
        # import openai
        # response = openai.Embedding.create(input=text, model=self.model)
        # return response['data'][0]['embedding']
        
        # Mock embedding
        np.random.seed(hash(text) % (2**32))
        return np.random.rand(self.dimension).tolist()
    
    def batch_embed(self, texts: List[str]) -> List[DocumentEmbedding]:
        """Batch embed multiple texts."""
        return [self.embed_text(text) for text in texts]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


class SemanticSearchEngine:
    """Semantic search across all content using vector similarity."""
    
    def __init__(self, embedding_service: VectorEmbeddingService):
        self.embedding_service = embedding_service
        self.index: Dict[str, DocumentEmbedding] = {}
    
    def index_document(self, doc_id: str, content: str, metadata: Dict = None):
        """Index document for semantic search."""
        embedding = self.embedding_service.embed_text(content, metadata)
        self.index[doc_id] = embedding
    
    def search(self, query: str, top_k: int = 10, filters: Dict = None) -> List[Dict]:
        """Perform semantic search."""
        # Generate query embedding
        query_embedding = self.embedding_service._generate_embedding(query)
        
        # Calculate similarities with all documents
        results = []
        for doc_id, doc_embedding in self.index.items():
            # Apply filters
            if filters and not self._matches_filters(doc_embedding.metadata, filters):
                continue
            
            similarity = self.embedding_service.cosine_similarity(
                query_embedding,
                doc_embedding.embedding
            )
            
            results.append({
                "doc_id": doc_id,
                "content": doc_embedding.content,
                "similarity": similarity,
                "metadata": doc_embedding.metadata
            })
        
        # Sort by similarity and return top-k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def _matches_filters(self, metadata: Dict, filters: Dict) -> bool:
        """Check if metadata matches filters."""
        for key, value in filters.items():
            if metadata.get(key) != value:
                return False
        return True
    
    def hybrid_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Combine semantic + keyword search."""
        # Semantic search
        semantic_results = self.search(query, top_k * 2)
        
        # Keyword search
        keyword_results = self._keyword_search(query, top_k * 2)
        
        # Combine with weighted scores
        combined = self._merge_results(semantic_results, keyword_results, weights=(0.7, 0.3))
        
        return combined[:top_k]
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict]:
        """Traditional keyword-based search."""
        query_terms = query.lower().split()
        results = []
        
        for doc_id, doc_embedding in self.index.items():
            content_lower = doc_embedding.content.lower()
            
            # Count matching terms
            matches = sum(1 for term in query_terms if term in content_lower)
            score = matches / len(query_terms) if query_terms else 0
            
            results.append({
                "doc_id": doc_id,
                "content": doc_embedding.content,
                "score": score,
                "metadata": doc_embedding.metadata
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _merge_results(self, semantic: List[Dict], keyword: List[Dict], weights: Tuple[float, float]) -> List[Dict]:
        """Merge search results with weighted scores."""
        doc_scores = defaultdict(lambda: {"score": 0, "doc": None})
        
        for result in semantic:
            doc_id = result["doc_id"]
            doc_scores[doc_id]["score"] += result["similarity"] * weights[0]
            doc_scores[doc_id]["doc"] = result
        
        for result in keyword:
            doc_id = result["doc_id"]
            doc_scores[doc_id]["score"] += result["score"] * weights[1]
            if not doc_scores[doc_id]["doc"]:
                doc_scores[doc_id]["doc"] = result
        
        merged = sorted(doc_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        return [item[1]["doc"] for item in merged if item[1]["doc"]]


class KnowledgeGraph:
    """Auto-build relationships between content."""
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
        self.relationships: Dict[str, List[str]] = defaultdict(list)
    
    def add_node(self, node_id: str, node_type: str, properties: Dict):
        """Add node to knowledge graph."""
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "properties": properties,
            "created_at": time.time()
        }
    
    def add_relationship(self, from_node: str, to_node: str, relationship_type: str, properties: Dict = None):
        """Add relationship between nodes."""
        edge = {
            "id": str(uuid.uuid4()),
            "from": from_node,
            "to": to_node,
            "type": relationship_type,
            "properties": properties or {},
            "weight": 1.0,
            "created_at": time.time()
        }
        
        self.edges.append(edge)
        self.relationships[from_node].append(to_node)
        
        return edge
    
    def find_path(self, start_node: str, end_node: str, max_depth: int = 5) -> Optional[List[str]]:
        """Find path between two nodes."""
        if start_node not in self.nodes or end_node not in self.nodes:
            return None
        
        # BFS to find shortest path
        queue = [(start_node, [start_node])]
        visited = {start_node}
        
        while queue:
            current, path = queue.pop(0)
            
            if current == end_node:
                return path
            
            if len(path) >= max_depth:
                continue
            
            for neighbor in self.relationships.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def find_related_nodes(self, node_id: str, depth: int = 2) -> List[Dict]:
        """Find all related nodes within depth."""
        if node_id not in self.nodes:
            return []
        
        related = []
        queue = [(node_id, 0)]
        visited = {node_id}
        
        while queue:
            current, current_depth = queue.pop(0)
            
            if current_depth >= depth:
                continue
            
            for neighbor in self.relationships.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    related.append({
                        "node": self.nodes[neighbor],
                        "depth": current_depth + 1
                    })
                    queue.append((neighbor, current_depth + 1))
        
        return related
    
    def auto_discover_relationships(self, embedding_service: VectorEmbeddingService):
        """Automatically discover relationships between nodes."""
        node_ids = list(self.nodes.keys())
        
        for i, node1_id in enumerate(node_ids):
            node1 = self.nodes[node1_id]
            
            # Get embedding for node1 content
            content1 = json.dumps(node1["properties"])
            emb1 = embedding_service._generate_embedding(content1)
            
            for node2_id in node_ids[i+1:]:
                node2 = self.nodes[node2_id]
                
                # Get embedding for node2
                content2 = json.dumps(node2["properties"])
                emb2 = embedding_service._generate_embedding(content2)
                
                # Calculate similarity
                similarity = embedding_service.cosine_similarity(emb1, emb2)
                
                # Create relationship if similar enough
                if similarity > 0.7:
                    relationship_type = self._infer_relationship_type(node1, node2)
                    self.add_relationship(
                        node1_id, 
                        node2_id, 
                        relationship_type,
                        {"similarity": similarity}
                    )
    
    def _infer_relationship_type(self, node1: Dict, node2: Dict) -> str:
        """Infer relationship type between nodes."""
        type1 = node1["type"]
        type2 = node2["type"]
        
        relationships_map = {
            ("content", "content"): "SIMILAR_TO",
            ("user", "content"): "CREATED",
            ("content", "tag"): "TAGGED_WITH",
            ("content", "category"): "BELONGS_TO",
        }
        
        return relationships_map.get((type1, type2), "RELATED_TO")
    
    def get_subgraph(self, node_id: str, depth: int = 2) -> Dict:
        """Get subgraph around a node."""
        related_nodes = self.find_related_nodes(node_id, depth)
        node_ids = {node_id} | {r["node"]["id"] for r in related_nodes}
        
        # Get edges between these nodes
        subgraph_edges = [
            e for e in self.edges 
            if e["from"] in node_ids and e["to"] in node_ids
        ]
        
        return {
            "nodes": [self.nodes[nid] for nid in node_ids],
            "edges": subgraph_edges
        }


class ConversationalSearchEngine:
    """Ask questions, get precise answers."""
    
    def __init__(self, semantic_search: SemanticSearchEngine, knowledge_graph: KnowledgeGraph):
        self.semantic_search = semantic_search
        self.knowledge_graph = knowledge_graph
        self.conversation_history: Dict[str, List[Dict]] = defaultdict(list)
    
    def ask(self, session_id: str, question: str) -> Dict:
        """Ask a question and get contextual answer."""
        # Get conversation context
        context = self.conversation_history[session_id]
        
        # Expand question with context
        expanded_query = self._expand_query_with_context(question, context)
        
        # Search for relevant information
        search_results = self.semantic_search.search(expanded_query, top_k=5)
        
        # Extract answer from results
        answer = self._extract_answer(question, search_results)
        
        # Find related information in knowledge graph
        related = self._find_related_info(answer.get("source_ids", []))
        
        # Format response
        response = {
            "answer": answer["text"],
            "confidence": answer["confidence"],
            "sources": answer["sources"],
            "related": related,
            "follow_up_questions": self._generate_follow_up_questions(question, answer)
        }
        
        # Update conversation history
        self.conversation_history[session_id].append({
            "question": question,
            "answer": response["answer"],
            "timestamp": time.time()
        })
        
        return response
    
    def _expand_query_with_context(self, question: str, context: List[Dict]) -> str:
        """Expand query using conversation context."""
        if not context:
            return question
        
        # Add context from recent conversation
        recent = context[-2:] if len(context) > 1 else context
        context_text = " ".join([f"{c['question']} {c['answer']}" for c in recent])
        
        return f"{context_text} {question}"
    
    def _extract_answer(self, question: str, search_results: List[Dict]) -> Dict:
        """Extract precise answer from search results."""
        if not search_results:
            return {
                "text": "I couldn't find relevant information to answer that question.",
                "confidence": 0.0,
                "sources": [],
                "source_ids": []
            }
        
        # Use most relevant result
        top_result = search_results[0]
        
        # Extract answer snippet (in production, use extractive QA model)
        answer_text = self._extract_snippet(question, top_result["content"])
        
        return {
            "text": answer_text,
            "confidence": top_result["similarity"],
            "sources": [{"doc_id": r["doc_id"], "title": r["metadata"].get("title", "Document")} for r in search_results[:3]],
            "source_ids": [r["doc_id"] for r in search_results]
        }
    
    def _extract_snippet(self, question: str, content: str, window: int = 200) -> str:
        """Extract relevant snippet from content."""
        # Find most relevant part of content
        # In production: use BERT-based extractive QA
        
        sentences = content.split(". ")
        question_terms = set(question.lower().split())
        
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            sentence_terms = set(sentence.lower().split())
            overlap = len(question_terms & sentence_terms)
            
            if overlap > best_score:
                best_score = overlap
                best_sentence = sentence
        
        return best_sentence if best_sentence else content[:window]
    
    def _find_related_info(self, doc_ids: List[str]) -> List[Dict]:
        """Find related information using knowledge graph."""
        related = []
        
        for doc_id in doc_ids[:3]:
            related_nodes = self.knowledge_graph.find_related_nodes(doc_id, depth=1)
            for node_info in related_nodes[:2]:
                related.append({
                    "title": node_info["node"]["properties"].get("title", "Related content"),
                    "type": node_info["node"]["type"]
                })
        
        return related
    
    def _generate_follow_up_questions(self, question: str, answer: Dict) -> List[str]:
        """Generate follow-up questions."""
        # In production: use GPT to generate contextual follow-ups
        return [
            "Can you tell me more about this?",
            "What are the related topics?",
            "How does this compare to alternatives?"
        ]


class SmartRecommendationEngine:
    """Context-aware recommendations using embeddings."""
    
    def __init__(self, embedding_service: VectorEmbeddingService, knowledge_graph: KnowledgeGraph):
        self.embedding_service = embedding_service
        self.knowledge_graph = knowledge_graph
        self.user_preferences: Dict[str, Dict] = {}
    
    def recommend_content(self, user_id: str, context: Dict = None, count: int = 10) -> List[Dict]:
        """Recommend content based on user preferences and context."""
        # Get user preference vector
        user_vector = self._get_user_preference_vector(user_id)
        
        # Get candidates
        candidates = self._get_candidate_content(user_id, context)
        
        # Score candidates
        recommendations = []
        for candidate in candidates:
            score = self._score_recommendation(user_vector, candidate, context)
            recommendations.append({
                "content_id": candidate["id"],
                "title": candidate["title"],
                "score": score,
                "reason": self._explain_recommendation(user_vector, candidate)
            })
        
        # Sort and return top N
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:count]
    
    def _get_user_preference_vector(self, user_id: str) -> List[float]:
        """Calculate user preference vector from history."""
        user_prefs = self.user_preferences.get(user_id, {})
        
        if "vector" in user_prefs:
            return user_prefs["vector"]
        
        # Calculate from user interactions
        # Average embeddings of content user engaged with
        return [0.0] * self.embedding_service.dimension
    
    def _get_candidate_content(self, user_id: str, context: Dict) -> List[Dict]:
        """Get candidate content for recommendations."""
        # Mock candidates
        return [
            {"id": "1", "title": "Content 1", "embedding": [0.1] * 1536},
            {"id": "2", "title": "Content 2", "embedding": [0.2] * 1536},
        ]
    
    def _score_recommendation(self, user_vector: List[float], candidate: Dict, context: Dict) -> float:
        """Score recommendation."""
        # Combine multiple signals
        similarity_score = self.embedding_service.cosine_similarity(user_vector, candidate["embedding"])
        
        # Context boost
        context_boost = 0.1 if context else 0.0
        
        return similarity_score + context_boost
    
    def _explain_recommendation(self, user_vector: List[float], candidate: Dict) -> str:
        """Explain why content was recommended."""
        return "Based on your interests and recent activity"
