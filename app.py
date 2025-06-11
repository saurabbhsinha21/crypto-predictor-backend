from flask import Flask, request, jsonify
from dateutil import parser
import traceback

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        pair = data.get("pair")
        time_str = data.get("target_time")
        target_price = float(data.get("target_price"))

        print(f"Incoming request: pair={pair}, time_str={time_str}, target_price={target_price}")

        # Parse time in flexible way (supports multiple formats)
        target_time = parser.parse(time_str)

        # Import your actual model and prediction logic here
        # Example stub:
        # prediction = your_model.predict(pair, target_time, target_price)
        prediction = "above"  # ← Temporary stub for testing

        return jsonify({"prediction": prediction})
    
    except Exception as e:
        print("Prediction error:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)