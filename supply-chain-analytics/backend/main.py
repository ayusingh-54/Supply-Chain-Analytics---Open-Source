"""
FastAPI Backend - Main Application
Supply Chain Analytics System
"""
import sys
import os

# Add parent directory so imports work when running from backend/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import files, database, templates, mcp_config
from core.database import get_connection

app = FastAPI(
    title="Supply Chain Analytics API",
    description="Backend API for file upload, validation, and supply chain analytics",
    version="1.0.0",
)

# CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(database.router, prefix="/api/database", tags=["Database"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(mcp_config.router, prefix="/api/mcp", tags=["MCP Config"])


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    get_connection()


@app.get("/")
async def root():
    return {
        "name": "Supply Chain Analytics API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health():
    try:
        conn = get_connection()
        conn.execute("SELECT 1").fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
