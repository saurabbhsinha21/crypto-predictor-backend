from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    pair = data.get('pair')
    target_time = data.get('target_time')
    target_price = float(data.get('target_price'))

    # Log received inputs
    print(f"Received pair={pair}, target_time={target_time}, target_price={target_price}")

    try:
        # Real logic goes here – for now just mock prediction
        prediction_direction = "ABOVE" if target_price < 108000 else "BELOW"

        return jsonify({
            "prediction": f"{pair} will go {prediction_direction} the target price of {target_price} by {target_time}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ REQUIRED for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
