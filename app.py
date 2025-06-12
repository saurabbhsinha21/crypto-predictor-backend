from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

def get_current_price(pair):
    try:
        pair = pair.upper()
        if pair == "BTC/USDT":
            coin_id = "bitcoin"
        elif pair == "ETH/USDT":
            coin_id = "ethereum"
        else:
            raise Exception("Unsupported pair")

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        res = requests.get(url).json()
        return float(res[coin_id]["usd"])
    except Exception as e:
        print("Error fetching price:", e)
        raise Exception("Failed to retrieve current price")

def make_prediction(pair, target_price, target_time):
    current_price = get_current_price(pair)
    print(f"DEBUG: Current price for {pair}: {current_price}, Target price: {target_price}")
    
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
