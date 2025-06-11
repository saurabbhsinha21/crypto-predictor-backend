
from flask import Flask, request, jsonify
import requests
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
import datetime as dt

app = Flask(__name__)

def fetch_price_data(pair="bitcoin", days=1, interval="minute"):
    url = f"https://api.coingecko.com/api/v3/coins/{pair}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": interval
    }
    response = requests.get(url, params=params)
    data = response.json()
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def add_technical_indicators(df):
    df["return"] = df["price"].pct_change()
    df["rsi"] = compute_rsi(df["price"], 14)
    df["macd"] = df["price"].ewm(span=12).mean() - df["price"].ewm(span=26).mean()
    df["signal"] = df["macd"].ewm(span=9).mean()
    df["bollinger_upper"] = df["price"].rolling(20).mean() + 2 * df["price"].rolling(20).std()
    df["bollinger_lower"] = df["price"].rolling(20).mean() - 2 * df["price"].rolling(20).std()
    df = df.dropna()
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def train_model(df):
    df = add_technical_indicators(df)
    df["target"] = np.where(df["price"].shift(-5) > df["price"], 1, 0)
    X = df[["rsi", "macd", "signal", "bollinger_upper", "bollinger_lower"]]
    y = df["target"]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = XGBClassifier()
    model.fit(X_scaled, y)
    return model, scaler, df

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        pair = data["pair"].split("/")[0].lower()  # "bitcoin" or "ethereum"
        target_time = pd.to_datetime(data["target_time"])
        target_price = float(data["target_price"])
        df = fetch_price_data(pair)
        model, scaler, df = train_model(df)
        last_row = df.iloc[-1:][["rsi", "macd", "signal", "bollinger_upper", "bollinger_lower"]]
        X_last = scaler.transform(last_row)
        prediction = model.predict(X_last)[0]
        direction = "ABOVE" if prediction == 1 else "BELOW"
        result = f"{data['pair']} will go {direction} the target price of {target_price} by {target_time}"
        return jsonify({"prediction": result})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
