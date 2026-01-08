import React, { useState, useEffect, useRef } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import io from 'socket.io-client';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const LiveMonitor = () => {
  const [monitoringActive, setMonitoringActive] = useState(false);
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState('patient_001');
  const [vitalData, setVitalData] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [ecgData, setEcgData] = useState(Array(100).fill(0));
  const [connected, setConnected] = useState(false);
  const socketRef = useRef(null);

  // Initialize WebSocket connection
  useEffect(() => {
    // Connect to WebSocket
    socketRef.current = io('http://localhost:5001', {
      transports: ['websocket', 'polling']
    });
    
    socketRef.current.on('connect', () => {
      console.log('Connected to monitoring server');
      setConnected(true);
    });

    socketRef.current.on('connected', (data) => {
      console.log('Server connected:', data);
    });

    socketRef.current.on('live_vitals', (data) => {
      console.log('Live vitals received:', data);
      setVitalData(data);
      
      // Update ECG data for selected patient
      if (data[selectedPatient]) {
        const newEcgPoints = data[selectedPatient].ecg_lead || [];
        setEcgData(prev => {
          const updated = [...prev.slice(newEcgPoints.length), ...newEcgPoints];
          return updated.slice(-100); // Keep last 100 points
        });
      }
    });

    socketRef.current.on('monitoring_status', (data) => {
      setMonitoringActive(data.active);
      console.log('Monitoring status:', data);
    });

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from monitoring server');
      setConnected(false);
      setMonitoringActive(false);
    });

    // Fetch initial patients data
    fetchPatients();
    fetchAlerts();

    // Cleanup on unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [selectedPatient]);

  const fetchPatients = async () => {
    try {
      const response = await fetch('http://localhost:5001/monitor/api/monitor/patients');
      const data = await response.json();
      setPatients(data);
    } catch (error) {
      console.error('Error fetching patients:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch('http://localhost:5001/monitor/api/monitor/alerts');
      const data = await response.json();
      setAlerts(data || []);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const startMonitoring = () => {
    if (socketRef.current && connected) {
      socketRef.current.emit('start_monitoring');
      // Also call REST API
      fetch('http://localhost:5001/api/live/start', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          console.log('Monitoring started:', data);
          setMonitoringActive(true);
        })
        .catch(err => console.error('Error starting monitoring:', err));
    }
  };

  const stopMonitoring = () => {
    if (socketRef.current && connected) {
      socketRef.current.emit('stop_monitoring');
      // Also call REST API
      fetch('http://localhost:5001/api/live/stop', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          console.log('Monitoring stopped:', data);
          setMonitoringActive(false);
        })
        .catch(err => console.error('Error stopping monitoring:', err));
    }
  };

  const getPatientVitals = (patientId) => {
    return vitalData[patientId] || {
      heart_rate: '--',
      blood_pressure: '--/--',
      oxygen_saturation: '--',
      respiratory_rate: '--',
      temperature: '--',
      timestamp: new Date().toISOString()
    };
  };

  // Chart configurations for dark theme
  const ecgChartData = {
    labels: Array.from({ length: ecgData.length }, (_, i) => i),
    datasets: [
      {
        label: 'ECG Signal',
        data: ecgData,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0
      }
    ]
  };

  const ecgChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 0
    },
    scales: {
      x: {
        display: false,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      y: {
        min: -1,
        max: 2,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)'
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: false
      }
    }
  };

  // Get current patient vitals for bar chart
  const currentVitals = getPatientVitals(selectedPatient);
  const vitalsChartData = {
    labels: ['Heart Rate', 'O₂ Saturation', 'Resp Rate', 'Temperature'],
    datasets: [
      {
        label: 'Current Value',
        data: [
          currentVitals.heart_rate !== '--' ? currentVitals.heart_rate : 0,
          currentVitals.oxygen_saturation !== '--' ? currentVitals.oxygen_saturation : 0,
          currentVitals.respiratory_rate !== '--' ? currentVitals.respiratory_rate : 0,
          currentVitals.temperature !== '--' ? parseFloat(currentVitals.temperature) * 10 : 0
        ],
        backgroundColor: [
          '#ef4444', // Heart Rate - Red
          '#10b981', // O2 Sat - Green
          '#3b82f6', // Resp Rate - Blue
          '#f59e0b'  // Temperature - Yellow
        ]
      }
    ]
  };

  const vitalsChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)'
        }
      },
      x: {
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 p-4 md:p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 md:mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white gradient-text">Live Monitor</h1>
          <p className="text-gray-400 mt-1">Real-time patient vital signs monitoring</p>
        </div>
        
        <div className="flex flex-wrap items-center gap-4">
          <div className={`px-4 py-2 rounded-full flex items-center gap-2 ${connected ? 'bg-green-900/30 text-green-400 border border-green-700/50' : 'bg-red-900/30 text-red-400 border border-red-700/50'}`}>
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            {connected ? 'CONNECTED' : 'DISCONNECTED'}
          </div>
          
          <div className={`px-4 py-2 rounded-full ${monitoringActive ? 'bg-green-900/30 text-green-400 border border-green-700/50' : 'bg-gray-800 text-gray-400 border border-gray-700/50'}`}>
            {monitoringActive ? '● LIVE MONITORING' : '● IDLE'}
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={startMonitoring}
              disabled={!connected || monitoringActive}
              className={`px-4 py-2 rounded-lg font-semibold ${!connected || monitoringActive ? 'bg-gray-700 cursor-not-allowed text-gray-500' : 'bg-green-600 hover:bg-green-700 text-white'} transition-colors`}
            >
              Start
            </button>
            <button
              onClick={stopMonitoring}
              disabled={!monitoringActive}
              className={`px-4 py-2 rounded-lg font-semibold ${!monitoringActive ? 'bg-gray-700 cursor-not-allowed text-gray-500' : 'bg-red-600 hover:bg-red-700 text-white'} transition-colors`}
            >
              Stop
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Patients List */}
        <div className="lg:col-span-1 space-y-6">
          {/* Patients Card */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl p-4 md:p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Monitored Patients</h2>
            <div className="space-y-4">
              {patients.map(patient => {
                const vitals = getPatientVitals(patient.id);
                const isSelected = selectedPatient === patient.id;
                
                return (
                  <div
                    key={patient.id}
                    className={`p-4 rounded-lg cursor-pointer transition-all duration-200 ${isSelected ? 'bg-blue-900/30 border-2 border-blue-700/50' : 'bg-gray-800/50 hover:bg-gray-800 border border-gray-700/50'}`}
                    onClick={() => setSelectedPatient(patient.id)}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-white">{patient.name}</h3>
                        <p className="text-sm text-gray-400">{patient.condition} • Room {patient.room}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <div className={`w-2 h-2 rounded-full ${
                            patient.status === 'critical' ? 'bg-red-500' :
                            patient.status === 'stable' ? 'bg-green-500' : 'bg-yellow-500'
                          }`}></div>
                          <span className="text-sm font-medium text-gray-300 capitalize">{patient.status}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-400">Age {patient.age}</div>
                      </div>
                    </div>
                    
                    {/* Quick vitals display */}
                    <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-gray-700/50">
                      <div className="text-center p-2 bg-gray-800/50 rounded border border-gray-700/50">
                        <div className="text-xs text-gray-400">Heart Rate</div>
                        <div className="text-lg font-semibold text-white">{vitals.heart_rate}</div>
                        <div className="text-xs text-gray-500">bpm</div>
                      </div>
                      <div className="text-center p-2 bg-gray-800/50 rounded border border-gray-700/50">
                        <div className="text-xs text-gray-400">SpO₂</div>
                        <div className="text-lg font-semibold text-white">{vitals.oxygen_saturation}</div>
                        <div className="text-xs text-gray-500">%</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* System Status Card */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl p-4 md:p-6">
            <h2 className="text-xl font-semibold text-white mb-4">System Status</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">WebSocket Connection</span>
                <span className={`px-2 py-1 rounded text-sm ${connected ? 'bg-green-900/50 text-green-400 border border-green-700/30' : 'bg-red-900/50 text-red-400 border border-red-700/30'}`}>
                  {connected ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Data Streaming</span>
                <span className={`px-2 py-1 rounded text-sm ${monitoringActive ? 'bg-green-900/50 text-green-400 border border-green-700/30' : 'bg-gray-800 text-gray-400 border border-gray-700/30'}`}>
                  {monitoringActive ? 'Live' : 'Paused'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Patients Monitored</span>
                <span className="font-semibold text-white">{patients.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Last Update</span>
                <span className="text-sm text-gray-400">
                  {currentVitals.timestamp ? new Date(currentVitals.timestamp).toLocaleTimeString() : '--:--:--'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Charts & Alerts */}
        <div className="lg:col-span-2 space-y-6">
          {/* ECG Chart Card */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl p-4 md:p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-white">Real-time ECG</h2>
              <div className="text-sm text-gray-400">
                Patient: {patients.find(p => p.id === selectedPatient)?.name || selectedPatient}
              </div>
            </div>
            <div className="h-64 md:h-80">
              <Line data={ecgChartData} options={ecgChartOptions} />
            </div>
          </div>

          {/* Vitals Chart Card */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl p-4 md:p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Vital Signs Overview</h2>
            <div className="h-48 md:h-64">
              <Bar data={vitalsChartData} options={vitalsChartOptions} />
            </div>
          </div>

          {/* Alerts Card */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl p-4 md:p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-white">Alerts & Notifications</h2>
              <span className="px-3 py-1 bg-red-900/50 text-red-400 rounded-full text-sm font-medium border border-red-700/30">
                {alerts.filter(a => !a.acknowledged).length} Unread
              </span>
            </div>
            <div className="space-y-3">
              {alerts.length > 0 ? (
                alerts.map(alert => (
                  <div
                    key={alert.id}
                    className={`p-4 rounded-lg border-l-4 ${
                      alert.acknowledged 
                        ? 'border-gray-700 bg-gray-800/50' 
                        : 'border-red-500 bg-red-900/20'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          {!alert.acknowledged && (
                            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                          )}
                          <span className="font-semibold text-white">
                            {alert.type ? alert.type.toUpperCase() : 'ALERT'}
                          </span>
                          <span className="text-sm text-gray-400">• Patient {alert.patient_id}</span>
                        </div>
                        <p className="text-gray-300">{alert.message}</p>
                        <div className="flex items-center gap-4 mt-2">
                          <span className={`text-xs px-2 py-1 rounded ${
                            alert.severity === 'high' ? 'bg-red-900/50 text-red-400 border border-red-700/30' :
                            alert.severity === 'medium' ? 'bg-yellow-900/50 text-yellow-400 border border-yellow-700/30' :
                            'bg-blue-900/50 text-blue-400 border border-blue-700/30'
                          }`}>
                            {alert.severity || 'info'}
                          </span>
                          <span className="text-xs text-gray-500">
                            {alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : ''}
                          </span>
                        </div>
                      </div>
                      {!alert.acknowledged && (
                        <button className="text-sm text-blue-400 hover:text-blue-300 font-medium">
                          Acknowledge
                        </button>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No alerts at this time
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 text-center text-sm text-gray-500">
        Federated HeartCare Live Monitor • Data updates every 2 seconds • Last connected: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

export default LiveMonitor;