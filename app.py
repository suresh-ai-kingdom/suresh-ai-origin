from flask import Flask, jsonify
import razorpay
import os

app = Flask(__name__)

# Razorpay client (SECRET from Render ENV)
client = razorpay.Client(auth=(
    os.getenv("rzp_live_RxSvKRp2SAfKv4"),
    os.getenv("HXf6IHjG7d7lAZRrLV0yxsIl")
))

# ---------------- HOME ----------------
@app.route("/")
def home():
    return """
    <h1>SURESH AI ORIGIN</h1>
    <p>Digital Product – Starter Pack</p>
    <p><b>Price:</b> ₹49</p>
    <a href="/buy"><button>Buy Now</button></a>
    """

# ---------------- BUY PAGE ----------------
@app.route("/buy")
def buy():
    return """
    <h1>Checkout</h1>
    <p><b>Product:</b> Suresh AI Origin – Starter Pack</p>
    <p><b>Price:</b> ₹49</p>

    <button id="pay-btn">Pay ₹49</button>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
    document.getElementById("pay-btn").onclick = function () {
        fetch("/create-order")
        .then(res => res.json())
        .then(order => {
            var options = {
                "key": "rzp_live_XXXXXXXXXX",   // 🔥 PUT YOUR LIVE KEY ID HERE
                "amount": order.amount,
                "currency": "INR",
                "order_id": order.id,
                "name": "Suresh AI Origin",
                "description": "Digital Product",
                "handler": function (response) {
                    window.location.href = "/success";
                }
            };
            var rzp = new Razorpay(options);
            rzp.open();
        });
    };
    </script>
    """

# ---------------- CREATE ORDER ----------------
@app.route("/create-order")
def create_order():
    order = client.order.create({
        "amount": 4900,  # ₹49
        "currency": "INR",
        "payment_capture": 1
    })
    return jsonify(order)

# ---------------- SUCCESS ----------------
@app.route("/success")
def success():
    return "<h2>Payment Successful ✅</h2><p>Thank you!</p>"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
