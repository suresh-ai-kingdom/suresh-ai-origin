from flask import Flask, send_from_directory
import razorpay
import os

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
    <p><b>Intro Price: ₹1 (Limited Time)</b></p>
    <p>Instant Download After Payment</p>
    <a href="/buy">Buy Now</a>
    """

# ---------------- BUY PAGE ----------------
@app.route("/buy")
def buy():
    return f"""
    <h2>Checkout</h2>
    <p>Product: Suresh AI Origin – Starter Pack</p>
    <p>Price: ₹1</p>

    <button id="pay">Pay ₹1</button>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
    var options = {{
        "key": "{os.environ.get('RAZORPAY_KEY_ID')}",
        "amount": 100,
        "currency": "INR",
        "name": "Suresh AI Origin",
        "description": "Starter Pack",
        "handler": function (response){{
            window.location.href = "/success";
        }},
        "theme": {{
            "color": "#3399cc"
        }}
    }};
    var rzp = new Razorpay(options);
    document.getElementById('pay').onclick = function(e){{
        rzp.open();
        e.preventDefault();
    }}
    </script>
    """

# ---------------- PAYMENT SUCCESS ----------------
@app.route("/success")
def success():
    return """
    <h2>✅ Payment Successful</h2>
    <p>Thank you for your purchase.</p>
    <a href="/download/starter_pack">👉 Download Your Starter Pack</a>
    """

# ---------------- DOWNLOAD ----------------
@app.route("/download/starter_pack")
def download():
    return send_from_directory(
        directory="downloads",
        path="starter_pack.zip",
        as_attachment=True
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
