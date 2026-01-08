#!/usr/bin/env python3
"""
Simple test to verify models are working
"""
import pickle
import numpy as np
import pandas as pd

def test_model(model_path, test_features):
    """Test a single model"""
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        prediction = model.predict([test_features])
        proba = model.predict_proba([test_features])
        
        print(f"Model: {model_path}")
        print(f"  Prediction: {prediction[0]}")
        print(f"  Probability: {proba[0]}")
        print(f"  Classes: {model.classes_}")
        return True
    except Exception as e:
        print(f"Error loading {model_path}: {e}")
        return False

def main():
    """Test all models"""
    print("Testing trained models...\n")
    
    # Sample test features (13 features as per your data)
    # These are example values - adjust based on your actual feature ranges
    test_features = [
        63,  # age
        1,   # sex (1=male, 0=female)
        3,   # cp (chest pain type)
        145, # trestbps (resting blood pressure)
        233, # chol (cholesterol)
        1,   # fbs (fasting blood sugar)
        0,   # restecg (resting ECG)
        150, # thalach (max heart rate)
        0,   # exang (exercise induced angina)
        2.3, # oldpeak (ST depression)
        0,   # slope
        0,   # ca (number of vessels)
        1    # thal (thalassemia)
    ]
    
    models_to_test = [
        'models/centralized/heart_disease_model.pkl',
        'models/federated/heart_disease_federated.pkl',
        'models/federated/athletic.pkl',
        'models/federated/diver.pkl',
        'models/federated/typical.pkl'
    ]
    
    results = []
    for model_path in models_to_test:
        success = test_model(model_path, test_features)
        results.append((model_path, success))
        print()
    
    print("="*60)
    print("Summary:")
    print("="*60)
    
    for model_path, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {model_path}")

if __name__ == '__main__':
    main()