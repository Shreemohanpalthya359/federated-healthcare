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
  Heart
} from 'lucide-react';

const Landing = () => {
  const features = [
    {
      icon: <Lock className="w-6 h-6" />,
      title: 'Privacy First',
      description: 'Federated learning ensures patient data never leaves their device',
      color: 'from-cyan-500 to-blue-500'
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: 'Adaptive AI',
      description: 'Real-time concept drift detection and model adaptation',
      color: 'from-emerald-500 to-green-500'
    },
    {
      icon: <Activity className="w-6 h-6" />,
      title: 'Real-time Monitoring',
      description: 'Continuous health tracking with instant alerts',
      color: 'from-violet-500 to-purple-500'
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: 'High Accuracy',
      description: 'Specialized models for different user categories',
      color: 'from-orange-500 to-amber-500'
    }
  ];

  const stats = [
    { value: '99.2%', label: 'Privacy Protection', icon: <Shield /> },
    { value: '94.8%', label: 'Prediction Accuracy', icon: <TrendingUp /> },
    { value: '3s', label: 'Response Time', icon: <Zap /> },
    { value: '1M+', label: 'Models Trained', icon: <Users /> }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-900/10 via-transparent to-cyan-900/10" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl" />

        <div className="container mx-auto px-4 py-20 relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center max-w-4xl mx-auto"
          >
            <div className="inline-flex items-center space-x-3 px-4 py-2 bg-primary-500/10 border border-primary-500/30 rounded-full mb-6">
              <Heart className="w-4 h-4 text-primary-400" />
              <span className="text-sm text-primary-300 font-medium">
                AI-Powered Healthcare
              </span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="gradient-text">Federated HeartCare</span>
              <br />
              <span className="text-gray-100">Predictive Intelligence</span>
            </h1>

            <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
              A privacy-preserving AI system for heart disease prediction that adapts to 
              individual lifestyles while keeping sensitive health data secure.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Link
                to="/predict"
                className="px-6 py-3 bg-gradient-to-r from-primary-600 to-cyan-600 text-white font-semibold rounded-xl hover:from-primary-700 hover:to-cyan-700 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <Brain className="w-5 h-5" />
                <span>Start Prediction</span>
              </Link>
              <Link
                to="/monitor"
                className="px-6 py-3 bg-gray-800/50 border border-gray-700 text-gray-300 font-semibold rounded-xl hover:bg-gray-800 hover:border-gray-600 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <Activity className="w-5 h-5" />
                <span>Live Monitor</span>
              </Link>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-20">
              {stats.map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="backdrop-blur-lg bg-white/5 border border-white/10 p-6 rounded-2xl text-center"
                >
                  <div className="inline-flex p-3 rounded-xl bg-gradient-to-br from-primary-600/20 to-cyan-600/20 mb-4">
                    <div className="text-primary-400">
                      {stat.icon}
                    </div>
                  </div>
                  <div className="text-3xl font-bold bg-gradient-to-r from-primary-400 to-cyan-400 bg-clip-text text-transparent mb-2">
                    {stat.value}
                  </div>
                  <div className="text-sm text-gray-400">
                    {stat.label}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">
              <span className="bg-gradient-to-r from-primary-400 to-cyan-400 bg-clip-text text-transparent">Advanced Features</span>
            </h2>
            <p className="text-gray-400 text-lg">
              Cutting-edge technology for modern healthcare
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 + 0.3 }}
                className="backdrop-blur-lg bg-white/5 border border-white/10 p-6 rounded-2xl transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl"
              >
                <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${feature.color} mb-4`}>
                  <div className="text-white">
                    {feature.icon}
                  </div>
                </div>
                <h3 className="text-xl font-bold text-gray-100 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-400">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="backdrop-blur-lg bg-white/5 border border-white/10 rounded-3xl p-8 md:p-12 text-center max-w-4xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to revolutionize healthcare?
            </h2>
            <p className="text-gray-400 text-lg mb-8">
              Join thousands of healthcare providers using Federated HeartCare 
              to deliver personalized, privacy-preserving care.
            </p>
            <Link
              to="/predict"
              className="px-6 py-3 bg-gradient-to-r from-primary-600 to-cyan-600 text-white font-semibold rounded-xl hover:from-primary-700 hover:to-cyan-700 transition-all duration-300 inline-flex items-center space-x-2"
            >
              <Brain className="w-5 h-5" />
              <span>Get Started Free</span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Landing;