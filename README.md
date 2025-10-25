# 🔮 Future Sight - AI Data Visualization

An intelligent data visualization platform that converts natural language prompts into interactive charts using AI-powered analysis.

## ✨ Features

- **🤖 AI-Powered Chart Generation** - Natural language to visualization
- **📊 Multiple Chart Types** - Bar, Line, Pie, Doughnut, Scatter charts
- **📁 File Upload Support** - CSV and Excel file processing
- **🎨 Interactive Visualizations** - Powered by Chart.js
- **📱 Responsive Design** - Works on desktop and mobile
- **⚡ Real-time Processing** - Instant data analysis and visualization

## 🛠️ Tech Stack

### Frontend
- **React** - Interactive user interface
- **Chart.js & React-ChartJS-2** - Data visualization
- **Axios** - API communication
- **CSS3** - Modern responsive design

### Backend
- **FastAPI** - High-performance API framework
- **Python** - Data processing and AI integration
- **Pandas** - Data manipulation and analysis
- **Google Gemini AI** - Natural language processing

### AI & Data Processing
- **Google Gemini AI** - Code generation from natural language
- **Matplotlib** - Python plotting and visualization
- **NumPy** - Numerical computing
- **OpenPyXL** - Excel file processing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Gemini API key

### Option 1: Local Development

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/future-sight.git
cd future-sight
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Environment Configuration
Create `.env` file in backend directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

#### 4. Start Backend
```bash
python main.py
```
Backend runs on: http://localhost:8000

#### 5. Frontend Setup
```bash
cd frontend
npm install
npm start
```
Frontend runs on: http://localhost:3000

### Option 2: Deploy to Render (Recommended)

For production deployment, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed instructions.

**Quick Render Setup:**
1. Push your code to GitHub
2. Create a Web Service on Render for the backend
3. Create a Static Site on Render for the frontend
4. Set environment variables (GEMINI_API_KEY, REACT_APP_API_URL)
5. Deploy!

## 🎯 Usage

1. **Upload Dataset** - Select CSV or Excel file
2. **Enter Prompt** - Describe the chart you want
3. **Generate Visualization** - AI creates the chart automatically

### Example Prompts
- "Show monthly sales trend as a bar chart"
- "Create a pie chart of category distribution"
- "Display correlation between variables as scatter plot"
- "Show revenue trend over time as line chart"

## 📁 Project Structure

```
future-sight/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   └── venv/                # Virtual environment
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.js          # Main application
│   │   └── App.css         # Styling
│   ├── package.json        # Node.js dependencies
│   └── public/             # Static files
├── sample_data.csv         # Sample dataset
└── README.md               # This file
```

## 🔧 API Endpoints

- `GET /` - Health check
- `POST /upload` - Upload CSV/Excel file
- `POST /generate-chart` - Generate chart from prompt

## 🎨 Screenshots

### Upload Interface
![Upload Interface](docs/upload-interface.png)

### Generated Chart
![Generated Chart](docs/generated-chart.png)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Live Demo**: [Your Demo URL]
- **API Documentation**: http://localhost:8000/docs
- **GitHub Repository**: https://github.com/yourusername/future-sight

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Future Sight** - Turning data into insights with the power of AI! 🔮✨