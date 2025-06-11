from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from dateutil import parser
import requests
import pandas as pd
import xgboost as xgb
import os

app = Flask(__name__)
CORS(app)

# Load model
MODEL_PATH = "model_xgb.json"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Trained model not found.")

model = xgb.XGBClassifier()
model.load_model(MODEL_PATH)

# Mapping for CoinGecko
COIN_ID_MAP = {
    "BTC/USDT": "bitcoin",
    "ETH/USDT": "ethereum"
}

def fetch_current_price(pair):
    if pair not in COIN_ID_MAP:
        raise Exception("Unsupported pair")

    coin_id = COIN_ID_MAP[pair]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Failed to retrieve price from CoinGecko")

    data = response.json()
    return data[coin_id]["usd"]

def make_prediction(pair, target_price, target_time):
    current_price = fetch_current_price(pair)

    current_time = datetime.utcnow()
    target_time_dt = parser.parse(target_time)
    minutes_to_target = (target_time_dt - current_time).total_seconds() / 60.0

    if minutes_to_target < 1:
        raise Exception("Target time must be in the future")

    df = pd.DataFrame([{
        "current_price": current_price,
        "target_price": float(target_price),
        "minutes_to_target": minutes_to_target
    }])

    prediction = model.predict(df)[0]
    return "Above" if prediction == 1 else "Below"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        pair = data.get("pair")
        target_price = data.get("target_price")
        target_time = data.get("target_time")

        if not (pair and target_price and target_time):
            return jsonify({"error": "Missing required fields"}), 400

        prediction = make_prediction(pair, target_price, target_time)
        return jsonify({"prediction": prediction})

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": "Prediction failed"}), 500

@app.route("/")
def index():
    return "Crypto Price Predictor API"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
