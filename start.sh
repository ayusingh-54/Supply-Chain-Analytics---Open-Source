#!/bin/bash
set -e

echo "============================================"
echo " Supply Chain Analytics - Quick Start"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed."
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "[1/5] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[1/5] Virtual environment already exists."
fi

# Activate
echo "[2/5] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[3/5] Installing dependencies..."
pip install -r requirements.txt -q

# Initialize database
echo "[4/5] Setting up database..."
python scripts/setup_database.py

# Copy .env
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || true
    echo "       Created .env from template"
fi

# Create directories
mkdir -p data uploads

echo "[5/5] Starting services..."
echo ""
echo "  Backend API:  http://localhost:8000"
echo "  Streamlit UI: http://localhost:8501"
echo "  API Docs:     http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

# Start backend in background
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend
sleep 3

# Start Streamlit
streamlit run streamlit_app/app.py --server.port 8501

# Cleanup
kill $BACKEND_PID 2>/dev/null || true
