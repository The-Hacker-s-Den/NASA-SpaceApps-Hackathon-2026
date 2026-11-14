@echo off
setlocal
cd /d "%~dp0"

echo ======================================================================
echo    The Hackers Den - NASA Field Shift Weather AI
echo ======================================================================
echo.

rem Check for virtual environment in prithvi-env or venv
if exist "prithvi-env\Scripts\python.exe" (
    set "PY_EXE=prithvi-env\Scripts\python.exe"
    goto RUN
)
if exist "venv\Scripts\python.exe" (
    set "PY_EXE=venv\Scripts\python.exe"
    goto RUN
)

rem If no virtual environment, create one
echo [*] No existing virtual environment found.
echo [*] Creating virtual environment 'venv'...
python -m venv venv
if errorlevel 1 (
    echo [!] Failed to create venv. Ensure Python 3.10+ is installed and in your PATH.
    pause
    exit /b 1
)

set "PY_EXE=venv\Scripts\python.exe"
echo [*] Installing dependencies from requirements.txt...
"%PY_EXE%" -m pip install --upgrade pip
"%PY_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [!] Warning: Some dependencies failed to install.
)

:RUN
echo.
echo [*] Starting NASA Field Shift AI GUI Server on port 5000...
echo [*] Open your browser to: http://127.0.0.1:5000
echo.
"%PY_EXE%" prithvi_weather_gui.py --port 5000
pause
