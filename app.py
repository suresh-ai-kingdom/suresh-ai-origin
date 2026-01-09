from flask import Flask, render_template, request, send_from_directory, abort

app = Flask(__name__)

PRODUCTS = {
    "starter": {
        "name": "Starter Pack",
        "price": 49,
        "file": "starter_pack.zip"
    },
    "pro": {
        "name": "Pro Pack",
        "price": 99,
        "file": "pro_pack.zip"
    },
    "premium": {
        "name": "Premium Pack",
        "price": 199,
        "file": "premium_pack.zip"
    }
}

@app.route("/")
def home():
    return render_template("index.html", products=PRODUCTS)

@app.route("/buy")
def buy():
    product_key = request.args.get("product")
    if product_key not in PRODUCTS:
        abort(404)
    return render_template("buy.html", product=PRODUCTS[product_key], key=product_key)

@app.route("/success")
def success():
    product_key = request.args.get("product")
    if product_key not in PRODUCTS:
        abort(404)
    return render_template("success.html", key=product_key)

@app.route("/download/<product_key>")
def download(product_key):
    if product_key not in PRODUCTS:
        abort(404)

    return send_from_directory(
        directory="downloads",
        path=PRODUCTS[product_key]["file"],
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)
