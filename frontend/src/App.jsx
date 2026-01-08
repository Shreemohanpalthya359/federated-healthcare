import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Layout/Header';
import Landing from './pages/Landing';
import Predict from './pages/Predict';
import Model from './pages/Model';
import LiveMonitor from './components/LiveMonitor';  // Add this import

function App() {
  return (
    <div className="min-h-screen bg-gray-950">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/predict" element={<Predict />} />
          <Route path="/model" element={<Model />} />
          <Route path="/monitor" element={<LiveMonitor />} />  {/* Updated route */}
        </Routes>
      </main>
    </div>
  );
}

export default App;