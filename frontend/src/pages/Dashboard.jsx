// // import React, { useState, useCallback } from 'react';
// // import Papa from 'papaparse';
// // import Navbar from '../components/Navbar';
// // import ControlPanel from '../components/ControlPanel';
// // import InfoPanel from '../components/InfoPanel';
// // import GraphVisualizer from '../components/GraphVisualizer';
// // import Loader from '../components/Loader';
// // import MappingModal from '../components/MappingModal';
// // import { uploadCsvFile, uploadPdfFile, getGraphDataForAccount, getAccountSummary, analyzeGraphWithGNN } from '../services/api';
// // import '../assets/Dashboard.css';
// // import { FaProjectDiagram } from 'react-icons/fa';

// // const Dashboard = () => {
// //   // State Management
// //   const [selectedFile, setSelectedFile] = useState(null);
// //   const [csvHeaders, setCsvHeaders] = useState([]);
// //   const [isModalOpen, setIsModalOpen] = useState(false);
// //   const [graphData, setGraphData] = useState(null);
// //   const [isLoading, setIsLoading] = useState(false);
// //   const [error, setError] = useState('');

// //   // State for the new interactive panels
// //   const [selectedNode, setSelectedNode] = useState(null);
// //   const [summary, setSummary] = useState('');
// //   const [gnnAnalysis, setGnnAnalysis] = useState(null);

// //   // --- Data Ingestion Logic ---
// //   const handleFileUpload = (file) => {
// //     if (!file) {
// //       setSelectedFile(null);
// //       return;
// //     }
// //     setSelectedFile(file);
// //     if (file.type === 'text/csv') {
// //       Papa.parse(file, {
// //         preview: 1,
// //         complete: (results) => {
// //           setCsvHeaders(results.data[0]);
// //           setIsModalOpen(true);
// //         },
// //       });
// //     } else if (file.type === 'application/pdf') {
// //       processFile(() => uploadPdfFile(file));
// //     } else {
// //       setError('Unsupported file type.');
// //     }
// //   };

// //   const handleConfirmMapping = async (mapping) => {
// //     setIsModalOpen(false);
// //     if (!selectedFile) return;
// //     await processFile(() => uploadCsvFile(selectedFile, mapping));
// //   };

// //   const processFile = async (uploadFunction) => {
// //     setIsLoading(true);
// //     setError('');
// //     setGraphData(null);
// //     setSelectedNode(null);
// //     try {
// //       await uploadFunction();
// //       // After upload, automatically search for a default account to show a graph
// //       await handleSearch('C12345678'); 
// //     } catch (err) {
// //       setError(err.response?.data?.error || 'An error occurred during processing.');
// //     } finally {
// //       setIsLoading(false);
// //     }
// //   };

// //   // --- Graph Interaction Logic ---
// //   const handleSearch = useCallback(async (accountId) => {
// //     setIsLoading(true);
// //     setError('');
// //     setSelectedNode(null);
// //     try {
// //       const graphResponse = await getGraphDataForAccount(accountId);
// //       setGraphData(graphResponse);
// //     } catch (err) {
// //       setError(`Could not find account: ${accountId}`);
// //       setGraphData(null);
// //     } finally {
// //       setIsLoading(false);
// //     }
// //   }, []);

// //   const handleNodeClick = useCallback(async (node) => {
// //     setSelectedNode(node);
// //     setSummary('');
// //     setGnnAnalysis(null);
    
// //     try {
// //       // Fetch summary and GNN analysis in parallel
// //       const [summaryRes, gnnRes] = await Promise.all([
// //         getAccountSummary(node.id),
// //         analyzeGraphWithGNN(node.id)
// //       ]);
// //       setSummary(summaryRes.summary);
// //       setGnnAnalysis(gnnRes);
// //     } catch (err) {
// //       console.error("Error fetching node details:", err);
// //       setSummary('Could not load summary.');
// //     }
// //   }, []);

// //   return (
// //     <div className="dashboard">
// //       <Navbar />
// //       <MappingModal 
// //         isOpen={isModalOpen}
// //         onClose={() => setIsModalOpen(false)}
// //         headers={csvHeaders}
// //         onConfirm={handleConfirmMapping}
// //       />
// //       <div className="main-layout">
// //         <ControlPanel onFileUpload={handleFileUpload} onSearch={handleSearch} />
        
