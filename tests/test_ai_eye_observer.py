"""
Tests for AI Eye Observer System
"""

import pytest
import time
from ai_eye_observer import (
    get_ai_eye,
    observe_all_systems,
    get_live_dashboard_data,
    track_user_activity,
    track_payment,
    create_system_alert
)


class TestAIEyeObserver:
    """Test AI Eye observation system"""
    
    def test_ai_eye_singleton(self):
        """Test that AI Eye is a singleton"""
        eye1 = get_ai_eye()
        eye2 = get_ai_eye()
        assert eye1 is eye2
    
    def test_observe_all_systems(self, cleanup_db):
        """Test complete system observation"""
        observations = observe_all_systems(timeframe_minutes=60)
        
        # Check structure
        assert 'timestamp' in observations
        assert 'timeframe_minutes' in observations
        assert 'overview' in observations
        assert 'user_activity' in observations
        assert 'transactions' in observations
        assert 'ai_operations' in observations
        assert 'system_health' in observations
        assert 'security' in observations
        assert 'anomalies' in observations
        assert 'predictions' in observations
        assert 'insights' in observations
        
        # Check overview data
        overview = observations['overview']
        assert 'health_score' in overview
        assert 'total_observations' in overview
        assert 'active_alerts' in overview
        assert overview['status'] == 'operational'
    
    def test_user_activity_observation(self, cleanup_db):
        """Test user activity tracking"""
        observations = observe_all_systems(timeframe_minutes=60)
        
        user_activity = observations['user_activity']
        assert 'total_users' in user_activity
        assert 'new_users_timeframe' in user_activity
        assert 'active_users' in user_activity
        assert 'top_active_users' in user_activity
        assert 'signup_velocity' in user_activity
    
    def test_transaction_observation(self, cleanup_db):
        """Test transaction monitoring"""
        observations = observe_all_systems(timeframe_minutes=60)
        
        transactions = observations['transactions']
        assert 'total_transactions' in transactions
        assert 'successful' in transactions
        assert 'failed' in transactions
        assert 'pending' in transactions
        assert 'total_amount_paise' in transactions
        assert 'transaction_velocity' in transactions
    
    def test_ai_operations_observation(self, cleanup_db):
        """Test AI operations monitoring"""
        observations = observe_all_systems(timeframe_minutes=60)
        
        ai_ops = observations['ai_operations']
        assert 'total_ai_calls' in ai_ops
        assert 'ai_systems_active' in ai_ops
        assert ai_ops['ai_systems_active'] == 20
        assert 'operations' in ai_ops
        assert 'performance' in ai_ops
    
    def test_system_health_observation(self, cleanup_db):
        """Test system health monitoring"""
        observations = observe_all_systems(timeframe_minutes=60)
        
        health = observations['system_health']
        assert 'overall_health' in health
        assert 'status' in health
        assert 'components' in health
        assert 'resources' in health
        
        # Check components
        components = health['components']
        assert 'database' in components
        assert 'api' in components
        assert 'ai_service' in components
        assert 'payment_gateway' in components
        
        # Check resources
        resources = health['resources']
        assert 'cpu_usage' in resources
        assert 'memory_usage' in resources
        assert 'disk_usage' in resources
    
    def test_security_observation(self, cleanup_db):
        """Test security monitoring"""
        observations = observe_all_systems(timeframe_minutes=60)
        
        security = observations['security']
        assert 'security_score' in security
        assert 'threats_detected' in security
        assert 'threats_blocked' in security
        assert 'events' in security
        
        # Check security events
        events = security['events']
        assert 'failed_logins' in events
        assert 'suspicious_ips' in events
        assert 'rate_limit_triggers' in events
    
    def test_anomaly_detection(self, cleanup_db):
        """Test anomaly detection"""
        observations = observe_all_systems(timeframe_minutes=60)
        
        anomalies = observations['anomalies']
        assert isinstance(anomalies, list)
        
        # Each anomaly should have required fields
        for anomaly in anomalies:
            assert 'type' in anomaly
            assert 'severity' in anomaly
            assert 'description' in anomaly
    
    def test_predictions_generation(self, cleanup_db):
        """Test AI predictions"""
        observations = observe_all_systems(timeframe_minutes=60)
        
        predictions = observations['predictions']
        assert isinstance(predictions, list)
        assert len(predictions) > 0
        
        # Check prediction structure
        for prediction in predictions:
            assert 'type' in prediction
            assert 'timeframe' in prediction
            assert 'prediction' in prediction
            assert 'confidence' in prediction
    
    def test_insights_generation(self, cleanup_db):
        """Test AI insights"""
        observations = observe_all_systems(timeframe_minutes=60)
        
        insights = observations['insights']
        assert isinstance(insights, list)
        assert len(insights) > 0
        
        # Check insight structure
        for insight in insights:
            assert 'category' in insight
            assert 'insight' in insight
            assert 'impact' in insight
            assert 'action' in insight
    
    def test_track_user_activity(self):
        """Test real-time user tracking"""
        eye = get_ai_eye()
        
        # Track user action
        track_user_activity('TEST_USER_1', 'page_view', {'page': '/dashboard'})
        
        # Check tracking
        assert 'TEST_USER_1' in eye.live_users
        assert eye.live_users['TEST_USER_1']['action_count'] == 1
        assert len(eye.live_users['TEST_USER_1']['actions']) == 1
        assert eye.live_users['TEST_USER_1']['actions'][0]['action'] == 'page_view'
        
        # Track another action
        track_user_activity('TEST_USER_1', 'button_click', {'button': 'submit'})
        assert eye.live_users['TEST_USER_1']['action_count'] == 2
    
    def test_track_payment(self):
        """Test real-time payment tracking"""
        eye = get_ai_eye()
        
        # Track payment
        payment_data = {
            'amount': 5000,
            'currency': 'INR',
            'status': 'captured'
        }
        track_payment('TEST_TXN_1', payment_data)
        
        # Check tracking
        assert 'TEST_TXN_1' in eye.live_transactions
        assert eye.live_transactions['TEST_TXN_1']['data'] == payment_data
    
    def test_track_ai_call(self):
        """Test AI call tracking"""
        eye = get_ai_eye()
        
        # Track AI call
        call_id = 'TEST_CALL_1'
        eye.track_ai_call(call_id, 'recommendations', 'TEST_USER_1')
        
        # Check tracking
        assert call_id in eye.live_ai_calls
        assert eye.live_ai_calls[call_id]['operation'] == 'recommendations'
        assert eye.live_ai_calls[call_id]['user_id'] == 'TEST_USER_1'
        assert eye.live_ai_calls[call_id]['status'] == 'running'
        
        # Complete AI call
        eye.complete_ai_call(call_id, success=True)
        assert eye.live_ai_calls[call_id]['status'] == 'success'
        assert 'duration' in eye.live_ai_calls[call_id]
    
    def test_create_alert(self):
        """Test alert creation"""
        alert = create_system_alert(
            'high_traffic',
            'medium',
            'Traffic spike detected: 500 req/min',
            {'current_rpm': 500, 'threshold': 300}
        )
        
        # Check alert structure
        assert alert['type'] == 'high_traffic'
        assert alert['severity'] == 'medium'
        assert alert['message'] == 'Traffic spike detected: 500 req/min'
        assert alert['data']['current_rpm'] == 500
        assert alert['status'] == 'active'
        assert not alert['acknowledged']
        assert 'id' in alert
        assert 'created_at' in alert
    
    def test_live_dashboard_data(self):
        """Test live dashboard data retrieval"""
        # Add some test data
        track_user_activity('TEST_USER_1', 'page_view')
        track_user_activity('TEST_USER_2', 'page_view')
        track_payment('TEST_TXN_1', {'amount': 5000})
        
        # Get live data
        live_data = get_live_dashboard_data()
        
        # Check structure
        assert 'timestamp' in live_data
        assert 'live_metrics' in live_data
        assert 'recent_activity' in live_data
        assert 'active_alerts' in live_data
        assert 'recent_anomalies' in live_data
        
        # Check live metrics
        metrics = live_data['live_metrics']
        assert 'users_online' in metrics
        assert 'transactions_processing' in metrics
        assert 'ai_calls_active' in metrics
        assert 'requests_per_minute' in metrics
        assert 'health_score' in metrics
    
    def test_anomaly_persistence(self):
        """Test that anomalies are stored"""
        eye = get_ai_eye()
        
        # Observe systems (this detects anomalies)
        observe_all_systems(timeframe_minutes=60)
        
        # Anomalies should be stored
        assert isinstance(eye.anomalies, list)
    
    def test_observation_history(self):
        """Test that observations are recorded"""
        eye = get_ai_eye()
        
        # Make multiple observations
        observe_all_systems(timeframe_minutes=60)
        time.sleep(0.1)
        observe_all_systems(timeframe_minutes=60)
        
        # Check history
        assert len(eye.observations) >= 2
        assert 'timestamp' in eye.observations[0]
        assert 'data' in eye.observations[0]
    
    def test_timeframe_parameter(self, cleanup_db):
        """Test different timeframe parameters"""
        # 15 minute observation
        obs_15 = observe_all_systems(timeframe_minutes=15)
        assert obs_15['timeframe_minutes'] == 15
        
        # 1 hour observation
        obs_60 = observe_all_systems(timeframe_minutes=60)
        assert obs_60['timeframe_minutes'] == 60
        
        # 24 hour observation
        obs_1440 = observe_all_systems(timeframe_minutes=1440)
        assert obs_1440['timeframe_minutes'] == 1440
    
    def test_multiple_user_tracking(self):
        """Test tracking multiple users simultaneously"""
        eye = get_ai_eye()
        
        # Track multiple users
        for i in range(10):
            track_user_activity(f'TEST_USER_{i}', 'login')
        
        # Check all tracked
        assert len(eye.live_users) >= 10
        
        # Get top active users
        live_data = get_live_dashboard_data()
        assert 'recent_activity' in live_data
        assert 'last_10_users' in live_data['recent_activity']
    
    def test_alert_severity_levels(self):
        """Test different alert severity levels"""
        # Create alerts with different severities
        low_alert = create_system_alert('test', 'low', 'Low priority')
        medium_alert = create_system_alert('test', 'medium', 'Medium priority')
        high_alert = create_system_alert('test', 'high', 'High priority')
        critical_alert = create_system_alert('test', 'critical', 'Critical priority')
        
        assert low_alert['severity'] == 'low'
        assert medium_alert['severity'] == 'medium'
        assert high_alert['severity'] == 'high'
        assert critical_alert['severity'] == 'critical'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
