@echo off
echo ========================================
echo    Future Sight - Port Conflict Handler
echo ========================================
echo.

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

echo.
echo Starting Backend Server...
echo Backend will run on: http://localhost:8000
echo.
start "Future Sight Backend" cmd /k "cd /d %CD%\backend && call venv\Scripts\activate.bat && python main.py"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
echo Frontend will run on: http://localhost:3000
echo.
start "Future Sight Frontend" cmd /k "cd /d %CD%\frontend && npm start"

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



