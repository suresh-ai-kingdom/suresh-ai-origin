"""
Real-Time Collaboration Engine - Week 9 Ultra-Rare Tier
Live co-editing with AI, multi-user sessions, collaborative workflows
"""

import json
import time
import uuid
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib


@dataclass
class CollaborativeSession:
    """Real-time collaborative session."""
    session_id: str
    document_id: str
    participants: Set[str] = field(default_factory=set)
    ai_participants: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    shared_context: Dict = field(default_factory=dict)


@dataclass
class Operation:
    """Operational transformation for real-time editing."""
    op_id: str
    session_id: str
    user_id: str
    op_type: str  # "insert", "delete", "update"
    position: int
    content: str
    timestamp: float
    version: int


class CollaborativeEditEngine:
    """Real-time co-editing with conflict resolution."""
    
    def __init__(self):
        self.sessions: Dict[str, CollaborativeSession] = {}
        self.documents: Dict[str, str] = {}
        self.operation_history: Dict[str, List[Operation]] = defaultdict(list)
        self.version_vectors: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    def create_session(self, document_id: str, creator_id: str, with_ai: bool = True) -> CollaborativeSession:
        """Create collaborative editing session."""
        session = CollaborativeSession(
            session_id=str(uuid.uuid4()),
            document_id=document_id,
            participants={creator_id}
        )
        
        if with_ai:
            ai_id = f"ai_assistant_{uuid.uuid4().hex[:8]}"
            session.ai_participants.add(ai_id)
        
        self.sessions[session.session_id] = session
        
        # Initialize document if needed
        if document_id not in self.documents:
            self.documents[document_id] = ""
        
        return session
    
    def join_session(self, session_id: str, user_id: str) -> Dict:
        """User joins collaborative session."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.participants.add(user_id)
        session.last_activity = time.time()
        
        return {
            "session": session,
            "current_content": self.documents[session.document_id],
            "participants": list(session.participants),
            "ai_assistants": list(session.ai_participants)
        }
    
    def apply_operation(self, session_id: str, user_id: str, op_type: str, position: int, content: str) -> Dict:
        """Apply operation with operational transformation."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Create operation
        operation = Operation(
            op_id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            op_type=op_type,
            position=position,
            content=content,
            timestamp=time.time(),
            version=self.version_vectors[session_id][user_id]
        )
        
        # Transform against concurrent operations
        transformed_op = self._transform_operation(operation, session_id)
        
        # Apply to document
        self._apply_to_document(session.document_id, transformed_op)
        
        # Record operation
        self.operation_history[session_id].append(transformed_op)
        self.version_vectors[session_id][user_id] += 1
        
        # Broadcast to participants (in production: WebSocket)
        return {
            "operation": transformed_op,
            "new_content": self.documents[session.document_id],
            "version": self.version_vectors[session_id][user_id]
        }
    
    def _transform_operation(self, operation: Operation, session_id: str) -> Operation:
        """Operational transformation for conflict resolution."""
        # Get concurrent operations
        concurrent_ops = [
            op for op in self.operation_history[session_id]
            if op.timestamp > operation.timestamp - 0.1  # 100ms window
            and op.user_id != operation.user_id
        ]
        
        transformed_op = operation
        
        for concurrent_op in concurrent_ops:
            if concurrent_op.position <= operation.position:
                if concurrent_op.op_type == "insert":
                    # Shift position right
                    transformed_op.position += len(concurrent_op.content)
                elif concurrent_op.op_type == "delete":
                    # Shift position left
                    transformed_op.position -= len(concurrent_op.content)
        
        return transformed_op
    
    def _apply_to_document(self, document_id: str, operation: Operation):
        """Apply operation to document."""
        content = self.documents[document_id]
        
        if operation.op_type == "insert":
            self.documents[document_id] = (
                content[:operation.position] + 
                operation.content + 
                content[operation.position:]
            )
        elif operation.op_type == "delete":
            self.documents[document_id] = (
                content[:operation.position] + 
                content[operation.position + len(operation.content):]
            )
        elif operation.op_type == "update":
            # Replace at position
            self.documents[document_id] = (
                content[:operation.position] + 
                operation.content + 
                content[operation.position + len(operation.content):]
            )


