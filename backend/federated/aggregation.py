"""
Advanced aggregation strategies for federated learning
"""
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Tuple
from scipy import stats
import copy

from utils.logger import get_logger

logger = get_logger(__name__)

class AggregationStrategies:
    """Collection of aggregation strategies for federated learning"""
    
    @staticmethod
    def fedavg(client_weights: List[Dict[str, Any]], 
               client_samples: List[int]) -> Dict[str, Any]:
        """Federated Averaging"""
        total_samples = sum(client_samples)
        avg_weights = {}
        
        for i, weights in enumerate(client_weights):
            weight_factor = client_samples[i] / total_samples
            
            for key, value in weights.items():
                if key not in avg_weights:
                    avg_weights[key] = torch.zeros_like(value)
                avg_weights[key] += value * weight_factor
        
        return avg_weights
    
    @staticmethod
    def fedprox(client_weights: List[Dict[str, Any]], 
                client_samples: List[int],
                global_weights: Dict[str, Any],
                mu: float = 0.01) -> Dict[str, Any]:
        """FedProx aggregation with proximal term"""
        total_samples = sum(client_samples)
        avg_weights = {}
        
        for i, weights in enumerate(client_weights):
            weight_factor = client_samples[i] / total_samples
            
            for key, value in weights.items():
                if key not in avg_weights:
                    avg_weights[key] = torch.zeros_like(value)
                
                # Add proximal term
                proximal_term = mu * (value - global_weights[key])
                avg_weights[key] += (value - proximal_term) * weight_factor
        
        return avg_weights
    
    @staticmethod
    def fednova(client_weights: List[Dict[str, Any]],
                client_gradients: List[Dict[str, Any]],
                client_steps: List[int]) -> Dict[str, Any]:
        """FedNova aggregation for heterogeneous clients"""
        # Normalize by local steps
        normalized_weights = []
        
        for i, (weights, gradients, steps) in enumerate(
            zip(client_weights, client_gradients, client_steps)
        ):
            norm_weights = {}
            for key in weights.keys():
                # Normalize by gradient magnitude and steps
                if key in gradients:
                    grad_norm = torch.norm(gradients[key])
                    if grad_norm > 0:
                        norm_factor = steps / grad_norm
                        norm_weights[key] = weights[key] * norm_factor
                    else:
                        norm_weights[key] = weights[key]
                else:
                    norm_weights[key] = weights[key]
            normalized_weights.append(norm_weights)
        
        # Simple average of normalized weights
        avg_weights = {}
        for weights in normalized_weights:
            for key, value in weights.items():
                if key not in avg_weights:
                    avg_weights[key] = torch.zeros_like(value)
                avg_weights[key] += value
        
        for key in avg_weights:
            avg_weights[key] /= len(normalized_weights)
        
        return avg_weights
    
    @staticmethod
    def krum(client_weights: List[Dict[str, Any]], 
             byzantine_tolerance: int = 1) -> Dict[str, Any]:
        """Krum aggregation for Byzantine resilience"""
        n = len(client_weights)
        f = byzantine_tolerance
        
        if n <= 2 * f + 1:
            logger.warning("Not enough clients for Krum, using average")
            return AggregationStrategies.simple_average(client_weights)
        
        # Calculate distances between all client updates
        distances = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                dist = AggregationStrategies._weight_distance(
                    client_weights[i], 
                    client_weights[j]
                )
                distances[i, j] = dist
                distances[j, i] = dist
        
        # Find the update with minimal sum of distances to nearest n-f-2 updates
        scores = []
        for i in range(n):
            # Sort distances and take closest n-f-2
            sorted_dists = np.sort(distances[i])
            score = np.sum(sorted_dists[:n-f-2])
            scores.append(score)
        
        # Select the update with minimum score
        selected_idx = np.argmin(scores)
        
        logger.info(f"Krum selected client {selected_idx} from {n} clients")
        
        return client_weights[selected_idx]
    
    @staticmethod
    def trimmed_mean(client_weights: List[Dict[str, Any]], 
                     trim_ratio: float = 0.1) -> Dict[str, Any]:
        """Trimmed Mean aggregation for robustness"""
        n = len(client_weights)
        k = int(trim_ratio * n)
        
        if n <= 2 * k:
            logger.warning("Not enough clients for Trimmed Mean, using median")
            return AggregationStrategies.coordinatewise_median(client_weights)
        
        avg_weights = {}
        
        # For each parameter
        for key in client_weights[0].keys():
            values = [weights[key] for weights in client_weights]
            stacked = torch.stack(values)
            
            # Trim extreme values and average
            sorted_values, _ = torch.sort(stacked, dim=0)
            trimmed = sorted_values[k:n-k, :]
            avg_weights[key] = torch.mean(trimmed, dim=0)
        
        return avg_weights
    
    @staticmethod
    def coordinatewise_median(client_weights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Coordinate-wise Median aggregation"""
        avg_weights = {}
        
        for key in client_weights[0].keys():
            values = [weights[key] for weights in client_weights]
            stacked = torch.stack(values)
            avg_weights[key] = torch.median(stacked, dim=0).values
        
        return avg_weights
    
    @staticmethod
    def adaptive_aggregation(client_weights: List[Dict[str, Any]],
                            client_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Adaptive aggregation based on client metrics"""
        # Calculate adaptive weights based on metrics
        weights = []
        
        for metrics in client_metrics:
            # Combine multiple metrics
            accuracy = metrics.get('accuracy', 0.5)
            loss = metrics.get('loss', 1.0)
            samples = metrics.get('samples_used', 1)
            
            # Adaptive weight calculation
            weight = accuracy * np.log(samples) / (loss + 1e-8)
            weights.append(weight)
        
        # Normalize weights
        weights = np.array(weights)
        if np.sum(weights) > 0:
            weights = weights / np.sum(weights)
        else:
            weights = np.ones(len(weights)) / len(weights)
        
        # Weighted average
        avg_weights = {}
        for i, client_weight in enumerate(client_weights):
            for key, value in client_weight.items():
                if key not in avg_weights:
                    avg_weights[key] = torch.zeros_like(value)
                avg_weights[key] += value * weights[i]
        
        return avg_weights
    
    @staticmethod
    def _weight_distance(weights1: Dict[str, Any], 
                        weights2: Dict[str, Any]) -> float:
        """Calculate Euclidean distance between weight dictionaries"""
        distance = 0
        for key in weights1.keys():
            diff = weights1[key] - weights2[key]
            distance += torch.sum(diff ** 2).item()
        return np.sqrt(distance)
    
    @staticmethod
    def simple_average(client_weights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple average of client weights"""
        avg_weights = {}
        
        for weights in client_weights:
            for key, value in weights.items():
                if key not in avg_weights:
                    avg_weights[key] = torch.zeros_like(value)
                avg_weights[key] += value
        
        for key in avg_weights:
            avg_weights[key] /= len(client_weights)
        
        return avg_weights