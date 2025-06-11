from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import requests
import numpy as np
import pandas as pd
import xgboost as xgb
import ta

app = Flask(__name__)
CORS(app)

def get_current_price(pair):
    try:
        symbol = pair.split("/")[0].lower()
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        res = requests.get(url).json()
        return float(res[symbol]["usd"])
    except Exception:
        raise Exception("Failed to retrieve current price")

def make_prediction(pair, target_price, target_time):
    # Placeholder: Replace with real historical data fetching + indicators
    current_price = get_current_price(pair)
    
    if current_price > float(target_price):
        return "Below"
    else:
        return "Above"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        pair = data["pair"]
        target_price = float(data["target_price"])
        target_time = data["target_time"]

        prediction = make_prediction(pair, target_price, target_time)

        return jsonify({"prediction": prediction})
    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": "Prediction failed. Please try again."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
