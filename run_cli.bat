@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title NovaFit CLI

if not exist ".venv\Scripts\python.exe" (
  set "NOVAFIT_NO_PAUSE_PARENT=1"
  call setup_windows.bat
  if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -c "import matplotlib, tzdata" >nul 2>nul
if errorlevel 1 (
  set "NOVAFIT_NO_PAUSE_PARENT=1"
  call setup_windows.bat
  if errorlevel 1 exit /b 1
)
set "PYTHONUTF8=1"
".venv\Scripts\python.exe" -m novafit.cli --menu
pause