// //         <main className="graph-main-panel">
// //           <h2>Transaction Network Explorer</h2>
// //           <div className="graph-wrapper">
// //             {isLoading && <Loader />}
// //             {error && !isLoading && <p className="error-message">{error}</p>}
// //             {graphData ? (
// //               <GraphVisualizer 
// //                 data={graphData} 
// //                 onNodeClick={handleNodeClick}
// //                 selectedNodeId={selectedNode?.id}
// //               />
// //             ) : (
// //               !isLoading && (
// //                 <div className="placeholder-graph">
// //                   <FaProjectDiagram size={60} />
// //                   <p>Search for an account or upload data to begin.</p>
// //                 </div>
// //               )
// //             )}
// //           </div>
// //         </main>

// //         <InfoPanel 
// //           selectedNode={selectedNode}
// //           summary={summary}
// //           gnnAnalysis={gnnAnalysis}
// //         />
// //       </div>
// //     </div>
// //   );
// // };

// // export default Dashboard;


// import React, { useState, useCallback } from 'react';
// import Papa from 'papaparse';
// import Navbar from '../components/Navbar';
// import ControlPanel from '../components/ControlPanel';
// import InfoPanel from '../components/InfoPanel';
// import GraphVisualizer from '../components/GraphVisualizer';
// import Loader from '../components/Loader';
// import MappingModal from '../components/MappingModal';
// import { uploadCsvFile, uploadPdfFile, getGraphDataForAccount, getAccountSummary, analyzeGraphWithGNN } from '../services/api';
// import '../assets/Dashboard.css';
// import { FaProjectDiagram, FaCheckCircle } from 'react-icons/fa';

// const Dashboard = () => {
//   // State Management
//   const [selectedFile, setSelectedFile] = useState(null);
//   const [csvHeaders, setCsvHeaders] = useState([]);
//   const [isModalOpen, setIsModalOpen] = useState(false);
//   const [graphData, setGraphData] = useState(null);
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState('');
//   const [successMessage, setSuccessMessage] = useState(''); // New state for success messages

//   // State for the new interactive panels
//   const [selectedNode, setSelectedNode] = useState(null);
//   const [summary, setSummary] = useState('');
//   const [gnnAnalysis, setGnnAnalysis] = useState(null);

//   // --- Data Ingestion Logic ---
//   const handleFileUpload = (file) => {
//     if (!file) {
//       setSelectedFile(null);
//       return;
//     }
//     setSelectedFile(file);
//     if (file.type === 'text/csv') {
//       Papa.parse(file, {
//         preview: 1,
//         complete: (results) => {
//           setCsvHeaders(results.data[0]);
//           setIsModalOpen(true);
//         },
//       });
//     } else if (file.type === 'application/pdf') {
//       processFile(() => uploadPdfFile(file));
//     } else {
//       setError('Unsupported file type.');
//     }
//   };

//   const handleConfirmMapping = async (mapping) => {
//     setIsModalOpen(false);
//     if (!selectedFile) return;
//     await processFile(() => uploadCsvFile(selectedFile, mapping));
//   };

//   const processFile = async (uploadFunction) => {
//     setIsLoading(true);
//     setError('');
//     setSuccessMessage('');
//     setGraphData(null);
//     setSelectedNode(null);
//     try {
//       const response = await uploadFunction();
//       // Set a success message instead of auto-searching
//       setSuccessMessage(response.message || 'File processed successfully.');
//     } catch (err) {
//       setError(err.response?.data?.error || 'An error occurred during processing.');
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   // --- Graph Interaction Logic ---
//   const handleSearch = useCallback(async (accountId) => {
//     setIsLoading(true);
//     setError('');
//     setSuccessMessage('');
//     setSelectedNode(null);
//     try {
//       const graphResponse = await getGraphDataForAccount(accountId);
//       setGraphData(graphResponse);
//     } catch (err) {
//       setError(`Could not find account: ${accountId}`);
//       setGraphData(null);
//     } finally {
//       setIsLoading(false);
//     }
//   }, []);

//   const handleNodeClick = useCallback(async (node) => {
//     setSelectedNode(node);
//     setSummary('Loading...');
//     setGnnAnalysis(null);
    
//     try {
//       const [summaryRes, gnnRes] = await Promise.all([
//         getAccountSummary(node.id),
//         analyzeGraphWithGNN(node.id)
//       ]);
//       setSummary(summaryRes.summary);
//       setGnnAnalysis(gnnRes);
//     } catch (err) {
//       console.error("Error fetching node details:", err);
//       setSummary('Could not load summary for this account.');
//     }
//   }, []);

//   return (
//     <div className="dashboard">
//       <Navbar />
//       <MappingModal 
//         isOpen={isModalOpen}
//         onClose={() => setIsModalOpen(false)}
//         headers={csvHeaders}
//         onConfirm={handleConfirmMapping}
//       />
//       <div className="main-layout">
//         <ControlPanel onFileUpload={handleFileUpload} onSearch={handleSearch} />
        
