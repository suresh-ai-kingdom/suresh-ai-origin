import os
import hmac
import hashlib
import smtplib
from email.message import EmailMessage

from flask import Flask, render_template, request, jsonify, redirect, send_from_directory, abort
import razorpay
from dotenv import load_dotenv

# ---------------- LOAD ENV ----------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# ---------------- RAZORPAY ----------------
client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))

# ---------------- CONFIG ----------------
DOWNLOAD_FOLDER = "downloads"
PRODUCT_FILE = "starter_pack.zip"
PRODUCT_PRICE = 49 * 100  # paise

# ---------------- EMAIL CONFIG ----------------
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# ---------------- PAGES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/buy")
def buy():
    return render_template(
        "buy.html",
        razorpay_key=os.getenv("RAZORPAY_KEY_ID")
    )

@app.route("/success")
def success():
    return render_template("success.html")

# ---------------- CREATE ORDER ----------------
@app.route("/create-order", methods=["POST"])
def create_order():
    order = client.order.create({
        "amount": PRODUCT_PRICE,
        "currency": "INR",
        "payment_capture": 1
    })
    return jsonify(order)

# ---------------- VERIFY PAYMENT ----------------
@app.route("/verify-payment", methods=["POST"])
def verify_payment():
    data = request.json

    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")
    email = data.get("email")

    body = f"{razorpay_order_id}|{razorpay_payment_id}"

    secret = os.getenv("RAZORPAY_KEY_SECRET").encode()
    generated_signature = hmac.new(
        secret,
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    if generated_signature != razorpay_signature:
        return jsonify({"status": "failed"}), 400

    # SEND EMAIL
    send_download_email(email)

    return jsonify({"status": "success"})

# ---------------- DOWNLOAD ----------------
@app.route("/download")
def download():
    return send_from_directory(
        DOWNLOAD_FOLDER,
        PRODUCT_FILE,
        as_attachment=True
    )

# ---------------- EMAIL FUNCTION ----------------
def send_download_email(to_email):
    msg = EmailMessage()
    msg["Subject"] = "Your SURESH AI ORIGIN – Starter Pack"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    download_link = f"{request.url_root}download"

    msg.set_content(f"""
Thank you for your purchase ❤️

Download your Starter Pack here:
{download_link}

— SURESH AI ORIGIN
    """)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
