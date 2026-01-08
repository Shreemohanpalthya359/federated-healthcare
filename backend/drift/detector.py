"""
Concept drift detector for physiological signals
"""
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from utils.logger import get_logger

logger = get_logger(__name__)

class DriftDetector:
    """Detects concept drift in physiological signals"""
    
    def __init__(self, window_size: int = 100, threshold: float = 0.05):
        self.window_size = window_size
        self.threshold = threshold
        
        # Store patient-specific data streams
        self.patient_data = {}
        
        # Drift detection methods
        self.detection_methods = {
            'statistical': self._statistical_test,
            'distribution': self._distribution_change,
            'clustering': self._cluster_change,
            'custom': self._custom_pattern_detection
        }
        
        # User categories and their patterns
        self.user_categories = {
            'typical': {
                'heart_rate_mean': (60, 100),
                'heart_rate_std': (5, 20),
                'activity_level': (0.3, 0.6),
                'variability': 'moderate'
            },
            'athletic': {
                'heart_rate_mean': (40, 60),
                'heart_rate_std': (2, 10),
                'activity_level': (0.7, 1.0),
                'variability': 'low'
            },
            'diver': {
                'heart_rate_mean': (50, 70),
                'heart_rate_std': (10, 30),
                'activity_level': (0.4, 0.8),
                'variability': 'high'
            }
        }
        
        # Initialize detection history
        self.detection_history = {}
        
        logger.info("DriftDetector initialized")
    
    def detect_drift(self, features: List[float], prediction: int, 
                    patient_id: str, method: str = 'auto') -> Dict[str, Any]:
        """
        Detect concept drift for a patient
        
        Args:
            features: Current feature vector
            prediction: Model prediction
            patient_id: Patient identifier
            method: Detection method to use
            
        Returns:
            Drift detection results
        """
        try:
            # Initialize patient data if not exists
            if patient_id not in self.patient_data:
                self._initialize_patient(patient_id)
            
            # Update patient data stream
            self._update_patient_data(patient_id, features, prediction)
            
            # Check if enough data for detection
            if len(self.patient_data[patient_id]['features']) < self.window_size:
                return {
                    'drift_detected': False,
                    'confidence': 0.0,
                    'reason': 'Insufficient data',
                    'data_points': len(self.patient_data[patient_id]['features'])
                }
            
            # Select detection method
            if method == 'auto':
                detection_results = []
                for method_name, detector in self.detection_methods.items():
                    result = detector(patient_id)
                    detection_results.append(result)
                
                # Combine results
                final_result = self._combine_detection_results(detection_results)
            else:
                if method in self.detection_methods:
                    final_result = self.detection_methods[method](patient_id)
                else:
                    final_result = self._statistical_test(patient_id)
            
            # Update detection history
            self._update_detection_history(patient_id, final_result)
            
            # Determine drift type if detected
            if final_result['drift_detected']:
                drift_type = self._determine_drift_type(patient_id)
                final_result['drift_type'] = drift_type
                
                logger.info(
                    f"Drift detected for patient {patient_id}: "
                    f"{drift_type} (confidence: {final_result['confidence']:.3f})"
                )
            else:
                final_result['drift_type'] = 'none'
            
            return final_result
            
        except Exception as e:
            logger.error(f"Drift detection failed for patient {patient_id}: {e}")
            return {
                'drift_detected': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _initialize_patient(self, patient_id: str):
        """Initialize data structures for a new patient"""
        self.patient_data[patient_id] = {
            'features': [],
            'predictions': [],
            'timestamps': [],
            'statistics': {
                'mean': None,
                'std': None,
                'distribution': None
            },
            'current_category': 'typical',
            'category_history': []
        }
        
        self.detection_history[patient_id] = []
        
        logger.info(f"Initialized drift detection for patient {patient_id}")
    
    def _update_patient_data(self, patient_id: str, features: List[float], 
                            prediction: int):
        """Update patient data stream with new observation"""
        patient = self.patient_data[patient_id]
        
        patient['features'].append(features)
        patient['predictions'].append(prediction)
        patient['timestamps'].append(datetime.now())
        
        # Keep only recent data
        if len(patient['features']) > self.window_size * 2:
            patient['features'] = patient['features'][-self.window_size:]
            patient['predictions'] = patient['predictions'][-self.window_size:]
            patient['timestamps'] = patient['timestamps'][-self.window_size:]
    
    def _statistical_test(self, patient_id: str) -> Dict[str, Any]:
        """Statistical test for concept drift"""
        patient = self.patient_data[patient_id]
        features = np.array(patient['features'])
        
        if len(features) < self.window_size * 2:
            return {'drift_detected': False, 'confidence': 0.0}
        
        # Split into reference and recent windows
        reference = features[:self.window_size]
        recent = features[-self.window_size:]
        
        # Perform statistical tests on each feature
        p_values = []
        
        for i in range(features.shape[1]):
            # Kolmogorov-Smirnov test for distribution change
            if len(np.unique(recent[:, i])) > 1 and len(np.unique(reference[:, i])) > 1:
                ks_stat, ks_p = stats.ks_2samp(reference[:, i], recent[:, i])
                p_values.append(ks_p)
            
            # T-test for mean change (for normally distributed features)
            t_stat, t_p = stats.ttest_ind(reference[:, i], recent[:, i], 
                                         equal_var=False, nan_policy='omit')
            if not np.isnan(t_p):
                p_values.append(t_p)
        
        if not p_values:
            return {'drift_detected': False, 'confidence': 0.0}
        
        # Combine p-values using Fisher's method
        chi_squared = -2 * np.sum(np.log(p_values))
        combined_p = stats.chi2.sf(chi_squared, 2 * len(p_values))
        
        drift_detected = combined_p < self.threshold
        confidence = 1 - combined_p
        
        return {
            'drift_detected': drift_detected,
            'confidence': confidence,
            'method': 'statistical',
            'p_value': combined_p,
            'tested_features': len(p_values)
        }
    
    def _distribution_change(self, patient_id: str) -> Dict[str, Any]:
        """Detect distribution changes using KL divergence"""
        patient = self.patient_data[patient_id]
        features = np.array(patient['features'])
        
        if len(features) < self.window_size * 2:
            return {'drift_detected': False, 'confidence': 0.0}
        
        # Split into reference and recent windows
        reference = features[:self.window_size]
        recent = features[-self.window_size:]
        
        # Calculate KL divergence for each feature
        kl_divergences = []
        
        for i in range(features.shape[1]):
            # Create histograms
            ref_hist, bin_edges = np.histogram(reference[:, i], bins=10, density=True)
            rec_hist, _ = np.histogram(recent[:, i], bins=bin_edges, density=True)
            
            # Add small epsilon to avoid zero probabilities
            ref_hist = ref_hist + 1e-10
            rec_hist = rec_hist + 1e-10
            
            # Normalize
            ref_hist = ref_hist / np.sum(ref_hist)
            rec_hist = rec_hist / np.sum(rec_hist)
            
            # Calculate KL divergence
            kl_div = np.sum(ref_hist * np.log(ref_hist / rec_hist))
            kl_divergences.append(kl_div)
        
        avg_kl = np.mean(kl_divergences)
        
        # Determine drift based on threshold
        drift_detected = avg_kl > 0.5  # Threshold for KL divergence
        confidence = min(avg_kl / 2.0, 1.0)  # Normalize to [0, 1]
        
        return {
            'drift_detected': drift_detected,
            'confidence': confidence,
            'method': 'distribution',
            'avg_kl_divergence': avg_kl,
            'features_analyzed': len(kl_divergences)
        }
    
    def _cluster_change(self, patient_id: str) -> Dict[str, Any]:
        """Detect changes in clustering patterns"""
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        
        patient = self.patient_data[patient_id]
        features = np.array(patient['features'])
        
        if len(features) < 50:  # Need sufficient data for clustering
            return {'drift_detected': False, 'confidence': 0.0}
        
        # Cluster recent data
        kmeans = KMeans(n_clusters=3, random_state=42)
        recent_labels = kmeans.fit_predict(features[-self.window_size:])
        
        # Calculate clustering metrics
        silhouette = silhouette_score(features[-self.window_size:], recent_labels)
        
        # Compare with historical clustering if available
        if 'cluster_centers' in patient['statistics']:
            old_centers = patient['statistics']['cluster_centers']
            new_centers = kmeans.cluster_centers_
            
            # Calculate center movement
            center_distances = []
            for i in range(min(len(old_centers), len(new_centers))):
                dist = np.linalg.norm(old_centers[i] - new_centers[i])
                center_distances.append(dist)
            
            avg_movement = np.mean(center_distances)
            drift_detected = avg_movement > 1.0  # Threshold
            confidence = min(avg_movement / 2.0, 1.0)
        else:
            # First time clustering
            drift_detected = False
            confidence = 0.0
            avg_movement = 0.0
        
        # Update stored cluster centers
        patient['statistics']['cluster_centers'] = kmeans.cluster_centers_
        
        return {
            'drift_detected': drift_detected,
            'confidence': confidence,
            'method': 'clustering',
            'silhouette_score': silhouette,
            'center_movement': avg_movement
        }
    
    def _custom_pattern_detection(self, patient_id: str) -> Dict[str, Any]:
        """Custom pattern detection for specific user categories"""
        patient = self.patient_data[patient_id]
        features = np.array(patient['features'])
        
        if len(features) < 10:
            return {'drift_detected': False, 'confidence': 0.0}
        
        # Extract physiological patterns
        recent_features = features[-self.window_size:]
        
        # Calculate pattern metrics
        pattern_metrics = self._extract_pattern_metrics(recent_features)
        
        # Compare with current category
        current_category = patient['current_category']
        category_patterns = self.user_categories.get(current_category, {})
        
        # Calculate deviation from expected patterns
        deviations = []
        
        for metric, value in pattern_metrics.items():
            if metric in category_patterns and isinstance(category_patterns[metric], tuple):
                expected_min, expected_max = category_patterns[metric]
                if value < expected_min:
                    deviation = (expected_min - value) / expected_min
                elif value > expected_max:
                    deviation = (value - expected_max) / expected_max
                else:
                    deviation = 0
                deviations.append(deviation)
        
        avg_deviation = np.mean(deviations) if deviations else 0
        drift_detected = avg_deviation > 0.3  # 30% deviation threshold
        confidence = min(avg_deviation, 1.0)
        
        return {
            'drift_detected': drift_detected,
            'confidence': confidence,
            'method': 'custom_pattern',
            'avg_deviation': avg_deviation,
            'current_category': current_category
        }
    
    def _extract_pattern_metrics(self, features: np.ndarray) -> Dict[str, float]:
        """Extract pattern metrics from feature data"""
        # Assuming features include: age, sex, cp, trestbps, chol, fbs, restecg,
        # thalach, exang, oldpeak, slope, ca, thal
        
        metrics = {}
        
        if len(features) > 0:
            # Heart rate patterns (feature index 7 - thalach)
            if features.shape[1] > 7:
                heart_rates = features[:, 7]
                metrics['heart_rate_mean'] = np.mean(heart_rates)
                metrics['heart_rate_std'] = np.std(heart_rates)
                metrics['heart_rate_var'] = np.var(heart_rates)
            
            # Blood pressure patterns (feature index 3 - trestbps)
            if features.shape[1] > 3:
                bp = features[:, 3]
                metrics['bp_mean'] = np.mean(bp)
                metrics['bp_variability'] = np.std(bp) / np.mean(bp) if np.mean(bp) > 0 else 0
            
            # Cholesterol patterns (feature index 4 - chol)
            if features.shape[1] > 4:
                chol = features[:, 4]
                metrics['chol_mean'] = np.mean(chol)
            
            # Activity patterns (feature index 8 - exang)
            if features.shape[1] > 8:
                activity = features[:, 8]
                metrics['activity_level'] = np.mean(activity)
                metrics['activity_var'] = np.var(activity)
        
        return metrics
    
    def _combine_detection_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine results from multiple detection methods"""
        if not results:
            return {'drift_detected': False, 'confidence': 0.0}
        
        # Weighted voting
        drift_votes = 0
        total_confidence = 0
        total_weight = 0
        
        for result in results:
            if result['drift_detected']:
                drift_votes += 1
            confidence = result.get('confidence', 0.0)
            total_confidence += confidence
            total_weight += 1
        
        # Determine final decision
        drift_ratio = drift_votes / total_weight
        avg_confidence = total_confidence / total_weight if total_weight > 0 else 0
        
        # Threshold for consensus
        drift_detected = drift_ratio > 0.5 and avg_confidence > 0.6
        
        return {
            'drift_detected': drift_detected,
            'confidence': avg_confidence,
            'consensus_ratio': drift_ratio,
            'methods_used': len(results),
            'method': 'ensemble'
        }
    
    def _determine_drift_type(self, patient_id: str) -> str:
        """Determine the type of drift based on patterns"""
        patient = self.patient_data[patient_id]
        features = np.array(patient['features'][-self.window_size:])
        
        # Extract recent patterns
        patterns = self._extract_pattern_metrics(features)
        
        # Compare with each category
        best_match = 'typical'
        best_score = 0
        
        for category, category_patterns in self.user_categories.items():
            score = 0
            matches = 0
            
            for pattern_key, pattern_value in patterns.items():
                if pattern_key in category_patterns:
                    if isinstance(category_patterns[pattern_key], tuple):
                        min_val, max_val = category_patterns[pattern_key]
                        if min_val <= pattern_value <= max_val:
                            score += 1
                    matches += 1
            
            if matches > 0:
                category_score = score / matches
                if category_score > best_score:
                    best_score = category_score
                    best_match = category
        
        # Only update if significantly different from current
        current_category = patient['current_category']
        if best_match != current_category and best_score > 0.7:
            patient['current_category'] = best_match
            patient['category_history'].append({
                'category': best_match,
                'timestamp': datetime.now().isoformat(),
                'confidence': best_score
            })
        
        return best_match
    
    def _update_detection_history(self, patient_id: str, result: Dict[str, Any]):
        """Update detection history for a patient"""
        if patient_id not in self.detection_history:
            self.detection_history[patient_id] = []
        
        history_entry = {
            **result,
            'timestamp': datetime.now().isoformat()
        }
        
        self.detection_history[patient_id].append(history_entry)
        
        # Keep only recent history
        if len(self.detection_history[patient_id]) > 100:
            self.detection_history[patient_id] = self.detection_history[patient_id][-100:]
    
    def get_drift_history(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get drift detection history for a patient"""
        return self.detection_history.get(patient_id, [])
    
    def get_patient_category(self, patient_id: str) -> Dict[str, Any]:
        """Get current category and history for a patient"""
        if patient_id not in self.patient_data:
            return {'category': 'unknown', 'history': []}
        
        patient = self.patient_data[patient_id]
        
        return {
            'current_category': patient['current_category'],
            'category_history': patient['category_history'],
            'data_points': len(patient['features']),
            'last_updated': patient['timestamps'][-1].isoformat() 
                if patient['timestamps'] else None
        }
    
    def is_ready(self) -> bool:
        """Check if detector is ready"""
        return len(self.detection_methods) > 0