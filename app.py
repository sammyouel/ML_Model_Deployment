# app.py
import joblib
from flask import Flask, request, jsonify
import numpy as np
from prometheus_client import generate_latest, Counter, Gauge, make_wsgi_app, CollectorRegistry
import logging
from datetime import datetime
import os

app = Flask(__name__)
model = joblib.load("diabetes_model.joblib")

# Configure logging
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prediction.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define Prometheus metrics
registry = CollectorRegistry()
REQUEST_COUNT = Counter('model_api_requests_total', 'Total number of requests to the model API', registry=registry)
PREDICTION_GAUGE = Gauge('model_api_last_prediction', 'Last prediction made by the model', registry=registry)

@app.route('/predict', methods=['POST'])
def predict():
    REQUEST_COUNT.inc()
    try:
        data = request.get_json()
        features = np.array(data['features']).reshape(1, -1)
        prediction = model.predict(features)[0]
        PREDICTION_GAUGE.set(prediction)
        logging.info(f"Prediction: {prediction}, Features: {data['features']}")
        return jsonify({'prediction': prediction})
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return jsonify({'error': str(e)})

@app.route('/metrics')
def metrics():
    return generate_latest(registry)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')