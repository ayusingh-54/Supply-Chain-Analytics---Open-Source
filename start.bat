@echo off
echo ============================================
echo  Supply Chain Analytics - Quick Start
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Create virtual environment if not exists
if not exist "venv" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/5] Virtual environment already exists.
)

:: Activate venv
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo [3/5] Installing dependencies...
pip install -r requirements.txt -q

:: Initialize database
echo [4/5] Setting up database...
python scripts\setup_database.py

:: Copy .env if not exists
if not exist ".env" (
    copy .env.example .env > nul 2>&1
    echo        Created .env from template
)

:: Create directories
if not exist "data" mkdir data
if not exist "uploads" mkdir uploads

echo [5/5] Starting services...
echo.
echo   Backend API:  http://localhost:8000
echo   Streamlit UI: http://localhost:8501
echo   API Docs:     http://localhost:8000/docs
echo.
echo   Press Ctrl+C to stop.
echo.

:: Start backend in background
start "SC-Backend" cmd /c "venv\Scripts\activate.bat && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

:: Wait a moment for backend to start
timeout /t 3 /nobreak > nul

:: Start Streamlit
streamlit run streamlit_app/app.py --server.port 8501
