# routes/monitor_routes.py
from flask import Blueprint, jsonify
from datetime import datetime
import random

# Create blueprint for monitoring
monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/api/monitor/status')
def get_status():
    """Check tracking status"""
    return jsonify({
        "active": True,
        "message": "Live tracking system ready",
        "live_websocket": "available",
        "timestamp": datetime.now().isoformat()
    })

@monitor_bp.route('/api/monitor/people')
def get_people():
    """Get list of people available for tracking"""
    people = [
        {
            "id": "person_001",
            "name": "John Doe",
            "age": 58,
            "condition": "Hypertension",
            "room": "ICU-101",
            "status": "critical",
            "connected": True,
            "last_update": datetime.now().isoformat()
        },
        {
            "id": "person_002",
            "name": "Jane Smith",
            "age": 65,
            "condition": "Coronary Artery Disease",
            "room": "ICU-102",
            "status": "stable",
            "connected": True,
            "last_update": datetime.now().isoformat()
        },
        {
            "id": "person_003",
            "name": "Robert Johnson",
            "age": 72,
            "condition": "Heart Failure",
            "room": "ICU-103",
            "status": "monitoring",
            "connected": True,
            "last_update": datetime.now().isoformat()
        }
    ]
    return jsonify(people)

# Keep the old endpoint for backward compatibility
@monitor_bp.route('/api/monitor/patients')
def get_patients():
    """Backward compatibility endpoint"""
    return get_people()

@monitor_bp.route('/api/monitor/alerts')
def get_alerts():
    """Get current alerts"""
    alerts = [
        {
            "id": 1,
            "person_id": "person_001",
            "type": "heart_rate",
            "message": "Heart rate above threshold: 118 bpm",
            "severity": "high",
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False
        },
        {
            "id": 2,
            "person_id": "person_003",
            "type": "blood_pressure",
            "message": "Systolic BP elevated: 142 mmHg",
            "severity": "medium",
            "timestamp": datetime.now().isoformat(),
            "acknowledged": True
        }
    ]
    return jsonify(alerts)

@monitor_bp.route('/api/monitor/live-demo')
def live_demo():
    """Get demo live data"""
    return jsonify({
        "heart_rate": random.randint(60, 120),
        "blood_pressure": f"{random.randint(110, 140)}/{random.randint(70, 90)}",
        "oxygen_saturation": random.randint(95, 100),
        "respiratory_rate": random.randint(12, 20),
        "temperature": round(random.uniform(36.5, 37.5), 1),
        "timestamp": datetime.now().isoformat()
    })

@monitor_bp.route('/api/monitor/test')
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        "status": "success",
        "message": "Live tracking API is working correctly",
        "live_tracking": "available",
        "websocket": "enabled",
        "timestamp": datetime.now().isoformat()
    })