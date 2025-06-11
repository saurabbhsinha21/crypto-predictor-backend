from flask import Flask, request, jsonify
import datetime
import pandas as pd
import numpy as np
import xgboost as xgb
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from binance.client import Client

app = Flask(__name__)

# Binance API setup (public access, no keys needed)
client = Client()

def fetch_data(symbol, interval='1m', lookback='1 day ago UTC'):
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

def add_technical_indicators(df):
    df['rsi'] = RSIIndicator(close=df['close']).rsi()
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    bb = BollingerBands(close=df['close'])
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df.dropna(inplace=True)
    return df

def prepare_features(df):
    df['returns'] = df['close'].pct_change()
    df['target'] = df['close'].shift(-1) > df['close']
    df.dropna(inplace=True)
    features = ['close', 'volume', 'rsi', 'macd', 'macd_signal', 'bb_upper', 'bb_lower']
    return df[features], df['target']

def train_model(X, y):
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X, y)
    return model

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        symbol = data.get('pair', 'BTC/USDT').replace("/", "")
        target_price = float(data.get('target_price'))
        target_time = datetime.datetime.strptime(data.get('target_time'), "%Y-%m-%dT%H:%M")
        
        df = fetch_data(symbol)
        df = add_technical_indicators(df)
        X, y = prepare_features(df)
        
        model = train_model(X, y)
        latest_features = X.iloc[[-1]]
        prediction = model.predict(latest_features)[0]

        result = f"{data['pair']} will go {'ABOVE' if prediction else 'BELOW'} the target price of {target_price} by {target_time}"
        return jsonify({'prediction': result})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
