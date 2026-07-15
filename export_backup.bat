@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  call setup_windows.bat
  if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"
set "PYTHONUTF8=1"
python -m novafit.cli --export-json data\novafit_export.json
if errorlevel 1 goto :failed
python -m novafit.cli --export-csv data\novafit_export.csv
if errorlevel 1 goto :failed
echo.
echo Backups are available inside the data folder.
start "" "data"
pause
exit /b 0

:failed
echo.
echo Backup export failed. Run verify_windows.bat for details.
pause
exit /b 1
