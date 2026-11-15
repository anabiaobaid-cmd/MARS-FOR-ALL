@echo off
setlocal enabledelayedexpansion

title MARS FOR ALL - The Analog Atlas
cd /d "%~dp0"

echo ======================================================================
echo             MARS FOR ALL - THE ANALOG ATLAS
echo      Earth is our testing ground. Space is our frontier.
echo               NASA Space Apps Challenge 2026
echo ======================================================================
echo.

:: Detect Python executable
set "PY_CMD="

if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
    echo [*] Found local virtual environment: .venv
    goto :found_python
)

if exist "venv\Scripts\python.exe" (
    set "PY_CMD=venv\Scripts\python.exe"
    echo [*] Found local virtual environment: venv
    goto :found_python
)

py -3.13 --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=py -3.13"
    echo [*] Using Python 3.13 via py launcher
    goto :found_python
)

py --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=py"
    echo [*] Using default py launcher
    goto :found_python
)

python --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=python"
    echo [*] Using python command from PATH
    goto :found_python
)

echo [!] Error: Python was not found on your system.
echo     Please install Python 3.13 or add Python to your PATH.
echo.
pause
exit /b 1

:found_python
echo [*] Launching Analog Atlas web server...
echo [*] Opening browser at http://127.0.0.1:5000 in 3 seconds...
echo.

start "" /min cmd /c "timeout /t 3 >nul & start http://127.0.0.1:5000"

%PY_CMD% "src\backend\app.py"

if errorlevel 1 (
    echo.
    echo [!] Application stopped with an error code.
    echo     Please verify required dependencies: pip install -r requirements.txt
    pause
)
