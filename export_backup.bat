@echo off
setlocal EnableExtensions
pushd "%~dp0"
title NovaFit Complete Backup
set "PYTHONUTF8=1"

set "NEEDS_REPAIR=0"
if not exist ".venv\Scripts\python.exe" set "NEEDS_REPAIR=1"
if "%NEEDS_REPAIR%"=="0" (
  ".venv\Scripts\python.exe" -c "from novafit.backup import create_complete_backup" >nul 2>nul
  if errorlevel 1 set "NEEDS_REPAIR=1"
)
if "%NEEDS_REPAIR%"=="1" (
  set "NOVAFIT_NO_PAUSE=1"
  call bootstrap_windows.bat
  if errorlevel 1 goto :failed
)

if not exist "data\backups" mkdir "data\backups"
".venv\Scripts\python.exe" -m novafit.cli --backup "data\backups"
if errorlevel 1 goto :failed
echo.
echo Complete all-profile backup created and verified. [OK]
echo Backup folder: %CD%\data\backups
start "" "data\backups"
popd
pause
exit /b 0

:failed
echo.
echo Complete backup failed. Run VERIFY_ALL.bat for a full diagnosis. [ERROR]
popd
pause
exit /b 1
