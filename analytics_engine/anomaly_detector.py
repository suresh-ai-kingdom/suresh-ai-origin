"""
Anomaly Detector Module - Detect >20% drops in KPIs
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger("AnomalyDetector")


class AnomalyDetector:
    """Detect anomalies (>20% drops) in KPIs and alert."""
    
    def __init__(self, history_file: str = "data/kpi_history.jsonl"):
        """Initialize anomaly detector with historical data storage."""
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(exist_ok=True)
        self.threshold = 0.20  # 20% drop threshold
        
        logger.info(f"AnomalyDetector initialized (threshold: {self.threshold * 100}%)")
    
    def load_historical_kpis(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Load historical KPIs from JSONL file.
        
        Args:
            days: Number of days of history to load
        
        Returns:
            List of historical KPI records
        """
        logger.info(f"Loading historical KPIs (last {days} days)")
        
        try:
            if not self.history_file.exists():
                logger.warning("History file does not exist")
                return []
            
            history = []
            with open(self.history_file, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        history.append(record)
                    except json.JSONDecodeError:
                        pass
            
            # Sort by timestamp (most recent first)
            history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Return last N days
            if days > 0:
                history = history[:days]
            
            logger.info(f"✓ Loaded {len(history)} historical records")
            return history
        
        except Exception as e:
            logger.error(f"Failed to load historical KPIs: {e}", exc_info=True)
            return []
    
    def save_kpis(self, kpis: Dict[str, Any]) -> None:
        """
        Save current KPIs to history file.
        
        Args:
            kpis: Dictionary with KPI data
        """
        logger.info("Saving KPIs to history")
        
        try:
            with open(self.history_file, 'a') as f:
                f.write(json.dumps(kpis) + '\n')
            
            logger.info("✓ KPIs saved to history")
        
        except Exception as e:
            logger.error(f"Failed to save KPIs: {e}", exc_info=True)
    
    def detect_revenue_anomalies(self, current_kpis: Dict[str, Any], historical_kpis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect revenue-related anomalies.
        
        Args:
            current_kpis: Current KPI metrics
            historical_kpis: List of historical KPI records
        
        Returns:
            List of anomalies detected
        """
        logger.info("Detecting revenue anomalies")
        
        anomalies = []
        
        try:
            if not historical_kpis:
                logger.warning("No historical data - skipping anomaly detection")
                return anomalies
            
            current_revenue = current_kpis.get("revenue_metrics", {})
            previous_revenue = historical_kpis[0].get("revenue_metrics", {}) if len(historical_kpis) > 0 else {}
            
            # Check MRR drop
            current_mrr = current_revenue.get("mrr", 0)
            previous_mrr = previous_revenue.get("mrr", 0)
            
            if previous_mrr > 0:
                mrr_change = ((current_mrr - previous_mrr) / previous_mrr)
                
                if mrr_change < -self.threshold:
                    anomalies.append({
                        "metric": "MRR",
                        "current_value": current_mrr,
                        "previous_value": previous_mrr,
                        "change_percent": mrr_change * 100,
                        "severity": "critical" if mrr_change < -0.30 else "warning",
                        "message": f"MRR dropped {abs(mrr_change * 100):.1f}% (₹{previous_mrr:,.0f} → ₹{current_mrr:,.0f})"
                    })
            
            # Check ARR drop
            current_arr = current_revenue.get("arr", 0)
            previous_arr = previous_revenue.get("arr", 0)
            
            if previous_arr > 0:
                arr_change = ((current_arr - previous_arr) / previous_arr)
                
                if arr_change < -self.threshold:
                    anomalies.append({
                        "metric": "ARR",
                        "current_value": current_arr,
                        "previous_value": previous_arr,
                        "change_percent": arr_change * 100,
                        "severity": "critical",
                        "message": f"ARR dropped {abs(arr_change * 100):.1f}% (₹{previous_arr:,.0f} → ₹{current_arr:,.0f})"
                    })
            
            # Check churn spike
            current_churn = current_revenue.get("churn_rate", 0)
            previous_churn = previous_revenue.get("churn_rate", 0)
            
            churn_increase = current_churn - previous_churn
            
            if churn_increase > 5:  # Absolute 5% increase
                anomalies.append({
                    "metric": "Churn Rate",
                    "current_value": current_churn,
                    "previous_value": previous_churn,
                    "change_percent": churn_increase,
                    "severity": "warning",
                    "message": f"Churn rate increased {churn_increase:.1f}% ({previous_churn:.1f}% → {current_churn:.1f}%)"
                })
            
            if anomalies:
                logger.warning(f"⚠️ {len(anomalies)} revenue anomalies detected")
            else:
                logger.info("✓ No revenue anomalies detected")
            
            return anomalies
        
        except Exception as e:
            logger.error(f"Failed to detect revenue anomalies: {e}", exc_info=True)
            return anomalies
    
    def detect_growth_anomalies(self, current_kpis: Dict[str, Any], historical_kpis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect growth-related anomalies.
        
        Args:
            current_kpis: Current KPI metrics
            historical_kpis: List of historical KPI records
        
        Returns:
            List of anomalies detected
        """
        logger.info("Detecting growth anomalies")
        
        anomalies = []
        
        try:
            if not historical_kpis:
                return anomalies
            
            current_growth = current_kpis.get("growth_metrics", {})
            previous_growth = historical_kpis[0].get("growth_metrics", {}) if len(historical_kpis) > 0 else {}
            
            # Check active users drop
            current_users = current_growth.get("total_active_users", 0)
            previous_users = previous_growth.get("total_active_users", 0)
            
            if previous_users > 0:
                user_change = ((current_users - previous_users) / previous_users)
                
                if user_change < -self.threshold:
                    anomalies.append({
                        "metric": "Active Users",
                        "current_value": current_users,
                        "previous_value": previous_users,
                        "change_percent": user_change * 100,
                        "severity": "warning",
                        "message": f"Active users dropped {abs(user_change * 100):.1f}% ({previous_users:,} → {current_users:,})"
                    })
            
            # Check page views drop
            current_pageviews = current_growth.get("total_page_views", 0)
            previous_pageviews = previous_growth.get("total_page_views", 0)
            
            if previous_pageviews > 0:
                pageview_change = ((current_pageviews - previous_pageviews) / previous_pageviews)
                
                if pageview_change < -self.threshold:
                    anomalies.append({
                        "metric": "Page Views",
                        "current_value": current_pageviews,
                        "previous_value": previous_pageviews,
                        "change_percent": pageview_change * 100,
                        "severity": "info",
                        "message": f"Page views dropped {abs(pageview_change * 100):.1f}% ({previous_pageviews:,} → {current_pageviews:,})"
                    })
            
            if anomalies:
                logger.warning(f"⚠️ {len(anomalies)} growth anomalies detected")
            else:
                logger.info("✓ No growth anomalies detected")
            
            return anomalies
        
        except Exception as e:
            logger.error(f"Failed to detect growth anomalies: {e}", exc_info=True)
            return anomalies
    
    def detect_all_anomalies(self, current_kpis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect all anomalies across all KPIs.
        
        Args:
            current_kpis: Current KPI metrics
        
        Returns:
            Dictionary with all anomalies and summary
        """
        logger.info("=== Detecting all anomalies ===")
        
        try:
            # Load historical data
            historical_kpis = self.load_historical_kpis(days=7)
            
            # Detect anomalies by category
            revenue_anomalies = self.detect_revenue_anomalies(current_kpis, historical_kpis)
            growth_anomalies = self.detect_growth_anomalies(current_kpis, historical_kpis)
            
            all_anomalies = revenue_anomalies + growth_anomalies
            
            # Categorize by severity
            critical = [a for a in all_anomalies if a["severity"] == "critical"]
            warnings = [a for a in all_anomalies if a["severity"] == "warning"]
            info = [a for a in all_anomalies if a["severity"] == "info"]
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "anomalies_detected": len(all_anomalies) > 0,
                "total_anomalies": len(all_anomalies),
                "critical_count": len(critical),
                "warning_count": len(warnings),
                "info_count": len(info),
                "critical": critical,
                "warnings": warnings,
                "info": info,
                "all_anomalies": all_anomalies
            }
            
            # Save current KPIs to history
            self.save_kpis(current_kpis)
            
            if result["anomalies_detected"]:
                logger.warning(f"⚠️ {result['total_anomalies']} anomalies detected ({result['critical_count']} critical)")
            else:
                logger.info("✓ No anomalies detected - all metrics healthy")
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from data_collector import DataCollector
    from kpi_calculator import KPICalculator
    
    # Collect data and calculate KPIs
    collector = DataCollector()
    data = collector.collect_all_data()
    
    calculator = KPICalculator()
    kpis = calculator.calculate_all_kpis(data)
    
    # Detect anomalies
    detector = AnomalyDetector()
    anomalies = detector.detect_all_anomalies(kpis)
    
    print(f"\n=== Anomaly Detection ===")
    print(f"Anomalies detected: {anomalies['anomalies_detected']}")
    print(f"Total: {anomalies['total_anomalies']}")
    print(f"Critical: {anomalies['critical_count']}")
    print(f"Warnings: {anomalies['warning_count']}")
