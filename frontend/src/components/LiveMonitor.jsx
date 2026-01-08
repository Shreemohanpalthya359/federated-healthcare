import React, { useState, useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import io from 'socket.io-client';
import { 
  Activity, 
  Heart, 
  Thermometer, 
  Wind, 
  Wifi, 
  WifiOff, 
  AlertCircle,
  User,
  Clock,
  Battery
} from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const LiveMonitor = () => {
  const [monitoringActive, setMonitoringActive] = useState(false);
  const [connected, setConnected] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState('patient_001');
  const [vitalData, setVitalData] = useState(null);
  const [ecgData, setEcgData] = useState(Array(50).fill(0));
  const socketRef = useRef(null);

  // Simulated patients list
  const patients = [
    { id: 'patient_001', name: 'John Doe', status: 'Critical' },
    { id: 'patient_002', name: 'Jane Smith', status: 'Stable' },
    { id: 'patient_003', name: 'Robert Johnson', status: 'Stable' },
  ];

  useEffect(() => {
    // Simulate WebSocket for demo purposes if backend isn't running
    const simulateData = setInterval(() => {
      const newPoint = Math.random() * 2 - 1 + Math.sin(Date.now() / 200);
      setEcgData(prev => [...prev.slice(1), newPoint]);
      
      setVitalData({
        heartRate: 70 + Math.floor(Math.random() * 10),
        bloodPressure: { systole: 120, diastole: 80 },
        spo2: 98,
        temp: 36.6
      });
      setConnected(true);
      setMonitoringActive(true);
    }, 100);

    return () => clearInterval(simulateData);
  }, []);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 0 },
    scales: {
      x: { display: false },
      y: { 
        display: true,
        min: -2,
        max: 2,
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { display: false }
      }
    },
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false }
    },
    elements: {
      point: { radius: 0 },
      line: { tension: 0.4, borderWidth: 2 }
    }
  };

  const chartData = {
    labels: Array(50).fill(''),
    datasets: [{
      data: ecgData,
      borderColor: '#06b6d4', // Cyan-500
      backgroundColor: 'rgba(6, 182, 212, 0.1)',
      fill: true,
    }]
  };

  const VitalCard = ({ icon: Icon, label, value, unit, color, trend }) => (
    <div className="bg-gray-900/50 border border-white/10 rounded-2xl p-5 backdrop-blur-sm hover:border-white/20 transition-all">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-2 rounded-lg bg-${color}-500/10`}>
          <Icon className={`w-6 h-6 text-${color}-400`} />
        </div>
        {trend && (
          <span className="text-xs font-mono text-gray-400 bg-white/5 px-2 py-1 rounded">
            {trend}
          </span>
        )}
      </div>
      <div>
        <div className="text-3xl font-bold text-white mb-1">
          {value} <span className="text-sm font-normal text-gray-400">{unit}</span>
        </div>
        <div className="text-sm text-gray-400">{label}</div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-white p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-400 to-cyan-400 bg-clip-text text-transparent">
              Live Monitoring
            </h1>
            <p className="text-gray-400 text-sm mt-1 flex items-center">
              <span className={`w-2 h-2 rounded-full mr-2 ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
              {connected ? 'Real-time Data Stream Active' : 'Connecting to Telemetry Server...'}
            </p>
          </div>

          <div className="flex items-center space-x-4">
            <select 
              value={selectedPatient}
              onChange={(e) => setSelectedPatient(e.target.value)}
              className="bg-gray-900 border border-white/10 text-white text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5"
            >
              {patients.map(p => (
                <option key={p.id} value={p.id}>{p.name} ({p.status})</option>
              ))}
            </select>
            <div className="flex items-center space-x-2 px-3 py-2 bg-gray-900 rounded-lg border border-white/10">
              <Clock className="w-4 h-4 text-gray-400" />
              <span className="text-sm font-mono">{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-12 gap-6">
          
          {/* Main ECG Display */}
          <div className="lg:col-span-8 space-y-6">
            <div className="bg-gray-900/50 border border-white/10 rounded-2xl p-6 h-[400px] relative">
              <div className="absolute top-6 left-6 flex items-center space-x-2 z-10">
                <Activity className="w-5 h-5 text-cyan-400 animate-pulse" />
                <span className="text-sm font-bold text-cyan-400">LEAD II</span>
              </div>
              <div className="h-full w-full pt-8">
                <Line data={chartData} options={chartOptions} />
              </div>
            </div>

            {/* Vitals Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <VitalCard 
                icon={Heart}
                label="Heart Rate"
                value={vitalData?.heartRate || '--'}
                unit="bpm"
                color="red"
                trend="Normal"
              />
              <VitalCard 
                icon={Activity}
                label="Blood Pressure"
                value={`${vitalData?.bloodPressure?.systole || '--'}/${vitalData?.bloodPressure?.diastole || '--'}`}
                unit="mmHg"
                color="blue"
              />
              <VitalCard 
                icon={Wind}
                label="SpO2"
                value={vitalData?.spo2 || '--'}
                unit="%"
                color="cyan"
              />
              <VitalCard 
                icon={Thermometer}
                label="Temperature"
                value={vitalData?.temp || '--'}
                unit="°C"
                color="orange"
              />
            </div>
          </div>

          {/* Sidebar Info */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Patient Status Card */}
            <div className="bg-gray-900/50 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-semibold text-white">Device Status</h3>
                <Battery className="w-5 h-5 text-green-400" />
              </div>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400">Connection Quality</span>
                  <span className="text-green-400">Excellent (5ms)</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5">
                  <div className="bg-green-500 h-1.5 rounded-full w-[95%]" />
                </div>
                
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400">Battery Level</span>
                  <span className="text-white">84%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5">
                  <div className="bg-blue-500 h-1.5 rounded-full w-[84%]" />
                </div>
              </div>
            </div>

            {/* Recent Alerts */}
            <div className="bg-gray-900/50 border border-white/10 rounded-2xl p-6 h-[300px] overflow-hidden flex flex-col">
              <h3 className="font-semibold text-white mb-4 flex items-center">
                <AlertCircle className="w-4 h-4 mr-2 text-yellow-400" />
                Recent Alerts
              </h3>
              
              <div className="space-y-3 overflow-y-auto pr-2 custom-scrollbar flex-1">
                {[1, 2, 3].map((_, i) => (
                  <div key={i} className="flex items-start space-x-3 p-3 bg-white/5 rounded-lg border border-white/5">
                    <div className="w-1.5 h-1.5 rounded-full bg-yellow-400 mt-2" />
                    <div>
                      <p className="text-sm text-gray-200">Irregular heartbeat detected</p>
                      <p className="text-xs text-gray-500 mt-1">2 mins ago</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveMonitor;
