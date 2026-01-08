import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  Bell, 
  Shield, 
  Lock, 
  Moon, 
  Globe, 
  Smartphone,
  LogOut,
  ChevronRight,
  Save,
  Key,
  Mail,
  Building2 as Hospital,
  Stethoscope
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Settings = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('account');
  const [loading, setLoading] = useState(false);

  // Simulated state for form fields
  const [profile, setProfile] = useState({
    name: user?.name || 'Dr. Smith',
    email: user?.email || 'doctor@hospital.com',
    specialty: 'Cardiology',
    hospital: 'General Hospital',
    phone: '+1 (555) 000-0000',
    bio: 'Experienced cardiologist specializing in preventative care and heart failure management.'
  });

  const [security, setSecurity] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    pushNotifications: false,
    weeklyReport: true,
    securityAlerts: true,
    patientUpdates: true,
    marketingEmails: false
  });

  const handleSave = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      // Show success message logic here
    }, 1000);
  };

  const tabs = [
    { id: 'account', label: 'Account Profile', icon: User },
    { id: 'security', label: 'Security & Password', icon: Lock },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'preferences', label: 'Preferences', icon: Globe },
  ];

  const InputField = ({ label, icon: Icon, type = 'text', value, onChange, placeholder, className = '' }) => (
    <div className={`space-y-2 ${className}`}>
      <label className="text-sm font-medium text-gray-400 ml-1">{label}</label>
      <div className="relative group">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-primary-400 transition-colors">
          <Icon className="w-4 h-4" />
        </div>
        <input
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-gray-600 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all"
        />
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'account':
        return (
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white mb-1">Personal Information</h2>
                <p className="text-gray-400 text-sm">Update your photo and personal details here.</p>
              </div>
              <button 
                onClick={handleSave}
                disabled={loading}
                className="flex items-center space-x-2 px-6 py-2.5 bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700 text-white font-medium rounded-xl transition-all shadow-lg shadow-primary-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Save className="w-4 h-4" />}
                <span>Save Changes</span>
              </button>
            </div>

            <div className="bg-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-2xl p-8">
              <div className="flex items-center space-x-6 mb-8 pb-8 border-b border-gray-700/50">
                <div className="relative group cursor-pointer">
                  <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center text-4xl font-bold text-white shadow-xl shadow-primary-500/20 group-hover:scale-105 transition-transform duration-300">
                    {profile.name.charAt(0)}
                  </div>
                  <div className="absolute inset-0 bg-black/40 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white font-medium text-xs">
                    Change
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{profile.name}</h3>
                  <p className="text-primary-400 text-sm mb-2">{profile.specialty}</p>
                  <p className="text-gray-500 text-xs">Max file size: 5MB (JPG, PNG)</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InputField 
                  label="Full Name" 
                  icon={User} 
                  value={profile.name} 
                  onChange={(e) => setProfile({...profile, name: e.target.value})} 
                />
                <InputField 
                  label="Email Address" 
                  icon={Mail} 
                  type="email"
                  value={profile.email} 
                  onChange={(e) => setProfile({...profile, email: e.target.value})} 
                />
                <InputField 
                  label="Medical Specialty" 
                  icon={Stethoscope} 
                  value={profile.specialty} 
                  onChange={(e) => setProfile({...profile, specialty: e.target.value})} 
                />
                <InputField 
                  label="Hospital / Organization" 
                  icon={Hospital} 
                  value={profile.hospital} 
                  onChange={(e) => setProfile({...profile, hospital: e.target.value})} 
                />
                <InputField 
                  label="Phone Number" 
                  icon={Smartphone} 
                  value={profile.phone} 
                  onChange={(e) => setProfile({...profile, phone: e.target.value})} 
                />
                
                <div className="col-span-1 md:col-span-2 space-y-2">
                  <label className="text-sm font-medium text-gray-400 ml-1">Professional Bio</label>
                  <textarea
                    value={profile.bio}
                    onChange={(e) => setProfile({...profile, bio: e.target.value})}
                    rows={4}
                    className="w-full bg-gray-900/50 border border-gray-700 rounded-xl p-4 text-white placeholder:text-gray-600 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all resize-none"
                    placeholder="Write a short bio..."
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 'security':
        return (
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white mb-1">Security Settings</h2>
                <p className="text-gray-400 text-sm">Manage your password and security preferences.</p>
              </div>
              <button 
                onClick={handleSave}
                disabled={loading}
                className="flex items-center space-x-2 px-6 py-2.5 bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700 text-white font-medium rounded-xl transition-all shadow-lg shadow-primary-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Save className="w-4 h-4" />}
                <span>Update Password</span>
              </button>
            </div>

            <div className="bg-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-2xl p-8 space-y-8">
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-white border-b border-gray-700/50 pb-4">Change Password</h3>
                <div className="max-w-md space-y-4">
                  <InputField 
                    label="Current Password" 
                    icon={Key} 
                    type="password"
                    value={security.currentPassword} 
                    onChange={(e) => setSecurity({...security, currentPassword: e.target.value})}
                    placeholder="••••••••"
                  />
                  <InputField 
                    label="New Password" 
                    icon={Lock} 
                    type="password"
                    value={security.newPassword} 
                    onChange={(e) => setSecurity({...security, newPassword: e.target.value})}
                    placeholder="Min 8 characters"
                  />
                  <InputField 
                    label="Confirm New Password" 
                    icon={Shield} 
                    type="password"
                    value={security.confirmPassword} 
                    onChange={(e) => setSecurity({...security, confirmPassword: e.target.value})}
                    placeholder="Confirm new password"
                  />
                </div>
              </div>

              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-white border-b border-gray-700/50 pb-4">Two-Factor Authentication</h3>
                <div className="flex items-center justify-between py-2">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-primary-500/10 rounded-xl">
                      <Smartphone className="w-6 h-6 text-primary-400" />
                    </div>
                    <div>
                      <h4 className="text-white font-medium">Authenticator App</h4>
                      <p className="text-sm text-gray-400">Secure your account with 2FA.</p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        );

      case 'notifications':
        return (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-white mb-1">Notification Preferences</h2>
              <p className="text-gray-400 text-sm">Choose what updates you want to receive.</p>
            </div>
            
            <div className="bg-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-2xl p-8 space-y-4">
              {Object.entries(notifications).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between py-4 border-b border-gray-700/50 last:border-0 hover:bg-gray-800/30 px-4 -mx-4 rounded-lg transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg ${value ? 'bg-primary-500/10' : 'bg-gray-800'}`}>
                      <Bell className={`w-5 h-5 ${value ? 'text-primary-400' : 'text-gray-500'}`} />
                    </div>
                    <div>
                      <h3 className="text-white font-medium capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</h3>
                      <p className="text-sm text-gray-400">Receive updates about {key.toLowerCase().replace(/([A-Z])/g, ' $1').trim()}</p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={value}
                      onChange={() => setNotifications({...notifications, [key]: !value})}
                      className="sr-only peer" 
                    />
                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400">
            <Globe className="w-16 h-16 mb-4 opacity-20" />
            <p className="text-lg">Additional preferences coming soon...</p>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Sidebar */}
            <div className="w-full lg:w-72 flex-shrink-0">
              <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-4 sticky top-24 backdrop-blur-xl">
                <div className="px-4 py-4 mb-4 border-b border-gray-800">
                  <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider">Settings Menu</h3>
                </div>
                <nav className="space-y-1">
                  {tabs.map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`w-full flex items-center justify-between px-4 py-3.5 rounded-xl transition-all group ${
                          activeTab === tab.id
                            ? 'bg-primary-600/10 text-primary-400 border border-primary-500/20'
                            : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <Icon className={`w-5 h-5 ${activeTab === tab.id ? 'text-primary-400' : 'text-gray-500 group-hover:text-gray-400'}`} />
                          <span className="font-medium">{tab.label}</span>
                        </div>
                        {activeTab === tab.id && (
                          <motion.div
                            layoutId="activeTabIndicator"
                            className="w-1.5 h-1.5 rounded-full bg-primary-500"
                          />
                        )}
                      </button>
                    );
                  })}
                </nav>

                <div className="mt-8 pt-8 border-t border-gray-800 px-4">
                  <div className="flex items-center justify-between text-gray-400 mb-6 group cursor-pointer hover:text-white transition-colors">
                    <div className="flex items-center space-x-3">
                      <Moon className="w-5 h-5" />
                      <span className="text-sm font-medium">Dark Mode</span>
                    </div>
                    <div className="text-xs bg-primary-500/20 text-primary-400 px-2 py-0.5 rounded-full">On</div>
                  </div>
                  <div className="flex items-center justify-between text-gray-500">
                    <span className="text-xs">Version 1.0.2</span>
                    <span className="text-xs">Build 2024.01</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 min-w-0">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className="h-full"
              >
                {renderContent()}
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
