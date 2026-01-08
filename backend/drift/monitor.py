"""
Continuous monitor for concept drift and model performance
"""
import time
import threading
import schedule
from typing import Dict, List, Any, Callable
from datetime import datetime, timedelta
import json
import os

from utils.logger import get_logger
from drift.detector import DriftDetector
from services.evaluation_service import EvaluationService

logger = get_logger(__name__)

class DriftMonitor:
    """Continuous monitor for concept drift and model health"""
    
    def __init__(self, monitor_interval: int = 300):  # 5 minutes
        self.monitor_interval = monitor_interval
        self.drift_detector = DriftDetector()
        self.evaluation_service = EvaluationService()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.callbacks = []
        
        # Alert thresholds
        self.alert_thresholds = {
            'drift_confidence': 0.7,
            'performance_drop': 0.15,  # 15% drop
            'consecutive_drifts': 3
        }
        
        # Monitoring history
        self.monitoring_history = {
            'drift_events': [],
            'performance_alerts': [],
            'model_swaps': [],
            'system_checks': []
        }
        
        # Initialize monitoring directory
        self.monitor_dir = 'monitoring/'
        os.makedirs(self.monitor_dir, exist_ok=True)
        
        logger.info("DriftMonitor initialized")
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info("Started continuous monitoring")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        logger.info("Stopped continuous monitoring")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Perform monitoring tasks
                self._check_system_health()
                self._analyze_recent_predictions()
                self._check_model_performance()
                self._cleanup_old_data()
                
                # Save monitoring state periodically
                if len(self.monitoring_history['system_checks']) % 10 == 0:
                    self._save_monitoring_state()
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
            
            # Sleep until next interval
            time.sleep(self.monitor_interval)
    
    def _check_system_health(self):
        """Check system health and resources"""
        try:
            import psutil
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_check = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'status': 'healthy' if cpu_percent < 90 and memory.percent < 90 else 'warning'
            }
            
            self.monitoring_history['system_checks'].append(system_check)
            
            # Trigger alert if system health is poor
            if system_check['status'] == 'warning':
                self._trigger_alert({
                    'type': 'system_health',
                    'severity': 'high',
                    'message': 'System resources running low',
                    'details': system_check
                })
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
    
    def _analyze_recent_predictions(self):
        """Analyze recent predictions for drift patterns"""
        try:
            # This would typically analyze prediction logs
            # For now, implement as placeholder
            
            # Get recent drift events from detector
            recent_drifts = []
            for patient_id in self.drift_detector.detection_history:
                history = self.drift_detector.get_drift_history(patient_id)
                if history:
                    recent = history[-1]
                    if recent['drift_detected']:
                        recent_drifts.append({
                            'patient_id': patient_id,
                            'drift_type': recent.get('drift_type', 'unknown'),
                            'confidence': recent.get('confidence', 0),
                            'timestamp': recent.get('timestamp')
                        })
            
            # Analyze drift patterns
            if recent_drifts:
                self._analyze_drift_patterns(recent_drifts)
            
        except Exception as e:
            logger.error(f"Prediction analysis failed: {e}")
    
    def _analyze_drift_patterns(self, drifts: List[Dict[str, Any]]):
        """Analyze patterns in detected drifts"""
        try:
            # Group drifts by type
            drift_by_type = {}
            for drift in drifts:
                drift_type = drift['drift_type']
                if drift_type not in drift_by_type:
                    drift_by_type[drift_type] = []
                drift_by_type[drift_type].append(drift)
            
            # Check for concerning patterns
            alerts = []
            
            for drift_type, type_drifts in drift_by_type.items():
                # Check for frequent drifts
                if len(type_drifts) >= self.alert_thresholds['consecutive_drifts']:
                    alerts.append({
                        'type': 'frequent_drift',
                        'drift_type': drift_type,
                        'count': len(type_drifts),
                        'patients': list(set(d['patient_id'] for d in type_drifts))
                    })
                
                # Check for high confidence drifts
                high_conf_drifts = [
                    d for d in type_drifts 
                    if d['confidence'] > self.alert_thresholds['drift_confidence']
                ]
                if high_conf_drifts:
                    alerts.append({
                        'type': 'high_confidence_drift',
                        'drift_type': drift_type,
                        'count': len(high_conf_drifts),
                        'avg_confidence': sum(d['confidence'] for d in high_conf_drifts) / len(high_conf_drifts)
                    })
            
            # Trigger alerts
            for alert in alerts:
                self._trigger_alert(alert)
                
        except Exception as e:
            logger.error(f"Drift pattern analysis failed: {e}")
    
    def _check_model_performance(self):
        """Check model performance for degradation"""
        try:
            # Get recent performance metrics
            performance_summary = self.evaluation_service.get_performance_summary(
                period='daily'
            )
            
            if performance_summary and 'summary' in performance_summary:
                summary = performance_summary['summary']
                
                # Check for performance degradation
                if 'average_accuracy' in summary:
                    current_accuracy = summary['average_accuracy']
                    
                    # Get historical accuracy for comparison
                    weekly_summary = self.evaluation_service.get_performance_summary(
                        period='weekly'
                    )
                    
                    if weekly_summary and 'summary' in weekly_summary:
                        historical_accuracy = weekly_summary['summary'].get('average_accuracy', current_accuracy)
                        
                        # Check for significant drop
                        accuracy_drop = historical_accuracy - current_accuracy
                        if accuracy_drop > self.alert_thresholds['performance_drop']:
                            self._trigger_alert({
                                'type': 'performance_degradation',
                                'severity': 'high',
                                'current_accuracy': current_accuracy,
                                'historical_accuracy': historical_accuracy,
                                'drop_percentage': accuracy_drop * 100
                            })
            
        except Exception as e:
            logger.error(f"Model performance check failed: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        try:
            cutoff_time = datetime.now() - timedelta(days=30)
            cutoff_str = cutoff_time.isoformat()
            
            # Clean system checks
            self.monitoring_history['system_checks'] = [
                check for check in self.monitoring_history['system_checks']
                if check['timestamp'] > cutoff_str
            ]
            
            # Clean old alert files
            alert_file = os.path.join(self.monitor_dir, 'alerts.json')
            if os.path.exists(alert_file):
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
                
                recent_alerts = [
                    alert for alert in alerts
                    if alert.get('timestamp', '') > cutoff_str
                ]
                
                with open(alert_file, 'w') as f:
                    json.dump(recent_alerts, f, indent=2)
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def _trigger_alert(self, alert_data: Dict[str, Any]):
        """Trigger an alert"""
        try:
            alert_data['timestamp'] = datetime.now().isoformat()
            alert_data['monitor_id'] = id(self)
            
            # Add to monitoring history
            self.monitoring_history['performance_alerts'].append(alert_data)
            
            # Call registered callbacks
            for callback in self.callbacks:
                try:
                    callback(alert_data)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
            
            # Log alert
            logger.warning(f"Alert triggered: {alert_data['type']} - {alert_data.get('message', '')}")
            
            # Save alert to file
            self._save_alert(alert_data)
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
    
    def _save_alert(self, alert: Dict[str, Any]):
        """Save alert to file"""
        try:
            alert_file = os.path.join(self.monitor_dir, 'alerts.json')
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
            logger.error(f"Failed to save alert: {e}")
    
    def _save_monitoring_state(self):
        """Save monitoring state to file"""
        try:
            state_file = os.path.join(self.monitor_dir, 'monitoring_state.json')
            state = {
                'monitoring_history': self.monitoring_history,
                'alert_thresholds': self.alert_thresholds,
                'last_updated': datetime.now().isoformat(),
                'is_monitoring': self.is_monitoring
            }
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save monitoring state: {e}")
    
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback for alerts"""
        self.callbacks.append(callback)
        logger.info(f"Registered alert callback: {callback.__name__}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'is_monitoring': self.is_monitoring,
            'monitor_interval': self.monitor_interval,
            'alert_thresholds': self.alert_thresholds,
            'statistics': {
                'drift_events': len(self.monitoring_history['drift_events']),
                'performance_alerts': len(self.monitoring_history['performance_alerts']),
                'model_swaps': len(self.monitoring_history['model_swaps']),
                'system_checks': len(self.monitoring_history['system_checks'])
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return self.monitoring_history['performance_alerts'][-limit:]