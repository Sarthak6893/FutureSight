import React from 'react';

const DatasetInfo = ({ datasetInfo }) => {
  if (!datasetInfo) return null;

  return (
    <div className="dataset-info-container">
      <h3 className="dataset-title">📊 Dataset Information</h3>
      
      <div className="dataset-stats">
        <div className="stat-item">
          <span className="stat-label">Columns:</span>
          <span className="stat-value">{datasetInfo.columns?.length || 0}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Rows:</span>
          <span className="stat-value">{datasetInfo.row_count || 0}</span>
        </div>
      </div>

      <div className="columns-list">
        <h4>Column Names:</h4>
        <div className="columns-tags">
          {datasetInfo.columns?.map((column, index) => (
            <span key={index} className="column-tag">
              {column}
            </span>
          ))}
        </div>
      </div>

      {datasetInfo.sample_data && datasetInfo.sample_data.length > 0 && (
        <div className="sample-data">
          <h4>Sample Data:</h4>
          <div className="sample-data-container">
            <pre className="sample-data-content">
              {JSON.stringify(datasetInfo.sample_data, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatasetInfo;
