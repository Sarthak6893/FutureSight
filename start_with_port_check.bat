@echo off
echo ========================================
echo    Future Sight - Port Conflict Handler
echo ========================================
echo.

REM Kill processes on ports 8000 and 3000
echo Checking for processes using port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Found process using port 8000: PID %%a
    echo Killing process %%a...
    taskkill /PID %%a /F >nul 2>&1
)

echo Checking for processes using port 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo Found process using port 3000: PID %%a
    echo Killing process %%a...
    taskkill /PID %%a /F >nul 2>&1
)

REM Install backend requirements
echo.
echo Installing backend requirements...
pushd "%CD%\backend"
if %errorlevel% neq 0 (
    echo Failed to change directory to backend
    pause
    exit /b
)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install backend requirements!
    pause
    popd
    exit /b
)

REM Start backend in a new window, in backend folder
echo Starting Backend Server...
echo Backend will run on: http://localhost:8000
start "Backend" cmd /k "cd /d %CD% && uvicorn main:app --reload"
popd

REM Wait for backend to start
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

REM Start frontend
echo Starting Frontend Server...
echo Frontend will run on: http://localhost:3000
pushd "%CD%\frontend"
call npm install
if %errorlevel% neq 0 (
    echo npm install failed!
    pause
    popd
    exit /b
)
call npm start
if %errorlevel% neq 0 (
    echo Frontend failed to start!
    pause
    popd
    exit /b
)
popd

REM Success message
echo.
echo ========================================
echo    Project Started Successfully!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit this launcher...
pause > nul



