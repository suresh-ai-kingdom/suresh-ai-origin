from flask import Flask, render_template, request, send_from_directory, session
import razorpay
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "suresh-ai-origin-super-secure-key"

# Razorpay client
client = razorpay.Client(auth=(
    os.environ.get("RAZORPAY_KEY_ID"),
    os.environ.get("RAZORPAY_KEY_SECRET")
))

# ---------------- HOME (LANDING PAGE) ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- BUY / CHECKOUT ----------------
@app.route("/buy")
def buy():
    order = client.order.create({
        "amount": 4900,  # ₹49
        "currency": "INR",
        "payment_capture": 1
    })

    return render_template(
        "buy.html",
        key_id=os.environ.get("RAZORPAY_KEY_ID"),
        amount=order["amount"],
        order_id=order["id"]
    )

# ---------------- VERIFY PAYMENT ----------------
@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"]
        })

        # Payment success → unlock download
        session["paid"] = True

        return """
        <h2>✅ Payment Successful</h2>
        <p>Thank you for your purchase.</p>
        <a href="/download">👉 Download Starter Pack</a>
        """

    except:
        return "<h2>❌ Payment Verification Failed</h2>"

# ---------------- DOWNLOAD (SECURED) ----------------
@app.route("/download")
def download():
    if not session.get("paid"):
        return """
        <h3>❌ Access Denied</h3>
        <p>Please complete payment first.</p>
        <a href="/buy">Go to Checkout</a>
        """

    return send_from_directory(
        "downloads",
        "starter_pack.zip",
        as_attachment=True
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
