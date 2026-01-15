#!/usr/bin/env python3
"""
🌍 RARE 1% ORCHESTRATOR API ROUTES
Integration with Flask app to expose ecosystem intelligence.
"""

from rare_1_percent_orchestrator import (
    RareOnePercentOrchestrator, ServiceType, ServiceEvent
)
from flask import jsonify, request
from datetime import datetime

# Global orchestrator instance
ORCHESTRATOR = RareOnePercentOrchestrator()
ORCHESTRATOR.state = "active"


def init_orchestrator(app):
    """Initialize orchestrator with Flask app."""
    
    @app.route('/api/orchestrator/health', methods=['GET'])
    def orchestrator_health():
        """Get ecosystem health."""
        health = ORCHESTRATOR.get_ecosystem_health()
        return jsonify({
            "success": True,
            "health": health,
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/api/orchestrator/services', methods=['GET'])
    def orchestrator_services():
        """List all services in ecosystem."""
        services_list = []
        for name, service in ORCHESTRATOR.services.items():
            services_list.append({
                "name": name,
                "type": service.service_type.value,
                "status": service.status,
                "version": service.version,
                "capabilities": service.capabilities,
                "metrics": service.metrics
            })
        
        return jsonify({
            "success": True,
            "total_services": len(ORCHESTRATOR.services),
            "services": services_list
        })
    
    @app.route('/api/orchestrator/register-service', methods=['POST'])
    def register_service():
        """Register a new service."""
        try:
            data = request.get_json()
            name = data.get('name')
            service_type = data.get('service_type')
            capabilities = data.get('capabilities', [])
            
            if not name or not service_type:
                return jsonify({"success": False, "error": "Missing name or service_type"}), 400
            
            service_type_enum = ServiceType[service_type.upper()]
            service = ORCHESTRATOR.register_service(name, service_type_enum, capabilities)
            
            return jsonify({
                "success": True,
                "service": {
                    "name": service.name,
                    "type": service.service_type.value,
                    "capabilities": service.capabilities
                }
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/orchestrator/request-help', methods=['POST'])
    def request_help():
        """Service requests help from ecosystem."""
        try:
            data = request.get_json()
            from_service = data.get('from_service')
            need = data.get('need')
            context_data = data.get('data', {})
            
            if not from_service or not need:
                return jsonify({"success": False, "error": "Missing from_service or need"}), 400
            
            result = ORCHESTRATOR.request_help(from_service, need, context_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/orchestrator/share-learning', methods=['POST'])
    def share_learning():
        """Service shares learning with ecosystem."""
        try:
            data = request.get_json()
            service_name = data.get('service')
            learning = data.get('learning', {})
            
            if not service_name:
                return jsonify({"success": False, "error": "Missing service name"}), 400
            
            ORCHESTRATOR.share_learning(service_name, learning)
            
            return jsonify({
                "success": True,
                "message": f"Learning shared by {service_name}",
                "insights_count": len(ORCHESTRATOR.collective_mind.insights)
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/orchestrator/auto-upgrade', methods=['POST'])
    def auto_upgrade():
        """Orchestrator auto-upgrades a service."""
        try:
            data = request.get_json()
            service_name = data.get('service')
            upgrades = data.get('upgrades', {})
            
            if not service_name:
                return jsonify({"success": False, "error": "Missing service name"}), 400
            
            result = ORCHESTRATOR.auto_upgrade_service(service_name, upgrades)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/orchestrator/collective-intelligence', methods=['GET'])
    def collective_intelligence():
        """Get collective insights and patterns."""
        try:
            patterns = ORCHESTRATOR.collective_mind.identify_patterns()
            recommendations = ORCHESTRATOR.collective_mind.generate_recommendations()
            
            return jsonify({
                "success": True,
                "patterns": patterns,
                "recommendations": recommendations,
                "total_insights": len(ORCHESTRATOR.collective_mind.insights)
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/orchestrator/growth-plan', methods=['GET'])
    def growth_plan():
        """Get ecosystem growth plan."""
        try:
            plan = ORCHESTRATOR.plan_growth()
            return jsonify({
                "success": True,
                "plan": plan
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/orchestrator/decisions', methods=['GET'])
    def get_decisions():
        """Get all collective decisions made by ecosystem."""
        decisions = [
            {
                "type": d['type'],
                "decision": d['decision']['name'],
                "consensus": f"{d['consensus_strength']*100:.1f}%",
                "timestamp": datetime.fromtimestamp(d['timestamp']).isoformat()
            }
            for d in ORCHESTRATOR.decisions
        ]
        
        return jsonify({
            "success": True,
            "total_decisions": len(decisions),
            "decisions": decisions
        })
    
    @app.route('/admin/orchestrator', methods=['GET'])
    @admin_required
    def admin_orchestrator_dashboard():
        """Admin dashboard for rare 1% orchestrator."""
        health = ORCHESTRATOR.get_ecosystem_health()
        growth_plan = ORCHESTRATOR.plan_growth()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rare 1% Orchestrator - Suresh AI Origin</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    background: linear-gradient(135deg, #000 0%, #1a1a1a 100%);
                    color: #fff;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    padding: 20px;
                }}
                .container {{ max-width: 1400px; margin: 0 auto; }}
                .header {{
                    background: linear-gradient(135deg, #FFD700 0%, #FF6B00 100%);
                    padding: 30px;
                    border-radius: 12px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 20px rgba(255, 215, 0, 0.3);
                }}
                .header h1 {{ color: #000; font-size: 2.5em; margin-bottom: 10px; }}
                .header p {{ color: #000; opacity: 0.9; font-size: 1.1em; }}
                .back-link {{
                    display: inline-block;
                    color: #FFD700;
                    text-decoration: none;
                    margin-bottom: 20px;
                    font-weight: bold;
                }}
                .back-link:hover {{ text-decoration: underline; }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: #1a1a1a;
                    border: 2px solid #FFD700;
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                }}
                .stat-label {{ color: #FFD700; font-size: 0.9em; margin-bottom: 10px; }}
                .stat-value {{ font-size: 2.5em; font-weight: bold; color: #fff; }}
                .stat-subtext {{ color: #888; font-size: 0.85em; margin-top: 5px; }}
                
                .section {{
                    background: #1a1a1a;
                    border: 2px solid #FFD700;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 20px;
                }}
                .section h2 {{
                    color: #FFD700;
                    margin-bottom: 15px;
                    font-size: 1.5em;
                }}
                .section ul {{ margin-left: 20px; }}
                .section li {{ margin: 8px 0; color: #ccc; }}
                .section li strong {{ color: #FFD700; }}
                
                .service-box {{
                    background: #222;
                    border: 1px solid #FFD700;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 10px 0;
                }}
                .service-name {{ color: #FFD700; font-weight: bold; }}
                .service-capability {{ color: #888; font-size: 0.85em; margin-left: 10px; }}
                
                .recommendation {{
                    background: #222;
                    border-left: 4px solid #FF6B00;
                    padding: 12px;
                    margin: 10px 0;
                    border-radius: 4px;
                }}
                .recommendation-action {{ color: #FFD700; font-weight: bold; }}
                .recommendation-impact {{ color: #0F0; margin-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <a href="/admin" class="back-link">← Back to Admin Hub</a>
                
                <div class="header">
                    <h1>🌍 Rare 1% Orchestrator</h1>
                    <p>Unified Ecosystem Intelligence - All Services Working Together</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Active Services</div>
                        <div class="stat-value">{health['services_count']}</div>
                        <div class="stat-subtext">Connected & Communicating</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Requests</div>
                        <div class="stat-value">{health['total_requests']:,}</div>
                        <div class="stat-subtext">All Time</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Success Rate</div>
                        <div class="stat-value">{health['avg_success_rate']}</div>
                        <div class="stat-subtext">Ecosystem Average</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Health Score</div>
                        <div class="stat-value">{health['health_score']}</div>
                        <div class="stat-subtext">Overall Vitality</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🔌 Connected Services</h2>
                    <div id="services-list">
                        <div style="text-align:center;color:#888;">Loading services...</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📈 Growth Initiatives</h2>
                    <ul>
        """
        
        for initiative in growth_plan['growth_initiatives']:
            html += f"<li><strong>{initiative['initiative']}</strong> → {initiative['expected_impact']}</li>"
        
        html += """
                    </ul>
                </div>
                
                <div class="section">
                    <h2>📋 Ecosystem Recommendations</h2>
                    <div id="recommendations-list">
                        <div style="text-align:center;color:#888;">Loading recommendations...</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🧠 Collective Intelligence</h2>
                    <ul>
                        <li><strong>Total Insights Collected:</strong> <span id="insights-count">...</span></li>
                        <li><strong>Patterns Identified:</strong> <span id="patterns-count">...</span></li>
                        <li><strong>Decisions Made:</strong> <span id="decisions-count">...</span></li>
                    </ul>
                </div>
                
                <div class="section">
                    <h2>💡 Quick Actions</h2>
                    <button onclick="refreshData()" style="padding:10px 20px;background:#FFD700;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;">🔄 Refresh Data</button>
                    <button onclick="viewServiceComms()" style="padding:10px 20px;background:#FF6B00;color:#fff;border:none;border-radius:6px;font-weight:bold;cursor:pointer;margin-left:10px;">💬 Service Communications</button>
                </div>
            </div>
            
            <script>
                async function loadData() {{
                    try {{
                        // Load services
                        const servicesRes = await fetch('/api/orchestrator/services');
                        const servicesData = await servicesRes.json();
                        
                        if (servicesData.success) {{
                            let html = '';
                            for (const svc of servicesData.services) {{
                                html += `<div class="service-box">
                                    <div class="service-name">✓ ${{svc.name}}</div>
                                    <div class="service-capability">Type: ${{svc.type}} | Version: ${{svc.version}}</div>
                                    <div class="service-capability">Status: <span style="color:#0F0;">${{svc.status}}</span></div>
                                </div>`;
                            }}
                            document.getElementById('services-list').innerHTML = html;
                        }}
                        
                        // Load recommendations
                        const intRes = await fetch('/api/orchestrator/collective-intelligence');
                        const intData = await intRes.json();
                        
                        if (intData.success) {{
                            document.getElementById('insights-count').textContent = intData.total_insights;
                            document.getElementById('patterns-count').textContent = Object.keys(intData.patterns).length;
                            
                            let recHtml = '';
                            for (const rec of intData.recommendations) {{
                                recHtml += `<div class="recommendation">
                                    <div class="recommendation-action">→ ${{rec.action}}</div>
                                    <div class="recommendation-impact">Expected: ${{rec.expected_impact]}</div>
                                </div>`;
                            }}
                            document.getElementById('recommendations-list').innerHTML = recHtml;
                        }}
                        
                        // Load decisions
                        const decRes = await fetch('/api/orchestrator/decisions');
                        const decData = await decRes.json();
                        if (decData.success) {{
                            document.getElementById('decisions-count').textContent = decData.total_decisions;
                        }}
                    }} catch (e) {{
                        console.error('Error loading data:', e);
                    }}
                }}
                
                function refreshData() {{
                    location.reload();
                }}
                
                function viewServiceComms() {{
                    alert('Service communications dashboard coming soon!');
                }}
                
                loadData();
            </script>
        </body>
        </html>
        """
        
        return html


def get_orchestrator():
    """Get global orchestrator instance."""
    return ORCHESTRATOR
