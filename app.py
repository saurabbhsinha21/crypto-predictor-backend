from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import xgboost as xgb
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

app = Flask(__name__)
CORS(app)

def fetch_data(pair="BTC-USD", interval="1m", period="1d"):
    data = yf.download(tickers=pair, interval=interval, period=period)
    data = data.dropna()
    return data

def compute_indicators(df):
    df['rsi'] = RSIIndicator(close=df['Close']).rsi()
    macd = MACD(close=df['Close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    bb = BollingerBands(close=df['Close'])
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    return df.dropna()

def train_model(df):
    df['target'] = np.where(df['Close'].shift(-5) > df['Close'], 1, 0)
    features = ['rsi', 'macd', 'macd_signal', 'bb_upper', 'bb_lower']
    X = df[features]
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)
    return model, X_test, y_test

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        pair = data['pair']
        target_time = data['target_time']
        target_price = float(data['target_price'])

        symbol = pair.replace("/", "-")
        df = fetch_data(pair=symbol)
        df = compute_indicators(df)

        model, X_test, y_test = train_model(df)
        latest_features = X_test.iloc[-1:]
        prediction = model.predict(latest_features)[0]

        direction = "ABOVE" if prediction == 1 else "BELOW"
        return jsonify({
            "prediction": f"{pair} will likely go {direction} the target price of {target_price} by {target_time}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
