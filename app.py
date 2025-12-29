from flask import Flask, jsonify
import razorpay
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Razorpay Client
client = razorpay.Client(auth=(
    os.getenv("rzp_live_RxSvKRp2SAfKv4"),
    os.getenv("HXf6IHjG7d7lAZRrLV0yxsIl")
))

# ---------------- HOME ----------------
@app.route("/")
def home():
    return """
    <h1>Suresh AI Origin</h1>
    <p>Digital Product – ₹49</p>
    <button id="pay-btn">Pay ₹49</button>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
    fetch("/create-order")
    .then(res => res.json())
    .then(order => {
        document.getElementById("pay-btn").onclick = function () {
            var options = {
                "key": "REPLACE_WITH_LIVE_KEY_ID",
                "amount": order.amount,
                "currency": "INR",
                "order_id": order.id,
                "name": "Suresh AI Origin",
                "description": "Digital Product",
                "handler": function (response){
                    window.location.href = "/success?pid=" + response.razorpay_payment_id;
                }
            };
            var rzp = new Razorpay(options);
            rzp.open();
        };
    });
    </script>

    <p><a href="/privacy-policy">Privacy Policy</a></p>
    <p><a href="/terms-and-conditions">Terms & Conditions</a></p>
    <p><a href="/refund-policy">Refund Policy</a></p>
    <p><a href="/contact">Contact</a></p>
    """

# ---------------- CREATE ORDER ----------------
@app.route("/create-order")
def create_order():
    order = client.order.create({
        "amount": 4900,   # ₹49
        "currency": "INR",
        "payment_capture": 1
    })
    return jsonify(order)

# ---------------- SUCCESS ----------------
@app.route("/success")
def success():
    return """
    <h2>Payment Successful ✅</h2>
    <p>Thank you for your purchase.</p>
    <p>Your digital product will be delivered shortly.</p>
    """

# ---------------- POLICIES ----------------
@app.route("/privacy-policy")
def privacy():
    return """
    <h2>Privacy Policy</h2>
    <p>We do not store sensitive personal data.</p>
    <p>Payments are securely processed via Razorpay.</p>
    """

@app.route("/terms-and-conditions")
def terms():
    return """
    <h2>Terms & Conditions</h2>
    <p>This website sells digital products only.</p>
    <p>By purchasing, you agree to receive content electronically.</p>
    """

@app.route("/refund-policy")
def refund():
    return """
    <h2>Refund Policy</h2>
    <p>Refunds apply only if the digital product is not delivered.</p>
    <p>Requests must be raised within 3 days.</p>
    """

@app.route("/contact")
def contact():
    return """
    <h2>Contact</h2>
    <p>Email: sureshaiorigin@gmail.com</p>
    """

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
