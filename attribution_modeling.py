"""
Advanced Attribution Modeling Engine (Feature #20)
Multi-touch attribution across marketing channels with ROI optimization
Supports first-touch, last-touch, linear, and time-decay models
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
from collections import defaultdict


class AttributionModel(Enum):
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"


class TouchpointType(Enum):
    EMAIL = "email"
    PAID_SEARCH = "paid_search"
    ORGANIC_SEARCH = "organic_search"
    SOCIAL_MEDIA = "social_media"
    DIRECT = "direct"
    REFERRAL = "referral"
    DISPLAY = "display"
    VIDEO = "video"
    AFFILIATE = "affiliate"
    PUSH_NOTIFICATION = "push_notification"


class ConversionAttributor:
    """Attributes conversions to touchpoints using different models"""

    def __init__(self):
        self.conversion_paths = []
        self.attributed_revenue = defaultdict(float)
        self.attribution_details = []

    def attribute_first_touch(self, path: List[Dict], conversion_value: float) -> Dict:
        """First-touch attribution: 100% credit to first touchpoint"""
        if not path:
            return {}

        first_touchpoint = path[0]
        channel = first_touchpoint.get('channel', 'unknown')
        
        return {
            'model': AttributionModel.FIRST_TOUCH.value,
            'channel': channel,
            'attributed_value': conversion_value,
            'touchpoint_id': first_touchpoint.get('id'),
            'timestamp': first_touchpoint.get('timestamp'),
            'credit_percentage': 100.0
        }

    def attribute_last_touch(self, path: List[Dict], conversion_value: float) -> Dict:
        """Last-touch attribution: 100% credit to last touchpoint"""
        if not path:
            return {}

        last_touchpoint = path[-1]
        channel = last_touchpoint.get('channel', 'unknown')
        
        return {
            'model': AttributionModel.LAST_TOUCH.value,
            'channel': channel,
            'attributed_value': conversion_value,
            'touchpoint_id': last_touchpoint.get('id'),
            'timestamp': last_touchpoint.get('timestamp'),
            'credit_percentage': 100.0
        }

    def attribute_linear(self, path: List[Dict], conversion_value: float) -> List[Dict]:
        """Linear attribution: Equal credit to all touchpoints"""
        if not path:
            return []

        credit_per_touchpoint = conversion_value / len(path)
        credit_percentage = 100.0 / len(path)
        
        attributions = []
        for touchpoint in path:
            attributions.append({
                'model': AttributionModel.LINEAR.value,
                'channel': touchpoint.get('channel', 'unknown'),
                'attributed_value': credit_per_touchpoint,
                'touchpoint_id': touchpoint.get('id'),
                'timestamp': touchpoint.get('timestamp'),
                'credit_percentage': credit_percentage
            })
        
        return attributions

    def attribute_time_decay(self, path: List[Dict], conversion_value: float, decay_rate: float = 0.5) -> List[Dict]:
        """Time-decay attribution: Credit increases closer to conversion"""
        if not path:
            return []

        # Calculate weights using exponential decay
        weights = []
        total_weight = 0
        
        for i, _ in enumerate(path):
            # More recent touches get higher weight
            weight = decay_rate ** (len(path) - i - 1)
            weights.append(weight)
            total_weight += weight
        
        attributions = []
        for i, touchpoint in enumerate(path):
            credited_value = (weights[i] / total_weight) * conversion_value
            credit_percentage = (weights[i] / total_weight) * 100.0
            
            attributions.append({
                'model': AttributionModel.TIME_DECAY.value,
                'channel': touchpoint.get('channel', 'unknown'),
                'attributed_value': credited_value,
                'touchpoint_id': touchpoint.get('id'),
                'timestamp': touchpoint.get('timestamp'),
                'credit_percentage': credit_percentage
            })
        
        return attributions

    def track_conversion_path(self, customer_id: str, path: List[Dict], conversion_value: float, order_id: str = None) -> Dict:
        """Track complete conversion path with multiple attribution models"""
        attribution_results = {
            'customer_id': customer_id,
            'order_id': order_id or f"order_{customer_id}_{int(datetime.utcnow().timestamp())}",
            'conversion_value': conversion_value,
            'path_length': len(path),
            'attributions': {},
            'timestamp': datetime.utcnow().isoformat()
        }

        # Apply all models
        first_touch = self.attribute_first_touch(path, conversion_value)
        if first_touch:
            attribution_results['attributions'][AttributionModel.FIRST_TOUCH.value] = first_touch

        last_touch = self.attribute_last_touch(path, conversion_value)
        if last_touch:
            attribution_results['attributions'][AttributionModel.LAST_TOUCH.value] = last_touch

        linear = self.attribute_linear(path, conversion_value)
        if linear:
            attribution_results['attributions'][AttributionModel.LINEAR.value] = linear

        time_decay = self.attribute_time_decay(path, conversion_value)
        if time_decay:
            attribution_results['attributions'][AttributionModel.TIME_DECAY.value] = time_decay

        self.conversion_paths.append(attribution_results)
        return attribution_results

    def get_channel_revenue_by_model(self, model: AttributionModel) -> Dict[str, float]:
        """Calculate total attributed revenue per channel for a specific model"""
        channel_revenue = defaultdict(float)
        
        for path_data in self.conversion_paths:
            model_key = model.value
            if model_key in path_data['attributions']:
                attr = path_data['attributions'][model_key]
                
                if isinstance(attr, list):
                    # Linear and time-decay return lists
                    for item in attr:
                        channel = item.get('channel', 'unknown')
                        channel_revenue[channel] += item.get('attributed_value', 0)
                else:
                    # First and last touch return dicts
                    channel = attr.get('channel', 'unknown')
                    channel_revenue[channel] += attr.get('attributed_value', 0)
        
        return dict(channel_revenue)

    def get_conversion_paths(self) -> List[Dict]:
        """Get all tracked conversion paths"""
        return self.conversion_paths


class ChannelROICalculator:
    """Calculates ROI and efficiency metrics per marketing channel"""

    def __init__(self):
        self.channel_costs = defaultdict(float)
        self.channel_revenue = defaultdict(float)
        self.channel_conversions = defaultdict(int)
        self.channel_impressions = defaultdict(int)

    def add_channel_spend(self, channel: str, amount: float):
        """Record marketing spend for a channel"""
        self.channel_costs[channel] += amount

    def add_channel_revenue(self, channel: str, attributed_revenue: float, conversions: int = 1):
        """Record revenue attributed to a channel"""
        self.channel_revenue[channel] += attributed_revenue
        self.channel_conversions[channel] += conversions

    def add_impressions(self, channel: str, count: int):
        """Record impressions for a channel"""
        self.channel_impressions[channel] += count

    def calculate_roi(self, channel: str) -> Dict:
        """Calculate ROI metrics for a channel"""
        revenue = self.channel_revenue.get(channel, 0)
        cost = self.channel_costs.get(channel, 0)
        
        if cost == 0:
            roi_percent = 0 if revenue == 0 else float('inf')
            roas = 0 if revenue == 0 else float('inf')  # Return on Ad Spend
        else:
            roi_percent = ((revenue - cost) / cost) * 100
            roas = revenue / cost

        return {
            'channel': channel,
            'spend': round(cost, 2),
            'revenue': round(revenue, 2),
            'roi_percent': round(roi_percent, 2),
            'roas': round(roas, 2),
            'conversions': self.channel_conversions.get(channel, 0),
            'cost_per_conversion': round(cost / max(self.channel_conversions.get(channel, 1), 1), 2),
            'impressions': self.channel_impressions.get(channel, 0),
            'ctr': round((self.channel_conversions.get(channel, 0) / max(self.channel_impressions.get(channel, 1), 1)) * 100, 4),
        }

    def get_all_roi(self) -> Dict[str, Dict]:
        """Get ROI metrics for all channels"""
        all_channels = set(self.channel_costs.keys()) | set(self.channel_revenue.keys())
        roi_data = {}
        
        for channel in all_channels:
            roi_data[channel] = self.calculate_roi(channel)
        
        return roi_data

    def get_best_performing_channel(self) -> Tuple[str, Dict]:
        """Get highest ROI channel"""
        roi_data = self.get_all_roi()
        if not roi_data:
            return None, {}
        
        best_channel = max(roi_data, key=lambda c: roi_data[c]['roi_percent'])
        return best_channel, roi_data[best_channel]

    def get_budget_recommendation(self, total_budget: float) -> Dict:
        """Recommend budget allocation based on ROI performance"""
        roi_data = self.get_all_roi()
        
        if not roi_data:
            return {}
        
        # Allocate budget proportionally to ROI
        total_roi = sum(max(metrics['roi_percent'], 0) for metrics in roi_data.values())
        
        if total_roi == 0:
            # Equal allocation if no positive ROI
            per_channel = total_budget / len(roi_data)
            return {channel: per_channel for channel in roi_data.keys()}
        
        recommendations = {}
        for channel, metrics in roi_data.items():
            # Allocate more to higher ROI channels
            roi_weight = max(metrics['roi_percent'], 0) / total_roi
            recommendations[channel] = round(total_budget * roi_weight, 2)
        
        return recommendations


class ConversionPathAnalyzer:
    """Analyzes customer conversion journeys and patterns"""

    def __init__(self):
        self.all_paths = []
        self.path_patterns = defaultdict(int)

    def analyze_path(self, path: List[Dict]) -> Dict:
        """Analyze a single conversion path"""
        channels = [tp.get('channel', 'unknown') for tp in path]
        unique_channels = len(set(channels))
        path_length = len(path)
        
        # Calculate time between touchpoints
        time_differences = []
        for i in range(1, len(path)):
            # Assuming timestamps are ISO format strings
            prev_time = datetime.fromisoformat(path[i-1].get('timestamp', datetime.utcnow().isoformat()))
            curr_time = datetime.fromisoformat(path[i].get('timestamp', datetime.utcnow().isoformat()))
            diff = (curr_time - prev_time).total_seconds() / 3600  # Convert to hours
            time_differences.append(diff)

        avg_time_between = sum(time_differences) / len(time_differences) if time_differences else 0
        
        # Create path pattern string
        pattern = " → ".join(channels)
        self.path_patterns[pattern] += 1
        
        return {
            'channels': channels,
            'unique_channels': unique_channels,
            'path_length': path_length,
            'average_hours_between_touches': round(avg_time_between, 2),
            'pattern': pattern
        }

    def add_conversion_path(self, path: List[Dict]) -> Dict:
        """Add and analyze a conversion path"""
        analysis = self.analyze_path(path)
        self.all_paths.append(analysis)
        return analysis

    def get_common_patterns(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get most common conversion patterns"""
        sorted_patterns = sorted(self.path_patterns.items(), key=lambda x: x[1], reverse=True)
        return sorted_patterns[:top_n]

    def get_path_statistics(self) -> Dict:
        """Get overall path statistics"""
        if not self.all_paths:
            return {}

        lengths = [p['path_length'] for p in self.all_paths]
        unique_channels = [p['unique_channels'] for p in self.all_paths]
        avg_times = [p['average_hours_between_touches'] for p in self.all_paths]

        return {
            'total_paths_analyzed': len(self.all_paths),
            'avg_path_length': round(sum(lengths) / len(lengths), 2),
            'max_path_length': max(lengths),
            'min_path_length': min(lengths),
            'avg_unique_channels': round(sum(unique_channels) / len(unique_channels), 2),
            'avg_hours_between_touches': round(sum(avg_times) / len(avg_times), 2),
            'most_common_pattern': self.get_common_patterns(1)[0][0] if self.path_patterns else None,
        }


