from flask import Blueprint, request, jsonify
from moon_income_engine import get_moon_income_status, run_moon_income_automation

moon_income_bp = Blueprint('moon_income', __name__)

@moon_income_bp.route('/api/moon_income/status', methods=['GET'])
def moon_income_status():
    order_id = request.args.get('order_id')
    return jsonify(get_moon_income_status(order_id))

@moon_income_bp.route('/api/moon_income/run', methods=['POST'])
def moon_income_run():
    data = request.json
    order_id = data.get('order_id')
    params = data.get('params', {})
    return jsonify(run_moon_income_automation(order_id, params))

# To integrate the moon_income API into your main Flask app, add the following to app.py:
# from moon_income_api import moon_income_bp
# app.register_blueprint(moon_income_bp)
