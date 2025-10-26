import React, { useState, useEffect, createContext } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import DatasetInfo from './components/DatasetInfo';
import ChartGenerator from './components/ChartGenerator';
import ChartDisplay from './components/ChartDisplay';
import './App.css';

// Create a context for dark mode
export const ThemeContext = createContext();

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [dataset, setDataset] = useState(null);
  const [activeTab, setActiveTab] = useState('upload');
  const [showSettings, setShowSettings] = useState(false);

  const [generating, setGenerating] = useState(false);
  const [generationStatus, setGenerationStatus] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [expandedChart, setExpandedChart] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [sendingChat, setSendingChat] = useState(false);
  
  // Apply dark mode to body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  const handleFileUpload = async (file) => {
    console.log('Starting file upload process...', file);
    setUploading(true);
    setUploadResult(null);
    setDataset(null);
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

      setDataset(response.data);
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
        prompt: prompt,
        datasetInfo: dataset
      });

      console.log('Chart generation response:', response.data);

      if (response.data.success) {
        setChartData(response.data);
        setGenerationStatus({
          success: true,
          message: 'Chart generated successfully!'
        });
        
        // No longer opening in a new window - chart will display in the visualization section
      } else {
        setGenerationStatus({
          success: false,
          message: response.data.error || 'Failed to generate chart.'
        });
      }
    } catch (error) {
      console.error('Error generating chart:', error);
      setGenerationStatus({
        success: false,
        message: 'Error generating chart. Please try again.'
      });
    } finally {
      setGenerating(false);
    }
  };
  
  const handleSendChatMessage = async () => {
    if (!chatMessage.trim()) return;
    
    setSendingChat(true);
    const userMessage = { role: 'user', content: chatMessage };
    setChatHistory([...chatHistory, userMessage]);
    setChatMessage('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: chatMessage,
        datasetInfo: {
          columns: dataset.columns,
          sample_data: dataset.sample_data
        },
      });
      setChatHistory(prev => [...prev, { role: 'assistant', content: response.data.message }]);
    } catch (error) {
      console.error('Chat failed:', error);
      setChatHistory(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error processing your request.' }]);
    } finally {
      setSendingChat(false);
    }
  };

  return (
    <ThemeContext.Provider value={{ darkMode, setDarkMode }}>
      <div className={`app-container ${darkMode ? 'dark-mode' : ''}`}>
        <header className="app-header">
          <div className="app-branding">
            <h1 className="app-title">🔮 Future Sight</h1>
            <p className="app-tagline">AI-powered data prediction & visualization</p>
          </div>
          <div className="header-actions">
            <label className="toggle-switch" aria-label="Toggle dark mode">
              <input 
                type="checkbox" 
                checked={darkMode} 
                onChange={() => setDarkMode(!darkMode)}
              />
              <span className="toggle-slider">
                <span className="toggle-icon sun">☀️</span>
                <span className="toggle-icon moon">🌙</span>
              </span>
            </label>
            <button 
              className="btn btn-icon" 
              onClick={() => setShowSettings(!showSettings)}
              aria-label="Settings"
            >
              ⚙️
            </button>
            <button className="btn btn-secondary">Help</button>
          </div>
        </header>

        {showSettings && (
          <div className="settings-panel">
            <div className="settings-header">
              <h3>Settings</h3>
              <button className="btn-close" onClick={() => setShowSettings(false)}>×</button>
            </div>
            <div className="settings-content">
              <div className="setting-item">
                <label>
                  <input 
                    type="checkbox" 
                    checked={darkMode} 
                    onChange={() => setDarkMode(!darkMode)} 
                  />
                  Dark Mode
                </label>
              </div>
              <div className="setting-item">
                <label>Chart Animation Speed</label>
                <select defaultValue="medium">
                  <option value="slow">Slow</option>
                  <option value="medium">Medium</option>
                  <option value="fast">Fast</option>
                </select>
              </div>
              <div className="setting-item">
                <label>Data Precision</label>
                <select defaultValue="2">
                  <option value="0">0 decimal places</option>
                  <option value="1">1 decimal place</option>
                  <option value="2">2 decimal places</option>
                  <option value="3">3 decimal places</option>
                </select>
              </div>
            </div>
          </div>
        )}

        <nav className="app-nav">
          <ul>
            <li className={activeTab === 'upload' ? 'active' : ''}>
              <button onClick={() => setActiveTab('upload')}>Upload</button>
            </li>
            <li className={activeTab === 'dashboard' ? 'active' : ''}>
              <button onClick={() => setActiveTab('dashboard')}>Dashboard</button>
            </li>
            <li className={activeTab === 'insights' ? 'active' : ''}>
              <button onClick={() => setActiveTab('insights')}>Insights</button>
            </li>
            <li className={activeTab === 'about' ? 'active' : ''}>
              <button onClick={() => setActiveTab('about')}>About</button>
            </li>
          </ul>
        </nav>

        <main className="main-container">
          {activeTab === 'upload' && (
            <div className="content-wrapper">
              <div className="left-column">
                <section className="section">
                  <h2 className="section-title">Upload Dataset</h2>
                  <FileUpload
                    onFileUpload={handleFileUpload}
                    uploading={uploading}
                    uploadResult={uploadResult}
                  />
                </section>
                
                  {dataset && (
                  <section className="section">
                    <h2 className="section-title">Dataset Information</h2>
                    <DatasetInfo datasetInfo={dataset} />
                  </section>
                )}
              </div>
              
              <div className="right-column">
                <section className="section">
                  <h2 className="section-title">Generate Chart</h2>
                  {dataset ? (
                    <ChartGenerator
                      onGenerateChart={handleGenerateChart}
                      generating={generating}
                      generationStatus={generationStatus}
                      datasetUploaded={!!dataset}
                    />
                  ) : (
                    <div className="empty-state">
                      <div className="upload-icon">📊</div>
                      <p>Please upload a dataset first to generate charts.</p>
                    </div>
                  )}
                </section>

                <section className="section">
                  <h2 className="section-title">Visualization</h2>
                  {chartData ? (
                    <div className="chart-container">
                      <div className="chart-wrapper" onClick={() => setExpandedChart(true)}>
                        <ChartDisplay chartData={chartData} />
                        <div className="chart-overlay">
                          <span className="expand-icon">🔍 Click to expand</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="empty-chart-state">
                      <p>Your chart will appear here after generation</p>
                    </div>
                  )}
                </section>
                
                {expandedChart && (
                  <div className="expanded-chart-modal">
                    <div className="expanded-chart-content">
                      <button className="close-chart-btn" onClick={() => setExpandedChart(false)}>×</button>
                      <ChartDisplay chartData={chartData} />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'dashboard' && (
            <div className="dashboard-container">
              <h2 className="section-title">Interactive Dashboard</h2>
              {dataset ? (
                <div className="dashboard-content">
                  <div className="dashboard-card">
                    <h3>Dataset Summary</h3>
                    <div className="stat-grid">
                      <div className="stat-item">
                        <span className="stat-label">Rows</span>
                        <span className="stat-value">{dataset.row_count}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Columns</span>
                        <span className="stat-value">{dataset.column_count}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Data Types</span>
                        <span className="stat-value">{Object.keys(dataset.columns || {}).length}</span>
                      </div>
                    </div>
                  </div>
                  <div className="dashboard-card">
                    <h3>Data Quality</h3>
                    <div className="quality-meter">
                      <div className="quality-bar" style={{width: '85%'}}></div>
                      <span className="quality-score">85%</span>
                    </div>
                    <p>Your data is in good shape for analysis!</p>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">📊</div>
                  <h3>No Dataset Available</h3>
                  <p>Upload a dataset to view dashboard analytics</p>
                  <button 
                    className="btn btn-primary" 
                    onClick={() => setActiveTab('upload')}
                  >
                    Go to Upload
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'insights' && (
            <div className="insights-container">
              <h2 className="section-title">Chat with AI</h2>
              {dataset ? (
                <div className="chat-interface">
                  <div className="chat-messages">
                    {chatHistory.length === 0 ? (
                      <div className="chat-welcome">
                        <h3>Ask me anything about your data</h3>
                        <p>For example: "What trends do you see in this dataset?" or "Which products would perform well in the coming years?"</p>
                      </div>
                    ) : (
                      chatHistory.map((msg, index) => (
                        <div key={index} className={`chat-message ${msg.role}`}>
                          <div className="message-content">{msg.content}</div>
                        </div>
                      ))
                    )}
                    {sendingChat && (
                      <div className="chat-message assistant">
                        <div className="message-content typing">Thinking...</div>
                      </div>
                    )}
                  </div>
                  <div className="chat-input-container">
                    <input
                      type="text"
                      className="chat-input"
                      value={chatMessage}
                      onChange={(e) => setChatMessage(e.target.value)}
                      placeholder="Ask about your data..."
                      onKeyPress={(e) => e.key === 'Enter' && handleSendChatMessage()}
                    />
                    <button 
                      className="chat-send-btn"
                      onClick={handleSendChatMessage}
                      disabled={sendingChat || !chatMessage.trim()}
                    >
                      Send
                    </button>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">💡</div>
                  <h3>No Dataset Available</h3>
                  <p>Upload a dataset to chat with AI about your data</p>
                  <button 
                    className="btn btn-primary" 
                    onClick={() => setActiveTab('upload')}
                  >
                    Go to Upload
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'about' && (
            <div className="about-container">
              <h2 className="section-title">About Future Sight</h2>
              <div className="about-content">
                <div className="about-section">
                  <h3>Our Mission</h3>
                  <p>Future Sight is an AI-powered data visualization tool designed to help you uncover insights and predict trends in your data with minimal effort.</p>
                </div>
                <div className="about-section">
                  <h3>How It Works</h3>
                  <ol>
                    <li>Upload your CSV dataset</li>
                    <li>Our AI analyzes your data structure</li>
                    <li>Generate visualizations with natural language</li>
                    <li>Get AI-powered insights and predictions</li>
                  </ol>
                </div>
                <div className="about-section">
                  <h3>Technologies</h3>
                  <div className="tech-stack">
                    <span className="tech-badge">React</span>
                    <span className="tech-badge">Python</span>
                    <span className="tech-badge">FastAPI</span>
                    <span className="tech-badge">Pandas</span>
                    <span className="tech-badge">Gemini AI</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>

        <footer className="app-footer">
          <div className="footer-content">
            <p>© 2023 Future Sight | AI-Powered Data Visualization</p>
            <div className="footer-links">
              <a href="#">Privacy</a>
              <a href="#">Terms</a>
              <a href="#">Contact</a>
            </div>
          </div>
        </footer>
      </div>
    </ThemeContext.Provider>
  );
}

export default App;
