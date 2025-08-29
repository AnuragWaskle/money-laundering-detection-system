import React, { useState } from 'react';
import { FaUser, FaBuilding, FaUniversity } from 'react-icons/fa';
import '../assets/SuspectsList.css';

const SuspectsList = ({ suspects, onSelectSuspect }) => {
  const [filter, setFilter] = useState('');

  const getIconForSuspect = (suspectId) => {
    if (suspectId.startsWith('C')) return <FaUser />;
    if (suspectId.startsWith('M')) return <FaBuilding />;
    return <FaUniversity />; // For Banks/Entities
  };

  const filteredSuspects = suspects.filter(s => 
    s.id.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="suspects-list-container">
      <input
        type="text"
        className="filter-input"
        placeholder="Filter suspects..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />
      <div className="suspects-list">
        {filteredSuspects.map(suspect => (
          <div 
            key={suspect.id} 
            className="suspect-item"
            onClick={() => onSelectSuspect(suspect.id)}
          >
            <span className="suspect-icon">{getIconForSuspect(suspect.id)}</span>
            <span className="suspect-id">{suspect.id}</span>
            <span className={`suspect-risk risk-${suspect.risk.toLowerCase()}`}>
              {suspect.risk}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SuspectsList;
