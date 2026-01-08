import React from 'react';
import { Cpu, Shield, Zap, Activity, TrendingUp } from 'lucide-react';

const Models = () => {
  const models = [
    { type: 'federated', label: 'Federated', icon: <Shield />, accuracy: '94.8%', samples: '10K', color: 'from-cyan-500 to-blue-500' },
    { type: 'athletic', label: 'Athletic', icon: <Zap />, accuracy: '96.2%', samples: '2.5K', color: 'from-emerald-500 to-green-500' },
    { type: 'diver', label: 'Diver', icon: <Activity />, accuracy: '92.1%', samples: '1.8K', color: 'from-violet-500 to-purple-500' },
    { type: 'typical', label: 'Typical', icon: <Cpu />, accuracy: '93.5%', samples: '8.5K', color: 'from-orange-500 to-amber-500' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-400 to-cyan-400 bg-clip-text text-transparent mb-2">
            AI Models Dashboard
          </h1>
          <p className="text-gray-400">
            Monitor and manage specialized heart disease prediction models
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            { label: 'Overall Accuracy', value: '94.8%', icon: <TrendingUp /> },
            { label: 'Privacy Score', value: '99.2%', icon: <Shield /> },
            { label: 'Response Time', value: '3.2s', icon: <Zap /> },
            { label: 'Active Models', value: '4', icon: <Cpu /> }
          ].map((stat, index) => (
            <div key={index} className="backdrop-blur-lg bg-white/5 border border-white/10 p-6 rounded-2xl">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-primary-500/20 rounded-lg">
                  <div className="text-primary-400">
                    {stat.icon}
                  </div>
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-100">{stat.value}</p>
                  <p className="text-sm text-gray-400">{stat.label}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {models.map((model) => (
            <div key={model.type} className="backdrop-blur-lg bg-white/5 border border-white/10 p-6 rounded-2xl">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${model.color}`}>
                    <div className="text-white">
                      {model.icon}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-100">{model.label} Model</h3>
                    <p className="text-sm text-gray-400">Specialized AI Model</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-primary-300">{model.accuracy}</div>
                  <div className="text-sm text-gray-400">Accuracy</div>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Training Samples</span>
                  <span className="text-gray-300">{model.samples}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Last Updated</span>
                  <span className="text-gray-300">2 days ago</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Drift Status</span>
                  <span className="text-green-400">Stable</span>
                </div>
              </div>

              <div className="mt-6">
                <button className="w-full py-2 bg-primary-500/20 text-primary-300 rounded-lg hover:bg-primary-500/30 transition-colors">
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Models;