import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, 
  Activity, 
  Zap, 
  AlertTriangle, 
  CheckCircle,
  Shield,
  User,
  Heart
} from 'lucide-react';
import { toast } from 'react-hot-toast';

const Predict = () => {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [activeModel, setActiveModel] = useState('federated');
  const [formData, setFormData] = useState({
    age: 45,
    sex: 1,
    cp: 2,
    trestbps: 130,
    chol: 240,
    fbs: 0,
    restecg: 1,
    thalach: 150,
    exang: 0,
    oldpeak: 1.5,
    slope: 1,
    ca: 0,
    thal: 2
  });

  const models = [
    { type: 'federated', label: 'Federated', icon: <Shield />, color: 'from-cyan-500 to-blue-500' },
    { type: 'athletic', label: 'Athletic', icon: <Zap />, color: 'from-emerald-500 to-green-500' },
    { type: 'diver', label: 'Diver', icon: <Activity />, color: 'from-violet-500 to-purple-500' },
    { type: 'typical', label: 'Typical', icon: <User />, color: 'from-orange-500 to-amber-500' }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: parseFloat(value) || value
    }));
  };

  const handlePredict = async () => {
    setLoading(true);
    setPrediction(null);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Mock prediction result
      const mockPrediction = {
        prediction: Math.random() > 0.5 ? 1 : 0,
        probability: Math.random(),
        risk_level: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'moderate' : 'low',
        model_used: activeModel,
        timestamp: new Date().toISOString()
      };

      setPrediction(mockPrediction);
      toast.success('Prediction completed successfully!');
      
    } catch (error) {
      console.error('Prediction error:', error);
      toast.error('Failed to make prediction');
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevel = (probability) => {
    if (probability < 0.3) return { level: 'Low', color: 'text-green-400', bg: 'bg-green-500/20' };
    if (probability < 0.7) return { level: 'Moderate', color: 'text-yellow-400', bg: 'bg-yellow-500/20' };
    return { level: 'High', color: 'text-red-400', bg: 'bg-red-500/20' };
  };

  const risk = prediction ? getRiskLevel(prediction.probability) : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="mb-6">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-400 to-cyan-400 bg-clip-text text-transparent mb-2">
              Heart Disease Prediction
            </h1>
            <p className="text-gray-400">
              Advanced AI-powered prediction with privacy-preserving federated learning
            </p>
          </div>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column: Input Form */}
          <div className="lg:col-span-2 space-y-8">
            {/* Model Selection */}
            <div className="backdrop-blur-lg bg-white/5 border border-white/10 p-6 rounded-2xl">
              <h2 className="text-xl font-bold text-gray-100 mb-4">
                Select Prediction Model
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {models.map((model) => (
                  <button
                    key={model.type}
                    onClick={() => setActiveModel(model.type)}
                    className={`p-4 rounded-xl text-left transition-all duration-300 ${
                      activeModel === model.type
                        ? 'bg-gradient-to-br from-gray-900 to-gray-800 border-2 border-primary-500/50'
                        : 'bg-gray-900/30 hover:bg-gray-800/30 border border-gray-700'
                    }`}
                  >
                    <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${model.color} mb-3`}>
                      {model.icon}
                    </div>
                    <h3 className="font-bold text-gray-100 capitalize">
                      {model.label} Model
                    </h3>
                    <p className="text-sm text-gray-400 mt-1">
                      {model.type === 'federated' && 'Privacy-preserving'}
                      {model.type === 'athletic' && 'For athletic individuals'}
                      {model.type === 'diver' && 'For diving activities'}
                      {model.type === 'typical' && 'General population'}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Input Form */}
            <div className="backdrop-blur-lg bg-white/5 border border-white/10 p-6 rounded-2xl">
              <h2 className="text-xl font-bold text-gray-100 mb-6">
                Patient Health Metrics
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                {[
                  { label: 'Age (years)', field: 'age', type: 'number', min: 0, max: 120 },
                  { label: 'Sex', field: 'sex', type: 'select', options: [
                    { value: 1, label: 'Male' },
                    { value: 0, label: 'Female' }
                  ]},
                  { label: 'Chest Pain Type', field: 'cp', type: 'select', options: [
                    { value: 1, label: 'Typical Angina' },
                    { value: 2, label: 'Atypical Angina' },
                    { value: 3, label: 'Non-anginal Pain' },
                    { value: 4, label: 'Asymptomatic' }
                  ]},
                  { label: 'Resting BP (mm Hg)', field: 'trestbps', type: 'number', min: 50, max: 250 },
                  { label: 'Cholesterol (mg/dl)', field: 'chol', type: 'number', min: 100, max: 600 },
                  { label: 'Fasting Blood Sugar', field: 'fbs', type: 'select', options: [
                    { value: 0, label: '≤ 120 mg/dl' },
                    { value: 1, label: '> 120 mg/dl' }
                  ]},
                  { label: 'Resting ECG', field: 'restecg', type: 'select', options: [
                    { value: 0, label: 'Normal' },
                    { value: 1, label: 'ST-T Abnormality' },
                    { value: 2, label: 'LV Hypertrophy' }
                  ]},
                  { label: 'Max Heart Rate (bpm)', field: 'thalach', type: 'number', min: 40, max: 220 },
                  { label: 'Exercise Angina', field: 'exang', type: 'select', options: [
                    { value: 0, label: 'No' },
                    { value: 1, label: 'Yes' }
                  ]},
                  { label: 'ST Depression (mm)', field: 'oldpeak', type: 'number', step: '0.1', min: 0, max: 10 },
                  { label: 'ST Segment Slope', field: 'slope', type: 'select', options: [
                    { value: 1, label: 'Upsloping' },
                    { value: 2, label: 'Flat' },
                    { value: 3, label: 'Downsloping' }
                  ]},
                  { label: 'Major Vessels (0-3)', field: 'ca', type: 'number', min: 0, max: 3 },
                  { label: 'Thalassemia', field: 'thal', type: 'select', options: [
                    { value: 3, label: 'Normal' },
                    { value: 6, label: 'Fixed Defect' },
                    { value: 7, label: 'Reversible Defect' }
                  ]},
                ].map((field) => (
                  <div key={field.field}>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      {field.label}
                    </label>
                    {field.type === 'select' ? (
                      <select
                        value={formData[field.field]}
                        onChange={(e) => handleInputChange(field.field, e.target.value)}
                        className="w-full px-4 py-3 bg-gray-900/50 border border-gray-700 rounded-xl text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      >
                        {field.options.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type={field.type}
                        value={formData[field.field]}
                        onChange={(e) => handleInputChange(field.field, e.target.value)}
                        className="w-full px-4 py-3 bg-gray-900/50 border border-gray-700 rounded-xl text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        min={field.min}
                        max={field.max}
                        step={field.step}
                      />
                    )}
                  </div>
                ))}
              </div>

              <button
                onClick={handlePredict}
                disabled={loading}
                className="w-full py-4 bg-gradient-to-r from-primary-600 to-cyan-600 text-white font-semibold rounded-xl hover:from-primary-700 hover:to-cyan-700 transition-all duration-300 flex items-center justify-center space-x-3 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Brain className="w-6 h-6" />
                    <span>Predict Heart Disease Risk</span>
                    <Zap className="w-5 h-5" />
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Column: Results */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <div className="backdrop-blur-lg bg-white/5 border border-white/10 p-6 rounded-2xl">
                <h2 className="text-xl font-bold text-gray-100 mb-6">
                  Prediction Results
                </h2>

                {prediction ? (
                  <div className="space-y-6">
                    {/* Risk Level */}
                    <div className={`p-4 rounded-xl ${risk.bg} border ${risk.color.replace('text-', 'border-')}/30`}>
                      <div className="flex items-center space-x-3 mb-2">
                        {prediction.risk_level === 'high' && <AlertTriangle className="w-5 h-5 text-red-400" />}
                        {prediction.risk_level === 'moderate' && <Activity className="w-5 h-5 text-yellow-400" />}
                        {prediction.risk_level === 'low' && <CheckCircle className="w-5 h-5 text-green-400" />}
                        <span className={`font-bold ${risk.color}`}>
                          {risk.level} Risk
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-primary-600 to-cyan-600 rounded-full"
                            style={{ width: `${prediction.probability * 100}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-400 font-mono">
                          {(prediction.probability * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>

                    {/* Details */}
                    <div className="space-y-4">
                      <div className="p-4 bg-gray-900/50 rounded-xl">
                        <h3 className="text-sm font-medium text-gray-400 mb-2">Details</h3>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-gray-400">Prediction</span>
                            <span className={`font-bold ${prediction.prediction === 1 ? 'text-red-400' : 'text-green-400'}`}>
                              {prediction.prediction === 1 ? 'Heart Disease' : 'No Heart Disease'}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Model Used</span>
                            <span className="font-bold text-cyan-300 capitalize">
                              {prediction.model_used}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Time</span>
                            <span className="text-sm text-gray-400">
                              {new Date(prediction.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Recommendations */}
                      <div className="p-4 bg-gray-900/50 rounded-xl">
                        <h3 className="text-sm font-medium text-gray-400 mb-2">Recommendations</h3>
                        <ul className="space-y-2">
                          {prediction.risk_level === 'high' && (
                            <>
                              <li className="flex items-start space-x-2 text-sm">
                                <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                                <span className="text-gray-300">Schedule immediate consultation</span>
                              </li>
                              <li className="flex items-start space-x-2 text-sm">
                                <Heart className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                                <span className="text-gray-300">Avoid strenuous activities</span>
                              </li>
                            </>
                          )}
                          <li className="flex items-start space-x-2 text-sm">
                            <Shield className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-300">Data privacy maintained</span>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="inline-flex p-4 rounded-xl bg-gray-800/50 mb-4">
                      <Brain className="w-8 h-8 text-gray-500" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-300 mb-2">
                      No Prediction Yet
                    </h3>
                    <p className="text-gray-500">
                      Enter health metrics and click "Predict"
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Predict;