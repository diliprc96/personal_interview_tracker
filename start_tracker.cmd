@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo ======================================
echo Interview Tracker - Startup
echo ======================================

set "PY_LAUNCH=python"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PY_LAUNCH=py -3"
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PY_LAUNCH% -m venv .venv
    if %ERRORLEVEL% NEQ 0 goto :error
)

call ".venv\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 goto :error

echo Installing dependencies (if needed)...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 goto :error

echo Starting Interview Tracker...
echo Web UI: http://127.0.0.1:8000
echo Press Ctrl+C in this window to stop the app.
start "" http://127.0.0.1:8000
python main.py
goto :end

:error
echo.
echo Startup failed. Check error messages above.
echo.
pause
exit /b 1

:end
endlocal
