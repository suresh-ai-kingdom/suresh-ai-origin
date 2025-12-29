from flask import Flask, jsonify, render_template_string
import razorpay
import os

app = Flask(__name__)

client = razorpay.Client(
    auth=(
        os.getenv("rzp_live_RxW5W1elhj941G"),
        os.getenv("bevX9WICL6IdQLGq7dZahBGD")
    )
)

@app.route("/")
def home():
    return '<a href="/buy">Buy Now</a>'

@app.route("/buy")
def buy():
    return render_template_string("""
    <h1>Checkout</h1>
    <p>Product: Suresh AI Origin – Starter Pack</p>
    <p>Price: ₹49</p>
    <button onclick="pay()">Pay ₹49</button>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
    async function pay() {
        const res = await fetch("/create-order");
        const order = await res.json();

        var options = {
            "key": "{{ key }}",
            "amount": order.amount,
            "currency": "INR",
            "name": "Suresh AI Origin",
            "description": "Starter Pack",
            "order_id": order.id,
            "handler": function (response){
                window.location.href = "/success";
            }
        };
        var rzp = new Razorpay(options);
        rzp.open();
    }
    </script>
    """, key=os.getenv("RAZORPAY_KEY_ID"))

@app.route("/create-order")
def create_order():
    order = client.order.create({
        "amount": 4900,
        "currency": "INR",
        "payment_capture": 1
    })
    return jsonify(order)

@app.route("/success")
def success():
    return "<h2>Payment Successful ✅</h2>"

if __name__ == "__main__":
    app.run()
