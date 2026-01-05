from flask import Flask, render_template, request, jsonify
import razorpay
import os
import hmac
import hashlib
from dotenv import load_dotenv 

load_dotenv()

app = Flask(__name__)

# Razorpay
client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)

DOWNLOAD_FOLDER = "downloads"

# ------------------ PAGES ------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/buy")
def buy():
    return render_template("buy.html")

@app.route("/success")
def success():
    return render_template("success.html")

# ------------------ PAYMENT ------------------

@app.route("/create-order", methods=["POST"])
def create_order():
    order = client.order.create({
        "amount": 49 * 100,
        "currency": "INR",
        "payment_capture": 1
    })

    return jsonify({
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "key": os.getenv("RAZORPAY_KEY_ID")
    })

# ------------------ WEBHOOK ------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    signature = request.headers.get("X-Razorpay-Signature")
    secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")

    generated = hmac.new(
        bytes(secret, "utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()

    if generated != signature:
        return "Invalid signature", 400

    data = request.json
    event = data.get("event")

    if event == "payment.captured":
        email = data["payload"]["payment"]["entity"].get("email")
        send_email(email)

    return "OK", 200

# ------------------ EMAIL ------------------

def send_email(to_email):
    if not to_email:
        return

    msg = EmailMessage()
    msg["Subject"] = "✅ Your SURESH AI ORIGIN Access"
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = to_email

    msg.set_content(f"""
Thank you for your purchase 🎉

Your download links:
Starter Pack:
https://suresh-ai-origin.onrender.com/download/starter_pack.zip

Quick Wins Pack:
https://suresh-ai-origin.onrender.com/download/quick_wins_pack.zip

— SURESH AI ORIGIN
""")

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(
            os.getenv("EMAIL_USER"),
            os.getenv("EMAIL_PASS")
        )
        server.send_message(msg)

# ------------------ DOWNLOAD ------------------

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(
        DOWNLOAD_FOLDER,
        filename,
        as_attachment=True
    )

# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(debug=True)
