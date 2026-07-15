@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title NovaFit Self-Healing Verification

set "NOVAFIT_NO_PAUSE=1"
call bootstrap_windows.bat
if errorlevel 1 goto :failed

set "PYTHONUTF8=1"
set "MPLBACKEND=Agg"
".venv\Scripts\python.exe" scripts\verify.py
set "RESULT=%ERRORLEVEL%"
echo.
if "%RESULT%"=="0" (
  echo NovaFit verification passed. READY
) else (
  echo NovaFit verification failed. ERROR
)
if not defined NOVAFIT_NO_PAUSE_PARENT pause
exit /b %RESULT%

:failed
echo NovaFit environment repair failed. ERROR
if not defined NOVAFIT_NO_PAUSE_PARENT pause
exit /b 1
