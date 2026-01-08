"""
Data scaling utilities for heart disease prediction
"""
import numpy as np
import joblib
import os
from typing import List, Union, Optional
import json

class DataScaler:
    """Scaler for heart disease features"""
    
    def __init__(self, scaler_type: str = 'standard'):
        self.scaler_type = scaler_type
        self.scalers = {}
        self.feature_ranges = {}
        self.feature_names = []
        
        # Load or initialize scalers
        self._initialize_scalers()
    
    def _initialize_scalers(self):
        """Initialize scalers based on feature configurations"""
        # Define feature configurations
        self.feature_configs = {
            'age': {'min': 29, 'max': 77, 'scaler': 'minmax'},
            'sex': {'categories': [0, 1], 'scaler': 'none'},
            'chest_pain_type': {'min': 0, 'max': 3, 'scaler': 'minmax'},
            'resting_bp': {'min': 94, 'max': 200, 'scaler': 'minmax'},
            'cholesterol': {'min': 126, 'max': 564, 'scaler': 'minmax'},
            'fasting_blood_sugar': {'categories': [0, 1], 'scaler': 'none'},
            'resting_ecg': {'min': 0, 'max': 2, 'scaler': 'minmax'},
            'max_heart_rate': {'min': 71, 'max': 202, 'scaler': 'minmax'},
            'exercise_induced_angina': {'categories': [0, 1], 'scaler': 'none'},
            'oldpeak': {'min': 0, 'max': 6.2, 'scaler': 'minmax'},
            'slope': {'min': 0, 'max': 2, 'scaler': 'minmax'},
            'num_major_vessels': {'min': 0, 'max': 3, 'scaler': 'minmax'},
            'thalassemia': {'min': 0, 'max': 3, 'scaler': 'minmax'}
        }
        
        self.feature_names = list(self.feature_configs.keys())
        
        # Initialize scaling parameters
        for feature, config in self.feature_configs.items():
            self.feature_ranges[feature] = {
                'min': config.get('min', 0),
                'max': config.get('max', 1),
                'scaler': config.get('scaler', 'minmax')
            }
    
    def fit(self, X: np.ndarray, feature_names: List[str] = None):
        """
        Fit scaler to data
        
        Args:
            X: Feature matrix
            feature_names: List of feature names
        """
        if feature_names:
            self.feature_names = feature_names
        
        # Store feature statistics
        for i, feature in enumerate(self.feature_names):
            if i < X.shape[1]:
                feature_data = X[:, i]
                
                if feature in self.feature_ranges:
                    config = self.feature_configs[feature]
                    
                    if config['scaler'] == 'standard':
                        self.feature_ranges[feature]['mean'] = np.mean(feature_data)
                        self.feature_ranges[feature]['std'] = np.std(feature_data)
                    elif config['scaler'] == 'minmax':
                        self.feature_ranges[feature]['data_min'] = np.min(feature_data)
                        self.feature_ranges[feature]['data_max'] = np.max(feature_data)
    
    def transform(self, features: Union[List[float], np.ndarray]) -> List[float]:
        """
        Transform features using appropriate scaling
        
        Args:
            features: Input features
        
        Returns:
            Scaled features
        """
        if isinstance(features, list):
            features = np.array(features)
        
        scaled_features = []
        
        for i, feature_name in enumerate(self.feature_names):
            if i >= len(features):
                # Use default scaling if feature missing
                scaled_features.append(0.0)
                continue
            
            value = features[i]
            config = self.feature_ranges.get(feature_name, {})
            scaler_type = config.get('scaler', 'minmax')
            
            # Apply appropriate scaling
            if scaler_type == 'none':
                scaled_value = float(value)
            elif scaler_type == 'minmax':
                if 'data_min' in config and 'data_max' in config:
                    # Use learned min-max
                    min_val = config['data_min']
                    max_val = config['data_max']
                else:
                    # Use configured min-max
                    min_val = config.get('min', 0)
                    max_val = config.get('max', 1)
                
                if max_val > min_val:
                    scaled_value = (value - min_val) / (max_val - min_val)
                else:
                    scaled_value = 0.0
                
                # Clip to [0, 1]
                scaled_value = max(0.0, min(1.0, scaled_value))
                
            elif scaler_type == 'standard':
                if 'mean' in config and 'std' in config:
                    mean = config['mean']
                    std = config['std']
                    if std > 0:
                        scaled_value = (value - mean) / std
                    else:
                        scaled_value = 0.0
                else:
                    scaled_value = value
            else:
                scaled_value = float(value)
            
            scaled_features.append(scaled_value)
        
        return scaled_features
    
    def inverse_transform(self, scaled_features: List[float]) -> List[float]:
        """
        Inverse transform scaled features back to original scale
        
        Args:
            scaled_features: Scaled features
        
        Returns:
            Original scale features
        """
        original_features = []
        
        for i, feature_name in enumerate(self.feature_names):
            if i >= len(scaled_features):
                original_features.append(0.0)
                continue
            
            scaled_value = scaled_features[i]
            config = self.feature_ranges.get(feature_name, {})
            scaler_type = config.get('scaler', 'minmax')
            
            # Apply inverse scaling
            if scaler_type == 'none':
                original_value = scaled_value
            elif scaler_type == 'minmax':
                if 'data_min' in config and 'data_max' in config:
                    min_val = config['data_min']
                    max_val = config['data_max']
                else:
                    min_val = config.get('min', 0)
                    max_val = config.get('max', 1)
                
                original_value = scaled_value * (max_val - min_val) + min_val
                
            elif scaler_type == 'standard':
                if 'mean' in config and 'std' in config:
                    mean = config['mean']
                    std = config['std']
                    original_value = scaled_value * std + mean
                else:
                    original_value = scaled_value
            else:
                original_value = scaled_value
            
            original_features.append(original_value)
        
        return original_features
    
    def save(self, filepath: str):
        """Save scaler configuration"""
        config = {
            'feature_ranges': self.feature_ranges,
            'feature_names': self.feature_names,
            'scaler_type': self.scaler_type
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load(self, filepath: str):
        """Load scaler configuration"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                config = json.load(f)
            
            self.feature_ranges = config.get('feature_ranges', {})
            self.feature_names = config.get('feature_names', [])
            self.scaler_type = config.get('scaler_type', 'standard')
    
    def get_feature_info(self) -> Dict[str, Any]:
        """Get feature information and scaling details"""
        return {
            'feature_names': self.feature_names,
            'feature_configs': self.feature_configs,
            'scaler_type': self.scaler_type,
            'total_features': len(self.feature_names)
        }