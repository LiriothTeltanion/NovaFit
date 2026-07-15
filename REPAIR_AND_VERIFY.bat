@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "NOVAFIT_NO_PAUSE_PARENT=1"
call verify_windows.bat
set "RESULT=%ERRORLEVEL%"
echo.
if "%RESULT%"=="0" echo Repair and verification completed successfully. READY
if not "%RESULT%"=="0" echo Repair or verification failed. Review the message above. ERROR
pause
exit /b %RESULT%
