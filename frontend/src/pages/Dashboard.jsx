import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import StatCard from '../components/StatCard';
import FileUpload from '../components/FileUpload';
import GraphVisualizer from '../components/GraphVisualizer';
import Button from '../components/Button';
import Loader from '../components/Loader';
import { uploadFile, getGraphDataForAccount } from '../services/api';
import '../assets/Dashboard.css';

// Import icons
import { FaFileCsv, FaExclamationTriangle, FaCheckCircle, FaProjectDiagram } from 'react-icons/fa';

const Dashboard = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileUpload = (file) => {
    setSelectedFile(file);
    setAnalysisResult(null);
    setGraphData(null);
    setError('');
  };

  const handleAnalyzeClick = async () => {
    if (!selectedFile) {
      setError('Please upload a file first.');
      return;
    }
    setIsLoading(true);
    setError('');
    
    try {
      // Step 1: Upload the file
      const uploadResponse = await uploadFile(selectedFile);
      
      // Step 2: Fetch graph data for a default/example account
      // In a real app, you'd have a way to select an account
      const exampleAccountId = 'C12345678'; // Placeholder
      const graphResponse = await getGraphDataForAccount(exampleAccountId);
      setGraphData(graphResponse);

      // Mock analysis result based on upload
      setAnalysisResult({
        fileName: uploadResponse.filename,
        transactions: 15032, // Mock data
        suspicious: 42,      // Mock data
        modelAccuracy: "99.87%" // Mock data
      });

    } catch (err) {
      setError('An error occurred during analysis. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <Navbar />
      <main className="dashboard-content">
        <header className="dashboard-header">
          <h2>AML Transaction Analysis Dashboard</h2>
          <p>Upload transaction data to detect suspicious activities and visualize networks.</p>
        </header>

        <div className="stats-grid">
          <StatCard title="Transactions Processed" value={analysisResult ? analysisResult.transactions : 'N/A'} icon={<FaFileCsv />} />
          <StatCard title="Suspicious Activities" value={analysisResult ? analysisResult.suspicious : 'N/A'} icon={<FaExclamationTriangle />} />
          <StatCard title="Model F1-Score" value={analysisResult ? analysisResult.modelAccuracy : 'N/A'} icon={<FaCheckCircle />} />
          <StatCard title="Patterns Detected" value={graphData ? 'Cycles, Fan-out' : 'N/A'} icon={<FaProjectDiagram />} />
        </div>

        <div className="core-section">
          <div className="upload-analysis-panel">
            <h3>1. Upload & Analyze</h3>
            <FileUpload onFileUpload={handleFileUpload} />
            <Button onClick={handleAnalyzeClick} disabled={isLoading}>
              {isLoading ? 'Analyzing...' : 'Start Analysis'}
            </Button>
            {error && <p className="error-message">{error}</p>}
          </div>

          <div className="graph-panel">
            <h3>2. Transaction Graph</h3>
            <div className="graph-wrapper">
              {isLoading && <Loader />}
              {graphData ? (
                <GraphVisualizer data={graphData} />
              ) : (
                <div className="placeholder-graph">
                  <FaProjectDiagram size={60} />
                  <p>Graph visualization will appear here after analysis.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
