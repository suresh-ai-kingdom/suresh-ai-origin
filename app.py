from flask import Flask, render_template, send_from_directory, request
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

PRODUCTS = {
    "starter": "starter_pack.zip",
    "pro": "pro_pack.zip",
    "premium": "premium_pack.zip"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/buy")
def buy():
    product = request.args.get("product", "starter")
    return render_template("buy.html", product=product)

@app.route("/success")
def success():
    product = request.args.get("product", "starter")
    return render_template("success.html", product=product)

@app.route("/download/<product>")
def download(product):
    filename = PRODUCTS.get(product)
    if not filename:
        return "Invalid product", 404
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
