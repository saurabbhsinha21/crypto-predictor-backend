from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

# Health check route
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "Backend is working!"})

# Fetch current price from CoinGecko
def get_current_price(pair):
    try:
        symbol = pair.split("/")[0].lower()
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        print(f"DEBUG: Fetching current price from {url}")
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        price = float(data[symbol]["usd"])
        print(f"DEBUG: Retrieved price for {symbol.upper()}: {price}")
        return price
    except Exception as e:
        print(f"ERROR in get_current_price: {e}")
        raise Exception("Failed to retrieve current price")

# Dummy prediction logic based on current vs target price
def make_prediction(pair, target_price, target_time):
    try:
        print("DEBUG: Starting make_prediction()")
        current_price = get_current_price(pair)
        print(f"DEBUG: Current Price = {current_price}, Target Price = {target_price}")
        
        prediction = "Below" if current_price > float(target_price) else "Above"
        print(f"DEBUG: Prediction = {prediction}")
        return prediction
    except Exception as e:
        print(f"ERROR in make_prediction: {e}")
        raise

# Main prediction endpoint
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        pair = data["pair"]
        target_price = float(data["target_price"])
        target_time = data["target_time"]

        print(f"DEBUG: Received request - Pair: {pair}, Target Price: {target_price}, Target Time: {target_time}")

        prediction = make_prediction(pair, target_price, target_time)
        return jsonify({"prediction": prediction})
    
    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": "Server error or prediction failed."}), 500

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
