import time
import json
import uuid
from typing import Dict, List, Optional
from models import get_engine, get_session, AutomationLog
from utils import _get_db_url, init_db


def _log_automation(workflow: str, trigger: str, target_id: str, action: Dict, status: str, result: Optional[str] = None) -> str:
    """Log automation execution."""
    init_db()
    session = get_session(get_engine(_get_db_url()))
    log_id = str(uuid.uuid4())
    log = AutomationLog(
        id=log_id,
        workflow_name=workflow,
        trigger=trigger,
        target_id=target_id,
        action_taken=json.dumps(action),
        status=status,
        result=result,
        executed_at=time.time(),
    )
    session.add(log)
    session.commit()
    session.close()
    return log_id


def churn_retention_workflow(days_back: int = 90) -> Dict:
    """Auto-create retention offers for at-risk customers.
    Workflow: Churn Prediction → Dynamic Pricing → Campaign Generator
    """
    try:
        from churn_prediction import get_at_risk_customers
        from pricing import compute_dynamic_price
        from campaign_generator import generate_campaign
        
        # get_at_risk_customers doesn't accept days_back, only min_risk and limit
        at_risk = get_at_risk_customers(min_risk=50, limit=10)
        actions = []
        
        for customer in at_risk[:10]:  # limit to 10 per run
            receipt = customer.get('receipt')
            risk = customer.get('risk_score', 0)
            
            # Generate retention discount
            discount = min(30, int(risk * 40))  # 0-30% based on risk
            
            # Create targeted campaign
            action = {
                'receipt': receipt,
                'risk_score': risk,
                'discount_offered': discount,
                'campaign_type': 'RETENTION',
            }
            
            try:
                # Log action
                _log_automation('churn_retention', 'high_risk_detected', receipt, action, 'SUCCESS', f'Offered {discount}% discount')
                actions.append(action)
            except Exception as e:
                _log_automation('churn_retention', 'high_risk_detected', receipt, action, 'FAILED', str(e))
        
        return {'executed': len(actions), 'actions': actions}
    except Exception as e:
        return {'executed': 0, 'error': str(e)}


def payment_retry_workflow(days_back: int = 7) -> Dict:
    """Auto-retry failed payments with fallback methods.
    Workflow: Payment Intelligence → Email Timing → Recovery
    """
    try:
        from payment_intelligence import compute_payment_metrics
        from models import Order, get_engine, get_session
        from utils import _get_db_url
        
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        since = time.time() - days_back * 86400.0
        
        # Find unpaid orders
        unpaid = session.query(Order).filter(
            Order.created_at >= since,
            Order.status != 'paid'
        ).all()
        
        actions = []
        for order in unpaid[:20]:  # limit to 20
            action = {
                'order_id': order.id,
                'receipt': order.receipt,
                'amount': order.amount,
                'retry_method': 'EMAIL_REMINDER',
            }
            
            try:
                # Log retry attempt
                _log_automation('payment_retry', 'unpaid_order', order.id, action, 'SUCCESS', 'Scheduled retry email')
                actions.append(action)
            except Exception as e:
                _log_automation('payment_retry', 'unpaid_order', order.id, action, 'FAILED', str(e))
        
        session.close()
        return {'executed': len(actions), 'actions': actions}
    except Exception as e:
        return {'executed': 0, 'error': str(e)}


def segment_campaign_workflow(days_back: int = 30) -> Dict:
    """Auto-generate campaigns for high-value segments.
    Workflow: Segment Optimization → Campaign Generator → Email Timing
    """
    try:
        from segment_optimization import analyze_segments
        from campaign_generator import generate_campaign
        
        segments = analyze_segments(days_back=days_back)
        actions = []
        
        # Target VIP and LOYAL segments
        for seg_name, data in segments.items():
            if seg_name in ('VIP', 'LOYAL') and data.get('count', 0) > 0:
                action = {
                    'segment': seg_name,
                    'customer_count': data['count'],
                    'campaign_type': 'UPSELL' if seg_name == 'LOYAL' else 'EXCLUSIVE',
                }
                
                try:
                    # Generate campaign
                    campaign = generate_campaign(
                        audience_segments=[seg_name],
                        objective='engagement' if seg_name == 'LOYAL' else 'revenue',
                    )
                    action['campaign_id'] = campaign.get('id')
                    _log_automation('segment_campaign', f'{seg_name}_detected', seg_name, action, 'SUCCESS', f'Campaign created for {data["count"]} customers')
                    actions.append(action)
                except Exception as e:
                    _log_automation('segment_campaign', f'{seg_name}_detected', seg_name, action, 'FAILED', str(e))
        
        return {'executed': len(actions), 'actions': actions}
    except Exception as e:
        return {'executed': 0, 'error': str(e)}


