"""
File Upload & Management API Routes
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from services.file_service import (
    validate_file_extension,
    read_uploaded_file,
    validate_schema,
    run_quality_checks,
    calculate_quality_score,
    process_upload,
)
from services.duckdb_service import DuckDBService

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_category: str = Form(...),
    upload_mode: str = Form("replace"),
    uploaded_by: str = Form("system"),
):
    """Upload and process a data file"""
    # Validate extension
    if not validate_file_extension(file.filename):
        raise HTTPException(400, "Invalid file format. Use .csv or .xlsx")

    # Validate category
    valid_categories = ["sales", "inventory", "supplier", "purchase_order"]
    if file_category not in valid_categories:
        raise HTTPException(400, f"Invalid category. Use one of: {valid_categories}")

    # Read file bytes
    file_bytes = await file.read()

    # Process upload
    result = process_upload(
        file_bytes=file_bytes,
        filename=file.filename,
        file_category=file_category,
        upload_mode=upload_mode,
        uploaded_by=uploaded_by,
    )

    if result["status"] == "error":
        raise HTTPException(400, result)

    return result


@router.post("/validate")
async def validate_file(
    file: UploadFile = File(...),
    file_category: str = Form(...),
):
    """Validate a file without uploading it"""
    if not validate_file_extension(file.filename):
        raise HTTPException(400, "Invalid file format")

    file_bytes = await file.read()

    try:
        df = read_uploaded_file(file_bytes, file.filename)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    except Exception as e:
        raise HTTPException(400, f"Failed to read file: {str(e)}")

    # Schema validation
    schema_result = validate_schema(df, file_category)

    # Quality checks
    df_clean, issues = run_quality_checks(df, file_category)
    quality_score = calculate_quality_score(len(df), len(df_clean), issues)

    # Preview data (first 10 rows)
    preview = df.head(10).fillna("").to_dict("records")

    return {
        "valid": schema_result["valid"],
        "schema_valid": schema_result["schema_valid"],
        "required_columns_present": schema_result["required_columns_present"],
        "missing_columns": schema_result["missing_columns"],
        "extra_columns": schema_result["extra_columns"],
        "total_rows": len(df),
        "valid_rows": len(df_clean),
        "rejected_rows": len(df) - len(df_clean),
        "quality_score": quality_score,
        "issues": issues,
        "preview_data": preview,
    }


@router.get("/status")
async def get_all_file_status():
    """Get upload status for all file categories"""
    db = DuckDBService()
    return db.get_all_file_status()


@router.get("/status/{file_category}")
async def get_file_status(file_category: str):
    """Get upload status for a specific category"""
    db = DuckDBService()
    status = db.get_all_file_status()
    if file_category not in status:
        raise HTTPException(404, f"Unknown category: {file_category}")
    return status[file_category]


@router.get("/history/{file_category}")
async def get_file_history(file_category: str):
    """Get version history for a file category"""
    db = DuckDBService()
    return db.get_file_history(file_category)


@router.get("/preview/{file_category}")
async def get_data_preview(file_category: str, limit: int = 100):
    """Get a preview of uploaded data"""
    db = DuckDBService()
    data = db.get_data_preview(file_category, limit)
    total = db.get_row_count(file_category)
    return {"data": data, "total_rows": total}


@router.get("/schema/{file_category}")
async def get_file_schema(file_category: str):
    """Get the expected schema for a file category"""
    from core.config import settings

    rules = settings.SCHEMA_RULES.get(file_category)
    if not rules:
        raise HTTPException(404, f"Unknown category: {file_category}")
    return rules
