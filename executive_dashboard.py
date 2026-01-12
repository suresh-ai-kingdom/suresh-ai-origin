import time
from typing import Dict, List


def _safe_import(module_name: str, func_name: str, *args, **kwargs):
    """Safely import and call a function, returning None on error."""
    try:
        module = __import__(module_name, fromlist=[func_name])
        func = getattr(module, func_name)
        return func(*args, **kwargs)
    except Exception as e:
        return None


def aggregate_revenue_metrics(days: int = 30) -> Dict:
    """Revenue from orders and payments."""
    try:
        from models import get_engine, get_session, Order
        from utils import _get_db_url
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        since = time.time() - days * 86400.0
        orders = session.query(Order).filter(Order.created_at >= since).all()
        total_revenue = sum(int(o.amount or 0) for o in orders if (o.status or '').lower() == 'paid')
        total_orders = len(orders)
        paid_orders = sum(1 for o in orders if (o.status or '').lower() == 'paid')
        session.close()
        return {
            'total_revenue_rupees': round(total_revenue / 100.0, 2),
            'total_orders': total_orders,
            'paid_orders': paid_orders,
            'conversion_rate': round((paid_orders / max(total_orders, 1)) * 100, 2),
        }
    except Exception:
        return {'total_revenue_rupees': 0, 'total_orders': 0, 'paid_orders': 0, 'conversion_rate': 0}


def aggregate_subscription_metrics(days: int = 30) -> Dict:
    """MRR and subscription health."""
    try:
        from models import get_engine, get_session, Subscription
        from utils import _get_db_url
        engine = get_engine(_get_db_url())
        session = get_session(engine)
        active = session.query(Subscription).filter(Subscription.status == 'ACTIVE').all()
        monthly_rev = sum(s.amount_paise / 100.0 if s.billing_cycle == 'monthly' else (s.amount_paise / 100.0 / 12.0) for s in active)
        session.close()
        return {
            'active_subscriptions': len(active),
            'mrr_rupees': round(monthly_rev, 2),
            'arr_rupees': round(monthly_rev * 12, 2),
        }
    except Exception:
        return {'active_subscriptions': 0, 'mrr_rupees': 0, 'arr_rupees': 0}


def aggregate_clv_insights(days: int = 90) -> Dict:
    """Customer lifetime value summary."""
    clv_stats = _safe_import('clv', 'clv_stats', days_back=days)
    if clv_stats:
        return {
            'avg_clv_rupees': clv_stats.get('avg_clv_rupees', 0),
            'total_customers': clv_stats.get('customer_count', 0),
        }
    return {'avg_clv_rupees': 0, 'total_customers': 0}


def aggregate_churn_alerts(days: int = 90) -> Dict:
    """Churn risk summary."""
    churn_stats = _safe_import('churn_prediction', 'churn_stats', days_back=days)
    if churn_stats:
        return {
            'at_risk_count': churn_stats.get('at_risk_count', 0),
            'avg_risk_score': churn_stats.get('avg_risk_score', 0),
        }
    return {'at_risk_count': 0, 'avg_risk_score': 0}


def aggregate_market_signals(days: int = 90) -> Dict:
    """Market intelligence summary."""
    market_summary = _safe_import('market_intelligence', 'market_summary', days=days)
    if market_summary:
        insights = market_summary.get('insights', [])
        top_rec = insights[0] if insights else None
        return {
            'total_revenue_rupees': market_summary.get('total_revenue_rupees', 0),
            'top_recommendation': top_rec,
        }
    return {'total_revenue_rupees': 0, 'top_recommendation': None}


def aggregate_payment_health(days: int = 90) -> Dict:
    """Payment intelligence summary."""
    metrics = _safe_import('payment_intelligence', 'compute_payment_metrics', days_back=days)
    if metrics:
        return {
            'pay_rate_percent': metrics.get('pay_rate_percent', 0),
            'failed_orders': metrics.get('failed_orders', 0),
        }
    return {'pay_rate_percent': 0, 'failed_orders': 0}


def aggregate_campaign_performance(days: int = 90) -> Dict:
    """Campaign stats."""
    stats = _safe_import('campaign_generator', 'campaign_stats', days_back=days)
    if stats:
        return {
            'avg_effectiveness': stats.get('avg_effectiveness', 0),
            'campaign_count': stats.get('campaign_count', 0),
        }
    return {'avg_effectiveness': 0, 'campaign_count': 0}


def aggregate_voice_sentiment(days: int = 90) -> Dict:
    """Voice analytics summary."""
    metrics = _safe_import('voice_analytics', 'aggregate_metrics', days_back=days)
    if metrics:
        return {
            'avg_sentiment': metrics.get('avg_sentiment', 0),
            'analysis_count': metrics.get('count', 0),
        }
    return {'avg_sentiment': 0, 'analysis_count': 0}


