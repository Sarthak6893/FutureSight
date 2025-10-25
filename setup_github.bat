@echo off
echo ========================================
echo    Future Sight - GitHub Setup
echo ========================================
echo.

echo [1/4] Checking if Git is installed...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    echo Then run this script again.
    pause
    exit /b 1
)
echo ✅ Git is installed

echo.
echo [2/4] Initializing Git repository...
git init
if %errorlevel% neq 0 (
    echo ❌ Failed to initialize Git repository
    pause
    exit /b 1
)
echo ✅ Git repository initialized

echo.
echo [3/4] Adding files to Git...
git add .
if %errorlevel% neq 0 (
    echo ❌ Failed to add files to Git
    pause
    exit /b 1
)
echo ✅ Files added to Git

echo.
echo [4/4] Creating initial commit...
git commit -m "Initial commit: Future Sight AI Data Visualization"
if %errorlevel% neq 0 (
    echo ❌ Failed to create commit
    pause
    exit /b 1
)
echo ✅ Initial commit created

echo.
echo ========================================
echo    Git Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create a repository on GitHub.com
echo 2. Copy the repository URL
echo 3. Run these commands:
echo    git remote add origin YOUR_GITHUB_URL
echo    git branch -M main
echo    git push -u origin main
echo.
echo For detailed instructions, see GITHUB_SETUP.md
echo.
pause

