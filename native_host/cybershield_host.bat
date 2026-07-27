@echo off
REM CyberShield Native Messaging Host Launcher
REM This is called by Chrome to start the backend automatically.
REM DO NOT delete this file.

"%~dp0..\venv\Scripts\python.exe" "%~dp0cybershield_host.py" 2>nul
if errorlevel 1 (
    python "%~dp0cybershield_host.py"
)
