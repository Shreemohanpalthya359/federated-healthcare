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
  const [trackingActive, setTrackingActive] = useState(false);
  const [people, setPeople] = useState([]);
  const [selectedPerson, setSelectedPerson] = useState('person_001');
  const [vitalData, setVitalData] = useState(null);
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
      console.log('Connected to live tracking server');
      setConnected(true);
      
      // Request initial data for selected person
      if (selectedPerson) {
        socketRef.current.emit('request_person_data', { person_id: selectedPerson });
      }
    });

    socketRef.current.on('connected', (data) => {
      console.log('Server connected:', data);
    });

    socketRef.current.on('live_vitals', (data) => {
      console.log('Live vitals received:', data);
      if (data.person_id === selectedPerson) {
        setVitalData(data);
        
        // Update ECG data
        if (data.ecg_wave && Array.isArray(data.ecg_wave)) {
          setEcgData(prev => {
            const newData = [...prev, ...data.ecg_wave];
            return newData.slice(-100); // Keep last 100 points
          });
        }
      }
    });

    socketRef.current.on('tracking_status', (data) => {
      setTrackingActive(data.active);
      console.log('Tracking status:', data);
    });

    socketRef.current.on('person_selected', (data) => {
      console.log('Person selected:', data);
    });

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from live tracking server');
      setConnected(false);
      setTrackingActive(false);
    });

    // Fetch initial people data
    fetchPeople();

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [selectedPerson]);

  // Update backend when person changes
  useEffect(() => {
    if (connected && selectedPerson && socketRef.current) {
      socketRef.current.emit('select_person', { person_id: selectedPerson });
      setEcgData(Array(100).fill(0));
      setVitalData(null);
    }
  }, [selectedPerson, connected]);

  const fetchPeople = async () => {
    try {
      // First try the new endpoint
      const response = await fetch('http://localhost:5001/monitor/api/monitor/people');
      if (!response.ok) {
        throw new Error('People endpoint failed');
      }
      const data = await response.json();
      setPeople(data);
      
      // Set default selected person if not set
      if (data.length > 0 && !selectedPerson) {
        setSelectedPerson(data[0].id);
      }
    } catch (error) {
      console.warn('Could not fetch from /people, trying /patients:', error);
      
      // Fallback to old endpoint
      try {
        const response = await fetch('http://localhost:5001/monitor/api/monitor/patients');
        if (response.ok) {
          const data = await response.json();
          // Convert patient data to person format if needed
          const peopleData = data.map(item => ({
            ...item,
            id: item.id || `person_${item.id?.replace('patient_', '') || '001'}`
          }));
          setPeople(peopleData);
          
          if (peopleData.length > 0 && !selectedPerson) {
            setSelectedPerson(peopleData[0].id);
          }
        }
      } catch (fallbackError) {
        console.error('Both endpoints failed:', fallbackError);
        setPeople([]);
      }
    }
  };

  const startTracking = () => {
    if (socketRef.current && connected) {
      socketRef.current.emit('start_tracking', { person_id: selectedPerson });
      fetch('http://localhost:5001/api/live/start', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ person_id: selectedPerson })
      })
        .then(res => res.json())
        .then(data => {
          console.log('Live tracking started:', selectedPerson, data);
          setTrackingActive(true);
        })
        .catch(err => console.error('Error starting live tracking:', err));
    }
  };

  const stopTracking = () => {
    if (socketRef.current && connected) {
      socketRef.current.emit('stop_tracking');
      fetch('http://localhost:5001/api/live/stop', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          console.log('Live tracking stopped:', data);
          setTrackingActive(false);
        })
        .catch(err => console.error('Error stopping live tracking:', err));
    }
  };

  // Get selected person info
  const selectedPersonInfo = people.find(p => p.id === selectedPerson) || {};
  
  // Prepare data for display
  const currentVitals = vitalData || {
    heart_rate: '--',
    blood_pressure: '--/--',
    oxygen_saturation: '--',
    respiratory_rate: '--',
    temperature: '--',
    timestamp: new Date().toISOString()
  };

  // ECG Chart Configuration
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
        display: true,
        title: {
          display: true,
          text: 'Time (ms)',
          color: 'rgba(255, 255, 255, 0.7)'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)'
        }
      },
      y: {
        min: -1.0,
        max: 2.0,
        title: {
          display: true,
          text: 'Voltage (mV)',
          color: 'rgba(255, 255, 255, 0.7)'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)',
          callback: function(value) {
            return value.toFixed(1);
          }
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: true,
        mode: 'index',
        intersect: false
      }
    }
  };

  // Vitals Bar Chart Configuration
  const vitalsChartData = {
    labels: ['Heart Rate', 'O₂ Saturation', 'Resp. Rate', 'Temperature'],
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
        ],
        borderRadius: 6,
        borderSkipped: false,
      }
    ]
  };

  const vitalsChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const labels = ['Heart Rate', 'O₂ Saturation', 'Resp. Rate', 'Temperature'];
            const units = [' bpm', '%', ' breaths/min', '°C'];
            const index = context.dataIndex;
            const value = context.parsed.y;
            let displayValue = value;
            
            // Adjust for temperature scaling
            if (index === 3) {
              displayValue = (value / 10).toFixed(1);
            }
            
            return labels[index] + ': ' + displayValue + units[index];
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 200,
        title: {
          display: true,
          text: 'Value',
          color: 'rgba(255, 255, 255, 0.7)'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)',
          stepSize: 40
        }
      },
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)'
        }
      }
    }
  };

  // Handle person selection
  const handlePersonSelect = (personId) => {
    setSelectedPerson(personId);
  };

  return (
    <div className="min-h-screen bg-gray-950 p-4 md:p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 md:mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white gradient-text">Live Monitor</h1>
          <p className="text-gray-400 mt-1">Real-time vital signs tracking</p>
        </div>
        
        <div className="flex flex-wrap items-center gap-4">
          <div className={`px-4 py-2 rounded-full flex items-center gap-2 ${connected ? 'bg-green-900/30 text-green-400 border border-green-700/50' : 'bg-red-900/30 text-red-400 border border-red-700/50'}`}>
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            {connected ? 'CONNECTED' : 'DISCONNECTED'}
          </div>
          
          <div className={`px-4 py-2 rounded-full ${trackingActive ? 'bg-green-900/30 text-green-400 border border-green-700/50' : 'bg-gray-800 text-gray-400 border border-gray-700/50'}`}>
            {trackingActive ? '● LIVE TRACKING' : '● READY'}
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={startTracking}
              disabled={!connected || trackingActive || !selectedPerson}
              className={`px-4 py-2 rounded-lg font-semibold ${!connected || trackingActive || !selectedPerson ? 'bg-gray-700 cursor-not-allowed text-gray-500' : 'bg-green-600 hover:bg-green-700 text-white'} transition-colors`}
            >
              Start Tracking
            </button>
            <button
              onClick={stopTracking}
              disabled={!trackingActive}
              className={`px-4 py-2 rounded-lg font-semibold ${!trackingActive ? 'bg-gray-700 cursor-not-allowed text-gray-500' : 'bg-red-600 hover:bg-red-700 text-white'} transition-colors`}
            >
              Stop Tracking
            </button>
          </div>
        </div>
      </div>

      {/* Main Content - Simplified Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Live Tracking Selection */}
        <div className="lg:col-span-1">
          <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl p-6 mb-6">
            <h2 className="text-xl font-semibold text-white mb-4">Live Tracking</h2>
            <div className="space-y-4">
              {people.map(person => (
                <div
                  key={person.id}
                  onClick={() => handlePersonSelect(person.id)}
                  className={`p-4 rounded-lg cursor-pointer transition-all duration-200 ${
                    selectedPerson === person.id
                      ? 'bg-blue-900/30 border-2 border-blue-700/50'
                      : 'bg-gray-800/50 hover:bg-gray-800 border border-gray-700/50'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold text-white text-lg">{person.name}</h3>
                      <p className="text-gray-400">{person.condition}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-gray-400">Room {person.room}</div>
                      <div className="text-gray-500">Age {person.age}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      person.status === 'critical' ? 'bg-red-500' :
                      person.status === 'stable' ? 'bg-green-500' : 'bg-yellow-500'
                    }`}></div>
                    <span className="text-sm font-medium text-gray-300 capitalize">{person.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Current Vital Signs */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Current Readings</h2>
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                  <div className="text-sm text-gray-400 mb-1">Heart Rate</div>
                  <div className="text-3xl font-bold text-white">
                    {currentVitals.heart_rate !== '--' ? currentVitals.heart_rate : '--'}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">bpm</div>
                </div>
                
                <div className="text-center p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                  <div className="text-sm text-gray-400 mb-1">SpO₂</div>
                  <div className="text-3xl font-bold text-white">
                    {currentVitals.oxygen_saturation !== '--' ? currentVitals.oxygen_saturation : '--'}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">%</div>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-gray-800/30 rounded">
                  <span className="text-gray-400">Blood Pressure</span>
                  <span className="font-semibold text-white">{currentVitals.blood_pressure}</span>
                </div>
                
                <div className="flex justify-between items-center p-3 bg-gray-800/30 rounded">
                  <span className="text-gray-400">Resp. Rate</span>
                  <span className="font-semibold text-white">
                    {currentVitals.respiratory_rate !== '--' ? currentVitals.respiratory_rate : '--'}
                  </span>
                </div>
                
                <div className="flex justify-between items-center p-3 bg-gray-800/30 rounded">
                  <span className="text-gray-400">Temperature</span>
                  <span className="font-semibold text-white">
                    {currentVitals.temperature !== '--' ? currentVitals.temperature : '--'}
                  </span>
                </div>
              </div>
              
              <div className="pt-4 border-t border-gray-700/50">
                <div className="text-sm text-gray-400">Last Update</div>
                <div className="text-sm text-gray-300">
                  {currentVitals.timestamp ? new Date(currentVitals.timestamp).toLocaleTimeString() : '--:--:--'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Charts */}
        <div className="lg:col-span-2 space-y-6">
          {/* ECG Chart */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-white">Real-time ECG</h2>
              <div className="text-sm text-gray-400">
                {selectedPersonInfo?.name || 'Select a person'}
              </div>
            </div>
            <div className="h-64 md:h-80">
              <Line data={ecgChartData} options={ecgChartOptions} />
            </div>
          </div>

          {/* Vitals Chart */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-white">Vital Signs Overview</h2>
              <div className="text-sm text-gray-400">
                Live tracking • Updates every 2 seconds
              </div>
            </div>
            <div className="h-48 md:h-64">
              <Bar data={vitalsChartData} options={vitalsChartOptions} />
            </div>
          </div>

          {/* Status Bar */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl p-4">
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-400">
                {selectedPersonInfo?.name 
                  ? `Tracking: ${selectedPersonInfo.name} • ${selectedPersonInfo.condition}`
                  : 'Select a person to begin live tracking'}
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-400">
                  {connected ? 'WebSocket Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveMonitor;