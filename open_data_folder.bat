@echo off
setlocal
cd /d "%~dp0"
if not exist "data" mkdir "data"
start "" "data"
