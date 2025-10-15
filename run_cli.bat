@echo off
setlocal
set CURRENT_DIR=%~dp0
cd /d %CURRENT_DIR%
if not exist "%CURRENT_DIR%novafit" (
	echo ERROR: Ejecuta este archivo desde la carpeta NovaFit donde está la carpeta 'novafit'.
	echo.
	echo Presiona una tecla para cerrar...
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