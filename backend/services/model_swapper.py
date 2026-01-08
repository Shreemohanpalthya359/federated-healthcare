"""
Model swapping service for handling concept drift
"""
import os
import pickle
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)

class ModelSwapper:
    """Service for swapping models based on detected concept drift"""
    
    def __init__(self, model_dir: str = 'models/'):
        self.model_dir = model_dir
        self.specialized_models = {
            'athletic': 'specialized/athletic_model.pkl',
            'diver': 'specialized/diver_model.pkl',
            'typical': 'specialized/typical_model.pkl',
            'elderly': 'specialized/elderly_model.pkl',
            'diabetic': 'specialized/diabetic_model.pkl'
        }
        
        # Track active models per patient
        self.patient_models = {}  # patient_id -> model_type
        
        # Model performance history
        self.model_performance = {}
        
        # Drift detection thresholds
        self.drift_thresholds = {
            'athletic': {'heart_rate_var': 0.3, 'activity_level': 0.7},
            'diver': {'oxygen_saturation': 0.25, 'pressure_changes': 0.6},
            'typical': {'stability_score': 0.8}
        }
        
        # Load model metadata
        self.model_metadata = self._load_model_metadata()
        
        logger.info("ModelSwapper initialized")
    
    def _load_model_metadata(self):
        """Load metadata about available models"""
        metadata_path = os.path.join(self.model_dir, 'model_metadata.json')
        try:
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load model metadata: {e}")
        
        # Default metadata
        return {
            'athletic': {
                'description': 'Model optimized for athletic individuals',
                'trained_on': 'athletic_physiological_data',
                'accuracy': 0.92,
                'last_updated': '2024-01-01'
            },
            'diver': {
                'description': 'Model specialized for diving activities',
                'trained_on': 'diving_physiological_data',
                'accuracy': 0.88,
                'last_updated': '2024-01-01'
            },
            'typical': {
                'description': 'General model for typical individuals',
                'trained_on': 'general_population',
                'accuracy': 0.85,
                'last_updated': '2024-01-01'
            }
        }
    
    def swap_model(self, patient_id: str, drift_type: str, 
                   confidence: float = 0.7) -> Dict[str, Any]:
        """
        Swap the active model for a patient based on detected drift
        
        Args:
            patient_id: Unique patient identifier
            drift_type: Type of drift detected (athletic, diver, etc.)
            confidence: Confidence score of drift detection
            
        Returns:
            Dictionary with swap details
        """
        try:
            # Determine appropriate model based on drift type
            target_model = self._select_target_model(drift_type, confidence)
            
            # Load the new model
            new_model = self._load_model(target_model)
            if new_model is None:
                raise ValueError(f"Target model {target_model} not available")
            
            # Update patient model tracking
            previous_model = self.patient_models.get(patient_id, 'federated')
            self.patient_models[patient_id] = target_model
            
            # Record model swap
            swap_record = {
                'patient_id': patient_id,
                'previous_model': previous_model,
                'new_model': target_model,
                'drift_type': drift_type,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'model_metadata': self.model_metadata.get(target_model, {})
            }
            
            # Update performance tracking
            self._update_performance_tracking(patient_id, target_model)
            
            logger.info(f"Model swapped for patient {patient_id}: "
                       f"{previous_model} -> {target_model} (drift: {drift_type})")
            
            return swap_record
            
        except Exception as e:
            logger.error(f"Model swap failed for patient {patient_id}: {e}")
            return {
                'patient_id': patient_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _select_target_model(self, drift_type: str, confidence: float) -> str:
        """Select the most appropriate model based on drift type"""
        # Map drift types to target models
        drift_to_model = {
            'athletic': 'athletic',
            'diver': 'diver',
            'revert_to_normal': 'typical',
            'elderly': 'elderly',
            'diabetic': 'diabetic',
            'hypertensive': 'typical'  # Use typical as fallback
        }
        
        target_model = drift_to_model.get(drift_type, 'typical')
        
        # Check if model exists
        if target_model not in self.specialized_models:
            logger.warning(f"Target model {target_model} not found, using typical")
            target_model = 'typical'
        
        return target_model
    
    def _load_model(self, model_type: str):
        """Load a specialized model"""
        if model_type not in self.specialized_models:
            return None
        
        model_path = os.path.join(self.model_dir, self.specialized_models[model_type])
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to load model {model_type}: {e}")
        
        return None
    
    def _update_performance_tracking(self, patient_id: str, model_type: str):
        """Update performance tracking for model swaps"""
        if patient_id not in self.model_performance:
            self.model_performance[patient_id] = []
        
        self.model_performance[patient_id].append({
            'model_type': model_type,
            'timestamp': datetime.now().isoformat(),
            'swap_count': len(self.model_performance[patient_id]) + 1
        })
        
        # Keep only last 100 swaps per patient
        if len(self.model_performance[patient_id]) > 100:
            self.model_performance[patient_id] = self.model_performance[patient_id][-100:]
    
    def get_patient_model_history(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get model swap history for a patient"""
        return self.model_performance.get(patient_id, [])
    
    def get_active_model(self, patient_id: str) -> str:
        """Get currently active model for a patient"""
        return self.patient_models.get(patient_id, 'federated')
    
    def suggest_model_improvement(self, patient_id: str, 
                                  features: List[float]) -> Optional[str]:
        """
        Suggest if a model swap might be beneficial
        """
        try:
            # Analyze feature patterns
            feature_pattern = self._analyze_feature_pattern(features)
            
            # Check against drift thresholds
            for drift_type, thresholds in self.drift_thresholds.items():
                if self._check_drift_thresholds(feature_pattern, thresholds):
                    return drift_type
            
            return None
            
        except Exception as e:
            logger.error(f"Model suggestion failed: {e}")
            return None
    
    def _analyze_feature_pattern(self, features: List[float]) -> Dict[str, float]:
        """Analyze feature patterns for drift detection"""
        # This is a simplified implementation
        # In practice, this would use more sophisticated pattern analysis
        return {
            'heart_rate_var': abs(features[7] - 72) / 72,  # Assuming heart rate at index 7
            'activity_level': features[8] if len(features) > 8 else 0.5,
            'stability_score': 1.0 - np.std(features[:5]) / np.mean(features[:5])
        }
    
    def _check_drift_thresholds(self, pattern: Dict[str, float], 
                                thresholds: Dict[str, float]) -> bool:
        """Check if pattern exceeds drift thresholds"""
        for key, threshold in thresholds.items():
            if key in pattern and pattern[key] > threshold:
                return True
        return False
    
    def get_all_active_models(self) -> Dict[str, str]:
        """Get all currently active patient models"""
        return self.patient_models.copy()