@echo off
setlocal EnableExtensions
pushd "%~dp0"
title NovaFit - One Click Launch

echo ============================================================
echo   NovaFit - One Click Launch
echo ============================================================
echo   Project: %CD%
echo.

set "NEEDS_REPAIR=0"
if not exist ".venv\Scripts\python.exe" set "NEEDS_REPAIR=1"
if "%NEEDS_REPAIR%"=="0" (
  ".venv\Scripts\python.exe" -c "import tkinter, matplotlib, PIL, requests, faker, tzdata; from zoneinfo import ZoneInfo; ZoneInfo('Asia/Jerusalem')" >nul 2>nul
  if errorlevel 1 set "NEEDS_REPAIR=1"
)
if "%NEEDS_REPAIR%"=="1" (
  echo Preparing NovaFit for the first launch. This can take a few minutes...
  set "NOVAFIT_NO_PAUSE=1"
  call bootstrap_windows.bat
  if errorlevel 1 goto :failed
)

set "PYTHONUTF8=1"
echo Opening your NovaFit command center...
".venv\Scripts\python.exe" -m novafit --gui
if errorlevel 1 (
  goto :failed
)
popd
exit /b 0

:failed
echo.
echo NovaFit could not open. Double-click VERIFY_ALL.bat for a complete repair and diagnosis.
popd
pause
exit /b 1
