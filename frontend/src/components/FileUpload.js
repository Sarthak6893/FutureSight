import React, { useState } from 'react';

const FileUpload = ({ onFileUpload, uploading, uploadResult }) => {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    const allowedTypes = [
      'text/csv', 
      'application/csv',
      'application/vnd.ms-excel', 
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/excel',
      'application/x-excel',
      'application/x-msexcel'
    ];
    const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
    
    if (allowedTypes.includes(selectedFile.type) || ['csv', 'xlsx', 'xls'].includes(fileExtension)) {
      setFile(selectedFile);
    } else {
      alert(`Please select a CSV or Excel file. File type: ${selectedFile.type}, Extension: ${fileExtension}`);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = () => {
    if (file) {
      console.log('Uploading file:', file.name, 'Type:', file.type, 'Size:', file.size);
      onFileUpload(file);
    } else {
      console.log('No file selected for upload');
    }
  };

  return (
    <div className="file-upload-container">
      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="upload-content">
          <div className="upload-icon">📁</div>
          <h3>Drop your file here or click to browse</h3>
          <p>Supports CSV, XLSX, and XLS files</p>
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
            className="file-input"
          />
        </div>
      </div>
      
      {file && (
        <div className="file-info">
          <div className="file-details">
            <span className="file-name">📄 {file.name}</span>
            <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
          </div>
        </div>
      )}
      
      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className={`upload-button ${uploading ? 'uploading' : ''}`}
      >
        {uploading ? '⏳ Uploading...' : '🚀 Upload File'}
      </button>
      
      {uploadResult && (
        <div className={`status-message ${uploadResult.success ? 'success' : 'error'}`}>
          {uploadResult.message}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
