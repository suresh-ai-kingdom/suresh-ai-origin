from flask import Flask, request, send_from_directory
import razorpay
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env locally

app = Flask(__name__)

client = razorpay.Client(auth=(
    os.environ.get("RAZORPAY_KEY_ID"),
    os.environ.get("RAZORPAY_KEY_SECRET")
))

# -------- HOME --------
@app.route("/")
def home():
    return """
    <h1>SURESH AI ORIGIN</h1>
    <p>Digital Product – Starter Pack</p>
    <p><b>Price: ₹1</b></p>
    <a href="/buy">Buy Now</a>
    """

# -------- BUY --------
@app.route("/buy")
def buy():
    order = client.order.create({
        "amount": 100,
        "currency": "INR",
        "payment_capture": 1
    })

    key_id = os.environ.get("RAZORPAY_KEY_ID")

    return f"""
    <h2>Checkout</h2>
    <button id="pay">Pay ₹1</button>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
    var options = {{
        "key": "{key_id}",
        "amount": 100,
        "currency": "INR",
        "name": "Suresh AI Origin",
        "description": "Starter Pack",
        "order_id": "{order['id']}",
        "handler": function (response){{
            fetch("/verify", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify(response)
            }})
            .then(res => res.text())
            .then(html => document.body.innerHTML = html);
        }}
    }};
    var rzp = new Razorpay(options);
    document.getElementById("pay").onclick = function(e){{
        rzp.open();
        e.preventDefault();
    }}
    </script>
    """

# -------- VERIFY --------
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
        <h2>✅ Payment Verified</h2>
        <a href="/download">Download Starter Pack</a>
        """
    except Exception as e:
        return f"<h2>❌ Payment Failed</h2><pre>{e}</pre>"

# -------- DOWNLOAD --------
@app.route("/download")
def download():
    return send_from_directory("downloads", "starter_pack.zip", as_attachment=True)

# -------- RUN --------
if __name__ == "__main__":
    app.run()
