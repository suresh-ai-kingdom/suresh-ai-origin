from flask import Flask, jsonify
import razorpay
import os

app = Flask(__name__)

# Razorpay Client (LIVE keys from Render ENV)
client = razorpay.Client(auth=(
    os.getenv("rzp_live_RxSvKRp2SAfKv4"),
    os.getenv("HXf6IHjG7d7lAZRrLV0yxsIl")
))

# ---------------- HOME ----------------
@app.route("/")
def home():
    return """
    <h1>SURESH AI ORIGIN</h1>

    <p>Suresh AI Origin is a digital platform that provides AI automation guides,
    digital learning resources, and step-by-step blueprints.</p>

    <h2>Digital Product</h2>
    <p><b>Suresh AI Origin – Starter Pack</b></p>

    <ul>
      <li>AI Automation Roadmap (PDF)</li>
      <li>Beginner Income Blueprint</li>
      <li>Instant digital access after payment</li>
    </ul>

    <p><b>Price:</b> ₹49 (One-time payment)</p>
    <p>This is a digital product. No physical goods involved.</p>

    <a href="/buy"><button>Buy Now</button></a>

    <hr>
    <a href="/privacy-policy">Privacy Policy</a> |
    <a href="/terms-and-conditions">Terms & Conditions</a> |
    <a href="/refund-policy">Refund Policy</a> |
    <a href="/contact">Contact</a>
    """

# ---------------- BUY / CHECKOUT ----------------
@app.route("/buy")
def buy():
    key = os.getenv("RAZORPAY_KEY_ID")

    return f"""
    <h1>Checkout</h1>

    <p><b>Product:</b> Suresh AI Origin – Starter Pack</p>
    <p><b>Price:</b> ₹49</p>

    <button id="pay-btn">Pay ₹49</button>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
    fetch("/create-order")
    .then(res => res.json())
    .then(order => {{
        document.getElementById("pay-btn").onclick = function () {{
            var options = {{
                "key": "{key}",
                "amount": order.amount,
                "currency": "INR",
                "order_id": order.id,
                "name": "Suresh AI Origin",
                "description": "Digital Product",
                "handler": function (response) {{
                    window.location.href = "/success";
                }}
            }};
            var rzp = new Razorpay(options);
            rzp.open();
        }};
    });
    </script>

    <p><a href="/">← Back</a></p>
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
    <p>Thank you for purchasing Suresh AI Origin – Starter Pack.</p>
    <p>Your digital product will be delivered shortly.</p>
    """

# ---------------- POLICIES ----------------
@app.route("/privacy-policy")
def privacy():
    return """
    <h2>Privacy Policy</h2>
    <p>We do not collect or store sensitive personal data.</p>
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
    <p>Refunds are applicable only if the digital product is not delivered.</p>
    <p>Refund requests must be raised within 3 days of purchase.</p>
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
