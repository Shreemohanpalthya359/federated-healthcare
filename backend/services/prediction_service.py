"""
Prediction service for heart disease risk assessment
"""
import numpy as np
import joblib
import os
import pickle
from typing import Dict, List, Any, Tuple
from datetime import datetime
import json

from utils.logger import get_logger
from utils.scaler import DataScaler
from drift.detector import DriftDetector

logger = get_logger(__name__)

class PredictionService:
    """Service for making heart disease predictions"""
    
    def __init__(self, model_dir: str = 'models/'):
        self.model_dir = model_dir
        self.scaler = DataScaler()
        self.drift_detector = DriftDetector()
        
        # Load models
        self.models = {
            'centralized': self._load_model('centralized/heart_disease_model.pkl'),
            'federated': self._load_model('federated/heart_disease_federated.pkl'),
            'athletic': self._load_model('specialized/athletic_model.pkl'),
            'diver': self._load_model('specialized/diver_model.pkl'),
            'typical': self._load_model('specialized/typical_model.pkl')
        }
        
        # Load feature names
        self.feature_names = self._load_feature_names()
        
        # Initialize statistics
        self.prediction_stats = {
            'total_predictions': 0,
            'successful_predictions': 0,
            'failed_predictions': 0,
            'last_prediction_time': None,
            'model_usage': {model: 0 for model in self.models.keys()}
        }
        
        logger.info("PredictionService initialized")
    
    def _load_model(self, model_path: str):
        """Load a trained model from disk"""
        full_path = os.path.join(self.model_dir, model_path)
        try:
            if os.path.exists(full_path):
                with open(full_path, 'rb') as f:
                    model = pickle.load(f)
                logger.info(f"Loaded model from {full_path}")
                return model
            else:
                logger.warning(f"Model not found at {full_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to load model from {full_path}: {e}")
            return None
    
    def _load_feature_names(self):
        """Load feature names from configuration"""
        config_path = os.path.join(self.model_dir, 'feature_config.json')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return config.get('feature_names', [])
        except Exception as e:
            logger.error(f"Failed to load feature config: {e}")
        
        # Default feature names
        return [
            'age', 'sex', 'chest_pain_type', 'resting_bp', 'cholesterol',
            'fasting_blood_sugar', 'resting_ecg', 'max_heart_rate',
            'exercise_induced_angina', 'oldpeak', 'slope', 'num_major_vessels',
            'thalassemia'
        ]
    
    def predict(self, features: List[float], patient_id: str = None, 
                model_type: str = 'federated') -> Dict[str, Any]:
        """
        Make prediction for given features
        
        Args:
            features: List of feature values
            patient_id: Unique patient identifier
            model_type: Type of model to use
            
        Returns:
            Dictionary containing prediction and metadata
        """
        try:
            self.prediction_stats['total_predictions'] += 1
            
            # Validate input
            if len(features) != len(self.feature_names):
                raise ValueError(
                    f"Expected {len(self.feature_names)} features, "
                    f"got {len(features)}"
                )
            
            # Scale features
            scaled_features = self.scaler.transform(features)
            
            # Select model
            model = self.models.get(model_type, self.models['federated'])
            if model is None:
                raise ValueError(f"Model {model_type} not loaded")
            
            # Make prediction
            features_array = np.array(scaled_features).reshape(1, -1)
            prediction_proba = model.predict_proba(features_array)[0]
            prediction = model.predict(features_array)[0]
            
            # Interpret prediction
            risk_level = self._interpret_prediction(prediction_proba)
            
            # Update statistics
            self.prediction_stats['successful_predictions'] += 1
            self.prediction_stats['model_usage'][model_type] += 1
            self.prediction_stats['last_prediction_time'] = datetime.now()
            
            result = {
                'patient_id': patient_id,
                'prediction': int(prediction),
                'probability': float(prediction_proba[1]),  # Probability of heart disease
                'risk_level': risk_level,
                'confidence': self._calculate_confidence(prediction_proba),
                'model_used': model_type,
                'timestamp': datetime.now().isoformat(),
                'features_used': self.feature_names
            }
            
            logger.info(f"Prediction made for patient {patient_id}: "
                       f"risk={risk_level}, model={model_type}")
            
            return result
            
        except Exception as e:
            self.prediction_stats['failed_predictions'] += 1
            logger.error(f"Prediction failed: {e}")
            raise
    
    def _interpret_prediction(self, probabilities: np.ndarray) -> str:
        """Interpret prediction probabilities into risk levels"""
        disease_prob = probabilities[1]
        
        if disease_prob < 0.2:
            return 'Very Low'
        elif disease_prob < 0.4:
            return 'Low'
        elif disease_prob < 0.6:
            return 'Moderate'
        elif disease_prob < 0.8:
            return 'High'
        else:
            return 'Very High'
    
    def _calculate_confidence(self, probabilities: np.ndarray) -> float:
        """Calculate prediction confidence"""
        max_prob = np.max(probabilities)
        confidence = max_prob * 100
        return round(confidence, 2)
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current status of all models"""
        status = {
            'models_loaded': {},
            'prediction_statistics': self.prediction_stats,
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names,
            'timestamp': datetime.now().isoformat()
        }
        
        for model_name, model in self.models.items():
            status['models_loaded'][model_name] = model is not None
        
        return status
    
    def retrain_model(self, model_type: str) -> Dict[str, Any]:
        """Retrain a specific model"""
        # This would typically trigger federated training
        # For now, return placeholder response
        logger.info(f"Retraining model: {model_type}")
        
        return {
            'status': 'initiated',
            'model_type': model_type,
            'timestamp': datetime.now().isoformat(),
            'message': 'Retraining process started'
        }
    
    def models_loaded(self) -> bool:
        """Check if all models are loaded"""
        return all(model is not None for model in self.models.values())
    
    def is_ready(self) -> bool:
        """Check if service is ready to serve requests"""
        return len(self.models) > 0 and self.models_loaded()