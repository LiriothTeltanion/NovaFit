@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title NovaFit Ultimate - Analytics Gallery

if not exist ".venv\Scripts\python.exe" (
  call setup_windows.bat
  if errorlevel 1 exit /b 1
)

set "PYTHONUTF8=1"
set "MPLBACKEND=Agg"
if not exist "data\reports" mkdir "data\reports"

".venv\Scripts\python.exe" -m novafit.cli --chart "data\reports\01_command_center.png" --chart-view overview --chart-days 30
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m novafit.cli --chart "data\reports\02_trend_lab.png" --chart-view trends --chart-days 60
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m novafit.cli --chart "data\reports\03_consistency_map.png" --chart-view consistency --chart-days 90
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m novafit.cli --chart "data\reports\04_training_atlas.png" --chart-view training_atlas --chart-days 90
if errorlevel 1 goto :failed

echo.
echo Four high-resolution analytics workspaces were created in data\reports. READY
start "" "data\reports"
exit /b 0

:failed
echo.
echo Analytics export failed. Run REPAIR_AND_VERIFY.bat for details. ERROR
pause
exit /b 1
