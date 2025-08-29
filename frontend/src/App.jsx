import React from 'react';
<<<<<<< HEAD
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import GlobalDashboard from './pages/GlobalDashboard';
import CaseManagement from './pages/CaseManagement';
import TraceAndInvestigate from './pages/TraceAndInvestigate';
import './index.css';

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/global-dashboard" element={<GlobalDashboard />} />
          <Route path="/case-management" element={<CaseManagement />} />
          <Route path="/cases" element={<CaseManagement />} />
          <Route path="/trace" element={<TraceAndInvestigate />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
=======
import Dashboard from './pages/Dashboard';
import './index.css';
function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;
>>>>>>> 878aa4807e99ba5a524b32f89c231a7c1196f533
