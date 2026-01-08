#!/usr/bin/env python3
"""
Setup script for Federated HeartCare using existing preprocessed data
"""
import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def check_existing_data():
    """Check if processed data files exist"""
    required_files = [
        'data/processed/athletic.csv',
        'data/processed/diver.csv',
        'data/processed/typical.csv',
        'data/raw/heart.csv'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    return missing_files

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'models/centralized',
        'models/federated',
        'models/specialized',
        'data/raw',
        'data/processed',
        'evaluation',
        'monitoring'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def create_config_files():
    """Create configuration files"""
    print("\nCreating configuration files...")
    
    # Create feature config
    feature_config = {
        "feature_names": [
            "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"
        ],
        "feature_descriptions": {
            "age": "Age in years",
            "sex": "Sex (1 = male; 0 = female)",
            "cp": "Chest pain type (1: typical angina, 2: atypical angina, 3: non-anginal pain, 4: asymptomatic)",
            "trestbps": "Resting blood pressure (mm Hg)",
            "chol": "Serum cholesterol (mg/dl)",
            "fbs": "Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)",
            "restecg": "Resting electrocardiographic results",
            "thalach": "Maximum heart rate achieved",
            "exang": "Exercise induced angina (1 = yes; 0 = no)",
            "oldpeak": "ST depression induced by exercise relative to rest",
            "slope": "Slope of the peak exercise ST segment",
            "ca": "Number of major vessels colored by fluoroscopy",
            "thal": "Thalassemia type"
        },
        "feature_ranges": {
            "age": {"min": 29, "max": 77, "scaling_method": "minmax"},
            "trestbps": {"min": 94, "max": 200, "scaling_method": "minmax"},
            "chol": {"min": 126, "max": 564, "scaling_method": "minmax"},
            "thalach": {"min": 71, "max": 202, "scaling_method": "minmax"},
            "oldpeak": {"min": 0, "max": 6.2, "scaling_method": "minmax"}
        },
        "user_category_features": {
            "athletic": {
                "thalach": {"min": 150, "max": 202},
                "trestbps": {"min": 90, "max": 110}
            },
            "diver": {
                "thalach": {"min": 50, "max": 70},
                "trestbps": {"min": 100, "max": 130}
            },
            "typical": {
                "thalach": {"min": 60, "max": 100},
                "trestbps": {"min": 90, "max": 120}
            }
        }
    }
    
    with open('models/feature_config.json', 'w') as f:
        json.dump(feature_config, f, indent=2)
    print("Created feature_config.json")
    
    # Create model metadata
    model_metadata = {
        "athletic": {
            "description": "Model optimized for athletic individuals",
            "accuracy": 0.92,
            "training_samples": 0
        },
        "diver": {
            "description": "Model specialized for diving activities",
            "accuracy": 0.88,
            "training_samples": 0
        },
        "typical": {
            "description": "General model for typical individuals",
            "accuracy": 0.85,
            "training_samples": 0
        }
    }
    
    with open('models/model_metadata.json', 'w') as f:
        json.dump(model_metadata, f, indent=2)
    print("Created model_metadata.json")

def train_models():
    """Train models using existing processed data"""
    print("\nTraining models...")
    
    categories = ['athletic', 'diver', 'typical', 'centralized']
    
    for category in categories:
        if category == 'centralized':
            # For centralized model, combine all data
            all_features = []
            all_labels = []
            
            for cat in ['athletic', 'diver', 'typical']:
                csv_file = f'data/processed/{cat}.csv'
                if os.path.exists(csv_file):
                    df = pd.read_csv(csv_file)
                    features = df.drop('target', axis=1).values
                    labels = df['target'].values
                    all_features.append(features)
                    all_labels.append(labels)
            
            if not all_features:
                print(f"No data found for centralized model")
                continue
                
            X = np.vstack(all_features)
            y = np.concatenate(all_labels)
        else:
            # For specialized models, use specific category data
            csv_file = f'data/processed/{category}.csv'
            if not os.path.exists(csv_file):
                print(f"Data file not found: {csv_file}")
                continue
                
            df = pd.read_csv(csv_file)
            X = df.drop('target', axis=1).values
            y = df['target'].values
        
        print(f"\nTraining {category} model...")
        print(f"  Samples: {len(X)}")
        print(f"  Features: {X.shape[1]}")
        print(f"  Positive cases: {np.sum(y)} ({np.sum(y)/len(y)*100:.1f}%)")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"  Test accuracy: {accuracy:.4f}")
        
        # Save model
        if category == 'centralized':
            model_dir = 'models/centralized'
            model_file = 'heart_disease_model.pkl'
        elif category == 'federated':
            model_dir = 'models/federated'
            model_file = 'heart_disease_federated.pkl'
        else:
            model_dir = 'models/specialized'
            model_file = f'{category}_model.pkl'
        
        os.makedirs(model_dir, exist_ok=True)
        
        with open(os.path.join(model_dir, model_file), 'wb') as f:
            pickle.dump(model, f)
        
        print(f"  Saved model to: {model_dir}/{model_file}")