class MultiUserAISession:
    """Shared AI context across multiple users."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.shared_memory: Dict[str, List[Dict]] = defaultdict(list)
    
    def create_shared_session(self, team_id: str, members: List[str]) -> str:
        """Create shared AI session for team."""
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "team_id": team_id,
            "members": set(members),
            "shared_context": {},
            "conversation_threads": defaultdict(list),
            "created_at": time.time()
        }
        
        return session_id
    
    def add_to_shared_context(self, session_id: str, user_id: str, message: str, ai_response: str):
        """Add to shared conversation context."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Add to shared memory
        interaction = {
            "user_id": user_id,
            "message": message,
            "ai_response": ai_response,
            "timestamp": time.time(),
            "visible_to": list(session["members"])
        }
        
        self.shared_memory[session_id].append(interaction)
        
        # Update shared context
        session["shared_context"][user_id] = {
            "last_query": message,
            "last_response": ai_response
        }
    
    def get_team_context(self, session_id: str) -> Dict:
        """Get full team conversation context."""
        return {
            "shared_memory": self.shared_memory[session_id],
            "session_info": self.sessions[session_id],
            "context_summary": self._summarize_context(session_id)
        }
    
    def _summarize_context(self, session_id: str) -> str:
        """Summarize team conversation for AI context."""
        memory = self.shared_memory[session_id]
        
        if not memory:
            return "No previous context"
        
        # Recent interactions
        recent = memory[-5:] if len(memory) > 5 else memory
        
        summary = "Team conversation context:\n"
        for interaction in recent:
            summary += f"- {interaction['user_id']}: {interaction['message'][:100]}...\n"
        
        return summary


