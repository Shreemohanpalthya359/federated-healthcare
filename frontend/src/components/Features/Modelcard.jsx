import React from 'react';
import { Shield, Zap, Cpu, Lock, TrendingUp } from 'lucide-react';

const ModelCard = ({ model, isActive, onClick }) => {
  const getModelIcon = (type) => {
    switch (type) {
      case 'federated':
        return <Lock className="w-5 h-5" />;
      case 'athletic':
        return <Zap className="w-5 h-5" />;
      case 'diver':
        return <Shield className="w-5 h-5" />;
      case 'typical':
        return <Cpu className="w-5 h-5" />;
      default:
        return <Cpu className="w-5 h-5" />;
    }
  };

  const getModelColor = (type) => {
    switch (type) {
      case 'federated':
        return 'from-cyan-500 to-blue-500';
      case 'athletic':
        return 'from-emerald-500 to-green-500';
      case 'diver':
        return 'from-violet-500 to-purple-500';
      case 'typical':
        return 'from-orange-500 to-amber-500';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const getModelDescription = (type) => {
    switch (type) {
      case 'federated':
        return 'Privacy-preserving model trained across distributed data';
      case 'athletic':
        return 'Optimized for athletic individuals with active lifestyles';
      case 'diver':
        return 'Specialized for diving activities and underwater physiology';
      case 'typical':
        return 'General model for typical population patterns';
      default:
        return 'Machine learning model for heart disease prediction';
    }
  };

  return (
    <button
      onClick={onClick}
      className={`relative w-full text-left p-6 rounded-2xl transition-all duration-300 card-hover ${
        isActive
          ? 'bg-gradient-to-br from-gray-900 to-gray-800 border-2 border-primary-500/50'
          : 'glass hover:bg-gray-800/30'
      }`}
    >
      {/* Active indicator */}
      {isActive && (
        <div className="absolute -top-2 -right-2">
          <div className="relative">
            <div className="absolute animate-ping bg-primary-500 rounded-full w-4 h-4 opacity-75"></div>
            <div className="relative bg-primary-600 rounded-full w-4 h-4"></div>
          </div>
        </div>
      )}

      {/* Model Icon */}
      <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${getModelColor(model.type)} mb-4`}>
        {getModelIcon(model.type)}
      </div>

      {/* Model Info */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-bold text-gray-100 capitalize">
            {model.type} Model
          </h3>
          {model.accuracy && (
            <span className="text-sm font-semibold text-primary-300">
              {(model.accuracy * 100).toFixed(1)}%
            </span>
          )}
        </div>

        <p className="text-sm text-gray-400 mb-4">
          {getModelDescription(model.type)}
        </p>

        {/* Model Stats */}
        <div className="space-y-2">
          {model.samples && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Training Samples</span>
              <span className="text-gray-300 font-medium">{model.samples.toLocaleString()}</span>
            </div>
          )}
          
          {model.lastUpdated && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Last Updated</span>
              <span className="text-gray-300 font-medium">{model.lastUpdated}</span>
            </div>
          )}

          {model.driftDetected !== undefined && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Concept Drift</span>
              <span className={`font-medium ${model.driftDetected ? 'text-red-400' : 'text-green-400'}`}>
                {model.driftDetected ? 'Detected' : 'Stable'}
              </span>
            </div>
          )}
        </div>

        {/* Active Badge */}
        {isActive && (
          <div className="mt-4 inline-flex items-center space-x-2 px-3 py-1 bg-primary-500/20 text-primary-300 rounded-full text-sm">
            <TrendingUp className="w-3 h-3" />
            <span>Currently Active</span>
          </div>
        )}
      </div>
    </button>
  );
};

export default ModelCard;