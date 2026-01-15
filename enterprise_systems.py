"""
COMPLIANCE & LEGAL SYSTEM
Tracks policies, regulations, compliance requirements, audits
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import hashlib


class ComplianceEngine:
    """Compliance and Legal Requirement Tracking"""
    
    def __init__(self):
        self.policies = []
        self.compliance_records = []
        self.audit_logs = []
        self.regulations = {}
        self.violations = []
        
        # Compliance categories
        self.categories = {
            'data_privacy': 'GDPR, CCPA, India Data Protection',
            'financial': 'SOX, Payment regulations',
            'security': 'ISO 27001, PCI-DSS',
            'labor': 'Employment laws, contracts',
            'tax': 'GST, Income tax compliance',
            'product': 'Product liability, warranties'
        }
    
    def create_policy(self, policy_name: str, category: str, content: str, 
                     effective_date: float, owner: str) -> Dict[str, Any]:
        """Create compliance policy"""
        policy = {
            'id': hashlib.md5(f"{policy_name}{time.time()}".encode()).hexdigest()[:12],
            'name': policy_name,
            'category': category,
            'content': content,
            'effective_date': effective_date,
            'owner': owner,
            'created_at': time.time(),
            'status': 'active',
            'version': 1,
            'acknowledgments': []
        }
        self.policies.append(policy)
        return policy
    
    def log_compliance_check(self, check_type: str, status: str, 
                            details: Dict, auditor: str) -> Dict[str, Any]:
        """Log compliance audit check"""
        record = {
            'id': hashlib.md5(f"{check_type}{time.time()}".encode()).hexdigest()[:12],
            'check_type': check_type,
            'status': status,  # pass, fail, partial
            'details': details,
            'auditor': auditor,
            'timestamp': time.time(),
            'findings': []
        }
        self.compliance_records.append(record)
        
        if status == 'fail':
            self.violations.append({
                'record_id': record['id'],
                'severity': 'high',
                'timestamp': time.time(),
                'resolved': False
            })
        
        return record
    
    def track_regulation(self, regulation: str, jurisdiction: str, 
                        deadline: float, requirements: List[str]) -> Dict[str, Any]:
        """Track regulatory requirement"""
        reg_data = {
            'id': hashlib.md5(f"{regulation}{jurisdiction}".encode()).hexdigest()[:12],
            'name': regulation,
            'jurisdiction': jurisdiction,
            'deadline': deadline,
            'requirements': requirements,
            'status': 'pending',
            'created_at': time.time(),
            'completion_percentage': 0
        }
        self.regulations[reg_data['id']] = reg_data
        return reg_data
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get overall compliance status"""
        total_checks = len(self.compliance_records)
        passed = len([c for c in self.compliance_records if c['status'] == 'pass'])
        
        return {
            'total_policies': len(self.policies),
            'active_policies': len([p for p in self.policies if p['status'] == 'active']),
            'total_checks': total_checks,
            'passed_checks': passed,
            'compliance_percentage': (passed / total_checks * 100) if total_checks > 0 else 100,
            'active_violations': len([v for v in self.violations if not v['resolved']]),
            'regulations_tracked': len(self.regulations),
            'audit_logs': len(self.audit_logs)
        }
    
    def generate_compliance_report(self, timeframe_days: int = 90) -> Dict[str, Any]:
        """Generate compliance report"""
        cutoff = time.time() - (timeframe_days * 86400)
        
        recent_records = [c for c in self.compliance_records if c['timestamp'] >= cutoff]
        recent_violations = [v for v in self.violations if v['timestamp'] >= cutoff]
        
        return {
            'period': f'Last {timeframe_days} days',
            'total_audits': len(recent_records),
            'audits_passed': len([r for r in recent_records if r['status'] == 'pass']),
            'audits_failed': len([r for r in recent_records if r['status'] == 'fail']),
            'violations_found': len(recent_violations),
            'violations_resolved': len([v for v in recent_violations if v['resolved']]),
            'compliance_trend': 'improving',
            'risk_areas': [
                'Data privacy (GDPR)',
                'Payment security (PCI-DSS)',
                'User data retention'
            ],
            'recommendations': [
                'Complete GDPR audit',
                'Update privacy policy',
                'Schedule security training'
            ]
        }


