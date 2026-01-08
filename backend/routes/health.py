"""
Health check and monitoring endpoints
"""
from flask import Blueprint, jsonify
import psutil
import os
from datetime import datetime

from utils.logger import get_logger

health_bp = Blueprint('health', __name__)
logger = get_logger(__name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    try:
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'Federated HeartCare API',
            'version': '1.0.0',
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2)
            }
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check for load balancers"""
    try:
        # Check if all services are ready
        from services.prediction_service import PredictionService
        from drift.detector import DriftDetector
        
        prediction_service = PredictionService()
        drift_detector = DriftDetector()
        
        services_ready = {
            'prediction_service': prediction_service.is_ready(),
            'drift_detector': drift_detector.is_ready(),
            'models_loaded': prediction_service.models_loaded()
        }
        
        all_ready = all(services_ready.values())
        
        return jsonify({
            'ready': all_ready,
            'services': services_ready,
            'timestamp': datetime.now().isoformat()
        }), 200 if all_ready else 503
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            'ready': False,
            'error': str(e)
        }), 503

@health_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get system and application metrics"""
    try:
        from services.evaluation_service import EvaluationService
        
        eval_service = EvaluationService()
        metrics = eval_service.get_system_metrics()
        
        # Add process metrics
        process = psutil.Process(os.getpid())
        metrics['process'] = {
            'cpu_percent': process.cpu_percent(),
            'memory_mb': round(process.memory_info().rss / (1024**2), 2),
            'threads': process.num_threads(),
            'connections': len(process.connections())
        }
        
        return jsonify({
            'status': 'success',
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get metrics',
            'error': str(e)
        }), 500