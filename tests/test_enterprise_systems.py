"""
Tests for Enterprise Systems (Compliance, Governance, Knowledge, Access Control, Mobile, Learning)
"""

import pytest
import time
from enterprise_systems import (
    get_compliance_engine, get_governance_engine, get_knowledge_base, get_access_control
)
from mobile_and_global import get_mobile_api_manager, get_global_operations
from learning_system import get_learning_management_system


class TestComplianceEngine:
    
    def test_create_policy(self):
        compliance = get_compliance_engine()
        policy = compliance.create_policy(
            'Data Privacy',
            'data_privacy',
            'Must comply with GDPR and CCPA',
            time.time(),
            'CEO'
        )
        assert policy['name'] == 'Data Privacy'
        assert policy['status'] == 'active'
    
    def test_log_compliance_check(self):
        compliance = get_compliance_engine()
        record = compliance.log_compliance_check(
            'GDPR Audit',
            'pass',
            {'items_checked': 15, 'passed': 15},
            'auditor@company.com'
        )
        assert record['status'] == 'pass'
    
    def test_track_regulation(self):
        compliance = get_compliance_engine()
        reg = compliance.track_regulation(
            'GDPR',
            'EU',
            time.time() + 86400,
            ['Data Protection', 'User Consent']
        )
        assert reg['status'] == 'pending'
    
    def test_compliance_status(self):
        compliance = get_compliance_engine()
        status = compliance.get_compliance_status()
        assert 'total_policies' in status
        assert 'compliance_percentage' in status


class TestGovernanceEngine:
    
    def test_create_decision(self):
        governance = get_governance_engine()
        decision = governance.create_decision(
            'Launch New Feature',
            'Enable recommendation engine',
            'high',
            'product@company.com',
            time.time() + 86400
        )
        assert decision['status'] == 'pending'
    
    def test_approve_decision(self):
        governance = get_governance_engine()
        decision = governance.create_decision(
            'Test Decision',
            'Test',
            'medium',
            'user@company.com',
            time.time() + 86400
        )
        
        approval = governance.approve_decision(
            decision['id'],
            'approver@company.com',
            'approve',
            'Looks good'
        )
        assert approval['type'] == 'approve'
    
    def test_governance_metrics(self):
        governance = get_governance_engine()
        metrics = governance.get_governance_metrics()
        assert 'total_decisions' in metrics
        assert 'governance_health' in metrics


class TestKnowledgeBase:
    
    def test_create_article(self):
        kb = get_knowledge_base()
        article = kb.create_article(
            'Getting Started with API',
            'Complete guide to API usage',
            'tutorials',
            'docs@company.com',
            ['api', 'tutorial', 'beginner']
        )
        assert article['title'] == 'Getting Started with API'
        assert article['status'] == 'published'
    
    def test_search_knowledge_base(self):
        kb = get_knowledge_base()
        kb.create_article(
            'Python Basics',
            'Introduction to Python programming',
            'tutorials',
            'docs@company.com',
            ['python', 'basics']
        )
        
        results = kb.search_knowledge_base('Python')
        assert len(results) > 0
    
    def test_rate_article(self):
        kb = get_knowledge_base()
        article = kb.create_article(
            'Test Article',
            'Content',
            'tutorials',
            'docs@company.com',
            ['test']
        )
        
        kb.rate_article(article['id'], 5, 'user@company.com')
        assert article['helpful'] == 1


class TestAccessControl:
    
    def test_create_role(self):
        access = get_access_control()
        role = access.create_role(
            'Admin',
            ['read', 'write', 'delete', 'manage_users'],
            'Full system access'
        )
        assert 'manage_users' in role['permissions']
    
    def test_assign_role(self):
        access = get_access_control()
        role = access.create_role(
            'Viewer',
            ['read'],
            'Read-only access'
        )
        
        assignment = access.assign_role('user123', role['id'])
        assert assignment['status'] == 'active'
    
    def test_check_permission(self):
        access = get_access_control()
        role = access.create_role(
            'Editor',
            ['read', 'write'],
            'Edit content'
        )
        
        access.assign_role('user456', role['id'])
        assert access.check_permission('user456', 'write') == True
        assert access.check_permission('user456', 'delete') == False


class TestMobileAPI:
    
    def test_create_api_key(self):
        mobile = get_mobile_api_manager()
        key = mobile.create_api_key(
            'MyApp iOS',
            'ios',
            'com.company.myapp'
        )
        assert key['app_type'] == 'ios'
        assert key['status'] == 'active'
    
    def test_authenticate_session(self):
        mobile = get_mobile_api_manager()
        key = mobile.create_api_key('TestApp', 'ios', 'test.bundle')
        
        session = mobile.authenticate_session(
            key['key_id'],
            'device_123',
            'user_456'
        )
        assert session['status'] == 'active'
    
    def test_log_request(self):
        mobile = get_mobile_api_manager()
        key = mobile.create_api_key('TestApp', 'ios', 'test')
        session = mobile.authenticate_session(key['key_id'], 'device', 'user')
        
        log = mobile.log_request(
            session['session_id'],
            '/api/user/profile',
            'GET',
            200,
            0.234
        )
        assert log['status_code'] == 200


class TestGlobalOperations:
    
    def test_register_region(self):
        global_ops = get_global_operations()
        region = global_ops.register_region(
            'US-EAST',
            'United States East',
            'America/New_York',
            ['CCPA', 'SOX']
        )
        assert region['status'] == 'active'
    
    def test_add_language_support(self):
        global_ops = get_global_operations()
        lang = global_ops.add_language_support(
            'es',
            'Spanish',
            rtl=False
        )
        assert lang['code'] == 'es'


class TestLearningManagementSystem:
    
    def test_create_course(self):
        lms = get_learning_management_system()
        course = lms.create_course(
            'Python Advanced',
            'Advanced Python programming',
            'instructor@company.com',
            12,
            40
        )
        assert course['title'] == 'Python Advanced'
        assert course['status'] == 'published'
    
    def test_enroll_user(self):
        lms = get_learning_management_system()
        course = lms.create_course(
            'Test Course',
            'Test',
            'instructor@company.com',
            5,
            20
        )
        
        enrollment = lms.enroll_user('student123', course['id'])
        assert enrollment['status'] == 'enrolled'
    
    def test_track_progress(self):
        lms = get_learning_management_system()
        course = lms.create_course(
            'Learn AI',
            'AI fundamentals',
            'instructor@company.com',
            8,
            30
        )
        
        progress = lms.track_learning_progress(
            'student123',
            course['id'],
            1,
            45.5
        )
        assert progress['completion'] == 45.5
    
    def test_issue_certification(self):
        lms = get_learning_management_system()
        course = lms.create_course(
            'Certification Course',
            'Get certified',
            'instructor@company.com',
            10,
            50
        )
        
        cert = lms.issue_certification('student456', course['id'], 85)
        assert cert is not None
        assert cert['status'] == 'active'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