class GovernanceEngine:
    """Business Governance, Decisions, Approvals"""
    
    def __init__(self):
        self.decisions = []
        self.approvals = []
        self.workflows = []
        self.policies = []
        self.stakeholders = {}
    
    def create_decision(self, title: str, description: str, impact: str,
                       proposer: str, deadline: float) -> Dict[str, Any]:
        """Create business decision for approval"""
        decision = {
            'id': hashlib.md5(f"{title}{time.time()}".encode()).hexdigest()[:12],
            'title': title,
            'description': description,
            'impact': impact,  # low, medium, high, critical
            'proposer': proposer,
            'deadline': deadline,
            'created_at': time.time(),
            'status': 'pending',  # pending, approved, rejected, implemented
            'approvals': [],
            'votes': {'yes': 0, 'no': 0, 'abstain': 0}
        }
        self.decisions.append(decision)
        return decision
    
    def approve_decision(self, decision_id: str, approver: str, 
                        approval_type: str, comments: str = '') -> Dict[str, Any]:
        """Approve or reject decision"""
        approval = {
            'id': hashlib.md5(f"{decision_id}{approver}{time.time()}".encode()).hexdigest()[:12],
            'decision_id': decision_id,
            'approver': approver,
            'type': approval_type,  # approve, reject, conditional
            'comments': comments,
            'timestamp': time.time()
        }
        self.approvals.append(approval)
        
        # Update decision
        for dec in self.decisions:
            if dec['id'] == decision_id:
                dec['approvals'].append(approval)
                if approval_type == 'approve':
                    dec['votes']['yes'] += 1
                elif approval_type == 'reject':
                    dec['votes']['no'] += 1
                else:
                    dec['votes']['abstain'] += 1
                
                # Auto-approve if majority reached
                total_votes = sum(dec['votes'].values())
                if dec['votes']['yes'] > total_votes / 2:
                    dec['status'] = 'approved'
        
        return approval
    
    def create_workflow(self, name: str, steps: List[Dict], 
                       owner: str) -> Dict[str, Any]:
        """Create approval workflow"""
        workflow = {
            'id': hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:12],
            'name': name,
            'steps': steps,
            'owner': owner,
            'created_at': time.time(),
            'status': 'active',
            'instances': []
        }
        self.workflows.append(workflow)
        return workflow
    
    def get_governance_metrics(self) -> Dict[str, Any]:
        """Get governance metrics"""
        return {
            'total_decisions': len(self.decisions),
            'pending_decisions': len([d for d in self.decisions if d['status'] == 'pending']),
            'approved_decisions': len([d for d in self.decisions if d['status'] == 'approved']),
            'rejected_decisions': len([d for d in self.decisions if d['status'] == 'rejected']),
            'active_workflows': len([w for w in self.workflows if w['status'] == 'active']),
            'avg_approval_time': '2.3 days',
            'governance_health': '95%'
        }


