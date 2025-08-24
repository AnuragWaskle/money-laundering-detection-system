import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import '../assets/FileUpload.css';

const FileUpload = ({ onFileUpload }) => {
  const [uploadedFile, setUploadedFile] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedFile(file);
      onFileUpload(file);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 
      'text/csv': ['.csv'],
      'application/pdf': ['.pdf'] 
    },
    multiple: false,
  });

  const removeFile = () => {
    setUploadedFile(null);
    onFileUpload(null);
  };

  return (
    <div className="upload-container">
      <div {...getRootProps({ className: `dropzone ${isDragActive ? 'active' : ''}` })}>
        <input {...getInputProps()} />
        <div className="upload-icon">
          <svg width="60" height="60" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
            <path d="M14 3v4a1 1 0 0 0 1 1h4" />
            <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
            <path d="M12 11v6" />
            <path d="M9.5 13.5l2.5 -2.5l2.5 2.5" />
          </svg>
        </div>
        {isDragActive ? (
          <p>Drop a file here ...</p>
        ) : (
          <p>Drag 'n' drop a CSV or PDF file here, or click to select</p>
        )}
      </div>
      {uploadedFile && (
        <div className="file-info">
          <span>{uploadedFile.name}</span>
          <button onClick={removeFile} className="remove-btn">×</button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
