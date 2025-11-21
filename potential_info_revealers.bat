@echo off
REM This file contains commands that may reveal sensitive information.

echo --- System Information ---
systeminfo | findstr /i "OS Name" 
systeminfo | findstr /i "OS Version"
echo.
echo --- Network Configuration ---
ipconfig /all
echo.
echo --- Current User ---
echo %USERNAME%
echo.
echo --- Installed Applications ---
wmic product get name, version