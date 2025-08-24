import React, { useState, useEffect } from 'react';
import Button from './Button';
import '../assets/MappingModal.css';

const MappingModal = ({ isOpen, onClose, headers, onConfirm }) => {
  const canonicalFields = [
    'step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 
    'newbalanceOrig', 'nameDest', 'oldbalanceDest', 
    'newbalanceDest', 'isFraud'
  ];

  const [mapping, setMapping] = useState({});

  useEffect(() => {
    // Auto-map fields if headers match canonical names (case-insensitive)
    const initialMapping = {};
    canonicalFields.forEach(field => {
      const foundHeader = headers.find(h => h.toLowerCase() === field.toLowerCase());
      initialMapping[field] = foundHeader || '';
    });
    setMapping(initialMapping);
  }, [headers]);

  if (!isOpen) return null;

  const handleSelectChange = (canonicalField, selectedHeader) => {
    setMapping(prev => ({ ...prev, [canonicalField]: selectedHeader }));
  };

  const handleConfirm = () => {
    // Validate that all required fields are mapped
    const mappedValues = Object.values(mapping);
    if (mappedValues.some(val => !val)) {
      alert('Please map all required fields.');
      return;
    }
    onConfirm(mapping);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Map Your CSV Columns</h2>
        <p>Match our system's required fields to the columns found in your uploaded file.</p>
        <div className="mapping-grid">
          {canonicalFields.map(field => (
            <div className="mapping-row" key={field}>
              <label className="canonical-field">{field}:</label>
              <select
                value={mapping[field] || ''}
                onChange={(e) => handleSelectChange(field, e.target.value)}
              >
                <option value="">-- Select Your Column --</option>
                {headers.map(header => (
                  <option key={header} value={header}>{header}</option>
                ))}
              </select>
            </div>
          ))}
        </div>
        <div className="modal-actions">
          <Button onClick={onClose} variant="secondary">Cancel</Button>
          <Button onClick={handleConfirm}>Confirm & Process</Button>
        </div>
      </div>
    </div>
  );
};

export default MappingModal;
