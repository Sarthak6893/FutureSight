# 🚀 Quick Start Guide

## One-Click Launch

### Option 1: Batch File (Recommended for Windows)
```bash
# Double-click or run:
start_project.bat
```

### Option 2: PowerShell Script
```bash
# Right-click and "Run with PowerShell" or run:
.\start_project.ps1
```

## What the Launcher Does

1. ✅ **Checks Dependencies** - Ensures all Python packages are installed
2. ✅ **Starts Backend** - Launches FastAPI server on port 8000
3. ✅ **Starts Frontend** - Launches React app on port 3000
4. ✅ **Opens Browser** - Automatically opens the application

## Before Running

### ⚠️ IMPORTANT: Set Your API Key

1. **Edit the environment file:**
   ```
   future-sight/backend/.env
   ```

2. **Replace the placeholder with your actual Gemini API key:**
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Get your API key from:** [Google AI Studio](https://aistudio.google.com/)

## Manual Start (Alternative)

If the launcher doesn't work, you can start manually:

### Terminal 1 - Backend:
```bash
cd future-sight/backend
venv\Scripts\activate
python main.py
```

### Terminal 2 - Frontend:
```bash
cd future-sight/frontend
npm start
```

## URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Troubleshooting

### If Backend Fails:
- Check if port 8000 is free
- Verify `.env` file has valid API key
- Ensure Python dependencies are installed

### If Frontend Fails:
- Check if port 3000 is free
- Run `npm install` in frontend directory
- Clear npm cache: `npm cache clean --force`

### If Upload Doesn't Work:
- Check browser console (F12) for errors
- Verify backend is running
- Try with the included `sample_data.csv` file

## Test the Application

1. **Upload a file** (use `sample_data.csv`)
2. **Enter a prompt** like: "Show monthly sales trend as a bar chart"
3. **Generate chart** and see the AI visualization!

---

**Future Sight** - Turning data into insights with AI! 🔮✨

