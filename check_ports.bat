@echo off
echo ========================================
echo    Port Checker Utility
echo ========================================
echo.

echo Checking port 8000 (Backend)...
netstat -ano | findstr :8000
if %errorlevel% equ 0 (
    echo ❌ Port 8000 is BUSY
    echo.
    echo To kill the process using port 8000, run:
    echo taskkill /PID [PID_NUMBER] /F
    echo.
) else (
    echo ✅ Port 8000 is FREE
)

echo.
echo Checking port 3000 (Frontend)...
netstat -ano | findstr :3000
if %errorlevel% equ 0 (
    echo ❌ Port 3000 is BUSY
    echo.
    echo To kill the process using port 3000, run:
    echo taskkill /PID [PID_NUMBER] /F
    echo.
) else (
    echo ✅ Port 3000 is FREE
)

echo.
echo ========================================
echo    Port Status Complete
echo ========================================
echo.
echo If ports are busy, you can:
echo 1. Kill the processes using the PIDs shown above
echo 2. Use start_alternative_ports.bat to use different ports
echo 3. Use start_with_port_check.bat to auto-kill conflicting processes
echo.
pause



