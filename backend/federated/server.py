"""
Federated Learning Server for aggregating client updates
"""
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Tuple
from datetime import datetime
import json
import os
from collections import defaultdict

from utils.logger import get_logger

logger = get_logger(__name__)

class FederatedServer:
    """Server for federated learning aggregation"""
    
    def __init__(self, model_dir: str = 'models/federated/'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Server state
        self.global_model = self._create_global_model()
        self.client_updates = {}
        self.training_round = 0
        
        # Server configuration
        self.config = {
            'min_clients': 3,
            'max_clients': 10,
            'aggregation_method': 'fedavg',
            'rounds_before_eval': 5,
            'save_model_frequency': 10
        }
        
        # Training history
        self.training_history = {
            'rounds': [],
            'accuracies': [],
            'client_participation': [],
            'timestamps': []
        }
        
        # Initialize with saved model if exists
        self._load_saved_model()
        
        logger.info("Federated server initialized")
    
    def _create_global_model(self) -> nn.Module:
        """Create global model architecture"""
        model = nn.Sequential(
            nn.Linear(13, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 2),
            nn.Softmax(dim=1)
        )
        return model
    
    def _load_saved_model(self):
        """Load saved global model"""
        model_path = os.path.join(self.model_dir, 'global_model.pth')
        try:
            if os.path.exists(model_path):
                self.global_model.load_state_dict(torch.load(model_path))
                logger.info("Loaded saved global model")
                
                # Load training history
                history_path = os.path.join(self.model_dir, 'training_history.json')
                if os.path.exists(history_path):
                    with open(history_path, 'r') as f:
                        self.training_history = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load saved model: {e}")
    
    def register_client_update(self, client_id: str, 
                              model_weights: Dict[str, Any],
                              metrics: Dict[str, Any]):
        """Register client model update"""
        try:
            self.client_updates[client_id] = {
                'weights': model_weights,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat(),
                'samples': metrics.get('samples_used', 0)
            }
            
            logger.info(f"Registered update from client {client_id}")
            
            # Check if we have enough clients for aggregation
            if len(self.client_updates) >= self.config['min_clients']:
                return self.aggregate_updates()
            else:
                return {
                    'status': 'waiting',
                    'clients_received': len(self.client_updates),
                    'clients_needed': self.config['min_clients']
                }
                
        except Exception as e:
            logger.error(f"Failed to register client update: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def aggregate_updates(self) -> Dict[str, Any]:
        """Aggregate client updates using FedAvg or other methods"""
        if len(self.client_updates) < self.config['min_clients']:
            return {
                'status': 'insufficient_clients',
                'message': f"Need at least {self.config['min_clients']} clients"
            }
        
        try:
            self.training_round += 1
            
            # Select aggregation method
            if self.config['aggregation_method'] == 'fedavg':
                new_weights = self._fedavg_aggregation()
            elif self.config['aggregation_method'] == 'weighted_avg':
                new_weights = self._weighted_average_aggregation()
            else:
                new_weights = self._fedavg_aggregation()
            
            # Update global model
            self.global_model.load_state_dict(new_weights)
            
            # Calculate metrics
            aggregation_metrics = self._calculate_aggregation_metrics()
            
            # Save model periodically
            if self.training_round % self.config['save_model_frequency'] == 0:
                self._save_model()
            
            # Clear client updates for next round
            previous_updates = self.client_updates.copy()
            self.client_updates.clear()
            
            logger.info(f"Aggregation complete for round {self.training_round}")
            
            return {
                'status': 'success',
                'round': self.training_round,
                'clients_participated': len(previous_updates),
                'aggregation_method': self.config['aggregation_method'],
                'metrics': aggregation_metrics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _fedavg_aggregation(self) -> Dict[str, Any]:
        """Federated Averaging aggregation"""
        # Initialize averaged weights
        avg_weights = {}
        
        # Get total samples
        total_samples = sum(
            update['samples'] for update in self.client_updates.values()
        )
        
        # Average each parameter
        for client_id, update in self.client_updates.items():
            client_weights = update['weights']
            client_weight = update['samples'] / total_samples
            
            for key, value in client_weights.items():
                if key not in avg_weights:
                    avg_weights[key] = torch.zeros_like(value)
                avg_weights[key] += value * client_weight
        
        return avg_weights
    
    def _weighted_average_aggregation(self) -> Dict[str, Any]:
        """Weighted average based on client performance"""
        # Calculate weights based on client accuracy
        client_accuracies = {}
        total_accuracy = 0
        
        for client_id, update in self.client_updates.items():
            accuracy = update['metrics'].get('accuracy', [0])[-1]
            client_accuracies[client_id] = accuracy
            total_accuracy += accuracy
        
        # If all accuracies are 0, use equal weights
        if total_accuracy == 0:
            weight_per_client = 1.0 / len(self.client_updates)
            client_weights = {
                client_id: weight_per_client 
                for client_id in self.client_updates.keys()
            }
        else:
            client_weights = {
                client_id: accuracy / total_accuracy
                for client_id, accuracy in client_accuracies.items()
            }
        
        # Perform weighted aggregation
        avg_weights = {}
        for client_id, update in self.client_updates.items():
            client_model_weights = update['weights']
            weight = client_weights[client_id]
            
            for key, value in client_model_weights.items():
                if key not in avg_weights:
                    avg_weights[key] = torch.zeros_like(value)
                avg_weights[key] += value * weight
        
        return avg_weights
    
    def _calculate_aggregation_metrics(self) -> Dict[str, Any]:
        """Calculate metrics for the aggregation round"""
        if not self.client_updates:
            return {}
        
        metrics = {
            'round': self.training_round,
            'client_count': len(self.client_updates),
            'total_samples': sum(
                update['samples'] for update in self.client_updates.values()
            ),
            'avg_accuracy': np.mean([
                update['metrics'].get('accuracy', [0])[-1]
                for update in self.client_updates.values()
            ]),
            'avg_loss': np.mean([
                update['metrics'].get('loss', [0])[-1]
                for update in self.client_updates.values()
            ]),
            'client_ids': list(self.client_updates.keys())
        }
        
        # Update training history
        self.training_history['rounds'].append(self.training_round)
        self.training_history['accuracies'].append(metrics['avg_accuracy'])
        self.training_history['client_participation'].append(metrics['client_count'])
        self.training_history['timestamps'].append(datetime.now().isoformat())
        
        return metrics
    
    def _save_model(self):
        """Save global model and training history"""
        try:
            # Save model weights
            model_path = os.path.join(self.model_dir, 'global_model.pth')
            torch.save(self.global_model.state_dict(), model_path)
            
            # Save training history
            history_path = os.path.join(self.model_dir, 'training_history.json')
            with open(history_path, 'w') as f:
                json.dump(self.training_history, f, indent=2, default=str)
            
            logger.info(f"Saved model and history for round {self.training_round}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def get_global_model(self) -> Tuple[nn.Module, Dict[str, Any]]:
        """Get current global model and metadata"""
        metadata = {
            'training_round': self.training_round,
            'total_rounds': len(self.training_history['rounds']),
            'latest_accuracy': self.training_history['accuracies'][-1] 
                if self.training_history['accuracies'] else 0,
            'model_architecture': str(self.global_model),
            'timestamp': datetime.now().isoformat()
        }
        
        return self.global_model, metadata
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status and statistics"""
        return {
            'status': 'active',
            'training_round': self.training_round,
            'clients_registered': len(self.client_updates),
            'min_clients_required': self.config['min_clients'],
            'aggregation_method': self.config['aggregation_method'],
            'training_history': {
                'total_rounds': len(self.training_history['rounds']),
                'average_accuracy': np.mean(self.training_history['accuracies']) 
                    if self.training_history['accuracies'] else 0,
                'average_participation': np.mean(self.training_history['client_participation'])
                    if self.training_history['client_participation'] else 0
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def evaluate_global_model(self, test_data: Tuple[np.ndarray, np.ndarray]) -> Dict[str, Any]:
        """Evaluate global model on test data"""
        try:
            self.global_model.eval()
            
            X_test, y_test = test_data
            X_tensor = torch.FloatTensor(X_test)
            y_tensor = torch.LongTensor(y_test)
            
            with torch.no_grad():
                outputs = self.global_model(X_tensor)
                _, predicted = torch.max(outputs.data, 1)
                accuracy = (predicted == y_tensor).sum().item() / y_tensor.size(0)
            
            evaluation_results = {
                'round': self.training_round,
                'accuracy': accuracy,
                'samples': len(X_test),
                'predictions': predicted.numpy().tolist(),
                'labels': y_tensor.numpy().tolist(),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Global model evaluation: accuracy={accuracy:.4f}")
            
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Global model evaluation failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }