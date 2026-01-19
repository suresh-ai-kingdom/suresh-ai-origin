"""
Rarest Task Automation CLI Launcher (2026) - Suresh AI Origin
One-command access to complete task automation ecosystem.

Commands:
- python rarest_task_cli.py browse         → List all templates
- python rarest_task_cli.py search <query> → Search templates
- python rarest_task_cli.py buy <template> <count> → Purchase & execute jobs
- python rarest_task_cli.py scale <count>  → Auto-scale workers & dispatch N jobs
- python rarest_task_cli.py dashboard      → Show live dashboard
- python rarest_task_cli.py export         → Export CSV/HTML reports
- python rarest_task_cli.py stats          → Quick stats
- python rarest_task_cli.py demo           → Full automation demo

Integration: Unified entry point for all task automation modules.
"""

import sys
import json
import time

try:
    from rarest_task_automation_engine import RarestTaskAutomationEngine
except Exception:
    RarestTaskAutomationEngine = None  # type: ignore

try:
    from rarest_task_dispatcher_scaling import RarestTaskDispatcher
except Exception:
    RarestTaskDispatcher = None  # type: ignore

try:
    from rarest_task_template_marketplace import RarestTaskTemplateMarketplace
except Exception:
    RarestTaskTemplateMarketplace = None  # type: ignore

try:
    from rarest_task_automation_dashboard import RarestTaskAutomationDashboard
except Exception:
    RarestTaskAutomationDashboard = None  # type: ignore