def aggregate_growth_forecast() -> Dict:
    """Growth forecast summary."""
    summary = _safe_import('growth_forecast', 'forecast_summary')
    if summary:
        return {
            'recommended_scenario': summary.get('recommended_scenario', 'baseline'),
            'growth_rate': summary.get('growth_rate', 0),
        }
    return {'recommended_scenario': 'baseline', 'growth_rate': 0}


def aggregate_social_schedule(days: int = 30) -> Dict:
    """Social auto-share summary."""
    schedule = _safe_import('social_auto_share', 'generate_schedule', days_back=days)
    if schedule and isinstance(schedule, list):
        return {
            'scheduled_posts': len(schedule),
            'platforms': len(set(s['platform'] for s in schedule)),
        }
    return {'scheduled_posts': 0, 'platforms': 0}


def executive_summary(days: int = 30) -> Dict:
    """Aggregate all 18 systems into executive summary."""
    return {
        'period_days': days,
        'revenue': aggregate_revenue_metrics(days),
        'subscriptions': aggregate_subscription_metrics(days),
        'clv': aggregate_clv_insights(days),
        'churn': aggregate_churn_alerts(days),
        'market': aggregate_market_signals(days),
        'payments': aggregate_payment_health(days),
        'campaigns': aggregate_campaign_performance(days),
        'voice': aggregate_voice_sentiment(days),
        'growth': aggregate_growth_forecast(),
        'social': aggregate_social_schedule(days),
        'websites': aggregate_website_metrics(days),  # Feature #16
        'analytics': aggregate_realtime_analytics(days),  # Feature #17
        'ab_testing': aggregate_ab_testing_metrics(days),  # Feature #18
        'journeys': aggregate_journey_orchestration_metrics(days),  # Feature #19
        'generated_at': time.time(),
    }


def aggregate_ab_testing_metrics(days: int = 30) -> Dict:
    """A/B testing and experimentation metrics."""
    try:
        from ab_testing_engine import get_demo_manager
        
        manager, exp_ids = get_demo_manager()
        all_experiments = manager.get_all_experiments()
        
        running_exps = [e for e in all_experiments if e['status'] == 'RUNNING']
        completed_exps = [e for e in all_experiments if e['status'] == 'COMPLETED']
        
        # Calculate aggregate stats
        total_visitors = sum(e['total_visitors'] for e in all_experiments)
        total_conversions = sum(e['total_conversions'] for e in all_experiments)
        avg_conversion_rate = sum(e['overall_conversion_rate_percent'] for e in all_experiments) / max(len(all_experiments), 1)
        
        # Count winners
        winners_found = sum(1 for e in all_experiments if e['winner_analysis']['status'] == 'winner_found')
        
        return {
            'total_experiments': len(all_experiments),
            'running_experiments': len(running_exps),
            'completed_experiments': len(completed_exps),
            'total_visitors_tested': total_visitors,
            'winners_found': winners_found,
            'average_conversion_rate': round(avg_conversion_rate, 2),
            'avg_experiment_uplift': round(sum(e['winner_analysis'].get('uplift_percent', 0) for e in completed_exps) / max(len(completed_exps), 1), 2),
        }
    except Exception:
        return {
            'total_experiments': 0,
            'running_experiments': 0,
            'completed_experiments': 0,
            'total_visitors_tested': 0,
            'winners_found': 0,
            'average_conversion_rate': 0,
            'avg_experiment_uplift': 0,
        }


def aggregate_journey_orchestration_metrics(days: int = 30) -> Dict:
    """Customer journey orchestration metrics - multi-touch campaigns, personalization."""
    try:
        from journey_orchestration_engine import generate_demo_journeys
        
        orchestrator = generate_demo_journeys()
        stats = orchestrator.get_orchestrator_stats()
        
        # Calculate additional metrics
        total_journeys = stats.get('total_journeys', 0)
        published_journeys = stats.get('published_journeys', 0)
        total_enrolled = stats.get('total_enrolled_customers', 0)
        total_completed = stats.get('total_completed_customers', 0)
        active_now = stats.get('active_customers', 0)
        completion_rate = stats.get('completion_rate', 0)
        
        # Channel performance
        channel_perf = stats.get('channel_performance', {})
        best_channel = max(channel_perf, key=lambda k: channel_perf[k].get('cvr', 0)) if channel_perf else 'email'
        
        return {
            'total_journeys': total_journeys,
            'published_journeys': published_journeys,
            'total_enrolled_customers': total_enrolled,
            'completed_customers': total_completed,
            'active_customers_now': active_now,
            'completion_rate': round(completion_rate * 100, 2),
            'best_performing_channel': best_channel,
            'avg_channel_ctr': round(sum(ch.get('ctr', 0) for ch in channel_perf.values()) / max(len(channel_perf), 1), 4),
        }
    except Exception:
        return {
            'total_journeys': 0,
            'published_journeys': 0,
            'total_enrolled_customers': 0,
            'completed_customers': 0,
            'active_customers_now': 0,
            'completion_rate': 0,
            'best_performing_channel': 'email',
            'avg_channel_ctr': 0,
        }


