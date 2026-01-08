"""
Prediction endpoints for heart disease risk assessment
"""
from flask import Blueprint, request, jsonify
import numpy as np
import json

from services.prediction_service import PredictionService
from services.model_swapper import ModelSwapper
from drift.detector import DriftDetector
from utils.helpers import validate_patient_data

predict_bp = Blueprint('predict', __name__)

# Initialize services
prediction_service = PredictionService()
model_swapper = ModelSwapper()
drift_detector = DriftDetector()

@predict_bp.route('/predict', methods=['POST'])
def predict():
    """
    Make heart disease prediction for a patient
    Expects JSON with patient features
    """
    try:
        data = request.get_json()
        
        # Validate input
        validation_result = validate_patient_data(data)
        if not validation_result['valid']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid input data',
                'errors': validation_result['errors']
            }), 400
        
        # Extract patient data
        patient_id = data.get('patient_id', 'anonymous')
        features = data['features']
        model_type = data.get('model_type', 'federated')  # federated or centralized
        
        # Get prediction
        result = prediction_service.predict(
            features=features,
            patient_id=patient_id,
            model_type=model_type
        )
        
        # Check for concept drift
        drift_detected = drift_detector.detect_drift(
            features=features,
            prediction=result['prediction'],
            patient_id=patient_id
        )
        
        # If drift detected, swap model
        if drift_detected['drift_detected']:
            new_model = model_swapper.swap_model(
                patient_id=patient_id,
                drift_type=drift_detected['drift_type']
            )
            result['model_swapped'] = True
            result['new_model'] = new_model
        else:
            result['model_swapped'] = False
        
        # Add drift information
        result['drift_detected'] = drift_detected['drift_detected']
        result['drift_confidence'] = drift_detected['confidence']
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Prediction failed',
            'error': str(e)
        }), 500

@predict_bp.route('/batch_predict', methods=['POST'])
def batch_predict():
    """
    Make predictions for multiple patients
    """
    try:
        data = request.get_json()
        patients = data.get('patients', [])
        
        results = []
        for patient_data in patients:
            result = prediction_service.predict(
                features=patient_data['features'],
                patient_id=patient_data.get('patient_id', 'anonymous'),
                model_type=patient_data.get('model_type', 'federated')
            )
            results.append(result)
        
        return jsonify({
            'status': 'success',
            'data': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Batch prediction failed',
            'error': str(e)
        }), 500

@predict_bp.route('/model_status', methods=['GET'])
def get_model_status():
    """
    Get current model status and statistics
    """
    try:
        status = prediction_service.get_model_status()
        
        return jsonify({
            'status': 'success',
            'data': status
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get model status',
            'error': str(e)
        }), 500

@predict_bp.route('/retrain', methods=['POST'])
def retrain_model():
    """
    Trigger manual retraining of models
    """
    try:
        data = request.get_json()
        model_type = data.get('model_type', 'federated')
        
        result = prediction_service.retrain_model(model_type)
        
        return jsonify({
            'status': 'success',
            'message': 'Retraining initiated',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Retraining failed',
            'error': str(e)
        }), 500