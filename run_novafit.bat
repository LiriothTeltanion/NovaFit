@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title NovaFit Ultimate 4.0 Edition

set "NEEDS_REPAIR=0"
if not exist ".venv\Scripts\python.exe" set "NEEDS_REPAIR=1"
if "%NEEDS_REPAIR%"=="0" (
  ".venv\Scripts\python.exe" -c "import matplotlib, PIL, requests, faker, tzdata; from zoneinfo import ZoneInfo; ZoneInfo('Asia/Jerusalem')" >nul 2>nul
  if errorlevel 1 set "NEEDS_REPAIR=1"
)
if "%NEEDS_REPAIR%"=="1" (
  echo NovaFit is creating or repairing its local environment...
  set "NOVAFIT_NO_PAUSE_PARENT=1"
  call setup_windows.bat
  if errorlevel 1 exit /b 1
)

set "PYTHONUTF8=1"
".venv\Scripts\python.exe" -m novafit --gui
if errorlevel 1 (
  echo.
  echo NovaFit closed with an error. Run REPAIR_AND_VERIFY.bat for details.
  pause
)
