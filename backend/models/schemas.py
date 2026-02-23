"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── File Upload ──────────────────────────────────────────────

class FileUploadResponse(BaseModel):
    status: str
    upload_id: int
    file_category: str
    filename: str
    row_count: int
    quality_score: float
    issues: List[Dict[str, Any]] = []
    message: str = ""


class FileValidationResponse(BaseModel):
    valid: bool
    schema_valid: bool
    required_columns_present: List[str] = []
    missing_columns: List[str] = []
    extra_columns: List[str] = []
    total_rows: int = 0
    valid_rows: int = 0
    rejected_rows: int = 0
    quality_score: float = 0
    issues: List[Dict[str, Any]] = []
    preview_data: List[Dict[str, Any]] = []


class FileStatusResponse(BaseModel):
    file_category: str
    status: str  # 'active', 'missing', 'outdated'
    filename: Optional[str] = None
    upload_timestamp: Optional[str] = None
    uploaded_by: Optional[str] = None
    row_count: int = 0
    quality_score: float = 0
    needs_refresh: bool = False


class FileHistoryResponse(BaseModel):
    category: str
    current: Optional[Dict[str, Any]] = None
    versions: List[Dict[str, Any]] = []


# ─── Database Refresh ─────────────────────────────────────────

class RefreshRequest(BaseModel):
    mode: str = "full"  # full|incremental
    file_categories: Optional[List[str]] = None


class RefreshResponse(BaseModel):
    status: str
    message: str = ""
    files_refreshed: List[str] = []


# ─── MCP Config ───────────────────────────────────────────────

class MCPConfigResponse(BaseModel):
    claude_desktop: Dict[str, Any]
    claude_code: Dict[str, Any]
    cursor: Dict[str, Any]
    instructions: str = ""
