@echo off
setlocal EnableExtensions
pushd "%~dp0"
title NovaFit Complete Quality Check

echo ============================================================
echo   NovaFit - Complete Quality Check
echo ============================================================
echo   This checker preserves your local database and exports.
echo.

set "NOVAFIT_NO_PAUSE=1"
call bootstrap_windows.bat
if errorlevel 1 goto :failed

echo.
echo Installing the isolated quality tools...
".venv\Scripts\python.exe" -m pip install --prefer-binary -r requirements-dev.txt
if errorlevel 1 goto :failed

set "PYTHONUTF8=1"
set "MPLBACKEND=Agg"
echo.
echo Running compile, package audit, Ruff, Pyright, tests and smoke exports...
".venv\Scripts\python.exe" scripts\verify.py --quality
if errorlevel 1 goto :failed

rem Keep the package audit visible as an independent, non-destructive final gate.
".venv\Scripts\python.exe" tools\package_audit.py --quiet
if errorlevel 1 goto :failed

echo.
echo ============================================================
echo   NOVAFIT IS VERIFIED AND READY. [OK]
echo ============================================================
popd
if not defined NOVAFIT_NO_PAUSE_PARENT pause
exit /b 0

:failed
echo.
echo ============================================================
echo   NOVAFIT VERIFICATION NEEDS ATTENTION. [ERROR]
echo ============================================================
echo Review the first error above, keep this window open, and retry.
popd
if not defined NOVAFIT_NO_PAUSE_PARENT pause
exit /b 1
