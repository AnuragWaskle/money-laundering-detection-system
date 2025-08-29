import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import InfoPanel from '../components/InfoPanel';
import { FaUserSecret, FaClipboardList, FaSearchPlus } from 'react-icons/fa';
import '../assets/TraceAndInvestigate.css';

// Placeholder components until we build them
const SuspectsList = ({ suspects }) => (
  <div className="suspects-list">
    {suspects.map(s => <div key={s.id} className="suspect-item">{s.id}</div>)}
  </div>
);

const Neo4jGraph = () => (
  <div className="neo4j-graph-placeholder">
    <FaSearchPlus size={80} />
    <p>Live Neo4j Graph Visualization Will Be Embedded Here</p>
  </div>
);

const TraceAndInvestigate = () => {
  // Mock data for a case
  const [caseData, setCaseData] = useState({
    id: 'CASE-001',
    primarySuspect: 'C11112222',
    suspects: [
      { id: 'C11112222', risk: 'High' },
      { id: 'C33334444', risk: 'Medium' },
      { id: 'Shell Company A', risk: 'High' },
      { id: 'Offshore Bank D', risk: 'Critical' },
    ],
  });

  const [selectedNode, setSelectedNode] = useState(null);
  const [summary, setSummary] = useState('');
  const [gnnAnalysis, setGnnAnalysis] = useState(null);

  return (
    <div className="trace-page">
      <Navbar />
      <div className="trace-layout">
        {/* --- Left Panel: Suspects & Evidence --- */}
        <aside className="left-panel">
          <div className="panel-section">
            <h3><FaUserSecret /> Suspects & Entities</h3>
            <SuspectsList suspects={caseData.suspects} />
          </div>
          <div className="panel-section">
            <h3><FaClipboardList /> Evidence Locker</h3>
            <textarea placeholder="Add investigation notes here..."></textarea>
          </div>
        </aside>

        {/* --- Center Panel: The Graph --- */}
        <main className="center-panel">
          <h2>Investigation Board: {caseData.id}</h2>
          <div className="graph-container-main">
            <Neo4jGraph />
          </div>
        </main>

        {/* --- Right Panel: AI Analysis --- */}
        <aside className="right-panel">
          <InfoPanel
            selectedNode={selectedNode}
            summary={summary}
            gnnAnalysis={gnnAnalysis}
          />
        </aside>
      </div>
    </div>
  );
};

export default TraceAndInvestigate;
