import pandas as pd
import joblib
import os
import argparse

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# ----------------------------------
# Paths
# ----------------------------------
PROCESSED_DATA_DIR = "data/processed"
CENTRALIZED_MODEL_DIR = "models/centralized"
FEDERATED_MODEL_DIR = "models/federated"

os.makedirs(CENTRALIZED_MODEL_DIR, exist_ok=True)
os.makedirs(FEDERATED_MODEL_DIR, exist_ok=True)

# ----------------------------------
# Utility: Train & Save Model
# ----------------------------------
def train_and_save_model(data, model_path):
    # Drop user_type only if it exists
    drop_cols = ["target"]
    if "user_type" in data.columns:
        drop_cols.append("user_type")
        
    X = data.drop(columns=drop_cols)
    y = data["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print(f"\n📊 Model evaluation for {model_path}")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    joblib.dump(model, model_path)
    print(f"💾 Model saved at: {model_path}")

# ----------------------------------
# Centralized Training
# ----------------------------------
def train_centralized():
    print("\n🔹 Training Centralized Model...")

    typical = pd.read_csv(f"{PROCESSED_DATA_DIR}/typical.csv")
    athletic = pd.read_csv(f"{PROCESSED_DATA_DIR}/athletic.csv")
    diver = pd.read_csv(f"{PROCESSED_DATA_DIR}/diver.csv")

    combined_data = pd.concat([typical, athletic, diver], ignore_index=True)

    model_path = f"{CENTRALIZED_MODEL_DIR}/baseline.pkl"
    train_and_save_model(combined_data, model_path)

# ----------------------------------
# Federated Training (Simulated)
# ----------------------------------
def train_federated():
    print("\n🔹 Training Federated Models (Simulated)...")

    datasets = {
        "typical": "typical.csv",
        "athletic": "athletic.csv",
        "diver": "diver.csv"
    }

    for user_type, file_name in datasets.items():
        print(f"\n🤖 Training federated model for {user_type.capitalize()} users")

        data = pd.read_csv(f"{PROCESSED_DATA_DIR}/{file_name}")
        model_path = f"{FEDERATED_MODEL_DIR}/{user_type}.pkl"

        train_and_save_model(data, model_path)

# ----------------------------------
# Main
# ----------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["centralized", "federated"],
        required=True,
        help="Training mode"
    )
    args = parser.parse_args()

    if args.mode == "centralized":
        train_centralized()
    elif args.mode == "federated":
        train_federated()
