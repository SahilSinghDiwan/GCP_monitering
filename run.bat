@echo off
setlocal enabledelayedexpansion

:: Colors for output
set "RED=<NUL set /p=^[<NUL>&2 set /p=31m<NUL>"
set "GREEN=<NUL set /p=^[<NUL>&2 set /p=32m<NUL>"
set "YELLOW=<NUL set /p=^[<NUL>&2 set /p=33m<NUL>"
set "NC=<NUL set /p=^[<NUL>&2 set /p=0m<NUL>"

:: Function to log messages
:log
    echo [%DATE% %TIME%] %*
    echo [%DATE% %TIME%] %* >> logs\app.log
goto :eof

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    set "ADMIN=1"
) else (
    set "ADMIN=0"
)

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Check Python installation
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%Python not found. Installing Python...%NC%
    if %ADMIN%==1 (
        choco install python -y
    ) else (
        echo %RED%Please run this script as administrator to install Python%NC%
        pause
        exit /b 1
    )
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo %RED%Failed to activate virtual environment%NC%
    pause
    exit /b 1
)

echo Updating pip and installing dependencies...
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo %RED%Failed to upgrade pip%NC%
    pause
    exit /b 1
)

pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%Failed to install some dependencies. Continuing anyway...%NC%
)

:: Check if gcloud is installed
where gcloud >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Google Cloud SDK not found. Installing...
    if %ADMIN%==1 (
        choco install gcloudsdk -y
    ) else (
        echo %YELLOW%Please run this script as administrator to install Google Cloud SDK%NC%
    )
)

:: Authenticate with service account if credentials.json exists
if exist "credentials.json" (
    echo Authenticating with service account...
    gcloud auth activate-service-account --key-file=credentials.json
) else (
    echo %YELLOW%Warning: credentials.json not found. Some GCP functionality may be limited.%NC%
)

:: Run the application
echo %GREEN%Starting GCP Monitor...%NC%
python main.py

if "%1"=="--background" (
    start "GCP Monitor" /B python main.py ^> logs\app.log 2>&1
    echo GCP Monitor is running in the background. Check logs\app.log for output.
    echo To stop the application, close the terminal or use Task Manager.
) else (
    python main.py
)

pause
