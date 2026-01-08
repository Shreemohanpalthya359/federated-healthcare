
import sys
import os
import logging
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.prediction_service import PredictionService

# Configure logging
logging.basicConfig(level=logging.INFO)

def verify_variation():
    print("Initializing PredictionService...")
    service = PredictionService()
    
    # Row 1 (Healthy, Target 0)
    # 63.0,1.0,1.0,145.0,233.0,1.0,2.0,150.0,0.0,2.3,3.0,0.0,6.0
    healthy_features = [63.0, 1.0, 1.0, 145.0, 233.0, 1.0, 2.0, 150.0, 0.0, 2.3, 3.0, 0.0, 6.0]
    
    # Row 3 (Unhealthy, Target 1)
    # 67.0,1.0,4.0,120.0,229.0,0.0,2.0,129.0,1.0,2.6,2.0,2.0,7.0
    unhealthy_features = [67.0, 1.0, 4.0, 120.0, 229.0, 0.0, 2.0, 129.0, 1.0, 2.6, 2.0, 2.0, 7.0]
    
    print("\n--- Testing Healthy Case ---")
    res_h = service.predict(healthy_features, patient_id="healthy", model_type="federated")
    print(f"Risk: {res_h['risk_level']}")
    print(f"Prob: {res_h['probability']:.4f}")
    
    print("\n--- Testing Unhealthy Case ---")
    res_u = service.predict(unhealthy_features, patient_id="unhealthy", model_type="federated")
    print(f"Risk: {res_u['risk_level']}")
    print(f"Prob: {res_u['probability']:.4f}")
    
    # Test athletic model
    print("\n--- Testing Athletic Model (Unhealthy Input) ---")
    res_a = service.predict(unhealthy_features, patient_id="athlete", model_type="athletic")
    print(f"Risk: {res_a['risk_level']}")
    print(f"Prob: {res_a['probability']:.4f}")

    # Test diver model
    print("\n--- Testing Diver Model (Unhealthy Input) ---")
    res_d = service.predict(unhealthy_features, patient_id="diver", model_type="diver")
    print(f"Risk: {res_d['risk_level']}")
    print(f"Prob: {res_d['probability']:.4f}")

if __name__ == "__main__":
    verify_variation()
