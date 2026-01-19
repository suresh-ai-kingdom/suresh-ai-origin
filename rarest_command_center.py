"""
Rarest Command Center (2026) - Suresh AI Origin
Unified control hub for the 1% rarest stack: voice parsing, launchpad, physical bridges, dashboard, and alerts.

Features
- CLI loop: accepts text/voice-style commands, routes to launchpad/physical bridge/dashboard.
- NLP via voice_interface parser; rarity/auth enforced (>=98).
- Physical dispatch: uses real-world bridge (strict gate) with fallback alert.
- Dashboard pull: economy dashboard KPIs + alerts unified with telemetry stream.
- Web mode (optional): /center JSON + simple HTML (port 8003) for remote view.
- Demo command: "Launch rare drone optimizer for Mysuru traffic" → parse → launch → physical deploy → telemetry + evolution summary.
"""

import json
import logging
import threading
import time
from typing import Dict, Any, Optional

try:
    from flask import Flask, jsonify
except Exception:
    Flask = None  # type: ignore
    jsonify = None  # type: ignore

try:
    from rarest_agent_voice_interface import RarestVoiceLaunchpad
except Exception:
    RarestVoiceLaunchpad = None  # type: ignore

try:
    from rarest_agent_launchpad import RarestLaunchpad
except Exception:
    RarestLaunchpad = None  # type: ignore

try:
    from rarest_real_world_bridge import RarestRealWorldBridge
except Exception:
    RarestRealWorldBridge = None  # type: ignore

try:
    from rarest_agent_economy_dashboard import RarestEconomyDashboard
except Exception:
    RarestEconomyDashboard = None  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class RarestCommandCenter:
    def __init__(self, min_rarity: float = 98.0):
        self.min_rarity = min_rarity
        self.voice = RarestVoiceLaunchpad() if RarestVoiceLaunchpad else None
        self.launchpad = RarestLaunchpad() if RarestLaunchpad else None
        self.bridge = RarestRealWorldBridge() if RarestRealWorldBridge else None
        self.dashboard = RarestEconomyDashboard() if RarestEconomyDashboard else None
        self.last_unified: Dict[str, Any] = {}
        self.user_id = "suresh"
        self.user_rarity = 100.0

    # --------------------------------------------------------------
    def _rarity_gate(self, rarity: float):
        if rarity < self.min_rarity:
            raise PermissionError("Rarity gate: command center is elite-only (>=98)")

    # --------------------------------------------------------------
    def parse_and_route(self, command: str) -> Dict[str, Any]:
        self._rarity_gate(self.user_rarity)
        result: Dict[str, Any] = {}
        if self.voice:
            intent = self.voice.parse_voice_command(command)
            goal = intent.get("goal", command)
            tools = intent.get("tools", [])
            rarity = max(self.min_rarity, intent.get("rarity", self.user_rarity))
        else:
            goal, tools, rarity = command, ["rarity_engine", "neural_layers"], self.user_rarity

        # Launch skill
        launch_result = None
        if self.launchpad:
            launch_result = self.launchpad.run_one_click(goal=goal, tools=tools, rarity_score=rarity)
        result["launch"] = launch_result

        # Physical dispatch
        phys_result = None
        if self.bridge:
            try:
                # Build a simple route
                route = {"waypoints": ["Depot", "Ring Road", "VIP Tower"], "coords": [(12.970, 77.590), (12.975, 77.620), (12.985, 77.640)]}
                phys_result = self.bridge.run_full_cycle(goal=goal, route=route, rarity_score=rarity)
            except PermissionError as exc:
                phys_result = {"error": str(exc), "fallback": "use sim bridge"}
            except Exception as exc:
                phys_result = {"error": str(exc)}
        result["physical"] = phys_result

        # Dashboard view
        dash = None
        if self.dashboard:
            try:
                dash = self.dashboard.run_once(rarity_score=max(rarity, self.min_rarity), vip=True)
            except Exception as exc:
                dash = {"error": str(exc)}
        result["dashboard"] = dash

        # Alerts
        alerts = []
        if dash and isinstance(dash, dict):
            alerts.extend(dash.get("alerts", []))
        if phys_result and isinstance(phys_result, dict) and phys_result.get("telemetry", {}).get("final_status") == "failed":
            alerts.append("Physical dispatch failed")
        result["alerts"] = alerts

        self.last_unified = result
        return result

    # --------------------------------------------------------------
    def display_unified_view(self, payload: Optional[Dict[str, Any]] = None):
        payload = payload or self.last_unified
        print("\n=== Command Center Unified View ===")
        print(json.dumps(payload, indent=2))

    # --------------------------------------------------------------
    def start_cli_loop(self):
        print("Rarest Command Center (CLI). Type 'exit' to quit.")
        while True:
            cmd = input("command> ").strip()
            if cmd.lower() in {"exit", "quit"}:
                break
            if not cmd:
                continue
            try:
                res = self.parse_and_route(cmd)
                self.display_unified_view(res)
            except Exception as exc:
                print(f"Error: {exc}")

    # --------------------------------------------------------------
    def start_web_server(self, port: int = 8003):
        if not Flask or not jsonify:
            print("Flask not available; web server disabled")
            return None
        app = Flask(__name__)
        center = self

        @app.route("/center", methods=["GET"])
        def center_view():
            try:
                res = center.parse_and_route("Launch rare drone optimizer for Mysuru traffic")
                return jsonify(res)
            except Exception as exc:
                return jsonify({"error": str(exc)}), 500

        @app.route("/center/html", methods=["GET"])
        def center_html():
            try:
                res = center.parse_and_route("Launch rare drone optimizer for Mysuru traffic")
                return "<pre>" + json.dumps(res, indent=2) + "</pre>"
            except Exception as exc:
                return f"Error: {exc}", 500

        thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False), daemon=True)
        thread.start()
        logger.info(f"Web command center started on port {port}")
        return thread


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    center = RarestCommandCenter()
    demo_cmd = "Launch rare drone optimizer for Mysuru traffic"
    result = center.parse_and_route(demo_cmd)
    center.display_unified_view(result)
    # Uncomment to start interactive CLI
    # center.start_cli_loop()
    # Uncomment to start web server
    # center.start_web_server(port=8003)
