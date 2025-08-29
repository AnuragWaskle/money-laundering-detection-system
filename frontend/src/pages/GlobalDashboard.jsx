import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import StatCard from '../components/StatCard';
import { FaGlobeAmericas, FaExclamationTriangle, FaBriefcase, FaChartLine } from 'react-icons/fa';
import '../assets/GlobalDashboard.css';

const GlobalDashboard = () => {
  // Mock data for the dashboard widgets
  const [stats, setStats] = useState({
    monitoredTransactions: '1,250,432',
    suspiciousToday: '128',
    highRiskAccounts: '72',
    openCases: '4'
  });

  const [alerts, setAlerts] = useState([
    { id: 'TRX-998', risk: 99, reason: 'High-value transfer to offshore haven.' },
    { id: 'TRX-997', risk: 96, reason: 'Account C50505050 involved in a GNN-flagged pattern.' },
    { id: 'TRX-996', risk: 94, reason: 'Anomalous transaction amount for account C100100100.' },
  ]);

  return (
    <div className="global-dashboard-page">
      <Navbar />
      <main className="global-content">
        <header className="global-header">
          <h1>Global Risk Dashboard</h1>
          <p>A strategic overview of monitored financial activities and emerging threats.</p>
        </header>

        <div className="stats-grid">
          <StatCard title="Monitored Transactions" value={stats.monitoredTransactions} icon={<FaChartLine />} />
          <StatCard title="Suspicious Today" value={stats.suspiciousToday} icon={<FaExclamationTriangle />} />
          <StatCard title="Active High-Risk Accounts" value={stats.highRiskAccounts} icon={<FaGlobeAmericas />} />
          <StatCard title="Open Cases" value={stats.openCases} icon={<FaBriefcase />} />
        </div>

        <div className="dashboard-widgets">
          <div className="widget-container heatmap-container">
            <h3>High-Risk Corridors</h3>
            <div className="heatmap-placeholder">
              <FaGlobeAmericas size={100} />
              <p>World heatmap visualization of money flow would appear here.</p>
            </div>
          </div>
          <div className="widget-container alerts-container">
            <h3>Live Alerts Feed</h3>
            <div className="alerts-feed">
              {alerts.map(alert => (
                <div key={alert.id} className="alert-item">
                  <div className="alert-risk-score">{alert.risk}%</div>
                  <div className="alert-details">
                    <strong>{alert.id}</strong>
                    <p>{alert.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default GlobalDashboard;
