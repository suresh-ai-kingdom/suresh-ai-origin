import os
import razorpay
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Razorpay client
client = razorpay.Client(
    auth=(
        os.environ.get("RAZORPAY_KEY_ID"),
        os.environ.get("RAZORPAY_KEY_SECRET")
    )
)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return """
    <h1>SURESH AI ORIGIN</h1>
    <p>Digital Product – Starter Pack</p>
    <p>Price: ₹49</p>
    <a href="/buy">Buy Now</a>
    """

# ---------------- BUY PAGE ----------------
@app.route("/buy")
def buy():
    key_id = os.environ.get("RAZORPAY_KEY_ID")

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Checkout</title>
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
</head>
<body>

<h2>Checkout</h2>
<p>Product: Suresh AI Origin – Starter Pack</p>
<p>Price: ₹49</p>

<button onclick="pay()">Pay ₹49</button>

<script>
function pay() {{
    fetch("/create-order")
    .then(res => res.json())
    .then(order => {{
        var options = {{
            key: "{key_id}",
            amount: order.amount,
            currency: "INR",
            name: "Suresh AI Origin",
            description: "Starter Pack",
            order_id: order.id,
            handler: function (response) {{
                fetch("/verify-payment", {{
                    method: "POST",
                    headers: {{
                        "Content-Type": "application/json"
                    }},
                    body: JSON.stringify(response)
                }})
                .then(res => res.json())
                .then(data => {{
                    if (data.status === "success") {{
                        window.location.href = "/download";
                    }} else {{
                        alert("Payment verification failed");
                    }}
                }});
            }}
        }};
        var rzp = new Razorpay(options);
        rzp.open();
    }})
    .catch(() => alert("Order failed"));
}}
</script>

</body>
</html>
"""

# ---------------- CREATE ORDER ----------------
@app.route("/create-order")
def create_order():
    try:
        order = client.order.create({
            "amount": 4900,   # ₹49
            "currency": "INR",
            "payment_capture": 1
        })
        return jsonify(order)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- VERIFY PAYMENT ----------------
@app.route("/verify-payment", methods=["POST"])
def verify_payment():
    data = request.json
    try:
        client.utility.verify_payment_signature(data)
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "failed"})

# ---------------- DOWNLOAD ----------------
@app.route("/download")
def download():
    return """
    <h2>Payment Successful ✅</h2>
    <p>Thank you for your purchase!</p>
    <a href="/static/starter-pack.zip">Download your product</a>
    """

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
