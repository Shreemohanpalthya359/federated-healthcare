"""
Logging configuration for Federated HeartCare
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logger(name: str, log_file: str = 'logs/federated_heartcare.log', 
                level: int = logging.INFO) -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        log_file.replace('.log', '_error.log'),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class PerformanceLogger:
    """Logger for performance monitoring"""
    
    def __init__(self, log_dir: str = 'logs/performance/'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize loggers for different components
        self.predictions_logger = self._setup_performance_logger('predictions')
        self.training_logger = self._setup_performance_logger('training')
        self.drift_logger = self._setup_performance_logger('drift')
        
    def _setup_performance_logger(self, log_type: str) -> logging.Logger:
        """Setup performance-specific logger"""
        log_file = os.path.join(self.log_dir, f'{log_type}.log')
        logger = logging.getLogger(f'performance.{log_type}')
        
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            handler = RotatingFileHandler(
                log_file,
                maxBytes=5*1024*1024,
                backupCount=3
            )
            
            formatter = logging.Formatter(
                '%(asctime)s,%(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            logger.addHandler(handler)
            logger.propagate = False
        
        return logger
    
    def log_prediction(self, patient_id: str, model_type: str, 
                      prediction: int, confidence: float, 
                      processing_time: float):
        """Log prediction performance"""
        log_message = f"{patient_id},{model_type},{prediction},{confidence:.4f},{processing_time:.6f}"
        self.predictions_logger.info(log_message)
    
    def log_training(self, client_id: str, round_num: int, 
                    accuracy: float, loss: float, 
                    samples_used: int):
        """Log training performance"""
        log_message = f"{client_id},{round_num},{accuracy:.4f},{loss:.4f},{samples_used}"
        self.training_logger.info(log_message)
    
    def log_drift(self, patient_id: str, drift_type: str, 
                 confidence: float, previous_model: str, 
                 new_model: str):
        """Log drift detection and model swap"""
        log_message = f"{patient_id},{drift_type},{confidence:.4f},{previous_model},{new_model}"
        self.drift_logger.info(log_message)

def log_execution_time(func):
    """Decorator to log function execution time"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"Function {func.__name__} executed in {execution_time:.4f} seconds"
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"Function {func.__name__} failed after {execution_time:.4f} seconds: {e}"
            )
            raise
    
    return wrapper

# Initialize default logger
default_logger = setup_logger('federated_heartcare')