"""
Federated Learning Client for distributed training
"""
import numpy as np
import pickle
import json
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from utils.logger import get_logger

logger = get_logger(__name__)

class FederatedClient:
    """Client for federated learning"""
    
    def __init__(self, client_id: str, data_dir: str = 'data/processed/'):
        self.client_id = client_id
        self.data_dir = data_dir
        
        # Client state
        self.model = None
        self.local_data = None
        self.model_metadata = {}
        
        # Training configuration
        self.config = {
            'learning_rate': 0.01,
            'batch_size': 32,
            'epochs': 10,
            'local_iterations': 5
        }
        
        # Privacy parameters
        self.privacy_params = {
            'differential_privacy': True,
            'epsilon': 1.0,
            'delta': 1e-5,
            'clip_norm': 1.0
        }
        
        # Initialize client
        self._initialize_client()
        
        logger.info(f"Federated client {client_id} initialized")
    
    def _initialize_client(self):
        """Initialize client with local data"""
        # Load client-specific data
        data_path = os.path.join(self.data_dir, f'client_{self.client_id}.pkl')
        try:
            if os.path.exists(data_path):
                with open(data_path, 'rb') as f:
                    self.local_data = pickle.load(f)
                logger.info(f"Client {self.client_id} loaded local data")
            else:
                logger.warning(f"No local data found for client {self.client_id}")
        except Exception as e:
            logger.error(f"Failed to load client data: {e}")
    
    def load_global_model(self, model_weights: Dict[str, Any], 
                         model_metadata: Dict[str, Any]):
        """Load global model from server"""
        try:
            self.model = self._create_model()
            self.model.load_state_dict(model_weights)
            self.model_metadata = model_metadata
            
            logger.info(f"Client {self.client_id} loaded global model")
            return True
        except Exception as e:
            logger.error(f"Failed to load global model: {e}")
            return False
    
    def _create_model(self) -> nn.Module:
        """Create a neural network model for heart disease prediction"""
        model = nn.Sequential(
            nn.Linear(13, 64),  # 13 features
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 2),  # 2 classes: heart disease or not
            nn.Softmax(dim=1)
        )
        return model
    
    def train_local_model(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Train model on local data
        
        Returns:
            Tuple of (updated_weights, training_metrics)
        """
        if self.model is None or self.local_data is None:
            logger.error(f"Client {self.client_id}: No model or data available")
            return None, None
        
        try:
            # Prepare data
            X_train, y_train = self._prepare_training_data()
            
            # Convert to PyTorch tensors
            X_tensor = torch.FloatTensor(X_train)
            y_tensor = torch.LongTensor(y_train)
            
            # Create data loader
            dataset = TensorDataset(X_tensor, y_tensor)
            dataloader = DataLoader(
                dataset, 
                batch_size=self.config['batch_size'],
                shuffle=True
            )
            
            # Set up training
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(
                self.model.parameters(), 
                lr=self.config['learning_rate']
            )
            
            # Training loop
            self.model.train()
            training_metrics = {
                'loss': [],
                'accuracy': [],
                'client_id': self.client_id,
                'samples_used': len(X_train)
            }
            
            for epoch in range(self.config['local_iterations']):
                epoch_loss = 0.0
                correct = 0
                total = 0
                
                for batch_X, batch_y in dataloader:
                    optimizer.zero_grad()
                    
                    # Forward pass
                    outputs = self.model(batch_X)
                    loss = criterion(outputs, batch_y)
                    
                    # Backward pass with differential privacy
                    loss.backward()
                    
                    # Apply gradient clipping for privacy
                    if self.privacy_params['differential_privacy']:
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(), 
                            self.privacy_params['clip_norm']
                        )
                    
                    optimizer.step()
                    
                    # Calculate metrics
                    epoch_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    total += batch_y.size(0)
                    correct += (predicted == batch_y).sum().item()
                
                # Record epoch metrics
                epoch_accuracy = correct / total
                training_metrics['loss'].append(epoch_loss / len(dataloader))
                training_metrics['accuracy'].append(epoch_accuracy)
                
                logger.debug(
                    f"Client {self.client_id} - Epoch {epoch+1}: "
                    f"Loss: {epoch_loss/len(dataloader):.4f}, "
                    f"Accuracy: {epoch_accuracy:.4f}"
                )
            
            # Get updated weights
            updated_weights = self.model.state_dict()
            
            # Add noise for differential privacy
            if self.privacy_params['differential_privacy']:
                updated_weights = self._add_dp_noise(updated_weights)
            
            logger.info(
                f"Client {self.client_id} completed local training: "
                f"Final accuracy: {training_metrics['accuracy'][-1]:.4f}"
            )
            
            return updated_weights, training_metrics
            
        except Exception as e:
            logger.error(f"Client {self.client_id} training failed: {e}")
            return None, None
    
    def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from local dataset"""
        if isinstance(self.local_data, dict):
            X = np.array(self.local_data['features'])
            y = np.array(self.local_data['labels'])
        elif isinstance(self.local_data, tuple):
            X, y = self.local_data
        else:
            raise ValueError("Invalid local data format")
        
        return X, y
    
    def _add_dp_noise(self, weights: Dict[str, Any]) -> Dict[str, Any]:
        """Add differential privacy noise to weights"""
        noisy_weights = {}
        sensitivity = self.privacy_params['clip_norm'] / len(self.local_data[0])
        scale = sensitivity / self.privacy_params['epsilon']
        
        for key, value in weights.items():
            # Add Gaussian noise
            noise = torch.randn_like(value) * scale
            noisy_weights[key] = value + noise
        
        return noisy_weights
    
    def evaluate_local_model(self, test_data: Tuple[np.ndarray, np.ndarray] = None):
        """Evaluate model on local or provided test data"""
        if self.model is None:
            return None
        
        try:
            self.model.eval()
            
            # Use provided test data or local data
            if test_data is None:
                X_test, y_test = self._prepare_training_data()
            else:
                X_test, y_test = test_data
            
            # Convert to tensors
            X_tensor = torch.FloatTensor(X_test)
            y_tensor = torch.LongTensor(y_test)
            
            # Create dataset
            test_dataset = TensorDataset(X_tensor, y_tensor)
            test_loader = DataLoader(test_dataset, batch_size=32)
            
            # Evaluation
            correct = 0
            total = 0
            all_predictions = []
            all_labels = []
            
            with torch.no_grad():
                for batch_X, batch_y in test_loader:
                    outputs = self.model(batch_X)
                    _, predicted = torch.max(outputs.data, 1)
                    
                    total += batch_y.size(0)
                    correct += (predicted == batch_y).sum().item()
                    
                    all_predictions.extend(predicted.numpy())
                    all_labels.extend(batch_y.numpy())
            
            accuracy = correct / total
            
            evaluation_results = {
                'client_id': self.client_id,
                'accuracy': accuracy,
                'total_samples': total,
                'correct_predictions': correct,
                'predictions': all_predictions,
                'labels': all_labels,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Client {self.client_id} evaluation: accuracy={accuracy:.4f}")
            
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Client {self.client_id} evaluation failed: {e}")
            return None
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get client information and statistics"""
        data_info = {
            'client_id': self.client_id,
            'has_data': self.local_data is not None,
            'privacy_enabled': self.privacy_params['differential_privacy'],
            'epsilon': self.privacy_params['epsilon'],
            'config': self.config
        }
        
        if self.local_data is not None:
            if isinstance(self.local_data, tuple):
                data_info['samples'] = len(self.local_data[0])
                data_info['features'] = self.local_data[0].shape[1]
            elif isinstance(self.local_data, dict):
                data_info['samples'] = len(self.local_data['features'])
                data_info['features'] = len(self.local_data['features'][0])
        
        return data_info