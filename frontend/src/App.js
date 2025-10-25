import React, { useState } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import DatasetInfo from './components/DatasetInfo';
import ChartGenerator from './components/ChartGenerator';
import ChartDisplay from './components/ChartDisplay';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [datasetInfo, setDatasetInfo] = useState(null);

  const [generating, setGenerating] = useState(false);
  const [generationStatus, setGenerationStatus] = useState(null);
  const [chartData, setChartData] = useState(null);

  const handleFileUpload = async (file) => {
    console.log('Starting file upload process...', file);
    setUploading(true);
    setUploadResult(null);
    setDatasetInfo(null);
    setChartData(null); // Clear previous chart

    const formData = new FormData();
    formData.append('file', file);
    console.log('FormData created, sending to:', `${API_BASE_URL}/upload`);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData);
      console.log('Upload successful:', response.data);

      setUploadResult({
        success: true,
        message: 'File uploaded successfully!',
      });

      setDatasetInfo(response.data);
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadResult({
        success: false,
        message: error.response?.data?.detail || 'Failed to upload file. Please try again.',
      });
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateChart = async (prompt) => {
    setGenerating(true);
    setGenerationStatus(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/generate-chart`, {
        prompt,
      });

      setChartData(response.data);
      setGenerationStatus({
        success: true,
        message: 'Chart generated successfully!',
      });
    } catch (error) {
      setGenerationStatus({
        success: false,
        message: error.response?.data?.detail || 'Failed to generate chart. Please try again.',
      });
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">🔮 Future Sight</h1>
        <p className="app-tagline">AI-powered data prediction & visualization</p>
      </header>

      <main className="main-container">
        <div className="content-wrapper">
          <section className="section">
            <h2 className="section-title">Upload Dataset</h2>
            <FileUpload
              onFileUpload={handleFileUpload}
              uploading={uploading}
              uploadResult={uploadResult}
            />
          </section>

          {datasetInfo && (
            <section className="section">
              <DatasetInfo datasetInfo={datasetInfo} />
            </section>
          )}

          <section className="section">
            <ChartGenerator
              onGenerateChart={handleGenerateChart}
              generating={generating}
              generationStatus={generationStatus}
              datasetUploaded={!!datasetInfo}
            />
          </section>

          {chartData && (
            <section className="section">
              <ChartDisplay chartData={chartData} />
            </section>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>Built with React, FastAPI, and Gemini AI</p>
      </footer>
    </div>
  );
}

export default App;
