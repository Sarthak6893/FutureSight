# 🚀 Render Deployment Guide for Future Sight

## Prerequisites
- GitHub repository with your Future Sight project
- Render account (free tier available)
- Gemini API key

## Step 1: Prepare Your Repository

### 1.1 Push to GitHub
```bash
# If not already done, push your project to GitHub
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 1.2 Verify Project Structure
Your repository should contain:
```
FutureSight/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── package-lock.json
├── render.yaml
├── Procfile
└── README.md
```

## Step 2: Deploy Backend to Render

### 2.1 Create Backend Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `futuresight-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python main.py`
   - **Plan**: Free

### 2.2 Set Environment Variables
In the Render dashboard, add:
- **Key**: `GEMINI_API_KEY`
- **Value**: Your actual Gemini API key

### 2.3 Deploy
Click "Create Web Service" and wait for deployment.

## Step 3: Deploy Frontend to Render

### 3.1 Create Frontend Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Static Site"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `futuresight-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`
   - **Plan**: Free

### 3.2 Set Environment Variables
Add environment variable:
- **Key**: `REACT_APP_API_URL`
- **Value**: Your backend URL (e.g., `https://futuresight-backend.onrender.com`)

### 3.3 Deploy
Click "Create Static Site" and wait for deployment.

## Step 4: Configure CORS (Important!)

### 4.1 Update Backend CORS
The backend is already configured to allow all origins for production.

### 4.2 Test the Connection
1. Visit your frontend URL
2. Try uploading a file
3. Check browser console for any CORS errors

## Step 5: Environment Variables Summary

### Backend Environment Variables:
```
GEMINI_API_KEY=your_actual_gemini_api_key
```

### Frontend Environment Variables:
```
REACT_APP_API_URL=https://your-backend-url.onrender.com
```

## 🎯 Deployment URLs

After deployment, you'll have:
- **Backend API**: `https://futuresight-backend.onrender.com`
- **Frontend App**: `https://futuresight-frontend.onrender.com`
- **API Documentation**: `https://futuresight-backend.onrender.com/docs`

## 🔧 Troubleshooting

### Common Issues:

1. **Build Failures**
   - Check that all dependencies are in requirements.txt
   - Verify Python version compatibility

2. **CORS Errors**
   - Ensure backend allows all origins
   - Check that frontend is using correct API URL

3. **API Key Issues**
   - Verify GEMINI_API_KEY is set correctly
   - Check API key permissions

4. **Static Site Issues**
   - Ensure build command runs successfully
   - Check that publish directory is correct

## 📋 Render Configuration Files

### render.yaml (Optional - for Blueprint deployment)
```yaml
services:
  - type: web
    name: futuresight-backend
    env: python
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && python main.py
    envVars:
      - key: GEMINI_API_KEY
        sync: false
```

## 🎉 Success!

Your Future Sight application is now live on Render! Users can:
1. Visit your frontend URL
2. Upload CSV/Excel files
3. Generate AI-powered charts and predictions
4. View interactive visualizations

## 🔗 Useful Links

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Build Process](https://create-react-app.dev/docs/production-build/)