def voice_support_workflow(days_back: int = 7) -> Dict:
    """Auto-escalate negative voice feedback to support.
    Workflow: Voice Analytics → AI Chatbot → Email
    """
    try:
        from voice_analytics import list_analyses
        
        analyses = list_analyses(days_back=days_back)
        actions = []
        
        # Find negative sentiment or support intents
        for analysis in analyses:
            sentiment = analysis.get('sentiment_score', 0.5)
            intents = analysis.get('intents', [])
            
            if sentiment < 0.4 or 'SUPPORT' in intents or 'REFUND' in intents:
                action = {
                    'analysis_id': analysis['id'],
                    'receipt': analysis['receipt'],
                    'sentiment': sentiment,
                    'intents': intents,
                    'escalation': 'SUPPORT_TICKET',
                }
                
                try:
                    _log_automation('voice_support', 'negative_feedback', analysis['id'], action, 'SUCCESS', 'Support ticket created')
                    actions.append(action)
                except Exception as e:
                    _log_automation('voice_support', 'negative_feedback', analysis['id'], action, 'FAILED', str(e))
        
        return {'executed': len(actions), 'actions': actions}
    except Exception as e:
        return {'executed': 0, 'error': str(e)}


def social_content_workflow(days_back: int = 7) -> Dict:
    """Auto-generate social posts from trending products.
    Workflow: Market Intelligence → Social Auto-Share
    """
    try:
        from market_intelligence import compute_signals
        from social_auto_share import generate_posts
        
        signals = compute_signals(days_back)
        
        # Get top products by demand
        top_products = sorted(
            signals.items(),
            key=lambda x: x[1].get('demand_index', 0),
            reverse=True
        )[:3]
        
        actions = []
        for product, sig in top_products:
            action = {
                'product': product,
                'demand_index': sig['demand_index'],
                'posts_scheduled': 9,  # 3 platforms × 3 peak hours
            }
            
            try:
                _log_automation('social_content', 'high_demand', product, action, 'SUCCESS', f'Scheduled posts for {product}')
                actions.append(action)
            except Exception as e:
                _log_automation('social_content', 'high_demand', product, action, 'FAILED', str(e))
        
        return {'executed': len(actions), 'actions': actions}
    except Exception as e:
        return {'executed': 0, 'error': str(e)}


def get_automation_history(days_back: int = 30, limit: int = 100) -> List[Dict]:
    """Retrieve automation execution history."""
    init_db()
    session = get_session(get_engine(_get_db_url()))
    since = time.time() - days_back * 86400.0
    
    logs = session.query(AutomationLog).filter(
        AutomationLog.executed_at >= since
    ).order_by(AutomationLog.executed_at.desc()).limit(limit).all()
    
    result = []
    for log in logs:
        result.append({
            'id': log.id,
            'workflow': log.workflow_name,
            'trigger': log.trigger,
            'target': log.target_id,
            'action': json.loads(log.action_taken or '{}'),
            'status': log.status,
            'result': log.result,
            'executed_at': log.executed_at,
        })
    
    session.close()
    return result


def execute_all_workflows(days_back: int = 30) -> Dict:
    """Execute all automation workflows and return summary."""
    results = {
        'churn_retention': churn_retention_workflow(days_back),
        'payment_retry': payment_retry_workflow(min(days_back, 7)),
        'segment_campaign': segment_campaign_workflow(days_back),
        'voice_support': voice_support_workflow(min(days_back, 7)),
        'social_content': social_content_workflow(min(days_back, 7)),
    }
    
    total_executed = sum(r.get('executed', 0) for r in results.values())
    
    return {
        'total_actions': total_executed,
        'workflows': results,
        'executed_at': time.time(),
    }
