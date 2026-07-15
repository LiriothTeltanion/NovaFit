@echo off
setlocal EnableExtensions EnableDelayedExpansion
pushd "%~dp0"
title NovaFit 4.0 Environment Repair

echo ============================================================
echo   NovaFit 4.0 - Self-Healing Environment Repair
echo ============================================================
echo.

rem Reuse a healthy local environment. This keeps setup fast after the first run.
if exist ".venv\Scripts\python.exe" (
  echo Checking the existing NovaFit virtual environment...
  ".venv\Scripts\python.exe" scripts\bootstrap_environment.py --offline
  if not errorlevel 1 (
    echo Existing environment is healthy. READY
    goto :success
  )
  echo Existing environment is incomplete; it will be rebuilt. WARNING
  rmdir /s /q ".venv" >nul 2>nul
)

set "SETUP_OK=0"
where py >nul 2>nul
if not errorlevel 1 (
  rem Python 3.13 is tried first because binary scientific packages are broadly available.
  for %%V in (3.13 3.14 3.12 3.11 3.10) do (
    if "!SETUP_OK!"=="0" (
      py -%%V -c "import sys; print(sys.version)" >nul 2>nul
      if not errorlevel 1 (
        echo Trying Python %%V through the Windows launcher...
        py -%%V scripts\bootstrap_environment.py --force-recreate
        if not errorlevel 1 set "SETUP_OK=1"
        if "!SETUP_OK!"=="0" (
          echo Python %%V could not complete binary dependency setup; trying another installed version. WARNING
          rmdir /s /q ".venv" >nul 2>nul
        )
      )
    )
  )
)

if "!SETUP_OK!"=="0" (
  where python >nul 2>nul
  if not errorlevel 1 (
    echo Trying the Python command from PATH...
    python scripts\bootstrap_environment.py --force-recreate
    if not errorlevel 1 set "SETUP_OK=1"
  )
)

if "!SETUP_OK!"=="1" goto :success
goto :failed

:success
echo.
echo NovaFit environment repair completed. READY
popd
exit /b 0

:failed
echo.
echo NovaFit could not build a compatible local environment. ERROR
echo Install Python 3.13 x64 from python.org with the Python Launcher enabled,
echo confirm internet access, and run REPAIR_AND_VERIFY.bat again.
popd
if not defined NOVAFIT_NO_PAUSE pause
exit /b 1
