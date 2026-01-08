"""
Helper functions and utilities
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Union, Optional
from datetime import datetime
import hashlib
import json
import os

def validate_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate patient data for prediction
    
    Args:
        data: Patient data dictionary
    
    Returns:
        Validation result
    """
    errors = []
    warnings = []
    
    # Check required fields
    if 'features' not in data:
        errors.append("Missing 'features' field")
        return {'valid': False, 'errors': errors}
    
    features = data['features']
    
    # Check feature count
    if not isinstance(features, (list, np.ndarray)):
        errors.append("Features must be a list or array")
    else:
        feature_count = len(features)
        if feature_count != 13:  # Standard heart disease features
            warnings.append(f"Expected 13 features, got {feature_count}")
        
        # Validate feature values
        for i, value in enumerate(features):
            if not isinstance(value, (int, float, np.number)):
                errors.append(f"Feature {i} must be numeric")
                break
            
            # Check for extreme values
            if isinstance(value, (int, float)):
                if value < 0:
                    warnings.append(f"Feature {i} has negative value: {value}")
                if value > 1000:  # Arbitrary large value
                    warnings.append(f"Feature {i} has unusually large value: {value}")
    
    # Validate optional fields
    if 'patient_id' in data and not isinstance(data['patient_id'], str):
        errors.append("patient_id must be a string")
    
    if 'model_type' in data and data['model_type'] not in ['federated', 'centralized']:
        warnings.append(f"model_type should be 'federated' or 'centralized', got {data['model_type']}")
    
    # Check for missing values
    if isinstance(features, list):
        if any(v is None for v in features):
            errors.append("Features contain None values")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def calculate_risk_score(features: List[float], 
                        prediction: int, 
                        confidence: float) -> Dict[str, Any]:
    """
    Calculate comprehensive risk score
    
    Args:
        features: Patient features
        prediction: Model prediction (0 or 1)
        confidence: Prediction confidence
    
    Returns:
        Risk score details
    """
    # Base risk from prediction
    base_risk = prediction * confidence
    
    # Extract relevant features for risk calculation
    # Assuming standard heart disease feature order
    risk_factors = {
        'age_risk': min(features[0] / 100, 1.0) if len(features) > 0 else 0,
        'blood_pressure_risk': min(features[3] / 200, 1.0) if len(features) > 3 else 0,
        'cholesterol_risk': min(features[4] / 300, 1.0) if len(features) > 4 else 0,
        'heart_rate_risk': 1 - min(features[7] / 200, 1.0) if len(features) > 7 else 0,  # Lower is worse
        'oldpeak_risk': min(features[9] / 4, 1.0) if len(features) > 9 else 0
    }
    
    # Calculate weighted risk
    weights = {
        'age_risk': 0.2,
        'blood_pressure_risk': 0.25,
        'cholesterol_risk': 0.2,
        'heart_rate_risk': 0.2,
        'oldpeak_risk': 0.15
    }
    
    weighted_risk = sum(risk_factors[factor] * weights[factor] 
                       for factor in risk_factors.keys())
    
    # Combine with model prediction
    final_risk = 0.7 * base_risk + 0.3 * weighted_risk
    
    # Determine risk level
    if final_risk < 0.2:
        risk_level = 'Very Low'
        recommendation = 'Continue regular checkups'
    elif final_risk < 0.4:
        risk_level = 'Low'
        recommendation = 'Maintain healthy lifestyle'
    elif final_risk < 0.6:
        risk_level = 'Moderate'
        recommendation = 'Consult healthcare provider'
    elif final_risk < 0.8:
        risk_level = 'High'
        recommendation = 'Schedule immediate consultation'
    else:
        risk_level = 'Very High'
        recommendation = 'Seek immediate medical attention'
    
    return {
        'final_risk_score': round(final_risk, 4),
        'risk_level': risk_level,
        'recommendation': recommendation,
        'base_prediction_risk': round(base_risk, 4),
        'weighted_feature_risk': round(weighted_risk, 4),
        'risk_factors': {k: round(v, 4) for k, v in risk_factors.items()},
        'timestamp': datetime.now().isoformat()
    }

def anonymize_patient_id(patient_id: str, salt: str = 'federated-heartcare') -> str:
    """
    Anonymize patient ID for privacy
    
    Args:
        patient_id: Original patient ID
        salt: Salt for hashing
    
    Returns:
        Anonymized patient ID
    """
    if not patient_id:
        return 'anonymous'
    
    # Create hash of patient ID with salt
    hash_input = f"{patient_id}:{salt}:{datetime.now().strftime('%Y%W')}"
    hashed = hashlib.sha256(hash_input.encode()).hexdigest()
    
    # Return first 16 characters of hash
    return hashed[:16]

