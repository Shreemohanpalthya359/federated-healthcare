"""
Fixed Flask app for Federated HeartCare
"""
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Create app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'federated-heartcare-secret-key')
app.config['MODEL_STORAGE'] = 'models/'
app.config['DATA_STORAGE'] = 'data/'

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    """Log request details"""
    logger.info(f"Request: {datetime.now()} - {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Add security headers"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/')
def index():
    return jsonify({
        'service': 'Federated HeartCare API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/v1/health',
            'predict': '/api/v1/predict',
            'models': '/api/v1/models'
        }
    })

@app.route('/api/v1/health')
def health():
    return jsonify({
        'status': 'success',
        'data': {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'Federated HeartCare API',
            'version': '1.0.0'
        }
    })

@app.route('/api/v1/predict', methods=['POST'])
def predict():
    import pickle
    import numpy as np
    
    try:
        data = request.get_json()
        
        if not data or 'features' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing features in request'
            }), 400
        
        features = data['features']
        model_type = data.get('model_type', 'federated')
        
        # Load model
        if model_type == 'federated':
            model_path = 'models/federated/heart_disease_federated.pkl'
        elif model_type in ['athletic', 'diver', 'typical']:
            model_path = f'models/federated/{model_type}.pkl'
        else:
            model_path = 'models/centralized/heart_disease_model.pkl'
        
        if not os.path.exists(model_path):
            return jsonify({
                'status': 'error',
                'message': f'Model {model_type} not found'
            }), 404
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Make prediction
        features_array = np.array(features).reshape(1, -1)
        prediction = int(model.predict(features_array)[0])
        probability = float(model.predict_proba(features_array)[0][1])
        
        # Determine risk level
        if probability < 0.3:
            risk_level = 'Low'
        elif probability < 0.7:
            risk_level = 'Moderate'
        else:
            risk_level = 'High'
        
        return jsonify({
            'status': 'success',
            'data': {
                'prediction': prediction,
                'probability': probability,
                'risk_level': risk_level,
                'model_used': model_type,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/v1/models')
def list_models():
    """List available models"""
    models = []
    
    # Check federated models
    federated_dir = 'models/federated'
    if os.path.exists(federated_dir):
        for file in os.listdir(federated_dir):
            if file.endswith('.pkl'):
                models.append(file.replace('.pkl', ''))
    
    # Check centralized model
    centralized_file = 'models/centralized/heart_disease_model.pkl'
    if os.path.exists(centralized_file):
        models.append('centralized')
    
    return jsonify({
        'status': 'success',
        'data': {
            'models': models,
            'count': len(models)
        }
    })

if __name__ == '__main__':
    logger.info("Starting Federated HeartCare API on port 5001...")
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )