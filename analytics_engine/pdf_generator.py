"""
PDF Generator Module - Generate weekly PDF reports with matplotlib visualizations
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns

logger = logging.getLogger("PDFGenerator")

# Set style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (11, 8)
plt.rcParams["font.size"] = 10


class PDFGenerator:
    """Generate PDF reports with visualizations."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize PDF generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"PDFGenerator initialized (output: {self.output_dir})")
    
    def create_revenue_chart(self, kpis: Dict[str, Any]) -> plt.Figure:
        """Create revenue metrics chart."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Revenue Metrics", fontsize=16, fontweight="bold")
        
        revenue_metrics = kpis.get("revenue_metrics", {})
        
        # MRR/ARR chart
        ax1 = axes[0, 0]
        mrr = revenue_metrics.get("mrr", 0)
        arr = revenue_metrics.get("arr", 0)
        
        ax1.bar(["MRR", "ARR"], [mrr, arr], color=["#2196F3", "#4CAF50"])
        ax1.set_ylabel("Amount (₹)")
        ax1.set_title("Monthly & Annual Recurring Revenue")
        ax1.ticklabel_format(style='plain', axis='y')
        
        # Add value labels
        for i, v in enumerate([mrr, arr]):
            ax1.text(i, v, f'₹{v:,.0f}', ha='center', va='bottom')
        
        # Active vs Cancelled subscriptions
        ax2 = axes[0, 1]
        active_subs = revenue_metrics.get("active_subscriptions", 0)
        cancelled_subs = revenue_metrics.get("cancelled_subscriptions", 0)
        
        ax2.pie([active_subs, cancelled_subs], 
                labels=["Active", "Cancelled"],
                autopct='%1.1f%%',
                colors=["#4CAF50", "#f44336"],
                startangle=90)
        ax2.set_title("Subscription Status")
        
        # Churn rate gauge
        ax3 = axes[1, 0]
        churn_rate = revenue_metrics.get("churn_rate", 0)
        
        ax3.bar(["Churn Rate"], [churn_rate], color="#FF9800")
        ax3.set_ylabel("Percentage (%)")
        ax3.set_title("Customer Churn Rate")
        ax3.set_ylim([0, 50])
        ax3.axhline(y=20, color='r', linestyle='--', label='Target (20%)')
        ax3.legend()
        
        # Add value label
        ax3.text(0, churn_rate, f'{churn_rate:.1f}%', ha='center', va='bottom')
        
        # ARPU
        ax4 = axes[1, 1]
        arpu = revenue_metrics.get("arpu", 0)
        total_revenue = revenue_metrics.get("total_revenue", 0)
        
        ax4.bar(["ARPU", "Total Revenue"], [arpu, total_revenue / 1000], 
                color=["#9C27B0", "#FF5722"])
        ax4.set_ylabel("ARPU (₹) / Revenue (₹K)")
        ax4.set_title("Average Revenue Per User")
        
        # Add value labels
        ax4.text(0, arpu, f'₹{arpu:,.0f}', ha='center', va='bottom')
        ax4.text(1, total_revenue/1000, f'₹{total_revenue/1000:,.0f}K', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def create_growth_chart(self, kpis: Dict[str, Any]) -> plt.Figure:
        """Create growth metrics chart."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Growth Metrics", fontsize=16, fontweight="bold")
        
        growth_metrics = kpis.get("growth_metrics", {})
        
        # Users overview
        ax1 = axes[0, 0]
        total_users = growth_metrics.get("total_active_users", 0)
        new_users = growth_metrics.get("total_new_users", 0)
        
        ax1.bar(["Total Active", "New Users"], [total_users, new_users], 
                color=["#2196F3", "#4CAF50"])
        ax1.set_ylabel("Count")
        ax1.set_title("User Metrics (Last 30 Days)")
        
        for i, v in enumerate([total_users, new_users]):
            ax1.text(i, v, f'{v:,}', ha='center', va='bottom')
        
        # Growth rates
        ax2 = axes[0, 1]
        user_growth = growth_metrics.get("user_growth_wow", 0)
        pageview_growth = growth_metrics.get("pageview_growth_wow", 0)
        
        colors = ['#4CAF50' if x > 0 else '#f44336' for x in [user_growth, pageview_growth]]
        ax2.barh(["User Growth", "PageView Growth"], [user_growth, pageview_growth], color=colors)
        ax2.set_xlabel("Week-over-Week Growth (%)")
        ax2.set_title("Growth Rates (WoW)")
        ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        for i, v in enumerate([user_growth, pageview_growth]):
            ax2.text(v, i, f' {v:+.1f}%', va='center')
        
        # Daily averages
        ax3 = axes[1, 0]
        avg_daily_users = growth_metrics.get("avg_daily_users", 0)
        avg_daily_pageviews = growth_metrics.get("avg_daily_pageviews", 0)
        
        ax3.bar(["Avg Daily Users", "Avg Daily PageViews"], 
                [avg_daily_users, avg_daily_pageviews/10],  # Scale pageviews
                color=["#9C27B0", "#FF5722"])
        ax3.set_ylabel("Count")
        ax3.set_title("Daily Averages")
        
        ax3.text(0, avg_daily_users, f'{avg_daily_users:,.0f}', ha='center', va='bottom')
        ax3.text(1, avg_daily_pageviews/10, f'{avg_daily_pageviews:,.0f}', ha='center', va='bottom')
        
        # Total page views
        ax4 = axes[1, 1]
        total_pageviews = growth_metrics.get("total_page_views", 0)
        
        ax4.bar(["Total Page Views"], [total_pageviews], color="#00BCD4", width=0.4)
        ax4.set_ylabel("Count")
        ax4.set_title("Total Page Views (Last 30 Days)")
        ax4.ticklabel_format(style='plain', axis='y')
        
        ax4.text(0, total_pageviews, f'{total_pageviews:,}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def create_referrers_chart(self, kpis: Dict[str, Any]) -> plt.Figure:
        """Create top referrers chart."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle("Top Referrers", fontsize=16, fontweight="bold")
        
        top_referrers = kpis.get("top_referrers", [])
        
        if not top_referrers:
            ax = axes[0]
            ax.text(0.5, 0.5, "No referral data available", 
                   ha='center', va='center', fontsize=14)
            ax.set_xlim([0, 1])
            ax.set_ylim([0, 1])
            ax.axis('off')
            return fig
        
        df = pd.DataFrame(top_referrers).head(10)
        
        # Referrals by count
        ax1 = axes[0]
        ax1.barh(df["referrer_name"], df["referral_count"], color="#2196F3")
        ax1.set_xlabel("Referral Count")
        ax1.set_title("Top Referrers by Count")
        ax1.invert_yaxis()
        
        for i, v in enumerate(df["referral_count"]):
            ax1.text(v, i, f' {v}', va='center')
        
        # Referrals by revenue
        ax2 = axes[1]
        ax2.barh(df["referrer_name"], df["revenue"], color="#4CAF50")
        ax2.set_xlabel("Revenue (₹)")
        ax2.set_title("Top Referrers by Revenue")
        ax2.invert_yaxis()
        ax2.ticklabel_format(style='plain', axis='x')
        
        for i, v in enumerate(df["revenue"]):
            ax2.text(v, i, f' ₹{v:,.0f}', va='center')
        
        plt.tight_layout()
        return fig
    
    def create_prompt_stats_chart(self, kpis: Dict[str, Any]) -> plt.Figure:
        """Create prompt statistics chart."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("AI Prompt Statistics", fontsize=16, fontweight="bold")
        
        prompt_stats = kpis.get("prompt_statistics", {})
        
        # Total prompts
        ax1 = axes[0, 0]
        total_prompts = prompt_stats.get("total_prompts", 0)
        
        ax1.bar(["Total Prompts"], [total_prompts], color="#9C27B0", width=0.4)
        ax1.set_ylabel("Count")
        ax1.set_title("Total AI Prompts (Last 30 Days)")
        ax1.ticklabel_format(style='plain', axis='y')
        
        ax1.text(0, total_prompts, f'{total_prompts:,}', ha='center', va='bottom')
        
        # Success rate
        ax2 = axes[0, 1]
        success_rate = prompt_stats.get("overall_success_rate", 0)
        
        ax2.bar(["Success Rate"], [success_rate], color="#4CAF50", width=0.4)
        ax2.set_ylabel("Percentage (%)")
        ax2.set_title("Overall Success Rate")
        ax2.set_ylim([0, 100])
        
        ax2.text(0, success_rate, f'{success_rate:.1f}%', ha='center', va='bottom')
        
        # Most used feature
        ax3 = axes[1, 0]
        most_used = prompt_stats.get("most_used_feature", "N/A")
        most_used_count = prompt_stats.get("most_used_count", 0)
        
        ax3.bar([most_used], [most_used_count], color="#FF5722", width=0.5)
        ax3.set_ylabel("Prompt Count")
        ax3.set_title("Most Used Feature")
        ax3.tick_params(axis='x', rotation=45)
        
        ax3.text(0, most_used_count, f'{most_used_count:,}', ha='center', va='bottom')
        
        # Best performing feature
        ax4 = axes[1, 1]
        best_feature = prompt_stats.get("best_performing_feature", "N/A")
        best_success = prompt_stats.get("best_success_rate", 0)
        
        ax4.bar([best_feature], [best_success], color="#00BCD4", width=0.5)
        ax4.set_ylabel("Success Rate (%)")
        ax4.set_title("Best Performing Feature")
        ax4.set_ylim([0, 100])
        ax4.tick_params(axis='x', rotation=45)
        
        ax4.text(0, best_success, f'{best_success:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def create_summary_page(self, kpis: Dict[str, Any], anomalies: Dict[str, Any]) -> plt.Figure:
        """Create executive summary page."""
        fig = plt.figure(figsize=(11, 14))
        fig.suptitle("SURESH AI ORIGIN - Weekly Analytics Report", 
                    fontsize=18, fontweight="bold", y=0.98)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        plt.figtext(0.5, 0.95, f"Generated: {timestamp}", 
                   ha='center', fontsize=10, style='italic')
        
        # KPI Summary
        plt.figtext(0.1, 0.88, "KEY PERFORMANCE INDICATORS", 
                   fontsize=14, fontweight="bold")
        
        revenue_metrics = kpis.get("revenue_metrics", {})
        growth_metrics = kpis.get("growth_metrics", {})
        prompt_stats = kpis.get("prompt_statistics", {})
        
        summary_text = f"""
MRR (Monthly Recurring Revenue):        ₹{revenue_metrics.get('mrr', 0):,.2f}
ARR (Annual Recurring Revenue):         ₹{revenue_metrics.get('arr', 0):,.2f}
Active Subscriptions:                   {revenue_metrics.get('active_subscriptions', 0):,}
Churn Rate:                            {revenue_metrics.get('churn_rate', 0):.2f}%

Total Active Users (30d):              {growth_metrics.get('total_active_users', 0):,}
New Users (30d):                       {growth_metrics.get('total_new_users', 0):,}
User Growth (WoW):                     {growth_metrics.get('user_growth_wow', 0):+.1f}%
Page View Growth (WoW):                {growth_metrics.get('pageview_growth_wow', 0):+.1f}%

Total AI Prompts (30d):                {prompt_stats.get('total_prompts', 0):,}
Overall Success Rate:                  {prompt_stats.get('overall_success_rate', 0):.1f}%
Most Used Feature:                     {prompt_stats.get('most_used_feature', 'N/A')}
"""
        
        plt.figtext(0.1, 0.45, summary_text, fontsize=11, family='monospace')
        
        # Anomalies section
        plt.figtext(0.1, 0.38, "ANOMALIES & ALERTS", 
                   fontsize=14, fontweight="bold", color='#f44336')
        
        if anomalies.get("anomalies_detected"):
            anomaly_text = f"""
Total Anomalies:     {anomalies.get('total_anomalies', 0)}
Critical:           {anomalies.get('critical_count', 0)}
Warnings:           {anomalies.get('warning_count', 0)}

Recent Anomalies:
"""
            for i, anom in enumerate(anomalies.get("all_anomalies", [])[:5]):
                anomaly_text += f"• {anom['message']}\n"
            
            color = '#f44336'
        else:
            anomaly_text = "\n✓ No anomalies detected - all metrics healthy!"
            color = '#4CAF50'
        
        plt.figtext(0.1, 0.10, anomaly_text, fontsize=10, color=color)
        
        plt.axis('off')
        return fig
    
    def generate_weekly_report(self, kpis: Dict[str, Any], anomalies: Dict[str, Any]) -> str:
        """
        Generate weekly PDF report with all charts.
        
        Args:
            kpis: Dictionary with all KPIs
            anomalies: Dictionary with anomaly detection results
        
        Returns:
            Path to generated PDF file
        """
        logger.info("Generating weekly PDF report")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"weekly_report_{timestamp}.pdf"
            filepath = self.output_dir / filename
            
            with PdfPages(filepath) as pdf:
                # Page 1: Executive Summary
                fig1 = self.create_summary_page(kpis, anomalies)
                pdf.savefig(fig1, bbox_inches='tight')
                plt.close(fig1)
                
                # Page 2: Revenue Metrics
                fig2 = self.create_revenue_chart(kpis)
                pdf.savefig(fig2, bbox_inches='tight')
                plt.close(fig2)
                
                # Page 3: Growth Metrics
                fig3 = self.create_growth_chart(kpis)
                pdf.savefig(fig3, bbox_inches='tight')
                plt.close(fig3)
                
                # Page 4: Referrers
                fig4 = self.create_referrers_chart(kpis)
                pdf.savefig(fig4, bbox_inches='tight')
                plt.close(fig4)
                
                # Page 5: Prompt Statistics
                fig5 = self.create_prompt_stats_chart(kpis)
                pdf.savefig(fig5, bbox_inches='tight')
                plt.close(fig5)
                
                # Add metadata
                d = pdf.infodict()
                d['Title'] = 'SURESH AI ORIGIN - Weekly Analytics Report'
                d['Author'] = 'Analytics Engine'
                d['Subject'] = 'KPIs, Growth, Revenue, Anomalies'
                d['Keywords'] = 'Analytics, MRR, Churn, AI, Prompts'
                d['CreationDate'] = datetime.now()
            
            logger.info(f"✓ PDF report generated: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from data_collector import DataCollector
    from kpi_calculator import KPICalculator
    from anomaly_detector import AnomalyDetector
    
    # Collect data
    collector = DataCollector()
    data = collector.collect_all_data()
    
    # Calculate KPIs
    calculator = KPICalculator()
    kpis = calculator.calculate_all_kpis(data)
    
    # Detect anomalies
    detector = AnomalyDetector()
    anomalies = detector.detect_all_anomalies(kpis)
    
    # Generate PDF
    generator = PDFGenerator()
    pdf_path = generator.generate_weekly_report(kpis, anomalies)
    
    print(f"\n✓ PDF report generated: {pdf_path}")
