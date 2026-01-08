"""
Federated HeartCare API with Live Monitoring
"""
import os
import logging
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

# Global variables for live monitoring
monitoring_active = False
monitoring_thread = None

# Try to import and register monitor routes
try:
    from routes.monitor_routes import monitor_bp
    app.register_blueprint(monitor_bp, url_prefix='/monitor')
    MONITOR_AVAILABLE = True
    logger.info("✓ Monitor routes loaded successfully")
except ImportError as e:
    MONITOR_AVAILABLE = False
    logger.warning(f"Monitor routes not found: {e}")

# Live Monitoring Functions
def generate_live_vitals():
    """Generate mock real-time vital signs"""
    return {
        "timestamp": datetime.now().isoformat(),
        "heart_rate": random.randint(60, 120),
        "blood_pressure": f"{random.randint(110, 140)}/{random.randint(70, 90)}",
        "oxygen_saturation": random.randint(95, 100),
        "respiratory_rate": random.randint(12, 20),
        "temperature": round(random.uniform(36.5, 37.5), 1),
        "ecg_lead": [random.uniform(-0.5, 1.0) for _ in range(10)]
    }

def live_monitoring_loop():
    """Background thread for live data streaming"""
    global monitoring_active
    while monitoring_active:
        try:
            # Generate and emit live data
            live_data = {
                "patient_001": generate_live_vitals(),
                "patient_002": generate_live_vitals(),
                "patient_003": generate_live_vitals()
            }
            
            # Send to all connected WebSocket clients
            socketio.emit('live_vitals', live_data)
            time.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            logger.error(f"Live monitoring error: {e}")
            break

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {
        'status': 'connected',
        'message': 'Welcome to Federated HeartCare Live Monitor',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('start_monitoring')
def handle_start_monitoring():
    global monitoring_active, monitoring_thread
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=live_monitoring_loop, daemon=True)
        monitoring_thread.start()
        emit('monitoring_status', {'active': True, 'message': 'Live monitoring started'})

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    global monitoring_active
    monitoring_active = False
    emit('monitoring_status', {'active': False, 'message': 'Live monitoring stopped'})

# REST API Routes
@app.route('/')
def index():
    endpoints = {
        'health': '/api/v1/health',
        'predict': '/api/v1/predict',
        'models': '/api/v1/models',
        'websocket': 'ws://localhost:5001/socket.io (for live monitoring)'
    }
    
    if MONITOR_AVAILABLE:
        endpoints.update({
            'monitor_status': '/monitor/api/monitor/status',
            'monitor_patients': '/monitor/api/monitor/patients',
            'monitor_test': '/monitor/api/monitor/test',
            'live_monitor_start': '/api/live/start (POST)',
            'live_monitor_stop': '/api/live/stop (POST)'
        })
    
    return jsonify({
        'service': 'Federated HeartCare API',
        'version': '1.0.0',
        'status': 'running',
        'monitoring': 'available' if MONITOR_AVAILABLE else 'not available',
        'live_websocket': 'enabled',
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
            'monitoring': 'available' if MONITOR_AVAILABLE else 'not available',
            'live_websocket': 'active',
            'connected_clients': len(socketio.server.manager.rooms.get('/', {}))
        }
    })

# Live monitoring REST endpoints
@app.route('/api/live/start', methods=['POST'])
def start_live_monitoring():
    global monitoring_active, monitoring_thread
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=live_monitoring_loop, daemon=True)
        monitoring_thread.start()
        return jsonify({
            'status': 'success',
            'message': 'Live monitoring started',
            'timestamp': datetime.now().isoformat()
        })
    return jsonify({
        'status': 'already_running',
        'message': 'Live monitoring is already active'
    })

@app.route('/api/live/stop', methods=['POST'])
def stop_live_monitoring():
    global monitoring_active
    monitoring_active = False
    return jsonify({
        'status': 'success',
        'message': 'Live monitoring stopped',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/live/status')
def live_monitoring_status():
    return jsonify({
        'status': 'success',
        'data': {
            'active': monitoring_active,
            'connected_clients': len(socketio.server.manager.rooms.get('/', {})),
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
        
        # For now, return mock prediction
        return jsonify({
            'status': 'success',
            'data': {
                'prediction': 0,
                'probability': 0.25,
                'risk_level': 'Low',
                'model_used': 'federated',
                'timestamp': datetime.now().isoformat(),
                'note': 'Mock prediction - install scikit-learn for real predictions'
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
            'count': 5
        }
    })

if __name__ == '__main__':
    logger.info("🚀 Starting Federated HeartCare API on port 5001...")
    logger.info("📡 WebSocket Live Monitoring: ENABLED")
    logger.info("   Connect via: ws://localhost:5001/socket.io")
    logger.info("   Test monitor: http://localhost:5001/monitor/api/monitor/test")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=True,
        allow_unsafe_werkzeug=True
    )