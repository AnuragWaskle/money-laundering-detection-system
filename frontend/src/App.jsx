<<<<<<< HEAD
import React, { useState } from 'react';
import Navbar from './components/Navbar';
import FileUpload from './components/FileUpload';
import StatCard from './components/StatCard';
import GraphVisualizer from './components/GraphVisualizer';
import Loader from './components/Loader';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleFileUpload = async (file) => {
    setUploadedFile(file);
    setIsLoading(true);
    
    try {
      // Simulate API call for now
      setTimeout(() => {
        setAnalysisData({
          totalTransactions: 1250,
          suspiciousTransactions: 47,
          riskScore: 0.73,
          networkNodes: 156
        });
        setIsLoading(false);
      }, 2000);
    } catch (error) {
      console.error('Error processing file:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="app" style={{ minHeight: '100vh', background: '#0a0a14' }}>
      <Navbar />
      
      <main style={{ padding: '2rem' }}>
        {/* Hero Section */}
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1 style={{ 
            fontSize: '3rem', 
            color: '#00f2ff', 
            marginBottom: '1rem',
            fontWeight: '700'
          }}>
            Money Laundering Detection System
          </h1>
          <p style={{ 
            fontSize: '1.2rem', 
            color: '#e0e0e0', 
            maxWidth: '600px', 
            margin: '0 auto',
            opacity: 0.8
          }}>
            Advanced AI-powered financial transaction analysis using machine learning and graph networks
          </p>
        </div>

        {/* File Upload Section */}
        <div style={{ marginBottom: '3rem' }}>
          <FileUpload onFileUpload={handleFileUpload} />
        </div>

        {/* Loading State */}
        {isLoading && (
          <div style={{ textAlign: 'center', margin: '3rem 0' }}>
            <Loader />
            <p style={{ color: '#00f2ff', marginTop: '1rem' }}>
              Analyzing transactions and building knowledge graph...
            </p>
          </div>
        )}

        {/* Analysis Results */}
        {analysisData && !isLoading && (
          <div>
            {/* Statistics Cards */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '1.5rem',
              marginBottom: '3rem'
            }}>
              <StatCard 
                title="Total Transactions" 
                value={analysisData.totalTransactions.toLocaleString()}
                icon="📊"
              />
              <StatCard 
                title="Suspicious Transactions" 
                value={analysisData.suspiciousTransactions}
                icon="⚠️"
                highlight={true}
              />
              <StatCard 
                title="Risk Score" 
                value={`${(analysisData.riskScore * 100).toFixed(1)}%`}
                icon="🎯"
                highlight={analysisData.riskScore > 0.7}
              />
              <StatCard 
                title="Network Nodes" 
                value={analysisData.networkNodes}
                icon="🌐"
              />
            </div>

            {/* Graph Visualization */}
            <div style={{ marginBottom: '3rem' }}>
              <h2 style={{ 
                color: '#00f2ff', 
                marginBottom: '1.5rem',
                fontSize: '1.8rem',
                fontWeight: '600'
              }}>
                Transaction Network Analysis
              </h2>
              <GraphVisualizer data={analysisData} />
            </div>
          </div>
        )}

        {/* Welcome State */}
        {!uploadedFile && !isLoading && (
          <div style={{ 
            textAlign: 'center', 
            background: 'rgba(0, 242, 255, 0.05)',
            border: '1px solid rgba(0, 242, 255, 0.2)',
            borderRadius: '12px',
            padding: '3rem',
            margin: '2rem auto',
            maxWidth: '800px'
          }}>
            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🔍</div>
            <h2 style={{ color: '#00f2ff', marginBottom: '1rem' }}>
              Get Started with AML Detection
            </h2>
            <p style={{ color: '#e0e0e0', marginBottom: '2rem', opacity: 0.8 }}>
              Upload your financial transaction data to begin analysis. Our system supports CSV, Excel, and JSON formats.
            </p>
            <ul style={{ 
              color: '#e0e0e0', 
              textAlign: 'left', 
              maxWidth: '500px', 
              margin: '0 auto',
              opacity: 0.7
            }}>
              <li style={{ marginBottom: '0.5rem' }}>✓ Automated suspicious transaction detection</li>
              <li style={{ marginBottom: '0.5rem' }}>✓ Interactive network graph visualization</li>
              <li style={{ marginBottom: '0.5rem' }}>✓ Risk scoring and compliance reporting</li>
              <li>✓ Real-time analysis with machine learning</li>
            </ul>
          </div>
        )}
      </main>
=======
import React from 'react';
import Dashboard from './pages/Dashboard';
import './index.css'; // Importing global styles

function App() {
  return (
    <div className="App">
      <Dashboard />
>>>>>>> 34f40f9e006e9535e4d203671532bba432ab719a
    </div>
  );
}

<<<<<<< HEAD
export default App;
=======
export default App;
>>>>>>> 34f40f9e006e9535e4d203671532bba432ab719a
