from flask import Flask, request, send_from_directory
import razorpay
import os
from dotenv import load_dotenv

# Load .env locally (Render ignores this, uses dashboard ENV)
load_dotenv()

app = Flask(__name__)

# Razorpay client
client = razorpay.Client(auth=(
    os.environ.get("RAZORPAY_KEY_ID"),
    os.environ.get("RAZORPAY_KEY_SECRET")
))

# ---------------- HOME ----------------
@app.route("/")
def home():
    return """
    <h1>SURESH AI ORIGIN</h1>
    <p>Digital Product – Starter Pack</p>
    <p><b>Price: ₹49</b></p>
    <p>Instant Download After Payment</p>
    <a href="/buy">Buy Now</a>
    """

# ---------------- BUY ----------------
@app.route("/buy")
def buy():
    # ₹49 = 4900 paise
    order = client.order.create({
        "amount": 4900,
        "currency": "INR",
        "payment_capture": 1
    })

    key_id = os.environ.get("RAZORPAY_KEY_ID")

    return f"""
    <h2>Checkout</h2>
    <p>Product: Suresh AI Origin – Starter Pack</p>
    <p>Price: ₹49</p>

    <button id="pay">Pay ₹49</button>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
    var options = {{
        "key": "{key_id}",
        "amount": 4900,
        "currency": "INR",
        "name": "Suresh AI Origin",
        "description": "Starter Pack",
        "order_id": "{order['id']}",
        "handler": function (response){{
            fetch("/verify", {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/json"
                }},
                body: JSON.stringify(response)
            }})
            .then(res => res.text())
            .then(html => {{
                document.body.innerHTML = html;
            }});
        }}
    }};
    var rzp = new Razorpay(options);
    document.getElementById("pay").onclick = function(e){{
        rzp.open();
        e.preventDefault();
    }}
    </script>
    """

# ---------------- VERIFY ----------------
@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"]
        })

        return """
        <h2>✅ Payment Successful</h2>
        <p>Thank you for your purchase.</p>
        <a href="/download">👉 Download Starter Pack</a>
        """

    except Exception as e:
        return f"<h2>❌ Payment Verification Failed</h2><pre>{e}</pre>"

# ---------------- DOWNLOAD ----------------
@app.route("/download")
def download():
    return send_from_directory(
        "downloads",
        "starter_pack.zip",
        as_attachment=True
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
