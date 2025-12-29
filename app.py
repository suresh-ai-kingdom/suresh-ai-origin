from flask import Flask, jsonify, render_template_string
import razorpay
import os

app = Flask(__name__)

# Razorpay client
client = razorpay.Client(auth=(
    os.environ.get("rzp_live_RxW5W1elhj941G"),
    os.environ.get("bevX9WICL6IdQLGq7dZahBGD")
))

@app.route("/")
def home():
    return """
    <h1>SURESH AI ORIGIN</h1>
    <p>Digital Product – Starter Pack</p>
    <p>Price: ₹49</p>
    <a href="/buy">Buy Now</a>
    """


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
<h1>Checkout</h1>
<p>Product: Suresh AI Origin – Starter Pack</p>
<p>Price: ₹49</p>

<button onclick="pay()">Pay ₹49</button>

<script>
function pay() {{
    fetch("/create-order")
    .then(res => res.json())
    .then(order => {{
        var options = {{
            key: "{key_id}",   // ✅ REAL KEY injected here
            amount: order.amount,
            currency: "INR",
            name: "Suresh AI Origin",
            description: "Starter Pack",
            order_id: order.id,
            handler: function (response) {{
                window.location.href = "/success";
            }}
        }};
        var rzp = new Razorpay(options);
        rzp.open();
    }})
    .catch(err => {{
        alert("Order failed");
        console.error(err);
    }});
}}
</script>
</body>
</html>
"""


@app.route("/create-order")
def create_order():
    try:
        order = client.order.create({
            "amount": 4900,
            "currency": "INR",
            "payment_capture": 1
        })
        return jsonify(order)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/success")
def success():
    return "<h2>Payment Successful ✅</h2><p>Thank you!</p>"


if __name__ == "__main__":
    app.run()