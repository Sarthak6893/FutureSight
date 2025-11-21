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
echo [2/6] Checking Git repository...
if not exist ".git" (
    echo Initializing new Git repository...
    git init
    if %errorlevel% neq 0 (
        echo ❌ Failed to initialize Git repository
        pause
        exit /b 1
    )
    echo ✅ Git repository initialized
) else (
    echo ✅ Git repository already exists
)

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
echo [4/6] Checking for changes...
git diff --quiet --exit-code
if %errorlevel% equ 0 (
    git diff --cached --quiet --exit-code
    if %errorlevel% equ 0 (
        echo ℹ️  No changes to commit
        echo Skipping commit step...
        goto :push
    )
)

echo Creating commit...
git commit -m "Update: Future Sight AI Data Visualization Platform"
if %errorlevel% neq 0 (
    echo ⚠️  No changes to commit or commit failed
    echo Continuing with push...
)
echo ✅ Commit created or skipped

:push

echo.
echo [5/6] Checking remote repository...
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo Adding remote origin...
    git remote add origin https://github.com/sarthak6893/FutureSight.git
    if %errorlevel% neq 0 (
        echo ❌ Failed to add remote origin
        pause
        exit /b 1
    )
    echo ✅ Remote origin added
) else (
    echo Checking if remote URL is correct...
    git remote get-url origin | findstr /C:"sarthak6893/FutureSight" >nul 2>&1
    if %errorlevel% neq 0 (
        echo Updating remote URL to correct repository...
        git remote set-url origin https://github.com/sarthak6893/FutureSight.git
        if %errorlevel% neq 0 (
            echo ❌ Failed to update remote origin
            pause
            exit /b 1
        )
        echo ✅ Remote origin updated
    ) else (
        echo ✅ Remote origin already configured correctly
    )
)

echo.
echo [6/6] Pushing to GitHub...
git branch -M main
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Failed to rename branch to main
    echo Continuing anyway...
)

echo.
echo Checking if there are commits to push...
git log origin/main..HEAD --oneline >nul 2>&1
if %errorlevel% equ 0 (
    echo Found commits to push
) else (
    echo Checking if this is the first push...
    git ls-remote --heads origin main >nul 2>&1
    if %errorlevel% neq 0 (
        echo This appears to be the first push to the repository
    ) else (
        echo ℹ️  No new commits to push - repository is up to date
        echo.
        echo ========================================
        echo    Repository is already up to date!
        echo ========================================
        echo.
        echo Your repository is available at:
        echo https://github.com/sarthak6893/FutureSight
        echo.
        pause
        exit /b 0
    )
)

echo.
echo Attempting to push to GitHub...
echo Note: You may be prompted for GitHub credentials
echo If prompted, use your GitHub username and Personal Access Token (not password)
echo.
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to push to GitHub
    echo.
    echo Common issues and solutions:
    echo.
    echo 1. **Authentication Required:**
    echo    - GitHub now requires a Personal Access Token (PAT) instead of password
    echo    - Go to: https://github.com/settings/tokens
    echo    - Create a new token with 'repo' permissions
    echo    - Use the token as your password when prompted
    echo.
    echo 2. **Repository doesn't exist:**
    echo    - Make sure the repository exists at: https://github.com/sarthak6893/FutureSight
    echo    - If it doesn't exist, create it on GitHub first
    echo.
    echo 3. **Network issues:**
    echo    - Check your internet connection
    echo    - Try again in a few moments
    echo.
    echo 4. **Try manual push:**
    echo    - Open Git Bash or Command Prompt
    echo    - Run: git push -u origin main
    echo    - Enter your GitHub username and Personal Access Token when prompted
    echo.
    echo Current remote URL:
    git remote get-url origin
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    SUCCESS! Project Pushed to GitHub
echo ========================================
echo.
echo Your repository is now available at:
echo https://github.com/sarthak6893/FutureSight
echo.
echo 🎉 Future Sight is now live on GitHub!
echo.
pause


