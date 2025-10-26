import React, { useState, useRef, useEffect } from 'react';

const FileUpload = ({ onFileUpload, uploading, uploadResult }) => {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const fileInputRef = useRef(null);

  // Animation effect when component mounts
  useEffect(() => {
    setIsAnimating(true);
    const timer = setTimeout(() => setIsAnimating(false), 800);
    return () => clearTimeout(timer);
  }, []);

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
      // Add animation effect when file is selected
      setIsAnimating(true);
      setTimeout(() => setIsAnimating(false), 500);
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

  // Function to trigger file input click
  const handleAreaClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="file-upload-container">
      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleAreaClick}
      >
        <div className="upload-icon">
          {file ? '📄' : '📁'}
        </div>
        <p className="upload-text">Drop your file here or click to browse</p>
        <p className="upload-hint">Supports CSV, XLSX, and XLS files</p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
      </div>

      {file && (
        <div className="file-info">
          <div className="file-icon">📄</div>
          <div>
            <div className="file-name">{file.name}</div>
            <div className="file-size">{(file.size / 1024).toFixed(2)} KB</div>
          </div>
        </div>
      )}

      {file && !uploading && !uploadResult && (
        <button 
          className="btn btn-primary" 
          onClick={handleUpload}
          disabled={uploading}
        >
          Upload File
        </button>
      )}

      {uploading && (
        <div className="status-message">
          <div className="spinner"></div>
          <span>Uploading...</span>
        </div>
      )}

      {uploadResult && (
        <div className={`status-message ${uploadResult.success ? 'status-success' : 'status-error'}`}>
          {uploadResult.success ? '✅' : '❌'} {uploadResult.message}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
