#!/usr/bin/env python3
"""
Quick API test
"""
import requests
import json

def test_api():
    """Test the API endpoints"""
    
    # First, check if server is running
    try:
        print("Testing health endpoint...")
        response = requests.get("http://localhost:5000/api/v1/health", timeout=5)
        print(f"✓ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("✗ Server not running! Start it with: python3 app.py")
        return False
    
    # Test prediction
    print("\nTesting prediction endpoint...")
    
    # Sample features - make sure these match your actual feature count
    # Your CSV has: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target
    # So we need 13 features (excluding target)
    sample_features = [
        63,   # age
        1,    # sex
        3,    # cp
        145,  # trestbps
        233,  # chol
        1,    # fbs
        0,    # restecg
        150,  # thalach
        0,    # exang
        2.3,  # oldpeak
        0,    # slope
        0,    # ca
        1     # thal
    ]
    
    payload = {
        "patient_id": "test_001",
        "model_type": "federated",
        "features": sample_features
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/v1/predict",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"✓ Prediction test: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nPrediction successful!")
            print(f"Prediction: {result['data']['prediction']}")
            print(f"Risk Level: {result['data']['risk_level']}")
            print(f"Model Used: {result['data']['model_used']}")
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Prediction test failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Federated HeartCare API Test")
    print("="*60)
    
    success = test_api()
    
    print("\n" + "="*60)
    if success:
        print("✅ API tests passed!")
    else:
        print("❌ API tests failed")
    print("="*60)