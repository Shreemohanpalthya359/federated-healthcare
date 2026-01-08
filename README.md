# 🫀 Federated HeartCare

### Privacy-Preserving Heart Disease Prediction using Federated Learning & Concept Drift Adaptation

---

## 📌 Project Overview

**Federated HeartCare** is a full-stack AI-based healthcare system designed to predict heart disease while preserving patient privacy. Instead of collecting sensitive patient data in a centralized server, the system uses **federated learning** principles and **adaptive model selection** to perform predictions securely and efficiently.

The system also incorporates **concept drift awareness**, enabling it to adapt when a user’s physiological behavior changes over time (e.g., transitioning from a typical lifestyle to athletic training or diving activities).

---

## 🎯 Key Features

* 🔐 Privacy-preserving heart disease prediction
* 🌐 Full-stack web application (React + Flask)
* 🧠 Federated learning (simulated) with multiple client models
* 🔄 Concept drift detection and adaptive model switching
* 📊 Real-time prediction with risk probability
* 🧩 Modular and scalable architecture

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React.js)                       │
│  • Dashboard    • Live Monitor   • Predict   • Models       │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS / WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                    Backend (Flask / Python)                  │
│  • REST API     • WebSocket Server • Model Serving          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                Federated Learning Layer                      │
│  • Local Training  • Secure Aggregation • Global Model      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────┬───────────┴──────────┬──────────────┐
│ Hospital A   │ Hospital B            │ Hospital C   │
│ (Local Data) │ (Local Data)          │ (Local Data) │
└──────────────┴───────────────────────┴──────────────┘
```

---

## 🏗️ Complete Project Structure

```
Federated-HeartCare/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── config.json
│   ├── requirements.txt
│   ├── README.md
│   │
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   ├── clean_data.py
│   │   └── analyze_data.py
│   │
│   ├── models/
│   │   ├── centralized/
│   │   └── federated/
│   │       ├── typical.pkl
│   │       ├── athletic.pkl
│   │       └── diver.pkl
│   │
│   ├── federated/
│   │   ├── client.py
│   │   ├── server.py
│   │   └── aggregation.py
│   │
│   ├── drift/
│   │   ├── detector.py
│   │   └── monitor.py
│   │
│   ├── services/
│   │   ├── prediction_service.py
│   │   ├── model_swapper.py
│   │   └── evaluation_service.py
│   │
│   ├── routes/
│   │   ├── predict.py
│   │   └── health.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   ├── scaler.py
│   │   └── helpers.py
│   │
│   ├── tests/
│   └── logs/
│
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   ├── README.md
│   │
│   ├── src/
│   │   ├── api/
│   │   │   └── predictApi.js
│   │   ├── pages/
│   │   │   ├── Landing.jsx
│   │   │   └── Predict.jsx
│   │   ├── components/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│
└── .gitignore
```

---

## 🧠 Backend Architecture (Flask + ML)

### Responsibilities

* Handles REST API requests
* Loads trained ML models
* Performs heart disease prediction
* Simulates federated learning
* Detects concept drift and swaps models dynamically

### Important Modules

| Module       | Description                                   |
| ------------ | --------------------------------------------- |
| `federated/` | Simulated federated learning and FedAvg logic |
| `drift/`     | Concept drift detection and monitoring        |
| `services/`  | Business logic and model management           |
| `routes/`    | API endpoints                                 |
| `models/`    | Trained machine learning models               |
| `data/`      | Dataset preprocessing and analysis            |

---

## 🌐 Frontend Architecture (React + Tailwind CSS)

### Responsibilities

* Collects user health parameters
* Allows user-type selection (Typical / Athletic / Diver)
* Sends prediction requests to backend
* Displays prediction result and risk probability

### User Flow

```
User Input → React Form → Axios API Call → Flask Backend → Prediction Result → UI Display
```

---

## ⚙️ API Endpoints

### Prediction Endpoint

```
POST /api/predict
```

This endpoint accepts **clinically meaningful inputs from the UI** and internally maps them to **numeric values required by the machine learning model**.

---

### 🔁 UI-to-Model Feature Mapping

The frontend sends human-readable medical values, which are converted before prediction:

| Feature             | UI Value                                     | Model Value |
| ------------------- | -------------------------------------------- | ----------- |
| Sex                 | Male / Female                                | 1 / 0       |
| Chest Pain Type     | Typical, Atypical, Non-anginal, Asymptomatic | 0, 1, 2, 3  |
| Fasting Blood Sugar | ≤ 120 mg/dl / > 120 mg/dl                    | 0 / 1       |
| Resting ECG         | Normal / ST-T Abnormality / LVH              | 0 / 1 / 2   |
| Exercise Angina     | No / Yes                                     | 0 / 1       |
| ST Segment Slope    | Upsloping / Flat / Downsloping               | 0 / 1 / 2   |
| Thalassemia         | Normal / Fixed / Reversible                  | 1 / 2 / 3   |

---

### Sample Request (Frontend Payload)

```json
{
  "age": 45,
  "sex": "Male",
  "cp": "Atypical Angina",
  "trestbps": 130,
  "chol": 240,
  "fbs": "≤ 120 mg/dl",
  "restecg": "ST-T Abnormality",
  "thalach": 150,
  "exang": "No",
  "oldpeak": 1.5,
  "slope": "Upsloping",
  "ca": 0,
  "thal": "Normal",
  "user_type": "Typical"
}
```

---

### Sample Response

```json
{
  "prediction": 1,
  "risk_probability": 0.87
}
```

```
GET /api/health
```

### Prediction Endpoint

```
POST /api/predict
```

**Sample Request**

```json
{
  "age": 45,
  "sex": 1,
  "cp": 2,
  "trestbps": 120,
  "chol": 240,
  "thalach": 150,
  "user_type": "Athletic"
}
```

**Sample Response**

```json
{
  "prediction": 1,
  "risk_probability": 0.87
}
```

---

## 🔐 Privacy & Federated Learning

* Raw patient data is never stored centrally
* Models are trained locally (simulated clients)
* Federated Averaging is used for aggregation
* Enhances data security and privacy compliance

---

## 🔄 Concept Drift Adaptation

* Monitors changes in physiological patterns
* Detects significant deviations from baseline
* Dynamically switches to specialized ML models
* Maintains prediction accuracy over time

---

## ▶️ How to Run the Project

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Sample Output

* ⚠️ Heart Disease Detected
* 📊 Risk Probability: 100%
* Real-time prediction from federated models

---

## 🎓 Use Cases

* Smart healthcare monitoring
* Remote patient diagnosis
* Privacy-sensitive medical AI systems
* Academic and research projects

---

## 🏁 Conclusion

**Federated HeartCare** demonstrates how modern AI systems can be secure, adaptive, and privacy-preserving. By combining federated learning, concept drift handling, and full-stack development, this project provides a robust solution for real-world healthcare applications.

---

## 📌 Author

**Shree Mohan Chandra**
Computer Science Engineering (AI & ML)
