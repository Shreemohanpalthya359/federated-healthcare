import React from 'react';
import { AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react';

const RiskIndicator = ({ level, probability, showIcon = true }) => {
  const getRiskConfig = () => {
    switch (level?.toLowerCase()) {
      case 'low':
        return {
          color: 'health-low',
          bgColor: 'bg-green-500/10',
          borderColor: 'border-green-500/30',
          textColor: 'text-green-300',
          icon: <CheckCircle className="w-5 h-5" />,
          label: 'Low Risk',
          gradient: 'from-green-500 to-emerald-500'
        };
      case 'moderate':
        return {
          color: 'health-moderate',
          bgColor: 'bg-yellow-500/10',
          borderColor: 'border-yellow-500/30',
          textColor: 'text-yellow-300',
          icon: <AlertCircle className="w-5 h-5" />,
          label: 'Moderate Risk',
          gradient: 'from-yellow-500 to-amber-500'
        };
      case 'high':
        return {
          color: 'health-high',
          bgColor: 'bg-red-500/10',
          borderColor: 'border-red-500/30',
          textColor: 'text-red-300',
          icon: <AlertTriangle className="w-5 h-5" />,
          label: 'High Risk',
          gradient: 'from-red-500 to-rose-500'
        };
      default:
        return {
          color: 'health-low',
          bgColor: 'bg-gray-500/10',
          borderColor: 'border-gray-500/30',
          textColor: 'text-gray-300',
          icon: null,
          label: 'Unknown',
          gradient: 'from-gray-500 to-gray-600'
        };
    }
  };

  const config = getRiskConfig();

  return (
    <div className={`inline-flex items-center space-x-3 px-4 py-3 rounded-xl ${config.bgColor} ${config.borderColor} border`}>
      {showIcon && config.icon && (
        <div className={config.textColor}>
          {config.icon}
        </div>
      )}
      
      <div>
        <div className="flex items-center space-x-3">
          <span className={`font-bold ${config.textColor}`}>
            {config.label}
          </span>
          {probability !== undefined && (
            <div className="flex items-center space-x-2">
              <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className={`h-full bg-gradient-to-r ${config.gradient} rounded-full transition-all duration-500`}
                  style={{ width: `${probability * 100}%` }}
                />
              </div>
              <span className="text-sm text-gray-400 font-mono">
                {(probability * 100).toFixed(1)}%
              </span>
            </div>
          )}
        </div>
        <p className="text-sm text-gray-400 mt-1">
          {level === 'low' && 'Continue regular checkups and maintain healthy lifestyle'}
          {level === 'moderate' && 'Consider consulting a healthcare provider'}
          {level === 'high' && 'Recommend immediate medical consultation'}
        </p>
      </div>
    </div>
  );
};

export default RiskIndicator;