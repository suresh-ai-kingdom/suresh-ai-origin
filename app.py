import os
import hmac
import hashlib
import razorpay
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Razorpay client
client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)

# ------------------ PAGES ------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/buy")
def buy():
    return render_template("buy.html", key=os.getenv("RAZORPAY_KEY_ID"))

@app.route("/success")
def success():
    return render_template("success.html")

# ------------------ CREATE ORDER ------------------

@app.route("/create-order", methods=["POST"])
def create_order():
    order = client.order.create({
        "amount": 49 * 100,
        "currency": "INR",
        "payment_capture": 1
    })
    return jsonify(order)

# ------------------ VERIFY PAYMENT ------------------

@app.route("/verify-payment", methods=["POST"])
def verify_payment():
    data = request.json

    razorpay_order_id = data["razorpay_order_id"]
    razorpay_payment_id = data["razorpay_payment_id"]
    razorpay_signature = data["razorpay_signature"]

    secret = os.getenv("RAZORPAY_KEY_SECRET")
    message = f"{razorpay_order_id}|{razorpay_payment_id}"

    generated_signature = hmac.new(
        bytes(secret, "utf-8"),
        bytes(message, "utf-8"),
        hashlib.sha256
    ).hexdigest()

    if generated_signature == razorpay_signature:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failed"}), 400

# ------------------ WEBHOOK ------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    signature = request.headers.get("X-Razorpay-Signature")
    secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")

    expected_signature = hmac.new(
        bytes(secret, "utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()

    if hmac.compare_digest(expected_signature, signature):
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "invalid"}), 400


if __name__ == "__main__":
    app.run(debug=True)
