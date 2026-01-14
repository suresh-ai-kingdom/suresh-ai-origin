#!/usr/bin/env python3
"""Daily automation runner - executes all workflow automations."""

import os
import time
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from automation_workflows import execute_all_workflows
from scripts.nightly_backup import run_once as backup_run_once, notify

DAYS_BACK = int(os.getenv("AUTOMATION_DAYS_BACK", "30"))


def main() -> int:
    """Run all automated workflows and report results."""
    print(f"{'='*60}")
    print(f"Daily Automation Run: {datetime.now()}")
    print(f"{'='*60}\n")
    
    started = time.time()
    
    try:
        # Execute all workflow automations
        print("🤖 Running workflow automations...")
        results = execute_all_workflows(days_back=DAYS_BACK)
        
        total = results.get('total_actions', 0)
        workflows = results.get('workflows', {})
        
        # Build summary
        summary = [f"✅ Daily automations completed in {time.time() - started:.1f}s"]
        summary.append(f"Total actions: {total}")
        summary.append("")
        
        for name, data in workflows.items():
            executed = data.get('executed', 0)
            error = data.get('error')
            status = '❌' if error else '✅'
            summary.append(f"{status} {name}: {executed} actions")
            if error:
                summary.append(f"   Error: {error}")
        
        summary_text = '\n'.join(summary)
        print(f"\n{summary_text}\n")
        
        # Send success notification
        notify(
            "Daily automations complete",
            summary_text,
            include_success=os.getenv("AUTOMATION_NOTIFY_SUCCESS", "false").lower() == "true"
        )
        
        return 0
        
    except Exception as exc:
        error_msg = f"Daily automation run crashed: {exc}"
        print(f"❌ {error_msg}")
        notify("Daily automation failed", error_msg)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
