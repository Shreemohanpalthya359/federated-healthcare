import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Layout/Header';
import Landing from './pages/Landing';
import Predict from './pages/Predict';
import Models from './pages/Models';

function App() {
  return (
    <div className="min-h-screen bg-gray-950">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/predict" element={<Predict />} />
          <Route path="/models" element={<Models />} />
          <Route path="/monitor" element={
            <div className="container mx-auto px-4 py-8 text-center">
              <h1 className="text-4xl font-bold gradient-text mb-4">Live Monitor</h1>
              <p className="text-gray-400">Coming soon...</p>
            </div>
          } />
        </Routes>
      </main>
    </div>
  );
}

export default App;