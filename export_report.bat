@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title NovaFit Offline Report

if not exist ".venv\Scripts\python.exe" (
  call setup_windows.bat
  if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"
set "PYTHONUTF8=1"
set "MPLBACKEND=Agg"
if not exist "data\reports" mkdir "data\reports"
python -m novafit.cli --report-html "data\reports\novafit_report.html" --chart-view overview --chart-days 30
if errorlevel 1 goto :failed

echo.
echo Offline report created successfully.
start "" "data\reports\novafit_report.html"
exit /b 0

:failed
echo.
echo Report export failed. Run verify_windows.bat for details.
pause
exit /b 1
