@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title NovaFit CLI

if not exist "novafit\cli.py" (
  echo ❌ NovaFit source files are missing.
  echo Expected: %CD%\novafit\cli.py
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  call "%~dp0setup.bat"
  if errorlevel 1 (
    pause
    exit /b 1
  )
)

echo.
echo 🏃 Starting NovaFit CLI...
echo.
".venv\Scripts\python.exe" -m novafit.cli %*
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo.
  echo ❌ NovaFit CLI stopped with exit code %EXIT_CODE%.
  pause
)
exit /b %EXIT_CODE%
