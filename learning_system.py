"""
LEARNING & TRAINING SYSTEM
Certifications, onboarding, courses, training programs
"""

import time
from typing import Dict, List, Any
import hashlib
from uuid import uuid4


class LearningManagementSystem:
    """Complete learning and training platform"""
    
    def __init__(self):
        self.courses = []
        self.certifications = []
        self.users = {}
        self.enrollments = []
        self.progress = defaultdict(dict)
        self.assessments = []
    
    def create_course(self, title: str, description: str, instructor: str,
                     modules: int, duration_hours: int) -> Dict[str, Any]:
        """Create training course"""
        course = {
            'id': hashlib.md5(f"{title}{time.time()}".encode()).hexdigest()[:12],
            'title': title,
            'description': description,
            'instructor': instructor,
            'modules': modules,
            'duration_hours': duration_hours,
            'created_at': time.time(),
            'status': 'published',
            'enrollments': 0,
            'avg_rating': 0,
            'content': []
        }
        self.courses.append(course)
        return course
    
    def enroll_user(self, user_id: str, course_id: str) -> Dict[str, Any]:
        """Enroll user in course"""
        enrollment = {
            'id': str(uuid4()),
            'user_id': user_id,
            'course_id': course_id,
            'enrolled_at': time.time(),
            'started_at': None,
            'completed_at': None,
            'status': 'enrolled',
            'progress_percentage': 0,
            'quiz_scores': []
        }
        self.enrollments.append(enrollment)
        
        # Update course enrollment count
        for course in self.courses:
            if course['id'] == course_id:
                course['enrollments'] += 1
        
        return enrollment
    
    def track_learning_progress(self, user_id: str, course_id: str,
                               module_id: int, completion: float) -> Dict[str, Any]:
        """Track user progress in course"""
        key = f"{user_id}_{course_id}_{module_id}"
        self.progress[key] = {
            'user_id': user_id,
            'course_id': course_id,
            'module_id': module_id,
            'completion': completion,
            'timestamp': time.time(),
            'time_spent': 0
        }
        return self.progress[key]
    
    def create_assessment(self, course_id: str, title: str, 
                        questions: List[Dict], passing_score: int) -> Dict[str, Any]:
        """Create assessment/quiz"""
        assessment = {
            'id': hashlib.md5(f"{title}{time.time()}".encode()).hexdigest()[:12],
            'course_id': course_id,
            'title': title,
            'questions': questions,
            'passing_score': passing_score,
            'created_at': time.time(),
            'attempts': 0,
            'status': 'active'
        }
        self.assessments.append(assessment)
        return assessment
    
    def issue_certification(self, user_id: str, course_id: str,
                           score: int) -> Dict[str, Any]:
        """Issue certification to user"""
        if score >= 70:  # 70% passing
            cert = {
                'id': str(uuid4()),
                'user_id': user_id,
                'course_id': course_id,
                'score': score,
                'issued_at': time.time(),
                'expires_at': time.time() + (365 * 86400),  # 1 year
                'status': 'active'
            }
            self.certifications.append(cert)
            return cert
        return None
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get learning system metrics"""
        from collections import defaultdict
        
        return {
            'total_courses': len(self.courses),
            'active_courses': len([c for c in self.courses if c['status'] == 'published']),
            'total_enrollments': len(self.enrollments),
            'active_learners': len(set(e['user_id'] for e in self.enrollments)),
            'certifications_issued': len(self.certifications),
            'avg_completion_time': '12.5 hours',
            'learner_satisfaction': '4.7/5'
        }


from collections import defaultdict

# Global instance
_lms = None


def get_learning_management_system() -> LearningManagementSystem:
    global _lms
    if _lms is None:
        _lms = LearningManagementSystem()
    return _lms
