import React, { useState, useCallback } from 'react';
import Papa from 'papaparse';
import Navbar from '../components/Navbar';
import ControlPanel from '../components/ControlPanel';
import InfoPanel from '../components/InfoPanel';
import GraphVisualizer from '../components/GraphVisualizer';
import Loader from '../components/Loader';
import MappingModal from '../components/MappingModal';
import { uploadCsvFile, uploadPdfFile, getGraphDataForAccount, getAccountSummary, analyzeGraphWithGNN } from '../services/api';
import '../assets/Dashboard.css';
import { FaProjectDiagram } from 'react-icons/fa';

const Dashboard = () => {
  // State Management
  const [selectedFile, setSelectedFile] = useState(null);
  const [csvHeaders, setCsvHeaders] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [graphData, setGraphData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // State for the new interactive panels
  const [selectedNode, setSelectedNode] = useState(null);
  const [summary, setSummary] = useState('');
  const [gnnAnalysis, setGnnAnalysis] = useState(null);

  // --- Data Ingestion Logic ---
  const handleFileUpload = (file) => {
    if (!file) {
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
    if (file.type === 'text/csv') {
      Papa.parse(file, {
        preview: 1,
        complete: (results) => {
          setCsvHeaders(results.data[0]);
          setIsModalOpen(true);
        },
      });
    } else if (file.type === 'application/pdf') {
      processFile(() => uploadPdfFile(file));
    } else {
      setError('Unsupported file type.');
    }
  };

  const handleConfirmMapping = async (mapping) => {
    setIsModalOpen(false);
    if (!selectedFile) return;
    await processFile(() => uploadCsvFile(selectedFile, mapping));
  };

  const processFile = async (uploadFunction) => {
    setIsLoading(true);
    setError('');
    setGraphData(null);
    setSelectedNode(null);
    try {
      await uploadFunction();
      // After upload, automatically search for a default account to show a graph
      await handleSearch('C12345678'); 
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred during processing.');
    } finally {
      setIsLoading(false);
    }
  };

  // --- Graph Interaction Logic ---
  const handleSearch = useCallback(async (accountId) => {
    setIsLoading(true);
    setError('');
    setSelectedNode(null);
    try {
      const graphResponse = await getGraphDataForAccount(accountId);
      setGraphData(graphResponse);
    } catch (err) {
      setError(`Could not find account: ${accountId}`);
      setGraphData(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleNodeClick = useCallback(async (node) => {
    setSelectedNode(node);
    setSummary('');
    setGnnAnalysis(null);
    
    try {
      // Fetch summary and GNN analysis in parallel
      const [summaryRes, gnnRes] = await Promise.all([
        getAccountSummary(node.id),
        analyzeGraphWithGNN(node.id)
      ]);
      setSummary(summaryRes.summary);
      setGnnAnalysis(gnnRes);
    } catch (err) {
      console.error("Error fetching node details:", err);
      setSummary('Could not load summary.');
    }
  }, []);

  return (
    <div className="dashboard">
      <Navbar />
      <MappingModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        headers={csvHeaders}
        onConfirm={handleConfirmMapping}
      />
      <div className="main-layout">
        <ControlPanel onFileUpload={handleFileUpload} onSearch={handleSearch} />
        
        <main className="graph-main-panel">
          <h2>Transaction Network Explorer</h2>
          <div className="graph-wrapper">
            {isLoading && <Loader />}
            {error && !isLoading && <p className="error-message">{error}</p>}
            {graphData ? (
              <GraphVisualizer 
                data={graphData} 
                onNodeClick={handleNodeClick}
                selectedNodeId={selectedNode?.id}
              />
            ) : (
              !isLoading && (
                <div className="placeholder-graph">
                  <FaProjectDiagram size={60} />
                  <p>Search for an account or upload data to begin.</p>
                </div>
              )
            )}
          </div>
        </main>

        <InfoPanel 
          selectedNode={selectedNode}
          summary={summary}
          gnnAnalysis={gnnAnalysis}
        />
      </div>
    </div>
  );
};

export default Dashboard;
