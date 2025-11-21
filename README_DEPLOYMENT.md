# Render Deployment Guide

## Backend Service Configuration

### Build Command:
```
pip install -r backend/requirements.txt
```

### Start Command:
```
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables:
- `GEMINI_API_KEY` - Your Google Gemini API key (required)
- `PORT` - Automatically set by Render (don't override)

---

## Frontend Service Configuration

### Build Command:
```
cd frontend && npm install && npm run build
```

### Start Command:
```
cd frontend && npx serve -s build -l $PORT
```

### Environment Variables:
- `REACT_APP_API_URL` - Your backend URL (e.g., `https://futuresight-backend.onrender.com`)
- `PORT` - Automatically set by Render (don't override)

---

## Quick Setup on Render

1. **Create Backend Service:**
   - New → Web Service
   - Connect your GitHub repository
   - Name: `futuresight-backend`
   - Root Directory: Leave empty (or set to `backend` if using render.yaml)
   - Environment: Python 3
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add Environment Variable: `GEMINI_API_KEY` = your API key

2. **Create Frontend Service:**
   - New → Web Service
   - Connect your GitHub repository
   - Name: `futuresight-frontend`
   - Root Directory: Leave empty (or set to `frontend` if using render.yaml)
   - Environment: Node
   - Build Command: `cd frontend && npm install && npm run build`
   - Start Command: `cd frontend && npx serve -s build -l $PORT`
   - Add Environment Variable: `REACT_APP_API_URL` = your backend URL

3. **Alternative: Use render.yaml**
   - If you have a `render.yaml` file in your repo, Render will auto-detect it
   - You can create both services from the YAML file

---

## Notes

- The backend will be available at: `https://futuresight-backend.onrender.com`
- The frontend will be available at: `https://futuresight-frontend.onrender.com`
- Make sure to update `REACT_APP_API_URL` in the frontend service with your actual backend URL
- Both services may take a few minutes to build and deploy on first run