class AttributionModelComparator:
    """Compares different attribution models"""

    def __init__(self):
        self.conversion_data = []

    def add_conversion(self, path: List[Dict], value: float, customer_id: str):
        """Add a conversion for comparison"""
        self.conversion_data.append({
            'path': path,
            'value': value,
            'customer_id': customer_id
        })

    def compare_models(self) -> Dict:
        """Compare attribution across all models"""
        attributor = ConversionAttributor()
        comparisons = {
            AttributionModel.FIRST_TOUCH.value: defaultdict(float),
            AttributionModel.LAST_TOUCH.value: defaultdict(float),
            AttributionModel.LINEAR.value: defaultdict(float),
            AttributionModel.TIME_DECAY.value: defaultdict(float),
        }

        for conv_data in self.conversion_data:
            path = conv_data['path']
            value = conv_data['value']
            
            attributor.track_conversion_path(conv_data['customer_id'], path, value)

        # Aggregate by model
        for model in AttributionModel:
            channel_revenue = attributor.get_channel_revenue_by_model(model)
            for channel, revenue in channel_revenue.items():
                comparisons[model.value][channel] += revenue

        return {model: dict(channels) for model, channels in comparisons.items()}

    def get_model_variance(self) -> Dict:
        """Calculate variance in attribution across models for each channel"""
        comparison = self.compare_models()
        
        # Collect all channels
        all_channels = set()
        for model_data in comparison.values():
            all_channels.update(model_data.keys())

        variance_by_channel = {}
        for channel in all_channels:
            values = [comparison[model].get(channel, 0) for model in comparison.keys()]
            if values:
                avg = sum(values) / len(values)
                variance = sum((v - avg) ** 2 for v in values) / len(values)
                variance_by_channel[channel] = {
                    'variance': round(variance, 2),
                    'std_dev': round(variance ** 0.5, 2),
                    'avg_attributed': round(avg, 2)
                }

        return variance_by_channel