class RarestTaskCLI:
    """CLI interface for task automation platform."""

    def __init__(self):
        self.engine = RarestTaskAutomationEngine() if RarestTaskAutomationEngine else None
        self.dispatcher = RarestTaskDispatcher() if RarestTaskDispatcher else None
        self.marketplace = RarestTaskTemplateMarketplace() if RarestTaskTemplateMarketplace else None
        self.dashboard = RarestTaskAutomationDashboard() if RarestTaskAutomationDashboard else None

    def cmd_browse(self):
        """Browse all available templates."""
        if not self.marketplace:
            print("❌ Marketplace module unavailable")
            return
        templates = self.marketplace.list_templates()
        print(f"\n🔍 FOUND {len(templates)} TEMPLATES\n")
        for tpl in templates:
            print(f"  📦 {tpl['name']}")
            print(f"     ID: {tpl['template_id']}")
            print(f"     Type: {tpl['task_type']} | Pay: ₹{tpl['base_pay_inr']} | Rating: {tpl['rating']}/5")
            print(f"     {tpl['description']}\n")

    def cmd_search(self, query: str):
        """Search templates by keyword."""
        if not self.marketplace:
            print("❌ Marketplace module unavailable")
            return
        results = self.marketplace.search_templates(query)
        print(f"\n🔎 SEARCH RESULTS FOR '{query}': {len(results)} matches\n")
        for tpl in results:
            print(f"  📄 {tpl['name']} (₹{tpl['base_pay_inr']}) — {tpl['description']}")

    def cmd_buy(self, template_id: str, count: int):
        """Purchase jobs from template."""
        if not self.marketplace or not self.dispatcher:
            print("❌ Required modules unavailable")
            return
        print(f"\n💰 PURCHASING {count} jobs using template '{template_id}'...")
        purchase = self.marketplace.purchase_template_job(template_id, count, buyer_id="cli_user")
        print(f"✅ Purchase ID: {purchase['purchase_id']}")
        print(f"   Total Cost: ₹{purchase['total_cost_inr']:,.2f}")
        print(f"\n🚀 DISPATCHING {count} jobs to workers...")
        jobs = [{"task_type": "writing", "task_id": f"job_{i}"} for i in range(count)]
        job_ids = self.dispatcher.dispatch_bulk(jobs)
        self.dispatcher.auto_scale(max_workers=10)
        print(f"✅ Dispatched {len(job_ids)} jobs")
        print("⏳ Waiting for completion...")
        results = self.dispatcher.wait_for_completion(job_ids, timeout_sec=60)
        perf = self.dispatcher.calculate_metrics(results)
        earnings = self.dispatcher.process_earnings(results, base_pay_per_task=50)
        print(f"\n📊 RESULTS:")
        print(f"   Completed: {perf['success_count']}/{len(results)}")
        print(f"   Avg Quality: {perf['avg_quality']}")
        print(f"   Total Earnings: ₹{earnings['total_revenue_inr']:,.2f}")
        print(f"   Net Profit: ₹{earnings['net_profit_inr']:,.2f}")

    def cmd_scale(self, count: int):
        """Auto-scale and dispatch jobs."""
        if not self.dispatcher:
            print("❌ Dispatcher module unavailable")
            return
        print(f"\n⚡ SCALING TO HANDLE {count} JOBS...")
        result = self.dispatcher.run_job_batch(count, task_type="writing", max_workers=12, rarity_score=100)
        print(f"✅ BATCH COMPLETE:")
        print(f"   Jobs: {result['completed']}/{result['job_count']}")
        print(f"   Workers: {result['workers_active']}")
        print(f"   Earnings: ₹{result['earnings']['total_revenue_inr']:,.2f}")
        print(f"   Avg Quality: {result['performance']['avg_quality']}")
        print(f"   Latency (p95): {result['performance']['latency_p95']}s")

    def cmd_dashboard(self):
        """Show live dashboard."""
        if not self.dashboard:
            print("❌ Dashboard module unavailable")
            return
        summary = self.dashboard.get_dashboard_summary()
        print("\n📊 LIVE DASHBOARD\n")
        print(f"Queue Depth: {summary['live_metrics']['job_queue_depth']}")
        print(f"Active Workers: {summary['live_metrics']['workers_active']}")
        print(f"Jobs Completed Today: {summary['live_metrics']['jobs_completed_today']}")
        print(f"Earnings Velocity: ₹{summary['live_metrics']['earnings_velocity_inr_per_min']:.2f}/min")
        print(f"Avg Quality: {summary['live_metrics']['avg_quality_score']}")
        print(f"\n⚠️ ALERTS ({len(summary['alerts'])})")
        for alert in summary["alerts"]:
            print(f"   [{alert['severity'].upper()}] {alert['message']}")
        print(f"\n💰 EARNINGS TODAY")
        print(f"   Revenue: ₹{summary['earnings_today']['total_revenue_inr']:,.2f}")
        print(f"   Net Profit: ₹{summary['earnings_today']['net_profit_inr']:,.2f}")
        print(f"   ROI: {summary['earnings_today']['roi_percent']}%")

    def cmd_export(self):
        """Export reports."""
        if not self.dashboard:
            print("❌ Dashboard module unavailable")
            return
        csv = self.dashboard.export_csv_report()
        filename = f"task_report_{int(time.time())}.csv"
        with open(filename, "w") as f:
            f.write(csv)
        print(f"\n📄 CSV REPORT EXPORTED: {filename}")
        html = self.dashboard.format_html_dashboard()
        html_filename = f"dashboard_{int(time.time())}.html"
        with open(html_filename, "w") as f:
            f.write(html)
        print(f"🌐 HTML DASHBOARD EXPORTED: {html_filename}")

    def cmd_stats(self):
        """Quick stats."""
        if not self.dashboard:
            print("❌ Dashboard module unavailable")
            return
        stats = self.dashboard.get_quick_stats()
        print("\n⚡ QUICK STATS")
        print(json.dumps(stats, indent=2))

    def cmd_demo(self):
        """Full automation demo."""
        print("\n🎬 FULL AUTOMATION DEMO STARTING...\n")
        # Step 1: Browse templates
        print("STEP 1: Browse Templates")
        if self.marketplace:
            templates = self.marketplace.list_templates()
            print(f"   Found {len(templates)} templates ✅\n")
        # Step 2: Purchase jobs
        print("STEP 2: Purchase 20 SEO Blog Posts")
        if self.marketplace:
            purchase = self.marketplace.purchase_template_job("seo_blog_post", 20, buyer_id="demo_user")
            print(f"   Purchase ID: {purchase['purchase_id']} ✅")
            print(f"   Cost: ₹{purchase['total_cost_inr']:,.2f}\n")
        # Step 3: Dispatch & execute
        print("STEP 3: Dispatch & Execute Jobs")
        if self.dispatcher:
            result = self.dispatcher.run_job_batch(20, task_type="writing", max_workers=8, rarity_score=100)
            print(f"   Completed: {result['completed']}/20 ✅")
            print(f"   Workers: {result['workers_active']}")
            print(f"   Earnings: ₹{result['earnings']['total_revenue_inr']:,.2f}\n")
        # Step 4: Dashboard
        print("STEP 4: Show Dashboard")
        if self.dashboard:
            stats = self.dashboard.get_quick_stats()
            print(f"   Jobs Today: {stats['jobs_today']}")
            print(f"   Earnings: ₹{stats['earnings_inr']:,.2f} ✅\n")
        print("🎉 DEMO COMPLETE! Full automation cycle executed successfully.")


def main():
    cli = RarestTaskCLI()
    if len(sys.argv) < 2:
        print("""
🚀 RAREST TASK AUTOMATION CLI

Commands:
  browse              — List all templates
  search <query>      — Search templates
  buy <template> <N>  — Purchase & execute N jobs
  scale <N>           — Auto-scale & dispatch N jobs
  dashboard           — Show live dashboard
  export              — Export CSV/HTML reports
  stats               — Quick stats
  demo                — Full automation demo

Example:
  python rarest_task_cli.py demo
  python rarest_task_cli.py buy seo_blog_post 50
  python rarest_task_cli.py scale 1000
        """)
        return
    command = sys.argv[1].lower()
    if command == "browse":
        cli.cmd_browse()
    elif command == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        cli.cmd_search(query)
    elif command == "buy":
        template_id = sys.argv[2] if len(sys.argv) > 2 else "seo_blog_post"
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        cli.cmd_buy(template_id, count)
    elif command == "scale":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        cli.cmd_scale(count)
    elif command == "dashboard":
        cli.cmd_dashboard()
    elif command == "export":
        cli.cmd_export()
    elif command == "stats":
        cli.cmd_stats()
    elif command == "demo":
        cli.cmd_demo()
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