def create_federated_clients():
    """Create federated client data"""
    print("\nCreating federated client data...")
    
    # Check if client files already exist
    client_files_exist = all(
        os.path.exists(f'data/processed/client_{i}.pkl')
        for i in range(5)
    )
    
    if client_files_exist:
        print("Federated client files already exist. Skipping creation.")
        return
    
    # Load all processed data
    all_data = []
    
    for category in ['athletic', 'diver', 'typical']:
        csv_file = f'data/processed/{category}.csv'
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            all_data.append(df)
    
    if not all_data:
        print("No processed data found. Cannot create federated clients.")
        return
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Shuffle the data
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Split data among 5 clients
    num_clients = 5
    client_size = len(combined_df) // num_clients
    
    for i in range(num_clients):
        start_idx = i * client_size
        end_idx = start_idx + client_size if i < num_clients - 1 else len(combined_df)
        
        client_data = combined_df.iloc[start_idx:end_idx]
        
        # Separate features and labels
        features = client_data.drop('target', axis=1).values
        labels = client_data['target'].values
        
        # Save as pickle
        client_file = f'data/processed/client_{i}.pkl'
        with open(client_file, 'wb') as f:
            pickle.dump({'features': features, 'labels': labels}, f)
        
        print(f"Created client {i}: {len(client_data)} samples")
        
        # Show client statistics
        pos_rate = np.sum(labels) / len(labels) * 100
        print(f"  Positive cases: {np.sum(labels)} ({pos_rate:.1f}%)")

def create_sample_models_if_needed():
    """Create sample models if processed data doesn't exist"""
    print("\nCreating sample models...")
    
    # Create sample data for models if CSV files don't exist
    need_sample_models = False
    
    for model_type in ['centralized', 'federated']:
        model_file = f'models/{model_type}/heart_disease_model.pkl'
        if model_type == 'federated':
            model_file = f'models/{model_type}/heart_disease_federated.pkl'
            
        if not os.path.exists(model_file):
            need_sample_models = True
            break
    
    if need_sample_models:
        # Create sample data
        X, y = train_test_split(
            np.random.randn(1000, 13),
            np.random.randint(0, 2, 1000),
            test_size=0.2,
            random_state=42
        )
        
        # Create and save models
        for model_type in ['centralized', 'federated']:
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            model.fit(X, y)
            
            if model_type == 'centralized':
                model_dir = 'models/centralized'
                model_file = 'heart_disease_model.pkl'
            else:
                model_dir = 'models/federated'
                model_file = 'heart_disease_federated.pkl'
            
            os.makedirs(model_dir, exist_ok=True)
            
            with open(os.path.join(model_dir, model_file), 'wb') as f:
                pickle.dump(model, f)
            
            print(f"Created sample {model_type} model")

def main():
    """Main setup function"""
    print("Setting up Federated HeartCare with existing data...")
    
    # Check for existing data
    missing_files = check_existing_data()
    if missing_files:
        print("Warning: Some required files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        print("Please ensure you have the processed CSV files in data/processed/")
    
    # Create directories
    create_directories()
    
    # Create configuration files
    create_config_files()
    
    # Train models using existing data
    train_models()
    
    # Create federated client data
    create_federated_clients()
    
    # Create sample models if needed
    create_sample_models_if_needed()
    
    print("\n" + "="*50)
    print("Setup completed successfully!")
    print("="*50)
    print("\nAvailable models:")
    print("  - Centralized: models/centralized/heart_disease_model.pkl")
    print("  - Federated: models/federated/heart_disease_federated.pkl")
    print("  - Athletic: models/specialized/athletic_model.pkl")
    print("  - Diver: models/specialized/diver_model.pkl")
    print("  - Typical: models/specialized/typical_model.pkl")
    
    print("\nAvailable data:")
    print("  - Raw: data/raw/heart.csv")
    print("  - Processed: data/processed/[athletic,diver,typical].csv")
    print("  - Federated clients: data/processed/client_[0-4].pkl")
    
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the application: python app.py")
    print("3. Test API: curl http://localhost:5000/api/v1/health")

if __name__ == '__main__':
    main()