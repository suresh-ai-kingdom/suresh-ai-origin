from flask import Blueprint, request, jsonify
from invoice_sender import get_invoice_sender_status, run_invoice_sender_automation

invoice_sender_bp = Blueprint('invoice_sender', __name__)

@invoice_sender_bp.route('/api/invoice_sender/status', methods=['GET'])
def invoice_status():
    order_id = request.args.get('order_id')
    return jsonify(get_invoice_sender_status(order_id))

@invoice_sender_bp.route('/api/invoice_sender/run', methods=['POST'])
def invoice_run():
    data = request.json
    order_id = data.get('order_id')
    params = data.get('params', {})
    return jsonify(run_invoice_sender_automation(order_id, params))
