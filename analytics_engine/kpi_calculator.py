"""
KPI Calculator Module - Calculate MRR, churn, top referrers, prompt stats
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger("KPICalculator")


class KPICalculator:
    """Calculate key performance indicators from collected data."""
    
    def __init__(self):
        """Initialize KPI calculator."""
        logger.info("KPICalculator initialized")
    
    def calculate_mrr(self, stripe_data: Dict[str, Any]) -> float:
        """
        Calculate Monthly Recurring Revenue.
        
        Args:
            stripe_data: Stripe data dictionary
        
        Returns:
            MRR in rupees
        """
        logger.info("Calculating MRR")
        
        try:
            subscriptions = stripe_data.get("subscriptions", [])
            
            if not subscriptions:
                # Fallback to active_subscriptions count
                active_subs = stripe_data.get("active_subscriptions", 0)
                avg_price = 1999  # Default plan price
                mrr = active_subs * avg_price
            else:
                # Sum all active subscription amounts
                mrr = 0
                for sub in subscriptions:
                    if sub.get("status") == "active":
                        # Stripe stores amounts in cents/paise
                        amount = sub.get("items", {}).get("data", [{}])[0].get("price", {}).get("unit_amount", 0)
                        mrr += amount / 100
            
            logger.info(f"✓ MRR: ₹{mrr:,.2f}")
            return mrr
        
        except Exception as e:
            logger.error(f"Failed to calculate MRR: {e}", exc_info=True)
            return 0.0
    
    def calculate_churn_rate(self, stripe_data: Dict[str, Any]) -> float:
        """
        Calculate customer churn rate.
        
        Args:
            stripe_data: Stripe data dictionary
        
        Returns:
            Churn rate as percentage (0-100)
        """
        logger.info("Calculating churn rate")
        
        try:
            active_subs = stripe_data.get("active_subscriptions", 0)
            cancelled_subs = stripe_data.get("cancelled_subscriptions", 0)
            
            if active_subs + cancelled_subs == 0:
                churn_rate = 0.0
            else:
                churn_rate = (cancelled_subs / (active_subs + cancelled_subs)) * 100
            
            logger.info(f"✓ Churn rate: {churn_rate:.2f}%")
            return churn_rate
        
        except Exception as e:
            logger.error(f"Failed to calculate churn rate: {e}", exc_info=True)
            return 0.0
    
    def get_top_referrers(self, referral_data: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
        """
        Get top referrers sorted by revenue or count.
        
        Args:
            referral_data: DataFrame with referral data
            limit: Number of top referrers to return
        
        Returns:
            DataFrame with top referrers
        """
        logger.info(f"Getting top {limit} referrers")
        
        try:
            if referral_data.empty:
                logger.warning("Referral data is empty")
                return pd.DataFrame()
            
            # Group by referrer and sum
            top_referrers = referral_data.groupby("referrer_name").agg({
                "referral_count": "sum",
                "revenue": "sum"
            }).sort_values(by="revenue", ascending=False).head(limit)
            
            logger.info(f"✓ Top referrer: {top_referrers.index[0] if len(top_referrers) > 0 else 'N/A'}")
            return top_referrers.reset_index()
        
        except Exception as e:
            logger.error(f"Failed to get top referrers: {e}", exc_info=True)
            return pd.DataFrame()
    
    def calculate_prompt_statistics(self, prompt_stats: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate aggregate prompt statistics.
        
        Args:
            prompt_stats: DataFrame with prompt usage data
        
        Returns:
            Dictionary with prompt metrics
        """
        logger.info("Calculating prompt statistics")
        
        try:
            if prompt_stats.empty:
                logger.warning("Prompt stats is empty")
                return {}
            
            total_prompts = prompt_stats["prompt_count"].sum()
            avg_tokens = prompt_stats["avg_tokens"].mean()
            avg_success_rate = prompt_stats["success_rate"].mean()
            
            # Most used feature
            most_used = prompt_stats.loc[prompt_stats["prompt_count"].idxmax()]
            
            # Highest success rate
            best_performing = prompt_stats.loc[prompt_stats["success_rate"].idxmax()]
            
            stats = {
                "total_prompts": int(total_prompts),
                "avg_tokens_per_prompt": float(avg_tokens),
                "overall_success_rate": float(avg_success_rate * 100),
                "most_used_feature": most_used["feature_name"] if "feature_name" in most_used else "N/A",
                "most_used_count": int(most_used["prompt_count"]),
                "best_performing_feature": best_performing["feature_name"] if "feature_name" in best_performing else "N/A",
                "best_success_rate": float(best_performing["success_rate"] * 100)
            }
            
            logger.info(f"✓ Total prompts: {total_prompts:,}")
            return stats
        
        except Exception as e:
            logger.error(f"Failed to calculate prompt statistics: {e}", exc_info=True)
            return {}
    
    def calculate_revenue_metrics(self, stripe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive revenue metrics.
        
        Args:
            stripe_data: Stripe data dictionary
        
        Returns:
            Dictionary with revenue metrics
        """
        logger.info("Calculating revenue metrics")
        
        try:
            total_revenue = stripe_data.get("total_revenue", 0.0)
            active_subs = stripe_data.get("active_subscriptions", 0)
            
            # Calculate Average Revenue Per User (ARPU)
            arpu = total_revenue / active_subs if active_subs > 0 else 0
            
            # Calculate MRR
            mrr = self.calculate_mrr(stripe_data)
            
            # Calculate ARR (Annual Recurring Revenue)
            arr = mrr * 12
            
            # Calculate churn
            churn_rate = self.calculate_churn_rate(stripe_data)
            
            metrics = {
                "total_revenue": total_revenue,
                "mrr": mrr,
                "arr": arr,
                "arpu": arpu,
                "active_subscriptions": active_subs,
                "churn_rate": churn_rate
            }
            
            logger.info(f"✓ Revenue metrics calculated")
            return metrics
        
        except Exception as e:
            logger.error(f"Failed to calculate revenue metrics: {e}", exc_info=True)
            return {}
    
    def calculate_growth_metrics(self, ga_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate growth metrics from GA data.
        
        Args:
            ga_data: DataFrame with GA metrics
        
        Returns:
            Dictionary with growth metrics
        """
        logger.info("Calculating growth metrics")
        
        try:
            if ga_data.empty:
                logger.warning("GA data is empty")
                return {}
            
            # Sort by date
            ga_data["date"] = pd.to_datetime(ga_data["date"])
            ga_data = ga_data.sort_values("date")
            
            # Group by date
            daily_metrics = ga_data.groupby("date").agg({
                "active_users": "sum",
                "new_users": "sum",
                "page_views": "sum"
            })
            
            # Calculate week-over-week growth
            if len(daily_metrics) >= 14:
                last_week = daily_metrics.tail(7)
                prev_week = daily_metrics.tail(14).head(7)
                
                user_growth = ((last_week["active_users"].sum() - prev_week["active_users"].sum()) / 
                              prev_week["active_users"].sum() * 100 if prev_week["active_users"].sum() > 0 else 0)
                
                pageview_growth = ((last_week["page_views"].sum() - prev_week["page_views"].sum()) / 
                                  prev_week["page_views"].sum() * 100 if prev_week["page_views"].sum() > 0 else 0)
            else:
                user_growth = 0
                pageview_growth = 0
            
            metrics = {
                "total_active_users": int(daily_metrics["active_users"].sum()),
                "total_new_users": int(daily_metrics["new_users"].sum()),
                "total_page_views": int(daily_metrics["page_views"].sum()),
                "user_growth_wow": float(user_growth),
                "pageview_growth_wow": float(pageview_growth),
                "avg_daily_users": float(daily_metrics["active_users"].mean()),
                "avg_daily_pageviews": float(daily_metrics["page_views"].mean())
            }
            
            logger.info(f"✓ Growth metrics calculated")
            return metrics
        
        except Exception as e:
            logger.error(f"Failed to calculate growth metrics: {e}", exc_info=True)
            return {}
    
    def calculate_all_kpis(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate all KPIs from collected data.
        
        Args:
            all_data: Dictionary with all collected data
        
        Returns:
            Dictionary with all KPIs
        """
        logger.info("=== Calculating all KPIs ===")
        
        try:
            kpis = {
                "timestamp": datetime.now().isoformat(),
                "revenue_metrics": self.calculate_revenue_metrics(all_data.get("stripe_data", {})),
                "growth_metrics": self.calculate_growth_metrics(all_data.get("ga_data", pd.DataFrame())),
                "top_referrers": self.get_top_referrers(all_data.get("referral_data", pd.DataFrame())).to_dict("records"),
                "prompt_statistics": self.calculate_prompt_statistics(all_data.get("prompt_stats", pd.DataFrame()))
            }
            
            logger.info("✓ All KPIs calculated successfully")
            return kpis
        
        except Exception as e:
            logger.error(f"Failed to calculate all KPIs: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from data_collector import DataCollector
    
    collector = DataCollector()
    data = collector.collect_all_data()
    
    calculator = KPICalculator()
    kpis = calculator.calculate_all_kpis(data)
    
    print("\n=== KPI Summary ===")
    print(f"MRR: ₹{kpis['revenue_metrics'].get('mrr', 0):,.2f}")
    print(f"Churn Rate: {kpis['revenue_metrics'].get('churn_rate', 0):.2f}%")
    print(f"Total Prompts: {kpis['prompt_statistics'].get('total_prompts', 0):,}")
