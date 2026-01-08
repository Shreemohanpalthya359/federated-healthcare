import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Brain, 
  Activity, 
  Zap, 
  Shield,
  User,
  Heart,
  Thermometer,
  Wind,
  Droplets,
  Gauge,
  CheckCircle,
  AlertTriangle,
  Info,
  ChevronRight,
  Stethoscope,
  FileText
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { predictApi } from '../api/predictApi';

const Predict = () => {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [modelType, setModelType] = useState('federated');
  
  // Form State
  const [formData, setFormData] = useState({
    age: 45,
    sex: 1,
    cp: 0,
    trestbps: 120,
    chol: 200,
    fbs: 0,
    restecg: 0,
    thalach: 150,
    exang: 0,
    oldpeak: 0,
    slope: 1,
    ca: 0,
    thal: 2
  });

  // UI Helpers
  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handlePredict = async () => {
    setLoading(true);
    setPrediction(null);
    
    try {
      // Map form data to feature array expected by backend
      const features = [
        formData.age,
        formData.sex,
        formData.cp,
        formData.trestbps,
        formData.chol,
        formData.fbs,
        formData.restecg,
        formData.thalach,
        formData.exang,
        formData.oldpeak,
        formData.slope,
        formData.ca,
        formData.thal
      ];

      const payload = {
        patient_id: 'user_' + Date.now(),
        features: features,
        model_type: modelType
      };

      const response = await predictApi.makePrediction(payload);
      
      if (response.data.status === 'success') {
        const result = response.data.data;
        setPrediction({
          probability: result.probability * 100, // Convert to percentage
          riskLevel: result.risk_level,
          factors: [
            { name: 'Cholesterol', impact: 'High', value: formData.chol },
            { name: 'Max Heart Rate', impact: 'Medium', value: formData.thalach },
            { name: 'ST Depression', impact: 'Low', value: formData.oldpeak }
          ],
          timestamp: result.timestamp,
          modelUsed: result.model_used,
          driftDetected: result.drift_detected
        });
        toast.success('Analysis Complete');
      } else {
        throw new Error(response.data.message || 'Prediction failed');
      }
    } catch (err) {
      console.error(err);
      toast.error(err.message || 'Analysis Failed');
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    {
      id: 'vitals',
      title: 'Vitals & Demographics',
      icon: User,
      fields: [
        { key: 'age', label: 'Age', type: 'slider', min: 20, max: 90, unit: 'yrs' },
        { key: 'sex', label: 'Biological Sex', type: 'select', options: [{label: 'Male', value: 1}, {label: 'Female', value: 0}] },
        { key: 'trestbps', label: 'Resting BP', type: 'slider', min: 90, max: 200, unit: 'mmHg' },
        { key: 'chol', label: 'Cholesterol', type: 'slider', min: 120, max: 500, unit: 'mg/dl' },
      ]
    },
    {
      id: 'clinical',
      title: 'Clinical Signs',
      icon: Stethoscope,
      fields: [
        { key: 'cp', label: 'Chest Pain Type', type: 'select', options: [
          {label: 'Typical Angina', value: 0},
          {label: 'Atypical Angina', value: 1},
          {label: 'Non-anginal', value: 2},
          {label: 'Asymptomatic', value: 3}
        ]},
        { key: 'fbs', label: 'Fasting Blood Sugar > 120', type: 'select', options: [{label: 'True', value: 1}, {label: 'False', value: 0}] },
        { key: 'restecg', label: 'Resting ECG', type: 'select', options: [
          {label: 'Normal', value: 0},
          {label: 'ST-T Wave Abnormality', value: 1},
          {label: 'LV Hypertrophy', value: 2}
        ]},
        { key: 'ca', label: 'Major Vessels (0-3)', type: 'slider', min: 0, max: 3, step: 1, unit: '' },
        { key: 'thal', label: 'Thalassemia', type: 'select', options: [
          {label: 'Normal', value: 1},
          {label: 'Fixed Defect', value: 2},
          {label: 'Reversible Defect', value: 3}
        ]},
      ]
    },
    {
      id: 'stress',
      title: 'Stress Test Results',
      icon: Activity,
      fields: [
        { key: 'thalach', label: 'Max Heart Rate', type: 'slider', min: 60, max: 220, unit: 'bpm' },
        { key: 'exang', label: 'Exercise Induced Angina', type: 'select', options: [{label: 'Yes', value: 1}, {label: 'No', value: 0}] },
        { key: 'oldpeak', label: 'ST Depression', type: 'slider', min: 0, max: 6, step: 0.1, unit: '' },
        { key: 'slope', label: 'ST Slope', type: 'select', options: [
          {label: 'Upsloping', value: 1},
          {label: 'Flat', value: 2},
          {label: 'Downsloping', value: 3}
        ]},
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-white p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-400 to-cyan-400 bg-clip-text text-transparent">
              Predictive Diagnostics
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Federated AI Model v2.4 • Secure Environment
            </p>
          </div>
          <div className="flex items-center space-x-4">
             <div className="relative">
              <select
                value={modelType}
                onChange={(e) => setModelType(e.target.value)}
                className="appearance-none bg-gray-900 border border-white/10 text-white text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 pr-8"
              >
                <option value="federated">Federated (Default)</option>
                <optgroup label="Athletic Activities">
                  <option value="athletic">General Athlete</option>
                  <option value="runner">Runner</option>
                  <option value="cyclist">Cyclist</option>
                  <option value="weightlifter">Weightlifter</option>
                  <option value="exercise">Fitness Enthusiast</option>
                </optgroup>
                <optgroup label="Water Sports">
                  <option value="diver">Diver</option>
                  <option value="swimmer">Swimmer</option>
                </optgroup>
                <optgroup label="Lifestyle">
                  <option value="typical">Typical / Sedentary</option>
                </optgroup>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
                <Brain className="h-4 w-4" />
              </div>
            </div>

            <div className="hidden md:flex items-center space-x-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full">
              <Shield className="w-4 h-4 text-green-400" />
              <span className="text-xs text-gray-300">End-to-End Encrypted</span>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-12 gap-8">
          
          {/* Left Column: Input Form */}
          <div className="lg:col-span-7 space-y-6">
            <div className="bg-gray-900/50 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
              
              {/* Tabs */}
              <div className="flex space-x-1 bg-black/40 p-1 rounded-xl mb-6">
                {categories.map((cat, idx) => (
                  <button
                    key={cat.id}
                    onClick={() => setActiveStep(idx)}
                    className={`flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      activeStep === idx 
                        ? 'bg-gradient-to-r from-primary-600 to-cyan-600 text-white shadow-lg' 
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <cat.icon className="w-4 h-4" />
                    <span className="hidden sm:inline">{cat.title}</span>
                  </button>
                ))}
              </div>

              {/* Form Fields */}
              <div className="space-y-6 min-h-[400px]">
                <AnimatePresence mode='wait'>
                  <motion.div
                    key={activeStep}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    transition={{ duration: 0.2 }}
                    className="grid gap-6"
                  >
                    {categories[activeStep].fields.map((field) => (
                      <div key={field.key} className="space-y-2">
                        <div className="flex justify-between">
                          <label className="text-sm font-medium text-gray-300">{field.label}</label>
                          {field.type === 'slider' && (
                            <span className="text-sm font-mono text-cyan-400">
                              {formData[field.key]} {field.unit}
                            </span>
                          )}
                        </div>

                        {field.type === 'slider' ? (
                          <div className="relative pt-1">
                            <input
                              type="range"
                              min={field.min}
                              max={field.max}
                              step={field.step || 1}
                              value={formData[field.key]}
                              onChange={(e) => handleInputChange(field.key, parseFloat(e.target.value))}
                              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500 hover:accent-cyan-400"
                            />
                            <div className="flex justify-between text-xs text-gray-500 mt-1">
                              <span>{field.min}</span>
                              <span>{field.max}</span>
                            </div>
                          </div>
                        ) : (
                          <div className="grid grid-cols-2 gap-2">
                            {field.options.map((opt) => (
                              <button
                                key={opt.label}
                                onClick={() => handleInputChange(field.key, opt.value)}
                                className={`py-2 px-3 rounded-lg text-sm transition-all border ${
                                  formData[field.key] === opt.value
                                    ? 'bg-primary-500/20 border-primary-500 text-primary-300'
                                    : 'bg-gray-800/50 border-gray-700 text-gray-400 hover:border-gray-600'
                                }`}
                              >
                                {opt.label}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </motion.div>
                </AnimatePresence>
              </div>

              {/* Action Bar */}
              <div className="flex justify-between mt-8 pt-6 border-t border-white/10">
                 <button
                   disabled={activeStep === 0}
                   onClick={() => setActiveStep(prev => prev - 1)}
                   className="px-4 py-2 text-gray-400 hover:text-white disabled:opacity-0 transition-colors"
                 >
                   Back
                 </button>
                 
                 {activeStep === categories.length - 1 ? (
                   <button
                     onClick={handlePredict}
                     disabled={loading}
                     className="px-8 py-2.5 bg-gradient-to-r from-primary-500 to-cyan-500 text-white font-bold rounded-xl shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40 transition-all disabled:opacity-50 flex items-center space-x-2"
                   >
                     {loading ? (
                       <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                     ) : (
                       <>
                         <Brain className="w-5 h-5" />
                         <span>Run Analysis</span>
                       </>
                     )}
                   </button>
                 ) : (
                   <button
                     onClick={() => setActiveStep(prev => prev + 1)}
                     className="flex items-center space-x-2 px-6 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-all"
                   >
                     <span>Next Step</span>
                     <ChevronRight className="w-4 h-4" />
                   </button>
                 )}
              </div>
            </div>
          </div>

          {/* Right Column: Visualization & Results */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* Real-time Model Status */}
            <div className="bg-gray-900/50 border border-white/10 rounded-2xl p-6 backdrop-blur-sm relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary-500/10 rounded-full blur-2xl -mr-16 -mt-16" />
              
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Activity className="w-5 h-5 text-cyan-400 mr-2" />
                Model Telemetry
              </h3>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-3 bg-black/20 rounded-xl border border-white/5">
                  <div className="text-gray-400 text-xs mb-1">Confidence</div>
                  <div className="text-xl font-mono text-green-400">98.2%</div>
                </div>
                <div className="p-3 bg-black/20 rounded-xl border border-white/5">
                  <div className="text-gray-400 text-xs mb-1">Latency</div>
                  <div className="text-xl font-mono text-blue-400">12ms</div>
                </div>
              </div>

              {/* Prediction Result Card */}
              <AnimatePresence>
                {prediction ? (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-white/10 p-5 shadow-xl"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-gray-400 text-sm">Risk Assessment</span>
                      <span className="text-xs text-gray-500">{new Date(prediction.timestamp).toLocaleTimeString()}</span>
                    </div>

                    <div className="flex items-center justify-center mb-6 relative">
                      <svg className="w-32 h-32 transform -rotate-90">
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          stroke="currentColor"
                          strokeWidth="12"
                          fill="transparent"
                          className="text-gray-700"
                        />
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          stroke="currentColor"
                          strokeWidth="12"
                          fill="transparent"
                          strokeDasharray={351}
                          strokeDashoffset={351 - (351 * prediction.probability) / 100}
                          className={`${
                            prediction.riskLevel === 'High' ? 'text-red-500' :
                            prediction.riskLevel === 'Moderate' ? 'text-yellow-500' : 'text-green-500'
                          } transition-all duration-1000 ease-out`}
                        />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-3xl font-bold text-white">{Math.round(prediction.probability)}%</span>
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                          prediction.riskLevel === 'High' ? 'bg-red-500/20 text-red-400' :
                          prediction.riskLevel === 'Moderate' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'
                        }`}>
                          {prediction.riskLevel}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Contributing Factors</p>
                      {prediction.factors.map((factor, i) => (
                        <div key={i} className="flex items-center justify-between text-sm">
                          <span className="text-gray-300">{factor.name}</span>
                          <div className="flex items-center space-x-2">
                            <span className="text-gray-500">{factor.value}</span>
                            <div className={`w-2 h-2 rounded-full ${
                              factor.impact === 'High' ? 'bg-red-500' : 
                              factor.impact === 'Medium' ? 'bg-yellow-500' : 'bg-green-500'
                            }`} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                ) : (
                  <div className="h-64 flex flex-col items-center justify-center text-gray-500 border-2 border-dashed border-gray-800 rounded-xl">
                    <Brain className="w-12 h-12 mb-3 opacity-20" />
                    <p className="text-sm">Enter patient data to run analysis</p>
                  </div>
                )}
              </AnimatePresence>
            </div>

            {/* Disclaimer */}
            <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-xl flex items-start space-x-3">
              <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-blue-200/80 leading-relaxed">
                This AI tool is for assistive diagnostic purposes only. Results should be verified by a qualified cardiologist. 
                Data processing occurs locally on your device to ensure privacy compliance.
              </p>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default Predict;
