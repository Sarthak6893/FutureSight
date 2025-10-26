import React, { useState } from 'react';

const ChartGenerator = ({ onGenerateChart, generating, generationStatus, datasetUploaded }) => {
  const [prompt, setPrompt] = useState('');

  const examplePrompts = [
    "Show monthly sales trend as a bar chart",
    "Create a pie chart of category distribution",
    "Display correlation between variables as scatter plot",
    "Show revenue trend over time as line chart",
    "Create a doughnut chart of market share"
  ];

  const handleGenerate = () => {
    if (!datasetUploaded) {
      alert('Please upload a dataset first');
      return;
    }

    if (!prompt.trim()) {
      alert('Please enter a prompt');
      return;
    }

    onGenerateChart(prompt.trim());
  };

  const handleExampleClick = (examplePrompt) => {
    setPrompt(examplePrompt);
  };

  return (
    <div className="chart-generator-container">
      <h3 className="generator-title">Generate Chart</h3>
      
      <div className="prompt-section">
        <label htmlFor="prompt" className="prompt-label">
          Describe the chart you want:
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., Show monthly sales trend as a bar chart"
          className="prompt-textarea"
          rows="3"
        />
      </div>

      {/* Example prompts section removed as requested */}

      <button
        onClick={handleGenerate}
        disabled={!datasetUploaded || generating}
        className={`generate-button ${generating ? 'generating' : ''}`}
      >
        {generating ? '⏳ Generating...' : '🚀 Generate Chart'}
      </button>

      {generationStatus && (
        <div className={`status-message ${generationStatus.success ? 'success' : 'error'}`}>
          {generationStatus.message}
        </div>
      )}
    </div>
  );
};

export default ChartGenerator;
