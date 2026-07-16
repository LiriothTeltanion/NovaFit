@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "MPLBACKEND=Agg"
set "BUILD_VENV=build\standalone-venv"

echo.
echo ============================================================
echo   NovaFit - verified standalone Windows builder
echo ============================================================
echo.

if not exist "%BUILD_VENV%\Scripts\python.exe" (
    echo [1/5] Creating an isolated Python 3.13 build environment...
    py -3.13 -m venv "%BUILD_VENV%"
    if errorlevel 1 goto :failed
) else (
    echo [1/5] Reusing the isolated Python 3.13 build environment.
)

echo [2/5] Installing runtime and packaging tools...
"%BUILD_VENV%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
"%BUILD_VENV%\Scripts\python.exe" -m pip install --prefer-binary -r requirements-dev.txt -r requirements-build.txt
if errorlevel 1 goto :failed

echo [3/5] Running tests, static checks, and isolated smoke checks...
"%BUILD_VENV%\Scripts\python.exe" scripts\verify.py --quality
if errorlevel 1 goto :failed

echo [4/5] Regenerating the Windows icon...
"%BUILD_VENV%\Scripts\python.exe" scripts\generate_windows_icon.py
if errorlevel 1 goto :failed

echo [5/5] Building, auditing, smoke-testing, and hashing the standalone ZIP...
"%BUILD_VENV%\Scripts\python.exe" scripts\build_windows_distribution.py
if errorlevel 1 goto :failed

echo.
echo Standalone build completed successfully.
echo Open the dist folder to find the versioned ZIP and .sha256 file.
start "NovaFit standalone artifacts" "%~dp0dist"
echo.
pause
exit /b 0

:failed
echo.
echo Standalone build failed. Review the first error above.
echo No personal data was added to the package.
echo.
pause
exit /b 1