class AttributionAnalytics:
    """Main engine orchestrating all attribution analysis"""

    def __init__(self):
        self.attributor = ConversionAttributor()
        self.roi_calculator = ChannelROICalculator()
        self.path_analyzer = ConversionPathAnalyzer()
        self.model_comparator = AttributionModelComparator()
        self.total_conversions = 0
        self.total_revenue = 0

    def track_customer_journey(self, customer_id: str, touchpoints: List[Dict], 
                             conversion_value: float, order_id: str = None) -> Dict:
        """Track complete customer journey and calculate attributions"""
        path_result = self.attributor.track_conversion_path(
            customer_id, touchpoints, conversion_value, order_id
        )
        
        # Analyze path
        self.path_analyzer.add_conversion_path(touchpoints)
        
        # Add to comparator
        self.model_comparator.add_conversion(touchpoints, conversion_value, customer_id)
        
        # Update totals
        self.total_conversions += 1
        self.total_revenue += conversion_value
        
        return path_result

    def record_channel_spend(self, channel: str, spend: float, impressions: int = 0):
        """Record marketing spend for ROI calculation"""
        self.roi_calculator.add_channel_spend(channel, spend)
        if impressions:
            self.roi_calculator.add_impressions(channel, impressions)

    def record_channel_activity(self, channel: str, touchpoint_data: Dict):
        """Record channel activity (clicks, impressions, etc)"""
        if 'impressions' in touchpoint_data:
            self.roi_calculator.add_impressions(channel, touchpoint_data['impressions'])

    def get_full_attribution_report(self) -> Dict:
        """Generate comprehensive attribution report"""
        return {
            'summary': {
                'total_conversions': self.total_conversions,
                'total_revenue': round(self.total_revenue, 2),
                'avg_order_value': round(self.total_revenue / max(self.total_conversions, 1), 2),
            },
            'channel_roi': self.roi_calculator.get_all_roi(),
            'best_channel': self.roi_calculator.get_best_performing_channel(),
            'path_statistics': self.path_analyzer.get_path_statistics(),
            'common_patterns': self.path_analyzer.get_common_patterns(),
            'model_comparison': self.model_comparator.compare_models(),
            'model_variance': self.model_comparator.get_model_variance(),
        }

    def get_budget_optimization(self, total_budget: float) -> Dict:
        """Get optimized budget allocation"""
        return {
            'total_budget': total_budget,
            'recommendations': self.roi_calculator.get_budget_recommendation(total_budget),
            'current_roi': self.roi_calculator.get_all_roi(),
        }