class CollaborativeWorkflowEngine:
    """Multi-user workflows with branching and merging."""
    
    def __init__(self):
        self.workflows: Dict[str, Dict] = {}
        self.branches: Dict[str, List[Dict]] = defaultdict(list)
    
    def create_workflow(self, workflow_name: str, owner_id: str, steps: List[Dict]) -> str:
        """Create collaborative workflow."""
        workflow_id = str(uuid.uuid4())
        
        self.workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "name": workflow_name,
            "owner_id": owner_id,
            "collaborators": {owner_id},
            "main_branch": {
                "steps": steps,
                "version": 1,
                "updated_at": time.time()
            },
            "created_at": time.time()
        }
        
        return workflow_id
    
    def create_branch(self, workflow_id: str, user_id: str, branch_name: str) -> str:
        """Create workflow branch for experimentation."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        branch_id = str(uuid.uuid4())
        
        branch = {
            "branch_id": branch_id,
            "branch_name": branch_name,
            "workflow_id": workflow_id,
            "created_by": user_id,
            "based_on_version": workflow["main_branch"]["version"],
            "steps": workflow["main_branch"]["steps"].copy(),
            "modifications": [],
            "created_at": time.time()
        }
        
        self.branches[workflow_id].append(branch)
        
        return branch_id
    
    def modify_branch(self, workflow_id: str, branch_id: str, modifications: List[Dict]):
        """Modify workflow branch."""
        branches = self.branches[workflow_id]
        branch = next((b for b in branches if b["branch_id"] == branch_id), None)
        
        if not branch:
            raise ValueError(f"Branch {branch_id} not found")
        
        for mod in modifications:
            if mod["action"] == "add_step":
                branch["steps"].append(mod["step"])
            elif mod["action"] == "remove_step":
                branch["steps"] = [s for s in branch["steps"] if s.get("id") != mod["step_id"]]
            elif mod["action"] == "update_step":
                for i, step in enumerate(branch["steps"]):
                    if step.get("id") == mod["step_id"]:
                        branch["steps"][i] = mod["step"]
            
            branch["modifications"].append(mod)
    
    def merge_branch(self, workflow_id: str, branch_id: str, strategy: str = "auto") -> Dict:
        """Merge branch back to main workflow."""
        workflow = self.workflows[workflow_id]
        branches = self.branches[workflow_id]
        branch = next((b for b in branches if b["branch_id"] == branch_id), None)
        
        if not branch:
            raise ValueError(f"Branch {branch_id} not found")
        
        # Detect conflicts
        conflicts = self._detect_conflicts(workflow, branch)
        
        if conflicts and strategy == "auto":
            return {
                "status": "conflict",
                "conflicts": conflicts,
                "requires_manual_resolution": True
            }
        
        # Auto-merge (3-way merge)
        merged_steps = self._three_way_merge(
            workflow["main_branch"]["steps"],
            branch["steps"],
            []  # Base version
        )
        
        # Update main branch
        workflow["main_branch"]["steps"] = merged_steps
        workflow["main_branch"]["version"] += 1
        workflow["main_branch"]["updated_at"] = time.time()
        
        return {
            "status": "merged",
            "new_version": workflow["main_branch"]["version"],
            "merged_steps": len(merged_steps)
        }
    
    def _detect_conflicts(self, workflow: Dict, branch: Dict) -> List[Dict]:
        """Detect merge conflicts."""
        conflicts = []
        main_steps = {s.get("id"): s for s in workflow["main_branch"]["steps"]}
        branch_steps = {s.get("id"): s for s in branch["steps"]}
        
        # Check for conflicting modifications
        for step_id, branch_step in branch_steps.items():
            if step_id in main_steps:
                main_step = main_steps[step_id]
                if main_step != branch_step:
                    conflicts.append({
                        "step_id": step_id,
                        "main_version": main_step,
                        "branch_version": branch_step
                    })
        
        return conflicts
    
    def _three_way_merge(self, main: List[Dict], branch: List[Dict], base: List[Dict]) -> List[Dict]:
        """Three-way merge algorithm."""
        # Simple merge: take all unique steps from both branches
        merged = []
        step_ids = set()
        
        for step in main + branch:
            step_id = step.get("id", str(uuid.uuid4()))
            if step_id not in step_ids:
                merged.append(step)
                step_ids.add(step_id)
        
        return merged


class TeamKnowledgeBase:
    """Shared knowledge base for teams."""
    
    def __init__(self):
        self.knowledge_bases: Dict[str, Dict] = {}
        self.documents: Dict[str, List[Dict]] = defaultdict(list)
    
    def create_knowledge_base(self, team_id: str, name: str) -> str:
        """Create team knowledge base."""
        kb_id = str(uuid.uuid4())
        
        self.knowledge_bases[kb_id] = {
            "kb_id": kb_id,
            "team_id": team_id,
            "name": name,
            "members": set(),
            "created_at": time.time(),
            "categories": []
        }
        
        return kb_id
    
    def add_document(self, kb_id: str, title: str, content: str, author_id: str, tags: List[str] = None):
        """Add document to knowledge base."""
        doc = {
            "doc_id": str(uuid.uuid4()),
            "kb_id": kb_id,
            "title": title,
            "content": content,
            "author_id": author_id,
            "tags": tags or [],
            "created_at": time.time(),
            "updated_at": time.time(),
            "version": 1,
            "views": 0,
            "likes": 0
        }
        
        self.documents[kb_id].append(doc)
        
        return doc["doc_id"]
    
    def search_knowledge_base(self, kb_id: str, query: str) -> List[Dict]:
        """Search team knowledge base."""
        docs = self.documents[kb_id]
        query_terms = query.lower().split()
        
        results = []
        for doc in docs:
            # Simple keyword matching
            content_lower = (doc["title"] + " " + doc["content"]).lower()
            matches = sum(1 for term in query_terms if term in content_lower)
            
            if matches > 0:
                results.append({
                    "doc_id": doc["doc_id"],
                    "title": doc["title"],
                    "relevance": matches / len(query_terms),
                    "snippet": doc["content"][:200]
                })
        
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results


class ConflictResolver:
    """Intelligent conflict resolution for collaborative editing."""
    
    def resolve_conflict(self, conflict: Dict, strategy: str = "ai_suggest") -> Dict:
        """Resolve editing conflict."""
        if strategy == "ai_suggest":
            return self._ai_resolve(conflict)
        elif strategy == "keep_both":
            return self._keep_both_versions(conflict)
        elif strategy == "manual":
            return {"resolution": "manual_required", "conflict": conflict}
    
    def _ai_resolve(self, conflict: Dict) -> Dict:
        """AI-powered conflict resolution."""
        # Analyze both versions
        version_a = conflict.get("version_a", {})
        version_b = conflict.get("version_b", {})
        
        # Mock AI decision (in production: use LLM to merge intelligently)
        return {
            "resolution": "ai_merged",
            "merged_content": f"{version_a.get('content', '')} {version_b.get('content', '')}",
            "confidence": 0.85,
            "explanation": "Combined both versions preserving unique content from each"
        }
    
    def _keep_both_versions(self, conflict: Dict) -> Dict:
        """Keep both versions side-by-side."""
        return {
            "resolution": "both_kept",
            "version_a": conflict["version_a"],
            "version_b": conflict["version_b"],
            "requires_user_choice": True
        }
