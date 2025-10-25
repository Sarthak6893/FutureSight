import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Pie, Doughnut, Scatter } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const ChartDisplay = ({ chartData }) => {
  if (!chartData) {
    return (
      <div className="chart-container">
        <div className="no-chart-message">
          <div className="no-chart-title">No chart generated yet</div>
          <div className="no-chart-subtitle">Upload a dataset and generate a chart to see it here</div>
        </div>
      </div>
    );
  }

  // Handle the backend response format which returns base64 image
  if (chartData.chart_image) {
    return (
      <div className="chart-container">
        <h3 className="chart-title">Generated Chart</h3>
        <div className="chart-image-wrapper">
          <img 
            src={`data:image/png;base64,${chartData.chart_image}`}
            alt="Generated Chart"
            className="chart-image"
          />
        </div>
        <div className="chart-metadata">
          <span className="chart-type">Chart Type: AI Generated</span>
          {chartData.message && (
            <span className="chart-message">{chartData.message}</span>
          )}
        </div>
      </div>
    );
  }

  // Fallback for structured chart data (if backend changes to return structured data)
  const renderChart = () => {
    const commonOptions = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: !!chartData.metadata?.title,
          text: chartData.metadata?.title || '',
        },
      },
      ...chartData.options,
    };

    switch (chartData.type) {
      case 'bar':
        return <Bar data={chartData.data} options={commonOptions} />;
      case 'line':
        return <Line data={chartData.data} options={commonOptions} />;
      case 'pie':
        return <Pie data={chartData.data} options={commonOptions} />;
      case 'doughnut':
        return <Doughnut data={chartData.data} options={commonOptions} />;
      case 'scatter':
        return <Scatter data={chartData.data} options={commonOptions} />;
      default:
        return <div>Unsupported chart type</div>;
    }
  };

  return (
    <div className="chart-container">
      <h3 className="chart-title">Generated Chart</h3>

      {chartData.metadata && (
        <div className="chart-metadata">
          <div className="metadata-items">
            <span className="metadata-item">
              <strong>Type:</strong> <span className="capitalize">{chartData.type}</span>
            </span>
            {chartData.metadata.xLabel && (
              <span className="metadata-item">X-Axis: {chartData.metadata.xLabel}</span>
            )}
            {chartData.metadata.yLabel && (
              <span className="metadata-item">Y-Axis: {chartData.metadata.yLabel}</span>
            )}
          </div>
        </div>
      )}

      <div className="chart-wrapper">
        {renderChart()}
      </div>
    </div>
  );
};

export default ChartDisplay;
