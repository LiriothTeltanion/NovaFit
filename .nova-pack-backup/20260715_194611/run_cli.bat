@echo off
setlocal
set CURRENT_DIR=%~dp0
cd /d %CURRENT_DIR%
if not exist "%CURRENT_DIR%novafit" (
	echo ERROR: Run this file from the NovaFit folder where the 'novafit' folder is located.
	echo.
	echo Press any key to close...
	pause >nul
	exit /b
)
echo ========================================
echo      NovaFit - CLI Interface
echo ========================================
echo.
python -m novafit.cli
echo.
echo Press any key to close...
pause >nul