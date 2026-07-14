@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title NovaFit GUI

if not exist "novafit\gui.py" (
  echo ❌ NovaFit source files are missing.
  echo Expected: %CD%\novafit\gui.py
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
echo 🖼️ Starting NovaFit GUI...
echo.
".venv\Scripts\python.exe" -m novafit.gui %*
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo.
  echo ❌ NovaFit GUI stopped with exit code %EXIT_CODE%.
  pause
)
exit /b %EXIT_CODE%