def create_patient_summary(features: List[float], 
                          prediction_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create comprehensive patient summary
    
    Args:
        features: Patient features
        prediction_result: Prediction results
    
    Returns:
        Patient summary
    """
    # Map features to human-readable names
    feature_names = [
        'Age', 'Sex', 'Chest Pain Type', 'Resting Blood Pressure', 
        'Cholesterol', 'Fasting Blood Sugar', 'Resting ECG',
        'Maximum Heart Rate', 'Exercise Induced Angina',
        'ST Depression', 'Slope', 'Number of Major Vessels',
        'Thalassemia'
    ]
    
    # Create feature mapping
    feature_mapping = {}
    for i, (name, value) in enumerate(zip(feature_names, features)):
        if i < len(feature_names):
            feature_mapping[name] = {
                'value': float(value),
                'unit': self._get_feature_unit(name),
                'interpretation': self._interpret_feature(name, value)
            }
    
    # Extract key metrics from prediction
    summary = {
        'patient_id': prediction_result.get('patient_id', 'anonymous'),
        'prediction': {
            'has_heart_disease': bool(prediction_result.get('prediction', 0)),
            'probability': prediction_result.get('probability', 0),
            'confidence': prediction_result.get('confidence', 0),
            'risk_level': prediction_result.get('risk_level', 'Unknown')
        },
        'features': feature_mapping,
        'model_info': {
            'model_used': prediction_result.get('model_used', 'unknown'),
            'drift_detected': prediction_result.get('drift_detected', False),
            'model_swapped': prediction_result.get('model_swapped', False)
        },
        'timestamp': prediction_result.get('timestamp', datetime.now().isoformat()),
        'risk_assessment': calculate_risk_score(
            features,
            prediction_result.get('prediction', 0),
            prediction_result.get('confidence', 0)
        )
    }
    
    return summary

def _get_feature_unit(feature_name: str) -> str:
    """Get unit for a feature"""
    units = {
        'Age': 'years',
        'Resting Blood Pressure': 'mm Hg',
        'Cholesterol': 'mg/dL',
        'Maximum Heart Rate': 'bpm',
        'ST Depression': 'mm'
    }
    return units.get(feature_name, '')

def _interpret_feature(feature_name: str, value: float) -> str:
    """Interpret feature value"""
    interpretations = {
        'Age': lambda v: 'Young' if v < 40 else 'Middle-aged' if v < 60 else 'Senior',
        'Resting Blood Pressure': lambda v: 'Normal' if v < 120 else 'Elevated' if v < 130 
                                         else 'High Stage 1' if v < 140 
                                         else 'High Stage 2' if v < 180 else 'Hypertensive Crisis',
        'Cholesterol': lambda v: 'Desirable' if v < 200 else 'Borderline High' if v < 240 
                               else 'High',
        'Maximum Heart Rate': lambda v: 'Low' if v < 100 else 'Normal' if v < 150 
                                      else 'High',
        'Sex': lambda v: 'Female' if v == 0 else 'Male'
    }
    
    if feature_name in interpretations:
        try:
            return interpretations[feature_name](value)
        except:
            return 'Unknown'
    
    return 'Unknown'

def save_prediction_log(prediction_data: Dict[str, Any], 
                       log_dir: str = 'logs/predictions/'):
    """
    Save prediction to log file
    
    Args:
        prediction_data: Prediction data to log
        log_dir: Directory for log files
    """
    try:
        os.makedirs(log_dir, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(log_dir, f'predictions_{timestamp}.json')
        
        # Load existing logs or create new
        predictions = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                predictions = json.load(f)
        
        # Add new prediction
        predictions.append(prediction_data)
        
        # Save back to file
        with open(log_file, 'w') as f:
            json.dump(predictions, f, indent=2)
        
    except Exception as e:
        print(f"Failed to save prediction log: {e}")

def load_config(config_file: str = 'config.json') -> Dict[str, Any]:
    """
    Load configuration from file
    
    Args:
        config_file: Path to config file
    
    Returns:
        Configuration dictionary
    """
    default_config = {
        'server': {
            'host': '0.0.0.0',
            'port': 5000,
            'debug': False
        },
        'models': {
            'directory': 'models/',
            'default_model': 'federated',
            'retrain_interval': 3600  # seconds
        },
        'federated': {
            'min_clients': 3,
            'max_clients': 10,
            'rounds_before_eval': 5,
            'aggregation_method': 'fedavg'
        },
        'drift': {
            'detection_window': 100,
            'threshold': 0.05,
            'monitor_interval': 300
        },
        'privacy': {
            'differential_privacy': True,
            'epsilon': 1.0,
            'delta': 1e-5
        }
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
            
            # Merge with default config
            merged_config = default_config.copy()
            merged_config.update(loaded_config)
            return merged_config
        else:
            # Save default config
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    except Exception as e:
        print(f"Failed to load config: {e}")
        return default_config

def format_response(status: str, data: Any = None, 
                   message: str = None, error: str = None) -> Dict[str, Any]:
    """
    Format API response consistently
    
    Args:
        status: Response status
        data: Response data
        message: Optional message
        error: Optional error details
    
    Returns:
        Formatted response dictionary
    """
    response = {
        'status': status,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if error:
        response['error'] = error
    
    return response