"""
Federated HeartCare API with Live Tracking and Improved Prediction
"""
import os
import logging
import math
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
import random
import threading
import time

# Create app
app = Flask(__name__)
CORS(app)

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'federated-heartcare-secret-key')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for live tracking
tracking_active = False
tracking_thread = None
current_tracking_person = None
connected_clients = {}

# Import and register monitor routes
try:
    from routes.monitor_routes import monitor_bp
    app.register_blueprint(monitor_bp, url_prefix='/monitor')
    MONITOR_AVAILABLE = True
    logger.info("✓ Monitor routes loaded successfully")
except ImportError as e:
    MONITOR_AVAILABLE = False
    logger.warning(f"Monitor routes not found: {e}")

# Import and register prediction routes
try:
    from routes.predict import predict_bp
    app.register_blueprint(predict_bp, url_prefix='/api/v1')
    logger.info("✓ Prediction routes loaded successfully")
except ImportError as e:
    logger.warning(f"Prediction routes not found: {e}")

# Generate realistic vital signs for a specific person
def generate_vital_signs(person_id="person_001"):
    """Generate realistic vital signs for tracking"""
    base_values = {
        "person_001": {  # John Doe
            "heart_rate_range": (65, 85),
            "bp_systolic_range": (120, 135),
            "bp_diastolic_range": (75, 85),
            "o2_range": (96, 99),
            "resp_range": (14, 18),
            "temp_range": (36.5, 37.0)
        },
        "person_002": {  # Jane Smith
            "heart_rate_range": (70, 90),
            "bp_systolic_range": (125, 140),
            "bp_diastolic_range": (80, 90),
            "o2_range": (95, 98),
            "resp_range": (16, 20),
            "temp_range": (36.6, 37.1)
        },
        "person_003": {  # Robert Johnson
            "heart_rate_range": (75, 95),
            "bp_systolic_range": (130, 145),
            "bp_diastolic_range": (85, 95),
            "o2_range": (94, 97),
            "resp_range": (18, 22),
            "temp_range": (36.7, 37.2)
        }
    }
    
    person_config = base_values.get(person_id, base_values["person_001"])
    
    # Generate ECG wave data (simulated)
    ecg_points = 50
    ecg_wave = []
    for i in range(ecg_points):
        # Simulate ECG waveform
        t = i / 10.0
        base = random.uniform(-0.1, 0.1)
        
        # Add P wave
        if 2 <= t <= 3:
            base += random.uniform(0.1, 0.3)
        # Add QRS complex
        elif 3.5 <= t <= 4.5:
            base += random.uniform(0.8, 1.2)
        # Add T wave
        elif 5 <= t <= 6:
            base += random.uniform(0.2, 0.4)
        
        ecg_wave.append(round(base, 2))
    
    return {
        "person_id": person_id,
        "timestamp": datetime.now().isoformat(),
        "heart_rate": random.randint(*person_config["heart_rate_range"]),
        "blood_pressure": f"{random.randint(*person_config['bp_systolic_range'])}/{random.randint(*person_config['bp_diastolic_range'])}",
        "oxygen_saturation": random.randint(*person_config["o2_range"]),
        "respiratory_rate": random.randint(*person_config["resp_range"]),
        "temperature": round(random.uniform(*person_config["temp_range"]), 1),
        "ecg_wave": ecg_wave,
        "status": "tracking"
    }

