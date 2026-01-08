#!/usr/bin/env python3
"""
Fixed setup script that handles string columns properly
"""
import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("="*60)
print("FIXED Federated HeartCare Setup")
print("="*60)

# First, clean the CSV files
print("\n1. Cleaning CSV files...")
categories = ['athletic', 'diver', 'typical']

for category in categories:
    csv_path = f'data/processed/{category}.csv'
    
    if not os.path.exists(csv_path):
        print(f"  ✗ File not found: {csv_path}")
        continue
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"\n  {category.upper()} dataset:")
    print(f"    Original columns: {list(df.columns)}")
    print(f"    Original shape: {df.shape}")
    
    # Remove string columns (like 'user_type')
    string_cols = df.select_dtypes(include=['object']).columns
    if len(string_cols) > 0:
        print(f"    Removing string columns: {list(string_cols)}")
        df = df.drop(columns=string_cols)
    
    # Check for target column
    if 'target' not in df.columns:
        print(f"    ✗ No 'target' column found!")
        continue
    
    # Save cleaned version
    df.to_csv(csv_path, index=False)
    print(f"    Cleaned shape: {df.shape}")
    print(f"    Cleaned columns: {list(df.columns)}")

print("\n2. Training specialized models...")
for category in categories:
    csv_path = f'data/processed/{category}.csv'
    
    if not os.path.exists(csv_path):
        continue
    
    try:
        df = pd.read_csv(csv_path)
        
        if 'target' not in df.columns:
            print(f"  ✗ {category}: No 'target' column")
            continue
        
        X = df.drop('target', axis=1).values
        y = df['target'].values
        
        print(f"\n  Training {category} model:")
        print(f"    Samples: {len(X)}")
        print(f"    Features: {X.shape[1]}")
        print(f"    Heart disease rate: {y.mean()*100:.1f}%")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"    Test accuracy: {accuracy:.4f}")
        
        # Save model
        os.makedirs('models/federated', exist_ok=True)
        model_path = f'models/federated/{category}.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"    ✓ Saved: {model_path}")
        
        # Also save in specialized directory
        os.makedirs('models/specialized', exist_ok=True)
        specialized_path = f'models/specialized/{category}_model.pkl'
        with open(specialized_path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"    ✓ Also saved: {specialized_path}")
        
    except Exception as e:
        print(f"  ✗ Error training {category}: {e}")

print("\n3. Training centralized model...")
try:
    # Combine all data
    all_dfs = []
    for category in categories:
        csv_path = f'data/processed/{category}.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if 'target' in df.columns:
                all_dfs.append(df)
    
    if not all_dfs:
        print("  ✗ No data available for centralized model")
    else:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        X = combined_df.drop('target', axis=1).values
        y = combined_df['target'].values
        
        print(f"\n  Centralized model:")
        print(f"    Total samples: {len(X)}")
        print(f"    Features: {X.shape[1]}")
        print(f"    Heart disease rate: {y.mean()*100:.1f}%")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"    Test accuracy: {accuracy:.4f}")
        
        # Save centralized model
        os.makedirs('models/centralized', exist_ok=True)
        centralized_path = 'models/centralized/heart_disease_model.pkl'
        with open(centralized_path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"    ✓ Saved: {centralized_path}")
        
        # Save as federated base model
        federated_path = 'models/federated/heart_disease_federated.pkl'
        with open(federated_path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"    ✓ Also saved: {federated_path}")

except Exception as e:
    print(f"  ✗ Error training centralized model: {e}")

print("\n" + "="*60)
print("✅ SETUP COMPLETE!")
print("="*60)

# List created files
print("\n📁 Created files:")
model_files = [
    'models/centralized/heart_disease_model.pkl',
    'models/federated/heart_disease_federated.pkl',
    'models/federated/athletic.pkl',
    'models/federated/diver.pkl',
    'models/federated/typical.pkl',
    'models/specialized/athletic_model.pkl',
    'models/specialized/diver_model.pkl',
    'models/specialized/typical_model.pkl'
]

for file_path in model_files:
    if os.path.exists(file_path):
        print(f"  ✓ {file_path}")
    else:
        print(f"  ✗ {file_path} (not created)")

print("\n🚀 Next steps:")
print("  1. Install dependencies: pip3 install flask flask-cors numpy pandas scikit-learn joblib")
print("  2. Start server: python3 app.py")
print("  3. Test API: curl http://localhost:5000/api/v1/health")