def generate_demo_attribution_data() -> AttributionAnalytics:
    """Generate realistic demo attribution data"""
    analytics = AttributionAnalytics()
    
    # Demo conversion paths
    demo_journeys = [
        # Customer 1: Multi-channel journey
        {
            'customer_id': 'cust_001',
            'path': [
                {'id': 'tp_1', 'channel': 'paid_search', 'timestamp': '2026-01-10T08:00:00'},
                {'id': 'tp_2', 'channel': 'organic_search', 'timestamp': '2026-01-10T10:30:00'},
                {'id': 'tp_3', 'channel': 'email', 'timestamp': '2026-01-11T14:00:00'},
                {'id': 'tp_4', 'channel': 'direct', 'timestamp': '2026-01-12T09:15:00'},
            ],
            'value': 199.99,
            'order_id': 'ORD_001'
        },
        # Customer 2: Shorter path
        {
            'customer_id': 'cust_002',
            'path': [
                {'id': 'tp_5', 'channel': 'social_media', 'timestamp': '2026-01-11T16:00:00'},
                {'id': 'tp_6', 'channel': 'direct', 'timestamp': '2026-01-12T08:45:00'},
            ],
            'value': 99.99,
            'order_id': 'ORD_002'
        },
        # Customer 3: Email-dominant
        {
            'customer_id': 'cust_003',
            'path': [
                {'id': 'tp_7', 'channel': 'email', 'timestamp': '2026-01-10T09:00:00'},
                {'id': 'tp_8', 'channel': 'email', 'timestamp': '2026-01-11T09:00:00'},
                {'id': 'tp_9', 'channel': 'email', 'timestamp': '2026-01-12T09:00:00'},
            ],
            'value': 149.99,
            'order_id': 'ORD_003'
        },
        # Customer 4: Paid search heavy
        {
            'customer_id': 'cust_004',
            'path': [
                {'id': 'tp_10', 'channel': 'paid_search', 'timestamp': '2026-01-11T10:00:00'},
                {'id': 'tp_11', 'channel': 'display', 'timestamp': '2026-01-11T15:00:00'},
                {'id': 'tp_12', 'channel': 'paid_search', 'timestamp': '2026-01-12T10:00:00'},
            ],
            'value': 249.99,
            'order_id': 'ORD_004'
        },
        # Customer 5: Organic path
        {
            'customer_id': 'cust_005',
            'path': [
                {'id': 'tp_13', 'channel': 'organic_search', 'timestamp': '2026-01-10T12:00:00'},
                {'id': 'tp_14', 'channel': 'referral', 'timestamp': '2026-01-11T11:00:00'},
                {'id': 'tp_15', 'channel': 'direct', 'timestamp': '2026-01-12T14:00:00'},
            ],
            'value': 179.99,
            'order_id': 'ORD_005'
        },
    ]

    # Track journeys
    for journey in demo_journeys:
        analytics.track_customer_journey(
            journey['customer_id'],
            journey['path'],
            journey['value'],
            journey['order_id']
        )

    # Record channel spend
    channel_budgets = {
        'paid_search': 5000.0,
        'organic_search': 0.0,  # No cost
        'social_media': 3000.0,
        'email': 800.0,
        'display': 2000.0,
        'referral': 1500.0,
        'direct': 0.0,  # No cost
    }

    for channel, budget in channel_budgets.items():
        analytics.record_channel_spend(channel, budget)

    # Record impressions for CTR calculation
    impressions = {
        'paid_search': 25000,
        'social_media': 15000,
        'email': 8000,
        'display': 10000,
        'referral': 5000,
    }

    for channel, imp_count in impressions.items():
        analytics.record_channel_activity(channel, {'impressions': imp_count})

    return analytics