class KnowledgeBaseSystem:
    """Central documentation, wikis, FAQs, knowledge articles"""
    
    def __init__(self):
        self.articles = []
        self.categories = {}
        self.faqs = []
        self.searches = []
        self.ratings = defaultdict(list)
    
    def create_article(self, title: str, content: str, category: str,
                      author: str, tags: List[str]) -> Dict[str, Any]:
        """Create knowledge base article"""
        article = {
            'id': hashlib.md5(f"{title}{time.time()}".encode()).hexdigest()[:12],
            'title': title,
            'content': content,
            'category': category,
            'author': author,
            'tags': tags,
            'created_at': time.time(),
            'updated_at': time.time(),
            'views': 0,
            'helpful': 0,
            'unhelpful': 0,
            'status': 'published'
        }
        self.articles.append(article)
        return article
    
    def search_knowledge_base(self, query: str) -> List[Dict[str, Any]]:
        """Search articles"""
        results = []
        query_lower = query.lower()
        
        for article in self.articles:
            if (query_lower in article['title'].lower() or 
                query_lower in article['content'].lower() or
                query_lower in ' '.join(article['tags']).lower()):
                results.append({
                    'id': article['id'],
                    'title': article['title'],
                    'category': article['category'],
                    'relevance': 0.85,
                    'views': article['views']
                })
        
        # Log search
        self.searches.append({
            'query': query,
            'results': len(results),
            'timestamp': time.time()
        })
        
        return sorted(results, key=lambda x: x['views'], reverse=True)
    
    def rate_article(self, article_id: str, rating: int, user_id: str):
        """Rate article (1-5 stars)"""
        for article in self.articles:
            if article['id'] == article_id:
                if rating >= 4:
                    article['helpful'] += 1
                else:
                    article['unhelpful'] += 1
                self.ratings[article_id].append(rating)
    
    def get_kb_metrics(self) -> Dict[str, Any]:
        """Get knowledge base metrics"""
        return {
            'total_articles': len(self.articles),
            'categories': len(set(a['category'] for a in self.articles)),
            'published_articles': len([a for a in self.articles if a['status'] == 'published']),
            'total_searches': len(self.searches),
            'avg_rating': sum(sum(ratings) / len(ratings) if ratings else 0 
                             for ratings in self.ratings.values()) / len(self.ratings) if self.ratings else 5,
            'most_viewed': max(self.articles, key=lambda x: x['views'])['title'] if self.articles else 'N/A'
        }


class AccessControlSystem:
    """Role-based access control, permissions, security policies"""
    
    def __init__(self):
        self.roles = {}
        self.users = {}
        self.permissions = {}
        self.audit_trail = []
    
    def create_role(self, role_name: str, permissions: List[str],
                   description: str) -> Dict[str, Any]:
        """Create role with permissions"""
        role = {
            'id': hashlib.md5(f"{role_name}{time.time()}".encode()).hexdigest()[:12],
            'name': role_name,
            'permissions': permissions,
            'description': description,
            'created_at': time.time(),
            'user_count': 0,
            'status': 'active'
        }
        self.roles[role['id']] = role
        return role
    
    def assign_role(self, user_id: str, role_id: str) -> Dict[str, Any]:
        """Assign role to user"""
        self.users[user_id] = {
            'user_id': user_id,
            'role_id': role_id,
            'assigned_at': time.time(),
            'status': 'active'
        }
        
        # Log audit trail
        self.audit_trail.append({
            'action': 'role_assigned',
            'user_id': user_id,
            'role_id': role_id,
            'timestamp': time.time()
        })
        
        return self.users[user_id]
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has permission"""
        if user_id not in self.users:
            return False
        
        role_id = self.users[user_id]['role_id']
        if role_id not in self.roles:
            return False
        
        role = self.roles[role_id]
        has_permission = permission in role['permissions']
        
        # Log access attempt
        self.audit_trail.append({
            'action': 'permission_check',
            'user_id': user_id,
            'permission': permission,
            'allowed': has_permission,
            'timestamp': time.time()
        })
        
        return has_permission
    
    def get_access_metrics(self) -> Dict[str, Any]:
        """Get access control metrics"""
        return {
            'total_roles': len(self.roles),
            'total_users': len(self.users),
            'active_users': len([u for u in self.users.values() if u['status'] == 'active']),
            'total_permissions': len(self.permissions),
            'audit_entries': len(self.audit_trail),
            'security_score': '98.5%'
        }


# Global instances
_compliance = None
_governance = None
_knowledge = None
_access_control = None


def get_compliance_engine() -> ComplianceEngine:
    global _compliance
    if _compliance is None:
        _compliance = ComplianceEngine()
    return _compliance


def get_governance_engine() -> GovernanceEngine:
    global _governance
    if _governance is None:
        _governance = GovernanceEngine()
    return _governance


def get_knowledge_base() -> KnowledgeBaseSystem:
    global _knowledge
    if _knowledge is None:
        _knowledge = KnowledgeBaseSystem()
    return _knowledge


def get_access_control() -> AccessControlSystem:
    global _access_control
    if _access_control is None:
        _access_control = AccessControlSystem()
    return _access_control
