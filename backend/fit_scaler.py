
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
import joblib
import os

def fit_scaler():
    # Load raw data
    data_path = 'backend/data/raw/heart.csv'
    if not os.path.exists(data_path):
        # Try without backend/ prefix if running from root
        data_path = 'data/raw/heart.csv'
        if not os.path.exists(data_path):
             print(f"Error: {data_path} not found")
             return

    print(f"Loading data from {data_path}...")
    # No headers in raw file, so load with header=None and assign names
    columns = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"
    ]
    df = pd.read_csv(data_path, names=columns)
    
    # Drop target
    X = df.drop('target', axis=1)
    
    # Define ColumnTransformer to scale specific columns and keep order
    # Scaled: age(0), trestbps(3), chol(4), thalach(7), oldpeak(9)
    # Others: passthrough
    
    # Note: ColumnTransformer concatenates results of transformers.
    # To preserve order, we must define them in order.
    
    scaler = ColumnTransformer(
        transformers=[
            ('age', StandardScaler(), [0]),         # 0
            ('sex', 'passthrough', [1]),            # 1
            ('cp', 'passthrough', [2]),             # 2
            ('trestbps', StandardScaler(), [3]),    # 3
            ('chol', StandardScaler(), [4]),        # 4
            ('fbs', 'passthrough', [5]),            # 5
            ('restecg', 'passthrough', [6]),        # 6
            ('thalach', StandardScaler(), [7]),     # 7
            ('exang', 'passthrough', [8]),          # 8
            ('oldpeak', StandardScaler(), [9]),     # 9
            ('slope', 'passthrough', [10]),         # 10
            ('ca', 'passthrough', [11]),            # 11
            ('thal', 'passthrough', [12]),          # 12
        ]
    )
    
    print("Fitting scaler...")
    scaler.fit(X)
    
    # Ensure directory exists
    os.makedirs('backend/models', exist_ok=True)
    
    # Save scaler
    output_path = 'backend/models/scaler.pkl'
    joblib.dump(scaler, output_path)
    print(f"✅ Scaler saved to {output_path}")
    
    # Test transform
    sample = X.iloc[0:1]
    transformed = scaler.transform(sample)
    print("\nVerification:")
    print("Sample raw values (first 5):", sample.values[0][:5])
    print("Sample transformed (first 5):", transformed[0][:5])
    
    # Check if categorical are untouched
    print("Sex (idx 1) raw:", sample.values[0][1], "transformed:", transformed[0][1])
    print("CP (idx 2) raw:", sample.values[0][2], "transformed:", transformed[0][2])

if __name__ == "__main__":
    fit_scaler()