# Live tracking thread
def live_tracking_loop():
    """Background thread for live data streaming"""
    global tracking_active, current_tracking_person
    
    while tracking_active and current_tracking_person:
        try:
            # Generate live data for the tracked person
            live_data = generate_vital_signs(current_tracking_person)
            
            # Send to all connected WebSocket clients
            socketio.emit('live_vitals', live_data)
            
            # Log every 10 seconds to avoid spam
            if int(time.time()) % 10 == 0:
                logger.info(f"Live tracking: {current_tracking_person} - HR: {live_data['heart_rate']} bpm")
            
            time.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            logger.error(f"Live tracking error: {e}")
            break

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    connected_clients[client_id] = {
        'connected_at': datetime.now().isoformat(),
        'tracking_person': None
    }
    
    logger.info(f"Client connected: {client_id}")
    emit('connected', {
        'status': 'connected',
        'message': 'Connected to Federated HeartCare Live Tracking',
        'timestamp': datetime.now().isoformat(),
        'tracking_available': True
    })

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    if client_id in connected_clients:
        del connected_clients[client_id]
    logger.info(f"Client disconnected: {client_id}")

@socketio.on('select_person')
def handle_select_person(data):
    client_id = request.sid
    person_id = data.get('person_id')
    
    if client_id in connected_clients:
        connected_clients[client_id]['tracking_person'] = person_id
    
    logger.info(f"Client {client_id} selected person: {person_id}")
    emit('person_selected', {
        'person_id': person_id,
        'message': f'Now tracking {person_id}',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('start_tracking')
def handle_start_tracking(data):
    global tracking_active, tracking_thread, current_tracking_person
    
    person_id = data.get('person_id')
    
    if not tracking_active and person_id:
        current_tracking_person = person_id
        tracking_active = True
        tracking_thread = threading.Thread(target=live_tracking_loop, daemon=True)
        tracking_thread.start()
        
        logger.info(f"Live tracking started for: {person_id}")
        emit('tracking_status', {
            'active': True,
            'person_id': person_id,
            'message': f'Live tracking started for {person_id}',
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)

@socketio.on('stop_tracking')
def handle_stop_tracking():
    global tracking_active, current_tracking_person
    
    tracking_active = False
    current_tracking_person = None
    
    logger.info("Live tracking stopped")
    emit('tracking_status', {
        'active': False,
        'message': 'Live tracking stopped',
        'timestamp': datetime.now().isoformat()
    }, broadcast=True)

@socketio.on('request_person_data')
def handle_request_person_data(data):
    person_id = data.get('person_id')
    if person_id:
        person_data = generate_vital_signs(person_id)
        emit('person_vitals', person_data)

# REST API Routes
@app.route('/')
def index():
    endpoints = {
        'health': '/api/v1/health',
        'predict': '/api/v1/predict',
        'models': '/api/v1/models',
        'live_tracking': 'ws://localhost:5001/socket.io',
        'connected_clients': len(connected_clients)
    }
    
    if MONITOR_AVAILABLE:
        endpoints.update({
            'monitor_status': '/monitor/api/monitor/status',
            'monitor_people': '/monitor/api/monitor/people',
            'live_demo': '/monitor/api/monitor/live-demo'
        })
    
    return jsonify({
        'service': 'Federated HeartCare API',
        'version': '1.0.0',
        'status': 'running',
        'live_tracking': 'active' if tracking_active else 'inactive',
        'tracking_person': current_tracking_person,
        'endpoints': endpoints
    })

@app.route('/api/v1/health')
def health():
    return jsonify({
        'status': 'success',
        'data': {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'Federated HeartCare API',
            'version': '1.0.0',
            'live_tracking': {
                'active': tracking_active,
                'person': current_tracking_person,
                'connected_clients': len(connected_clients)
            }
        }
    })

# Live tracking REST endpoints
@app.route('/api/live/start', methods=['POST'])
def start_live_tracking():
    global tracking_active, tracking_thread, current_tracking_person
    
    data = request.get_json()
    person_id = data.get('person_id') if data else None
    
    if not tracking_active and person_id:
        current_tracking_person = person_id
        tracking_active = True
        tracking_thread = threading.Thread(target=live_tracking_loop, daemon=True)
        tracking_thread.start()
        
        return jsonify({
            'status': 'success',
            'message': f'Live tracking started for {person_id}',
            'person_id': person_id,
            'timestamp': datetime.now().isoformat()
        })
    
    return jsonify({
        'status': 'error' if tracking_active else 'invalid_request',
        'message': 'Live tracking is already active' if tracking_active else 'Person ID required',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/live/stop', methods=['POST'])
def stop_live_tracking():
    global tracking_active, current_tracking_person
    
    tracking_active = False
    current_tracking_person = None
    
    return jsonify({
        'status': 'success',
        'message': 'Live tracking stopped',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/live/status')
def live_tracking_status():
    return jsonify({
        'status': 'success',
        'data': {
            'active': tracking_active,
            'person': current_tracking_person,
            'connected_clients': len(connected_clients),
            'timestamp': datetime.now().isoformat()
        }
    })

@app.route('/api/v1/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        if not data or 'features' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing features in request'
            }), 400
        
        features = data['features']
        model_type = data.get('model_type', 'federated')
        
        # Validate features length
        if len(features) != 13:
            return jsonify({
                'status': 'error',
                'message': f'Expected 13 features, got {len(features)}'
            }), 400
        
        # Unpack features with proper names
        age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal = features
        
        # Validate physiological ranges
        validation_errors = []
        
        # Age validation
        if age < 20 or age > 100:
            validation_errors.append(f"Age ({age}) outside plausible range (20-100)")
        
        # Resting BP validation (in mmHg)
        if trestbps < 80 or trestbps > 200:
            validation_errors.append(f"Resting BP ({trestbps} mmHg) outside plausible range (80-200)")
        
        # Cholesterol validation (in mg/dl)
        if chol < 100 or chol > 600:
            validation_errors.append(f"Cholesterol ({chol} mg/dl) outside plausible range (100-600)")
        
        # Max heart rate validation (should be ~220 - age)
        expected_max_hr = 220 - age
        if thalach < 60 or thalach > 220:
            validation_errors.append(f"Max heart rate ({thalach} bpm) outside plausible range (60-220)")
        elif thalach > expected_max_hr * 1.2:  # Allow 20% above theoretical max
            validation_errors.append(f"Max heart rate ({thalach} bpm) exceeds plausible maximum (~{expected_max_hr})")
        
        # If validation errors, return them
        if validation_errors:
            return jsonify({
                'status': 'validation_error',
                'message': 'Input validation failed',
                'errors': validation_errors,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Calculate risk based on medical guidelines
        risk_score = 0
        
        # Age factor
        if age >= 55:
            risk_score += 2
        elif age >= 45:
            risk_score += 1
        
        # Gender factor (1 = male, 0 = female)
        if sex == 1:  # Male
            risk_score += 1
        
        # Cholesterol factor (>240 is high)
        if chol >= 240:
            risk_score += 2
        elif chol >= 200:
            risk_score += 1
        
        # Blood pressure factor
        if trestbps >= 140:
            risk_score += 2
        elif trestbps >= 130:
            risk_score += 1
        elif trestbps < 90:  # Hypotension
            risk_score += 1
        
        # Max heart rate factor (low HR can indicate issues)
        if thalach < 100:
            risk_score += 1
        
        # Chest pain type (higher number = more severe)
        # 1: typical angina, 2: atypical angina, 3: non-anginal pain, 4: asymptomatic
        if cp == 4:  # Asymptomatic (most severe)
            risk_score += 2
        elif cp == 1:  # Typical angina
            risk_score += 1
        
        # ST depression (oldpeak)
        if oldpeak >= 2:
            risk_score += 2
        elif oldpeak >= 1:
            risk_score += 1
        
        # Number of major vessels (0-3)
        risk_score += ca  # More vessels = higher risk
        
        # Thalassemia (3 = normal, 6 = fixed defect, 7 = reversible defect)
        if thal == 7:  # Reversible defect
            risk_score += 2
        elif thal == 6:  # Fixed defect
            risk_score += 1
        
        # Fasting blood sugar (>120 mg/dl = 1)
        if fbs == 1:
            risk_score += 1
        
        # Exercise induced angina (1 = yes)
        if exang == 1:
            risk_score += 1
        
        # Convert risk score to probability (0-1 scale)
        max_possible_score = 20
        raw_probability = risk_score / max_possible_score
        
        # Apply sigmoid-like curve for more realistic probabilities
        probability = 1 / (1 + math.exp(-5 * (raw_probability - 0.5)))
        
        # Cap between 0.05 and 0.95
        probability = max(0.05, min(0.95, probability))
        
        # Convert to prediction (1 = disease, 0 = no disease)
        prediction = 1 if probability > 0.5 else 0
        
        # Determine risk level
        if probability < 0.3:
            risk_level = 'Low'
            recommendation = 'Continue healthy lifestyle with regular checkups. Your vital signs are within normal ranges.'
        elif probability < 0.7:
            risk_level = 'Moderate'
            recommendation = 'Consider lifestyle changes (diet, exercise) and consult a cardiologist for further evaluation.'
        else:
            risk_level = 'High'
            recommendation = 'Immediate consultation with a cardiologist is recommended. Please seek medical attention.'
        
        # Add specific warnings based on abnormal values
        warnings = []
        if trestbps < 90:
            warnings.append("Low resting blood pressure detected (hypotension)")
        elif trestbps >= 140:
            warnings.append("High blood pressure detected (hypertension)")
        
        if chol >= 240:
            warnings.append("High cholesterol level (hypercholesterolemia)")
        
        if thalach < 100:
            warnings.append("Low maximum heart rate during exercise")
        
        if oldpeak >= 1.5:
            warnings.append("Significant ST depression detected")
        
        # Create risk factor analysis
        risk_factors = {
            'age_risk': 'High' if age >= 55 else 'Moderate' if age >= 45 else 'Low',
            'bp_risk': 'High' if trestbps >= 140 else 'Moderate' if trestbps >= 130 or trestbps < 90 else 'Low',
            'chol_risk': 'High' if chol >= 240 else 'Moderate' if chol >= 200 else 'Low',
            'hr_risk': 'Concerning' if thalach < 100 else 'Normal',
            'st_depression': 'Significant' if oldpeak >= 1.5 else 'Moderate' if oldpeak >= 1.0 else 'Normal'
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'prediction': prediction,
                'probability': round(probability, 3),
                'risk_level': risk_level,
                'risk_percentage': round(probability * 100, 1),
                'model_used': model_type,
                'timestamp': datetime.now().isoformat(),
                'recommendations': recommendation,
                'warnings': warnings,
                'risk_factors': risk_factors,
                'risk_score': risk_score,
                'max_risk_score': max_possible_score,
                'message': 'Prediction completed successfully',
                'interpretation': f'{risk_level} risk of cardiovascular disease'
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
    return jsonify({
        'status': 'success',
        'data': {
            'models': ['federated', 'centralized', 'athletic', 'diver', 'typical'],
            'count': 5,
            'description': 'Federated models preserve privacy by training on decentralized data'
        }
    })

# Quick test endpoint for prediction
@app.route('/api/v1/test-prediction', methods=['GET'])
def test_prediction():
    """Test endpoint with sample data"""
    sample_features = [45, 1, 2, 120, 240, 0, 1, 150, 0, 1.5, 1, 0, 3]
    
    # Call the predict function internally
    from flask import g
    with app.test_request_context(json={'features': sample_features, 'model_type': 'federated'}):
        return predict()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Resource not found'
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Federated HeartCare API on port 5001...")
    logger.info("📡 Live Tracking: ENABLED")
    logger.info("   WebSocket: ws://localhost:5001/socket.io")
    logger.info("   Test prediction: http://localhost:5001/api/v1/test-prediction")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=True,
        allow_unsafe_werkzeug=True
    )