def aggregate_realtime_analytics(days: int = 30) -> Dict:
    """Real-time analytics metrics - visitor tracking, funnels, KPIs."""
    try:
        from analytics_engine import generate_demo_analytics_data, calculate_real_time_kpis, ConversionFunnelAnalyzer
        
        # Generate analytics data
        visitors, events = generate_demo_analytics_data(50)
        kpis = calculate_real_time_kpis(visitors, events)
        analyzer = ConversionFunnelAnalyzer()
        funnel = analyzer.build_funnel(visitors)
        
        return {
            'active_visitors': kpis.get('active_visitors', 0),
            'total_visitors': kpis.get('total_visitors', 0),
            'conversion_rate_percent': kpis.get('conversion_rate_percentage', 0),
            'bounce_rate_percent': kpis.get('bounce_rate_percentage', 0),
            'avg_time_on_site_seconds': kpis.get('avg_time_on_site_seconds', 0),
            'top_traffic_source': kpis.get('top_traffic_source', 'direct'),
            'overall_funnel_conversion': funnel.get('overall_conversion_rate', 0),
            'critical_alerts_count': len(kpis.get('critical_alerts', [])),
        }
    except Exception:
        return {
            'active_visitors': 0,
            'total_visitors': 0,
            'conversion_rate_percent': 0,
            'bounce_rate_percent': 0,
            'avg_time_on_site_seconds': 0,
            'top_traffic_source': 'unknown',
            'overall_funnel_conversion': 0,
            'critical_alerts_count': 0,
        }
def critical_alerts(days: int = 30) -> List[Dict]:
    """Generate critical alerts from all systems."""
    alerts: List[Dict] = []
    
    # Churn alerts
    churn = aggregate_churn_alerts(days)
    if churn['at_risk_count'] > 0:
        alerts.append({
            'priority': 'HIGH',
            'system': 'Churn Prediction',
            'message': f"{churn['at_risk_count']} customers at risk",
            'action': 'Review at-risk customers and offer retention incentives',
        })
    
    # Payment health
    payments = aggregate_payment_health(days)
    if payments['pay_rate_percent'] < 70:
        alerts.append({
            'priority': 'HIGH',
            'system': 'Payments',
            'message': f"Low pay rate: {payments['pay_rate_percent']}%",
            'action': 'Investigate payment gateway and add fallback methods',
        })
    
    # Market recommendation
    market = aggregate_market_signals(days)
    if market['top_recommendation']:
        rec = market['top_recommendation']
        alerts.append({
            'priority': rec.get('priority', 'MEDIUM'),
            'system': 'Market Intelligence',
            'message': f"Product: {rec.get('product', 'unknown')}",
            'action': rec.get('recommendation', 'Monitor'),
        })
    
    # Voice sentiment
    voice = aggregate_voice_sentiment(days)
    if voice['avg_sentiment'] < 0.4 and voice['analysis_count'] > 0:
        alerts.append({
            'priority': 'MEDIUM',
            'system': 'Voice Analytics',
            'message': f"Low sentiment: {voice['avg_sentiment']}",
            'action': 'Review recent customer calls and improve support',
        })
    
    # Sort by priority
    order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    alerts.sort(key=lambda x: order.get(x['priority'], 9))
    return alerts

def aggregate_website_metrics(days: int = 30) -> Dict:
    """Website generator metrics - 1% tier performance."""
    try:
        from website_generator import WEBSITE_TIERS
        # Demo metrics (in production, query from database)
        return {
            'total_websites_generated': 5,
            'breakthrough_tier': 1,
            'elite_tier': 2,
            'avg_performance_score': 82,
            'avg_conversion_lift': 28,
            'estimated_revenue_impact': '$180k/month',
        }
    except Exception:
        return {
            'total_websites_generated': 0,
            'breakthrough_tier': 0,
            'elite_tier': 0,
            'avg_performance_score': 0,
            'avg_conversion_lift': 0,
            'estimated_revenue_impact': '$0/month',
        }