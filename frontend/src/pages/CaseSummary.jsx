import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Button from '../components/Button';
import { FaFilePdf, FaUserSecret, FaExclamationTriangle, FaProjectDiagram } from 'react-icons/fa';
import '../assets/CaseSummary.css';

const CaseSummary = () => {
  // Mock data for a completed case report
  const [caseReport, setCaseReport] = useState({
    caseId: 'CASE-001',
    status: 'Closed - High Confidence of Laundering',
    primarySuspect: 'C11112222',
    involvedEntities: ['C11112222', 'C33334444', 'Shell Company A', 'Offshore Bank D'],
    aiNarrative: "The investigation identified a classic layering and integration scheme originating from account C11112222. A large sum of $5,000,000 was moved through a domestic shell company before being transferred to an offshore bank known for lax regulations. The funds were then repatriated through a series of smaller, disguised transactions. The GNN model flagged the initial transfer with a 98.7% risk score due to the account's lack of prior history and the high-risk nature of the destination.",
    keyEvidence: [
      { id: 'TRX-001', from: 'C11112222', to: 'C33334444', amount: '$5,000,000', reason: 'Anomalously large transfer; zero balance after transaction.' },
      { id: 'TRX-002', from: 'C33334444', to: 'Offshore Bank D', amount: '$4,950,000', reason: 'Transfer to a high-risk jurisdiction.' },
    ],
    investigatorNotes: "The pattern is clear and consistent with established money laundering typologies. Recommend forwarding the case to the national financial intelligence unit for further action."
  });

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="case-summary-page">
      <Navbar />
      <main className="summary-content">
        <header className="summary-header">
          <h1>Case Summary Report</h1>
          <Button onClick={handlePrint}>
            <FaFilePdf style={{ marginRight: '8px' }} />
            Print / Export to PDF
          </Button>
        </header>

        <div className="report-body">
          <div className="report-section details-section">
            <h2>Case Details</h2>
            <p><strong>Case ID:</strong> {caseReport.caseId}</p>
            <p><strong>Status:</strong> <span className="status-highlight">{caseReport.status}</span></p>
            <p><strong>Primary Suspect:</strong> {caseReport.primarySuspect}</p>
          </div>

          <div className="report-section">
            <h2><FaUserSecret /> Involved Entities</h2>
            <ul className="entity-list">
              {caseReport.involvedEntities.map(entity => <li key={entity}>{entity}</li>)}
            </ul>
          </div>

          <div className="report-section">
            <h2>AI-Generated Narrative</h2>
            <p className="narrative-text">{caseReport.aiNarrative}</p>
          </div>

          <div className="report-section">
            <h2><FaExclamationTriangle /> Key Evidence (Flagged Transactions)</h2>
            <table className="evidence-table">
              <thead>
                <tr>
                  <th>Transaction ID</th>
                  <th>From</th>
                  <th>To</th>
                  <th>Amount</th>
                  <th>Reason for Suspicion</th>
                </tr>
              </thead>
              <tbody>
                {caseReport.keyEvidence.map(tx => (
                  <tr key={tx.id}>
                    <td>{tx.id}</td>
                    <td>{tx.from}</td>
                    <td>{tx.to}</td>
                    <td>{tx.amount}</td>
                    <td>{tx.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="report-section">
            <h2><FaProjectDiagram /> Graph Snapshot</h2>
            <div className="graph-snapshot-placeholder">
              <p>Image of the transaction network graph would be displayed here.</p>
            </div>
          </div>

           <div className="report-section">
            <h2>Investigator Notes</h2>
            <p className="notes-text">{caseReport.investigatorNotes}</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default CaseSummary;
