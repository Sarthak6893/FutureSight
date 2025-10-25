@echo off
echo ========================================
echo    Future Sight - Push to GitHub
echo ========================================
echo.

echo [1/6] Checking if Git is installed...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed!
    echo.
    echo Please install Git first:
    echo 1. Go to: https://git-scm.com/download/win
    echo 2. Download and install Git
    echo 3. Restart your computer
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)
echo ✅ Git is installed

echo.
echo [2/6] Initializing Git repository...
git init
if %errorlevel% neq 0 (
    echo ❌ Failed to initialize Git repository
    pause
    exit /b 1
)
echo ✅ Git repository initialized

echo.
echo [3/6] Adding files to Git...
git add .
if %errorlevel% neq 0 (
    echo ❌ Failed to add files to Git
    pause
    exit /b 1
)
echo ✅ Files added to Git

echo.
echo [4/6] Creating initial commit...
git commit -m "Initial commit: Future Sight AI Data Visualization Platform"
if %errorlevel% neq 0 (
    echo ❌ Failed to create commit
    pause
    exit /b 1
)
echo ✅ Initial commit created

echo.
echo [5/6] Connecting to GitHub repository...
git remote add origin https://github.com/Sarthak6893/FutureSight.git
if %errorlevel% neq 0 (
    echo ❌ Failed to add remote origin
    echo This might mean the remote already exists
    echo Continuing with push...
)
echo ✅ Connected to GitHub repository

echo.
echo [6/6] Pushing to GitHub...
git branch -M main
git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ Failed to push to GitHub
    echo.
    echo This might be due to:
    echo 1. Authentication issues
    echo 2. Network problems
    echo 3. Repository permissions
    echo.
    echo Please check your GitHub credentials and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo    SUCCESS! Project Pushed to GitHub
echo ========================================
echo.
echo Your repository is now available at:
echo https://github.com/Sarthak6893/FutureSight
echo.
echo 🎉 Future Sight is now live on GitHub!
echo.
pause

