import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';

const HeartRateChart = ({ data, title, showAverage = true }) => {
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass p-3 rounded-lg border border-white/10 shadow-xl">
          <p className="text-sm text-gray-300 mb-1">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: <span className="font-bold">{entry.value}</span>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Calculate average if showAverage is true
  const average = showAverage 
    ? data.reduce((sum, item) => sum + item.heartRate, 0) / data.length 
    : null;

  return (
    <div className="glass p-6 rounded-2xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-100">{title}</h3>
          {showAverage && average && (
            <p className="text-sm text-gray-400">
              Average: <span className="text-primary-300 font-bold">{average.toFixed(0)} bpm</span>
            </p>
          )}
        </div>
      </div>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorHeartRate" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="time" 
              stroke="#9ca3af"
              fontSize={12}
            />
            <YAxis 
              stroke="#9ca3af"
              fontSize={12}
              label={{ 
                value: 'Heart Rate (bpm)', 
                angle: -90, 
                position: 'insideLeft',
                style: { fill: '#9ca3af' }
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="heartRate"
              stroke="#0ea5e9"
              fillOpacity={1}
              fill="url(#colorHeartRate)"
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="heartRate"
              stroke="#0ea5e9"
              strokeWidth={2}
              dot={{ r: 4, fill: "#0ea5e9" }}
              activeDot={{ r: 6, fill: "#fff", stroke: "#0ea5e9", strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default HeartRateChart;