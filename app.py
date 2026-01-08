import os, hmac, hashlib
from flask import Flask, render_template, jsonify, request, send_from_directory
import razorpay
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Razorpay client
client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))

DOWNLOAD_FOLDER = "downloads"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/buy")
def buy():
    return render_template(
        "buy.html",
        key=os.getenv("RAZORPAY_KEY_ID")
    )

@app.route("/create-order", methods=["POST"])
def create_order():
    order = client.order.create({
        "amount": 49 * 100,
        "currency": "INR",
        "payment_capture": 1
    })
    return jsonify(order)

@app.route("/payment-success", methods=["POST"])
def payment_success():
    data = request.json

    params = {
        "razorpay_order_id": data["razorpay_order_id"],
        "razorpay_payment_id": data["razorpay_payment_id"],
        "razorpay_signature": data["razorpay_signature"]
    }

    try:
        client.utility.verify_payment_signature(params)
    except:
        return jsonify({"status": "failed"}), 400

    return jsonify({
        "status": "success",
        "download": "/download/starter_pack.zip"
    })

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
