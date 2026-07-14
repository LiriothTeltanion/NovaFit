@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ============================================================
echo   🏃 NovaFit Setup
echo ============================================================
echo.

call :find_python
if errorlevel 1 goto :fail

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating virtual environment...
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto :fail
) else (
  echo [1/3] Virtual environment already exists.
)

echo [2/3] Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :fail

echo [3/3] Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo.
echo ✅ NovaFit is ready.
exit /b 0

:find_python
where py >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_CMD=py -3"
  exit /b 0
)
where python >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_CMD=python"
  exit /b 0
)
echo ❌ Python 3 was not found.
echo Install Python 3.10 or newer and enable "Add Python to PATH".
exit /b 1

:fail
echo.
echo ❌ Setup failed. Review the error above.
exit /b 1
