import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Heart, 
  Shield, 
  Brain, 
  Activity, 
  Menu, 
  X,
  Settings,
  User,
  Bell,
  LogOut,
  LogIn
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsMenuOpen(false);
  };

  const navItems = user ? [
    { path: '/predict', label: 'Predict', icon: Brain },
    { path: '/models', label: 'Models', icon: Shield },
    { path: '/monitor', label: 'Monitor', icon: Heart },
  ] : [
    { path: '/', label: 'Dashboard', icon: Activity },
    { path: '/login', label: 'Login', icon: LogIn },
    { path: '/signup', label: 'Sign Up', icon: User },
  ];

  return (
    <header className="sticky top-0 z-50 glass border-b border-white/10">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-primary-600 to-cyan-600 rounded-lg blur opacity-30 group-hover:opacity-50 transition duration-300"></div>
              <div className="relative bg-gradient-to-r from-primary-600 to-cyan-600 p-2 rounded-lg">
                <Heart className="w-6 h-6 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">Federated HeartCare</h1>
              <p className="text-xs text-gray-400">Privacy-Powered AI</p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-300 ${
                    isActive
                      ? 'bg-gradient-to-r from-primary-600/20 to-cyan-600/20 text-primary-300 border border-primary-500/30'
                      : 'text-gray-400 hover:text-gray-300 hover:bg-gray-800/50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* User Actions */}
          <div className="flex items-center space-x-3">
            {user ? (
              <>
                <button className="p-2 text-gray-400 hover:text-gray-300 hover:bg-gray-800/50 rounded-lg transition-all">
                  <Bell className="w-5 h-5" />
                </button>
                <Link 
                  to="/settings"
                  className="p-2 text-gray-400 hover:text-gray-300 hover:bg-gray-800/50 rounded-lg transition-all"
                >
                  <Settings className="w-5 h-5" />
                </Link>
                <div className="flex items-center space-x-2 px-3 py-2 bg-gray-800/50 hover:bg-gray-800 rounded-lg transition-all">
                  <User className="w-4 h-4" />
                  <span className="text-sm font-medium">{user.name || 'User'}</span>
                </div>
                <button 
                  onClick={handleLogout}
                  className="p-2 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition-all"
                  title="Logout"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </>
            ) : (
              <div className="hidden md:block">
                 {/* Only show on desktop, mobile has links in menu */}
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 text-gray-400 hover:text-gray-300 hover:bg-gray-800/50 rounded-lg transition-all"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-white/10">
            <div className="flex flex-col space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMenuOpen(false)}
                    className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                      isActive
                        ? 'bg-primary-600/10 text-primary-400 border border-primary-500/20'
                        : 'text-gray-400 hover:bg-gray-800/50'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
              {user && (
                 <button
                    onClick={handleLogout}
                    className="flex items-center space-x-3 px-4 py-3 rounded-lg text-red-400 hover:bg-red-900/20 transition-all w-full text-left"
                  >
                    <LogOut className="w-5 h-5" />
                    <span className="font-medium">Logout</span>
                  </button>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
