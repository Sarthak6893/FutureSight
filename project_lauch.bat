@echo off
echo ========================================
echo     Future Sight Project Launcher
echo ========================================
echo.

REM ----------------------------------------
REM --- 1. Port Conflict Handler (8000 & 3000) ---
REM ----------------------------------------

echo Checking and killing processes on port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    if %%a neq 0 (
        echo Found process on 8000: PID %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

echo Checking and killing processes on port 3000 (Frontend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    if %%a neq 0 (
        echo Found process on 3000: PID %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)
echo Port cleanup complete.

REM ----------------------------------------
REM --- 2. Backend Setup and Launch ---
REM ----------------------------------------

echo.
echo Installing backend requirements...
pushd "%CD%\backend"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to change directory to backend.
    pause
    exit /b
)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend requirements! Ensure requirements.txt is correct.
    pause
    popd
    exit /b
)

echo Starting Backend Server...
echo Backend will run on: http://localhost:8000
REM Using 'start' opens the server in a new, persistent command window
start "FutureSight Backend" cmd /k "uvicorn main:app --reload"
popd

REM Wait for backend to start
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

REM ----------------------------------------
REM --- 3. Frontend Setup and Launch ---
REM ----------------------------------------

echo.
echo Starting Frontend Server...
echo Frontend will run on: http://localhost:3000
pushd "%CD%\frontend"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to change directory to frontend.
    pause
    exit /b
)

echo Running npm install...
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] npm install failed!
    pause
    popd
    exit /b
)

REM --- Fix for 9 vulnerabilities ---
echo Running npm audit fix --force to resolve vulnerabilities...
call npm audit fix --force
echo Vulnerability check complete.

REM --- FINAL FIX: Use the standard npm script call, but wrapped in 'start' for isolation ---
echo Running Frontend application via npm start (in new window)...

REM The START command is essential here. It tells Windows to open a new command window, 
REM which correctly sets up the environment needed to execute the local 'react-scripts' command 
REM defined inside 'npm start'.
start "FutureSight Frontend" cmd /k "npm start"

if %errorlevel% neq 0 (
    echo [ERROR] Frontend failed to launch the command.
    pause
    popd
    exit /b
)
popd

REM ----------------------------------------
REM --- 4. Final Message ---
REM ----------------------------------------

echo.
echo ========================================
echo     Project Launched Successfully!
echo ========================================
echo.
echo Backend (API):  http://localhost:8000 (Check the new window for output)
echo Frontend (App): http://localhost:3000 (Check the new window for output)
echo.
echo Press any key to close this launcher...
pause > nul