@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title NovaFit 4.0 Setup

set "NOVAFIT_NO_PAUSE=1"
call bootstrap_windows.bat
if errorlevel 1 goto :failed

set "PYTHONUTF8=1"
set "MPLBACKEND=Agg"
echo.
echo Running NovaFit verification inside the repaired local environment...
".venv\Scripts\python.exe" scripts\verify.py
if errorlevel 1 goto :failed

echo.
echo Setup and verification completed successfully. READY
echo Double-click run_novafit.bat to open the desktop application.
echo.
if not defined NOVAFIT_NO_PAUSE_PARENT pause
exit /b 0

:failed
echo.
echo Setup did not finish. ERROR
echo The checker now installs Matplotlib, Pillow, Faker, Requests, and tzdata automatically.
echo Review the first error above, confirm internet access, then rerun this file.
echo.
if not defined NOVAFIT_NO_PAUSE_PARENT pause
exit /b 1
