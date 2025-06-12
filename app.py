from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from dateutil import parser
import traceback
import requests

app = Flask(__name__)
CORS(app)

def get_latest_price(pair):
    # Example using CoinGecko for simplicity
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin" if pair == "BTC/USDT" else "ethereum",
        "vs_currencies": "usd"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return float(data["bitcoin"]["usd"] if pair == "BTC/USDT" else data["ethereum"]["usd"])
    except Exception as e:
        print("Error fetching latest price:", e)
        return None

def make_prediction(pair, target_price, target_time):
    current_price = get_latest_price(pair)
    if current_price is None:
        raise Exception("Failed to retrieve current price")
    print(f"Current price of {pair}: {current_price}, Target: {target_price}")
    return 'above' if current_price < target_price else 'below'

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print("Received data:", data)
        pair = data['pair']
        target_price = float(data['target_price'])
        target_time_str = data['target_time']
        target_time = parser.parse(target_time_str)
        prediction = make_prediction(pair, target_price, target_time)
        print("Prediction result:", prediction)
        return jsonify({'prediction': prediction})
    except Exception as e:
        print("Error during prediction:", str(e))
        traceback.print_exc()
        return jsonify({'error': 'Prediction failed'}), 500

@app.route('/', methods=['GET'])
def home():
    return "Crypto Predictor Backend Running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)