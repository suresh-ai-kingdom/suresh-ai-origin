from flask import Flask, render_template, request, jsonify, session, send_from_directory
import razorpay
import os
from dotenv import load_dotenv

# ---------------- LOAD ENV ----------------
load_dotenv()

app = Flask(__name__)
app.secret_key = "suresh-ai-origin-secret"

# ---------------- RAZORPAY CLIENT ----------------
client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- BUY PAGE ----------------
@app.route("/buy")
def buy():
    return render_template(
        "buy.html",
        key_id=os.getenv("RAZORPAY_KEY_ID")
    )

# ---------------- CREATE ORDER ----------------
@app.route("/create-order", methods=["POST"])
def create_order():
    order = client.order.create({
        "amount": 4900,   # ₹49
        "currency": "INR",
        "payment_capture": 1
    })
    session["order_id"] = order["id"]
    return jsonify(order)

# ---------------- VERIFY PAYMENT ----------------
@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"]
        })
        session["paid"] = True
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "failed"}), 400

# ---------------- SUCCESS ----------------
@app.route("/success")
def success():
    if not session.get("paid"):
        return "Access Denied"
    return """
    <h2>✅ Payment Successful</h2>
    <p>Downloads unlocked:</p>
    <ul>
        <li><a href="/download/starter">Download Starter Pack</a></li>
        <li><a href="/download/quick">Download Quick Wins Pack</a></li>
    </ul>
    """

# ---------------- DOWNLOADS ----------------
@app.route("/download/starter")
def download_starter():
    if not session.get("paid"):
        return "Access Denied"
    return send_from_directory("downloads", "starter_pack.zip", as_attachment=True)

@app.route("/download/quick")
def download_quick():
    if not session.get("paid"):
        return "Access Denied"
    return send_from_directory("downloads", "quick_wins_pack.zip", as_attachment=True)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=False)
