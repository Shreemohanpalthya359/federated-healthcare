# 🫀 Federated HeartCare: Hospital-Grade Privacy-Preserving AI

### Advanced Heart Disease Prediction System with Federated Learning & Real-Time Monitoring

---

## 📌 Project Overview

**Federated HeartCare** is a state-of-the-art healthcare platform designed to predict cardiovascular risks with hospital-grade accuracy while ensuring absolute patient privacy. By leveraging **Federated Learning**, the system trains models across decentralized data sources without ever transferring sensitive patient records to a central server.

This system is engineered for **precision medicine**, offering specialized predictive models for different physiological profiles (e.g., **Swimmers, Runners, Cyclists, Divers**) rather than a "one-size-fits-all" approach. It features real-time vital sign monitoring and instant risk assessment with granular probability analysis.

---

## 🎯 Key Capabilities

### 1. 🏥 Hospital-Standard Prediction Accuracy
- **Precision Scaling**: Utilizes clinically validated data scaling (StandardScaler/Z-score) for continuous vitals (BP, Cholesterol, Heart Rate) while preserving critical categorical signals (Chest Pain Type, Thalassemia).
- **Granular Risk Probability**: Provides detailed risk percentages (e.g., 12%, 39%, 99%) rather than binary outputs, enabling nuanced clinical decision-making.
- **Comprehensive Input Factors**: Analyzes 13 key clinical indicators including ST Slope, Fluoroscopy (CA), and Thalassemia.

### 2. 🧠 Specialized Model Architecture
- **Adaptive Model Selection**: Automatically selects the most appropriate model based on the user's lifestyle profile:
  - **Athletic Models**: Optimized for high-intensity cardio profiles (Runners, Cyclists, Weightlifters).
  - **Diver Models**: Tuned for bradycardic (low heart rate) profiles typical of swimmers and divers.
  - **Typical Models**: Calibrated for the general population.
- **Federated Aggregation**: Updates global models by aggregating encrypted weights from local hospital nodes, ensuring data sovereignty.

### 3. 💓 Single-Patient Live Monitoring
- **Real-Time Telemetry**: Continuous tracking of ECG, Heart Rate, SpO2, and Blood Pressure via WebSocket.
- **Focused Care**: Restricted to single-patient tracking to ensure dedicated resource allocation and prevent data cross-contamination in critical care settings.
- **Drift Detection**: Monitors for physiological concept drift (e.g., a patient transitioning from sedentary to active) and alerts for model retraining.

### 4. 🛡️ Privacy & Security
- **Local Inference**: All predictions occur locally or on secure edge nodes.
- **Encrypted Communication**: End-to-end encryption for all telemetry and model updates.
- **Role-Based Access**: Strict separation between Guest, Patient, and Doctor views.

---

## 🏗️ Project Structure

The project follows a modern microservices-ready architecture separating the React frontend from the Flask AI backend.

```
Federated-HeartCare/
├── backend/                        # Python/Flask AI Server
│   ├── app.py                      # Main Application Entry Point
│   ├── fit_scaler.py               # Hospital-Grade Scaler Generation
│   ├── data/                       # Data Management Layer
│   │   ├── raw/                    # Raw Clinical Datasets (Heart Disease UCI)
│   │   ├── processed/              # Normalized & Cleaned Data
│   │   └── preprocessing.py        # Data Transformation Pipelines
│   ├── models/                     # AI Model Registry
│   │   ├── federated/              # Specialized Models (Athletic, Diver, Typical)
│   │   ├── centralized/            # Baseline Models
│   │   └── scaler.pkl              # Production Data Scaler
│   ├── services/                   # Business Logic
│   │   ├── prediction_service.py   # Core Inference Engine (w/ Granular Logic)
│   │   ├── model_swapper.py        # Dynamic Model Switching
│   │   └── evaluation_service.py   # Accuracy Metrics
│   ├── federated/                  # Federated Learning Core
│   │   ├── server.py               # Aggregation Server
│   │   ├── client.py               # Local Training Node
│   │   └── aggregation.py          # FedAvg Implementation
│   ├── drift/                      # Concept Drift Detection
│   │   └── detector.py             # Statistical Drift Analyzers
│   ├── routes/                     # API Endpoints
│   │   ├── predict.py              # Prediction API
│   │   └── monitor_routes.py       # WebSocket Telemetry
│   └── utils/                      # Shared Utilities
│       └── scaler.py               # Custom Scaling Logic
│
├── frontend/                       # React.js Patient Interface
│   ├── src/
│   │   ├── components/
│   │   │   ├── LiveMonitor.jsx     # Real-Time Single-Patient Monitor
│   │   │   ├── Layout/             # UI Shell (Header, Sidebar)
│   │   │   └── Features/           # Reusable UI Components
│   │   ├── pages/
│   │   │   ├── Predict.jsx         # Clinical Prediction Form (13 Factors)
│   │   │   ├── Landing.jsx         # Home Page
│   │   │   └── Login/Signup.jsx    # Auth Pages
│   │   ├── api/                    # Axios API Client
│   │   └── context/                # Global State (Auth, Theme)
│   └── public/                     # Static Assets
└── README.md                       # Project Documentation
```

---

## 🚀 How It Works (Methodology)

1.  **Data Preprocessing**: Raw clinical data is processed to handle missing values and normalize continuous variables (Age, BP, Cholesterol) using Z-score scaling, while preserving categorical semantics (Sex, CP).
2.  **Federated Training**: Local models train on specialized datasets (e.g., "Athletic" data subset). Their weights are sent to the aggregation server.
3.  **Global Aggregation**: The server averages weights using **FedAvg** to create a robust global model without seeing raw data.
4.  **Inference**:
    *   User inputs 13 clinical factors in the frontend.
    *   System selects the best model (e.g., "Swimmer" -> Diver Model).
    *   Input is scaled using the production `scaler.pkl`.
    *   Model predicts risk probability (0-100%).
5.  **Monitoring**: Live WebSocket connection streams vital signs. If metrics deviate significantly (Drift), the system flags for re-evaluation.

---

## 🛠️ Setup & Installation

### Backend (Python)
```bash
cd backend
pip install -r requirements.txt
python fit_scaler.py               # Generate production scaler
python models/train.py --mode centralized # Generate baseline models
python models/train.py --mode federated   # Generate federated models
python app.py                      # Start API Server
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev            # Start UI
```

---

## 👨‍⚕️ Clinical Disclaimer
*This tool is intended for assistive diagnostic support. All high-risk predictions (e.g., >70%) should be immediately verified by a cardiologist using standard angiographic protocols.*
