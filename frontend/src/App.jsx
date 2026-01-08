import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Header from './components/Layout/Header';
import Landing from './pages/Landing';
import Predict from './pages/Predict';
import Model from './pages/model';
import LiveMonitor from './components/LiveMonitor';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Settings from './pages/Settings';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  const location = useLocation();
  // We want to hide the main header on login/signup pages to keep them focused
  const isAuthPage = location.pathname === '/login' || location.pathname === '/signup';

  return (
    <div className="min-h-screen bg-gray-950">
      {!isAuthPage && <Header />}
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          
          {/* Protected Routes */}
          <Route path="/predict" element={
            <ProtectedRoute>
              <Predict />
            </ProtectedRoute>
          } />
          <Route path="/model" element={
            <ProtectedRoute>
              <Model />
            </ProtectedRoute>
          } />
          <Route path="/monitor" element={
            <ProtectedRoute>
              <LiveMonitor />
            </ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } />
        </Routes>
      </main>
    </div>
  );
}

export default App;