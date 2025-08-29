import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Button from '../components/Button';
import { FaFolderOpen, FaPlusCircle } from 'react-icons/fa';
import '../assets/CaseManagement.css';

const CaseManagement = () => {
  // Mock data for demonstration purposes
  const [cases, setCases] = useState([
    { id: 'CASE-001', suspect: 'C11112222', status: 'Open', summary: 'Initial investigation into a large, suspicious transfer of $5,000,000.' },
    { id: 'CASE-002', suspect: 'C50505050', status: 'Open', summary: 'Potential layering activity detected involving multiple offshore accounts.' },
    { id: 'CASE-003', suspect: 'C99998888', status: 'Closed', summary: 'Resolved: transaction was a legitimate business acquisition.' },
    { id: 'CASE-004', suspect: 'C100100100', status: 'Open', summary: 'High-frequency, high-value transfers flagged by GNN model.' },
  ]);

  const handleInvestigate = (caseId) => {
    // In a real app, this would navigate to the TraceAndInvestigate page
    alert(`Navigating to investigate ${caseId}`);
  };

  return (
    <div className="case-management-page">
      <Navbar />
      <main className="case-content">
        <header className="case-header">
          <h1><FaFolderOpen /> Case Management</h1>
          <Button>
            <FaPlusCircle style={{ marginRight: '8px' }} />
            Create New Case
          </Button>
        </header>

        <div className="case-table-container">
          <table className="case-table">
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Primary Suspect</th>
                <th>Status</th>
                <th>Summary</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((caseItem) => (
                <tr key={caseItem.id}>
                  <td>{caseItem.id}</td>
                  <td>{caseItem.suspect}</td>
                  <td>
                    <span className={`status-badge status-${caseItem.status.toLowerCase()}`}>
                      {caseItem.status}
                    </span>
                  </td>
                  <td>{caseItem.summary}</td>
                  <td>
                    <Button onClick={() => handleInvestigate(caseItem.id)} variant="secondary">
                      Investigate
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
};

export default CaseManagement;
