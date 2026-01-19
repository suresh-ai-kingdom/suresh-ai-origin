from flask import Blueprint, request, jsonify
from automation_template import get_<feature>_status, run_<feature>_automation

automation_bp = Blueprint('automation', __name__)

@automation_bp.route('/api/<feature>/status', methods=['GET'])
def feature_status():
    order_id = request.args.get('order_id')
    return jsonify(get_<feature>_status(order_id))

@automation_bp.route('/api/<feature>/run', methods=['POST'])
def feature_run():
    data = request.json
    order_id = data.get('order_id')
    params = data.get('params', {})
    return jsonify(run_<feature>_automation(order_id, params))
