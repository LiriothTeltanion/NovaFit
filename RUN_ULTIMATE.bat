@echo off
setlocal
cd /d "%~dp0"
call run_novafit.bat
exit /b %ERRORLEVEL%
