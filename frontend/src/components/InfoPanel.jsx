import React from 'react';
import { FaUserCircle, FaExclamationCircle, FaBrain } from 'react-icons/fa';
import '../assets/InfoPanel.css';

const InfoPanel = ({ selectedNode, summary, gnnAnalysis }) => {
  if (!selectedNode) {
    return (
      <div className="info-panel placeholder">
        <FaUserCircle size={60} />
        <p>Click on an account in the graph to view its details, risk analysis, and AI-generated summary.</p>
      </div>
    );
  }

  return (
    <div className="info-panel">
      <div className="panel-section">
        <h3>Account Details</h3>
        <div className="details-grid">
          <div className="detail-item">
            <span className="detail-label">Account ID</span>
            <span className="detail-value">{selectedNode.id}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Risk Score</span>
            <span className="detail-value high-risk">92%</span>
          </div>
        </div>
      </div>

      <div className="panel-section">
        <h3><FaBrain /> AI-Generated Summary</h3>
        <p className="summary-text">
          {summary || 'Loading summary...'}
        </p>
      </div>
      
      <div className="panel-section">
        <h3><FaExclamationCircle /> GNN Risk Analysis</h3>
        <div className="gnn-results">
          {gnnAnalysis ? (
            gnnAnalysis.predictions.slice(0, 5).map((pred, index) => (
              <div key={index} className="gnn-item">
                <span>{`Link to ${pred.target}`}</span>
                <span className={`gnn-score ${pred.gnn_risk_score > 0.5 ? 'high-risk' : ''}`}>
                  {`${(pred.gnn_risk_score * 100).toFixed(1)}%`}
                </span>
              </div>
            ))
          ) : (
            <p>Loading GNN analysis...</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default InfoPanel;
