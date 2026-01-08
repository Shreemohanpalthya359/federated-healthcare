"""
Evaluation service for model performance monitoring
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import json
import os

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix
)

from utils.logger import get_logger

logger = get_logger(__name__)

class EvaluationService:
    """Service for evaluating model performance and monitoring"""
    
    def __init__(self, eval_dir: str = 'evaluation/'):
        self.eval_dir = eval_dir
        os.makedirs(eval_dir, exist_ok=True)
        
        # Performance history
        self.performance_history = {}
        
        # Thresholds for alerts
        self.alert_thresholds = {
            'accuracy': 0.75,
            'precision': 0.70,
            'recall': 0.70,
            'f1_score': 0.70,
            'auc_roc': 0.75
        }
        
        # Initialize with default metrics
        self._initialize_metrics()
        
        logger.info("EvaluationService initialized")
    
    def _initialize_metrics(self):
        """Initialize performance metrics storage"""
        self.performance_history = {
            'daily': {},
            'weekly': {},
            'monthly': {},
            'by_model': {},
            'by_patient_group': {}
        }
    
    def evaluate_model(self, y_true: List[int], y_pred: List[int], 
                      y_prob: List[float] = None, 
                      metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate model performance
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_prob: Predicted probabilities (optional)
            metadata: Additional metadata about evaluation
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            # Convert to numpy arrays
            y_true = np.array(y_true)
            y_pred = np.array(y_pred)
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
                'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
                'f1_score': f1_score(y_true, y_pred, average='weighted', zero_division=0),
                'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
            }
            
            # Calculate AUC-ROC if probabilities are provided
            if y_prob is not None and len(np.unique(y_true)) > 1:
                metrics['auc_roc'] = roc_auc_score(y_true, y_prob)
            
            # Add metadata
            if metadata:
                metrics['metadata'] = metadata
            
            # Add timestamp
            metrics['timestamp'] = datetime.now().isoformat()
            
            # Check for alerts
            alerts = self._check_for_alerts(metrics)
            if alerts:
                metrics['alerts'] = alerts
                self._trigger_alerts(alerts, metadata)
            
            # Store metrics
            self._store_metrics(metrics, metadata)
            
            logger.info(f"Model evaluation completed: accuracy={metrics['accuracy']:.3f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _check_for_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if any metrics fall below thresholds"""
        alerts = []
        
        for metric_name, threshold in self.alert_thresholds.items():
            if metric_name in metrics and metrics[metric_name] < threshold:
                alerts.append({
                    'type': 'performance_alert',
                    'metric': metric_name,
                    'value': metrics[metric_name],
                    'threshold': threshold,
                    'severity': 'high' if metrics[metric_name] < threshold * 0.8 else 'medium'
                })
        
        return alerts
    
    def _trigger_alerts(self, alerts: List[Dict[str, Any]], 
                       metadata: Dict[str, Any] = None):
        """Trigger alerts for performance issues"""
        for alert in alerts:
            logger.warning(
                f"Performance alert: {alert['metric']} = {alert['value']:.3f} "
                f"(threshold: {alert['threshold']})"
            )
            
            # In production, this would send notifications
            # For now, just log and store
            
            alert_record = {
                **alert,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            self._store_alert(alert_record)
    
    def _store_metrics(self, metrics: Dict[str, Any], 
                      metadata: Dict[str, Any] = None):
        """Store evaluation metrics"""
        try:
            timestamp = datetime.now()
            date_key = timestamp.strftime('%Y-%m-%d')
            week_key = timestamp.strftime('%Y-W%W')
            month_key = timestamp.strftime('%Y-%m')
            
            # Store daily metrics
            if date_key not in self.performance_history['daily']:
                self.performance_history['daily'][date_key] = []
            self.performance_history['daily'][date_key].append(metrics)
            
            # Store weekly metrics
            if week_key not in self.performance_history['weekly']:
                self.performance_history['weekly'][week_key] = []
            self.performance_history['weekly'][week_key].append(metrics)
            
            # Store by model type if metadata available
            if metadata and 'model_type' in metadata:
                model_type = metadata['model_type']
                if model_type not in self.performance_history['by_model']:
                    self.performance_history['by_model'][model_type] = []
                self.performance_history['by_model'][model_type].append(metrics)
            
            # Save to file periodically
            if len(self.performance_history['daily'][date_key]) % 100 == 0:
                self._save_metrics_to_file()
                
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    def _store_alert(self, alert: Dict[str, Any]):
        """Store alert record"""
        try:
            alert_file = os.path.join(self.eval_dir, 'alerts.json')
            alerts = []
            
            if os.path.exists(alert_file):
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
            
            alerts.append(alert)
            
            # Keep only last 1000 alerts
            if len(alerts) > 1000:
                alerts = alerts[-1000:]
            
            with open(alert_file, 'w') as f:
                json.dump(alerts, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
    
    def _save_metrics_to_file(self):
        """Save metrics to file"""
        try:
            metrics_file = os.path.join(self.eval_dir, 'metrics_history.json')
            with open(metrics_file, 'w') as f:
                json.dump(self.performance_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save metrics to file: {e}")
    
    def get_performance_summary(self, period: str = 'daily', 
                               model_type: str = None) -> Dict[str, Any]:
        """
        Get performance summary for a period
        
        Args:
            period: 'daily', 'weekly', 'monthly', or 'all'
            model_type: Filter by model type
            
        Returns:
            Performance summary
        """
        try:
            if period == 'all':
                data = self._aggregate_all_metrics()
            else:
                data = self.performance_history.get(period, {})
            
            # Filter by model type if specified
            if model_type:
                filtered_data = {}
                for key, metrics_list in data.items():
                    filtered_metrics = [
                        m for m in metrics_list 
                        if m.get('metadata', {}).get('model_type') == model_type
                    ]
                    if filtered_metrics:
                        filtered_data[key] = filtered_metrics
                data = filtered_data
            
            # Calculate summary statistics
            summary = self._calculate_summary_statistics(data)
            
            return {
                'period': period,
                'model_type': model_type,
                'summary': summary,
                'data_points': sum(len(metrics) for metrics in data.values()),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _aggregate_all_metrics(self) -> Dict[str, List]:
        """Aggregate all metrics across periods"""
        all_metrics = {}
        
        for period in ['daily', 'weekly', 'monthly', 'by_model', 'by_patient_group']:
            period_data = self.performance_history.get(period, {})
            for key, metrics_list in period_data.items():
                if key not in all_metrics:
                    all_metrics[key] = []
                all_metrics[key].extend(metrics_list)
        
        return all_metrics
    
    def _calculate_summary_statistics(self, data: Dict[str, List]) -> Dict[str, Any]:
        """Calculate summary statistics from metrics data"""
        all_metrics = []
        for metrics_list in data.values():
            all_metrics.extend(metrics_list)
        
        if not all_metrics:
            return {}
        
        summary = {
            'total_evaluations': len(all_metrics),
            'average_accuracy': np.mean([m.get('accuracy', 0) for m in all_metrics]),
            'average_precision': np.mean([m.get('precision', 0) for m in all_metrics]),
            'average_recall': np.mean([m.get('recall', 0) for m in all_metrics]),
            'average_f1_score': np.mean([m.get('f1_score', 0) for m in all_metrics]),
            'min_accuracy': np.min([m.get('accuracy', 0) for m in all_metrics]),
            'max_accuracy': np.max([m.get('accuracy', 0) for m in all_metrics]),
            'recent_trend': self._calculate_trend(all_metrics[-100:], 'accuracy')
        }
        
        return summary
    
    def _calculate_trend(self, metrics: List[Dict[str, Any]], 
                        metric_name: str) -> str:
        """Calculate trend for a metric"""
        if len(metrics) < 2:
            return 'stable'
        
        values = [m.get(metric_name, 0) for m in metrics]
        recent_values = values[-10:] if len(values) > 10 else values
        
        if len(recent_values) < 2:
            return 'stable'
        
        # Simple linear trend calculation
        x = np.arange(len(recent_values))
        y = np.array(recent_values)
        
        # Calculate slope
        if np.std(x) == 0:
            return 'stable'
        
        slope = np.cov(x, y)[0, 1] / np.var(x)
        
        if slope > 0.01:
            return 'improving'
        elif slope < -0.01:
            return 'declining'
        else:
            return 'stable'
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        return {
            'performance_history_size': {
                'daily': sum(len(m) for m in self.performance_history['daily'].values()),
                'weekly': sum(len(m) for m in self.performance_history['weekly'].values()),
                'monthly': sum(len(m) for m in self.performance_history['monthly'].values()),
                'by_model': {k: len(v) for k, v in self.performance_history['by_model'].items()}
            },
            'alert_thresholds': self.alert_thresholds,
            'storage_location': self.eval_dir,
            'timestamp': datetime.now().isoformat()
        }