//         <main className="graph-main-panel">
//           <div className="graph-wrapper">
//             {isLoading && <Loader />}
//             {error && !isLoading && <p className="error-message">{error}</p>}
            
//             {/* Display Success Message */}
//             {successMessage && !isLoading && !error && (
//               <div className="placeholder-graph">
//                   <div className="icon success"><FaCheckCircle /></div>
//                   <h2>Upload Successful</h2>
//                   <p>{successMessage}</p>
//                   <p>Use the search bar on the left to investigate an account.</p>
//               </div>
//             )}

//             {graphData && !error ? (
//               <GraphVisualizer 
//                 data={graphData} 
//                 onNodeClick={handleNodeClick}
//                 selectedNodeId={selectedNode?.id}
//               />
//             ) : (
//               !isLoading && !error && !successMessage && (
//                 <div className="placeholder-graph">
//                   <div className="icon">🔍</div>
//                   <h2>AML Guardian</h2>
//                   <p>
//                     Advanced AI-powered financial transaction analysis. 
//                     Upload your data or search for an account ID to begin your investigation.
//                   </p>
//                 </div>
//               )
//             )}
//           </div>
//         </main>

//         <InfoPanel 
//           selectedNode={selectedNode}
//           summary={summary}
//           gnnAnalysis={gnnAnalysis}
//         />
//       </div>
//     </div>
//   );
// };

// export default Dashboard;



const Dashboard = () => {
  // State Management
  const [selectedFile, setSelectedFile] = useState(null);
  const [csvHeaders, setCsvHeaders] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [graphData, setGraphData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Interactive Panel State
  const [selectedNode, setSelectedNode] = useState(null);
  const [summary, setSummary] = useState('');
  const [gnnAnalysis, setGnnAnalysis] = useState(null);
  
  // New State for Highlighting Nodes
  const [highlightedNodes, setHighlightedNodes] = useState([]);

  // --- Data Ingestion Logic ---
  const handleFileUpload = (file) => {
    if (!file) { setSelectedFile(null); return; }
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

  // --- Graph Interaction & Analysis Logic ---
  const handleSearch = useCallback(async (accountId) => {
    setIsLoading(true);
    setError(''); setSuccessMessage(''); setSelectedNode(null); setHighlightedNodes([]);
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
      setSummary('Could not load summary for this account.');
    }
  }, []);

  // --- NEW: Analysis Tool Handlers ---
  const handleHighlightCycles = async () => {
    setIsLoading(true);
    try {
      const response = await findCyclesInGraph();
      setHighlightedNodes(response.nodes);
      setSuccessMessage(`${response.nodes.length} nodes involved in cycles found and highlighted.`);
    } catch (err) {
      setError('Could not perform cycle analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleShowHighRiskNodes = async () => {
    setIsLoading(true);
    try {
      const response = await findHighRiskNodesInGraph();
      setHighlightedNodes(response.nodes);
      setSuccessMessage(`${response.nodes.length} high-risk nodes found and highlighted.`);
    } catch (err) {
      setError('Could not perform high-risk analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <Navbar />
      <MappingModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} headers={csvHeaders} onConfirm={handleConfirmMapping} />
      <div className="main-layout">
        <ControlPanel 
          onFileUpload={handleFileUpload} 
          onSearch={handleSearch}
          onHighlightCycles={handleHighlightCycles}
          onShowHighRiskNodes={handleShowHighRiskNodes}
        />
        <main className="graph-main-panel">
          <div className="graph-wrapper">
            {isLoading && <Loader />}
            {error && !isLoading && <p className="error-message">{error}</p>}
            {successMessage && !isLoading && !error && !graphData && (
              <div className="placeholder-graph">
                  <div className="icon success"><FaCheckCircle /></div>
                  <h2>Analysis Complete</h2>
                  <p>{successMessage}</p>
                  <p>Search for an account to view the results in the graph.</p>
              </div>
            )}
            {graphData && !error ? (
              <GraphVisualizer 
                data={graphData} 
                onNodeClick={handleNodeClick}
                selectedNodeId={selectedNode?.id}
                highlightedNodes={highlightedNodes}
              />
            ) : (
              !isLoading && !error && !successMessage && (
                <div className="placeholder-graph">
                  <div className="icon">🔍</div>
                  <h2>AML Guardian</h2>
                  <p>Upload data or search for an account ID to begin your investigation.</p>
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
