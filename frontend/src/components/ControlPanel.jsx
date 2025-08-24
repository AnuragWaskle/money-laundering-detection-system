import React, { useState } from 'react';
import FileUpload from './FileUpload';
import Button from './Button';
import { FaSearch } from 'react-icons/fa';
import '../assets/ControlPanel.css';

const ControlPanel = ({ onFileUpload, onSearch }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm) {
      onSearch(searchTerm);
    }
  };

  return (
    <div className="control-panel">
      <div className="panel-section">
        <h3>Investigate Account</h3>
        <form className="search-form" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Enter Account ID (e.g., C12345)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button type="submit"><FaSearch /></button>
        </form>
      </div>

      <div className="panel-section">
        <h3>Ingest Data</h3>
        <FileUpload onFileUpload={onFileUpload} />
      </div>
      
      <div className="panel-section">
        <h3>Analysis Tools</h3>
        <Button variant="secondary">Highlight Cycles</Button>
        <Button variant="secondary">Show High-Risk Nodes</Button>
      </div>
    </div>
  );
};

export default ControlPanel;
