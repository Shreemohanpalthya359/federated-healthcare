import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  Shield, 
  Brain, 
  Activity, 
  Zap, 
  TrendingUp,
  Users,
  Lock,
  Heart,
  ChevronRight,
  Database,
  Globe,
  Server
} from 'lucide-react';

const Landing = () => {
  const features = [
    {
      icon: <Lock className="w-6 h-6" />,
      title: 'Federated Privacy',
      description: 'Patient data stays on local devices. Only model updates are shared globally.',
      color: 'from-cyan-500 to-blue-500'
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: 'Adaptive AI Core',
      description: 'Self-learning models that adapt to concept drift and changing patient patterns.',
      color: 'from-emerald-500 to-green-500'
    },
    {
      icon: <Activity className="w-6 h-6" />,
      title: 'Real-time Vitals',
      description: 'Continuous monitoring stream with millisecond-latency anomaly detection.',
      color: 'from-violet-500 to-purple-500'
    },
    {
      icon: <Database className="w-6 h-6" />,
      title: 'Decentralized Data',
      description: 'Distributed ledger technology ensuring data integrity and audit trails.',
      color: 'from-orange-500 to-amber-500'
    }
  ];

  const stats = [
    { value: '99.9%', label: 'Uptime', icon: <Server /> },
    { value: '98.2%', label: 'Accuracy', icon: <TrendingUp /> },
    { value: '<50ms', label: 'Latency', icon: <Zap /> },
    { value: '256-bit', label: 'Encryption', icon: <Shield /> }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-white selection:bg-primary-500/30">
      {/* Background Gradients */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary-600/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-cyan-600/10 rounded-full blur-[128px]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />
      </div>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="container mx-auto px-4 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="text-center max-w-5xl mx-auto"
          >
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full mb-8 backdrop-blur-md">
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="text-xs font-medium text-gray-300 tracking-wide">SYSTEM OPERATIONAL</span>
            </div>

            <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold mb-8 tracking-tight leading-tight">
              The Future of <br />
              <span className="bg-gradient-to-r from-primary-400 via-cyan-400 to-primary-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient">
                Connected Health
              </span>
            </h1>

            <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed">
              Experience the next generation of healthcare analytics. 
              Secure, decentralized, and powered by advanced federated learning algorithms.
            </p>

            <div className="flex flex-col sm:flex-row gap-5 justify-center items-center">
              <Link
                to="/login"
                className="group relative px-8 py-4 bg-white text-black font-bold rounded-xl overflow-hidden transition-all hover:scale-105 active:scale-95"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-primary-400 to-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <div className="relative flex items-center space-x-2">
                  <span>Access Dashboard</span>
                  <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
              
              <Link
                to="/signup"
                className="px-8 py-4 bg-white/5 border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 transition-all hover:scale-105 active:scale-95 backdrop-blur-sm"
              >
                Create Account
              </Link>
            </div>
          </motion.div>

          {/* Dashboard Preview / Floating Cards */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="mt-24 relative"
          >
            <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0c] via-transparent to-transparent z-10" />
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
              {/* Card 1 */}
              <div className="bg-gray-900/50 border border-white/10 rounded-2xl p-6 backdrop-blur-md transform md:translate-y-12">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 bg-red-500/20 rounded-lg">
                    <Activity className="w-6 h-6 text-red-500" />
                  </div>
                  <span className="text-green-400 text-xs font-bold bg-green-500/10 px-2 py-1 rounded">+2.4%</span>
                </div>
                <div className="text-3xl font-bold text-white mb-1">98 BPM</div>
                <div className="text-sm text-gray-500">Average Heart Rate</div>
                <div className="mt-4 h-16 flex items-end space-x-1">
                  {[40, 60, 45, 70, 50, 80, 60, 90, 75, 50].map((h, i) => (
                    <div key={i} style={{ height: `${h}%` }} className="flex-1 bg-gray-700 rounded-t-sm hover:bg-red-500 transition-colors" />
                  ))}
                </div>
              </div>

              {/* Card 2 - Main Center */}
              <div className="bg-gray-800/80 border border-primary-500/30 rounded-2xl p-8 backdrop-blur-xl shadow-2xl shadow-primary-900/20 relative z-20">
                <div className="flex items-center space-x-4 mb-6">
                  <div className="h-12 w-12 rounded-full bg-gradient-to-r from-primary-500 to-cyan-500 flex items-center justify-center">
                    <Brain className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white">Model Confidence</h3>
                    <p className="text-sm text-gray-400">Real-time Inference</p>
                  </div>
                </div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400">Accuracy</span>
                  <span className="text-white font-bold">94.8%</span>
                </div>
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden mb-6">
                  <div className="h-full w-[94.8%] bg-gradient-to-r from-primary-500 to-cyan-500" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-900/50 rounded-xl p-3 text-center">
                    <div className="text-2xl font-bold text-white">1.2s</div>
                    <div className="text-xs text-gray-500">Inference Time</div>
                  </div>
                  <div className="bg-gray-900/50 rounded-xl p-3 text-center">
                    <div className="text-2xl font-bold text-white">Local</div>
                    <div className="text-xs text-gray-500">Processing</div>
                  </div>
                </div>
              </div>

              {/* Card 3 */}
              <div className="bg-gray-900/50 border border-white/10 rounded-2xl p-6 backdrop-blur-md transform md:translate-y-12">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 bg-blue-500/20 rounded-lg">
                    <Shield className="w-6 h-6 text-blue-500" />
                  </div>
                  <span className="text-blue-400 text-xs font-bold bg-blue-500/10 px-2 py-1 rounded">SECURE</span>
                </div>
                <div className="text-3xl font-bold text-white mb-1">Encrypted</div>
                <div className="text-sm text-gray-500">Data Transmission</div>
                <div className="mt-4 space-y-2">
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <span>Protocol</span>
                    <span className="text-white">TLS 1.3</span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <span>Status</span>
                    <span className="text-green-400">Active</span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <span>Keys</span>
                    <span className="text-white">Rotated</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 border-y border-white/5 bg-white/[0.02]">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center group cursor-default">
                <div className="inline-flex p-4 rounded-2xl bg-white/5 mb-4 group-hover:scale-110 group-hover:bg-primary-500/20 transition-all duration-300">
                  <div className="text-gray-400 group-hover:text-primary-400 transition-colors">
                    {stat.icon}
                  </div>
                </div>
                <div className="text-4xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-sm text-gray-500 uppercase tracking-wider">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-20">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">Enterprise-Grade Architecture</h2>
            <p className="text-gray-400 text-lg">
              Built on advanced federated learning principles to ensure scalability, 
              security, and performance at every level.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                whileHover={{ y: -5 }}
                className="group p-8 rounded-3xl bg-gray-900/50 border border-white/5 hover:border-primary-500/30 transition-all duration-300"
              >
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6 shadow-lg`}>
                  <div className="text-white">
                    {feature.icon}
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-primary-400 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/10 bg-black">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Heart className="w-6 h-6 text-primary-500" />
              <span className="text-xl font-bold text-white">Federated HeartCare</span>
            </div>
            <div className="text-gray-500 text-sm">
              © 2024 Federated Healthcare Systems. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
