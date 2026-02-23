"""
File Service - Handles file upload, validation, processing, and storage
"""
import pandas as pd
import os
import shutil
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from core.config import settings
from services.duckdb_service import DuckDBService


def _get_storage_path(subdir: str) -> str:
    """Get absolute storage path"""
    base = settings.STORAGE_PATH
    if not os.path.isabs(base):
        base = os.path.join(settings.BASE_DIR, base)
    path = os.path.join(base, subdir)
    os.makedirs(path, exist_ok=True)
    return path


def validate_file_extension(filename: str) -> bool:
    """Check if the file extension is allowed"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in settings.ALLOWED_EXTENSIONS


def read_uploaded_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Read uploaded file bytes into a DataFrame"""
    import io

    ext = os.path.splitext(filename)[1].lower()
    if ext == ".csv":
        return pd.read_csv(io.BytesIO(file_bytes))
    elif ext == ".xlsx":
        return pd.read_excel(io.BytesIO(file_bytes))
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def validate_schema(df: pd.DataFrame, file_category: str) -> Dict[str, Any]:
    """Validate DataFrame against the schema rules for a category"""
    rules = settings.SCHEMA_RULES.get(file_category)
    if not rules:
        return {"valid": False, "errors": [{"type": "unknown_category", "message": f"Unknown category: {file_category}"}]}

    errors = []
    required = rules["required_columns"]
    optional = rules.get("optional_columns", [])

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Check required columns
    present_required = [c for c in required if c in df.columns]
    missing = [c for c in required if c not in df.columns]

    if missing:
        errors.append({
            "type": "missing_columns",
            "severity": "critical",
            "columns": missing,
            "message": f"Missing required columns: {', '.join(missing)}",
        })

    # Extra columns (not required or optional)
    all_known = set(required + optional)
    extra = [c for c in df.columns if c not in all_known]

    return {
        "valid": len(missing) == 0,
        "schema_valid": len(missing) == 0,
        "required_columns_present": present_required,
        "missing_columns": missing,
        "extra_columns": extra,
        "errors": errors,
    }


def run_quality_checks(df: pd.DataFrame, file_category: str) -> Tuple[pd.DataFrame, List[Dict]]:
    """Run data quality checks and return cleaned DataFrame + issues list"""
    issues = []
    df_clean = df.copy()

    # 1. Duplicate detection
    duplicates = df_clean[df_clean.duplicated()]
    if len(duplicates) > 0:
        df_clean = df_clean.drop_duplicates()
        issues.append({
            "type": "duplicate_rows",
            "severity": "warning",
            "count": len(duplicates),
            "auto_resolved": True,
            "message": f"Removed {len(duplicates)} duplicate rows",
        })

    # 2. Null values in required columns
    required = settings.SCHEMA_RULES.get(file_category, {}).get("required_columns", [])
    for col in required:
        if col in df_clean.columns:
            null_count = df_clean[col].isnull().sum()
            if null_count > 0:
                df_clean = df_clean.dropna(subset=[col])
                issues.append({
                    "type": "null_required_field",
                    "severity": "error",
                    "count": int(null_count),
                    "column": col,
                    "auto_resolved": True,
                    "message": f"Removed {null_count} rows with null '{col}'",
                })

    # 3. Negative values check
    constraints = settings.SCHEMA_RULES.get(file_category, {}).get("constraints", {})
    for col, constraint in constraints.items():
        if col in df_clean.columns and "min" in constraint:
            min_val = constraint["min"]
            negative = df_clean[df_clean[col] < min_val]
            if len(negative) > 0:
                df_clean = df_clean[df_clean[col] >= min_val]
                issues.append({
                    "type": "constraint_violation",
                    "severity": "warning",
                    "count": len(negative),
                    "column": col,
                    "auto_resolved": True,
                    "message": f"Removed {len(negative)} rows where '{col}' < {min_val}",
                })

    # 4. Date validation for sales
    if file_category == "sales" and "date" in df_clean.columns:
        try:
            df_clean["date"] = pd.to_datetime(df_clean["date"], errors="coerce")
            future_dates = df_clean[df_clean["date"] > pd.Timestamp.now()]
            if len(future_dates) > 0:
                issues.append({
                    "type": "future_dates",
                    "severity": "warning",
                    "count": len(future_dates),
                    "auto_resolved": False,
                    "message": f"{len(future_dates)} rows have future dates",
                })
        except Exception:
            pass

    return df_clean, issues


def calculate_quality_score(total_rows: int, valid_rows: int, issues: List[Dict]) -> float:
    """Calculate a quality score 0-100"""
    if total_rows == 0:
        return 0.0

    base_score = (valid_rows / total_rows) * 100

    # Deduct for unresolved issues
    unresolved = [i for i in issues if not i.get("auto_resolved", False)]
    penalty = len(unresolved) * 2  # 2 points per unresolved issue

    return max(0.0, min(100.0, round(base_score - penalty, 2)))


def process_upload(
    file_bytes: bytes,
    filename: str,
    file_category: str,
    upload_mode: str = "replace",
    uploaded_by: str = "system",
) -> Dict[str, Any]:
    """
    Full upload processing pipeline:
    1. Read file
    2. Validate schema
    3. Run quality checks
    4. Store file
    5. Load to database
    6. Record metadata
    """
    db_service = DuckDBService()

    # Step 1: Read file
    df = read_uploaded_file(file_bytes, filename)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    total_rows = len(df)

    # Step 2: Validate schema
    schema_result = validate_schema(df, file_category)
    if not schema_result["valid"]:
        # Save to rejected folder
        rejected_path = os.path.join(_get_storage_path("rejected"), filename)
        with open(rejected_path, "wb") as f:
            f.write(file_bytes)
        return {
            "status": "error",
            "message": "Schema validation failed",
            "validation": schema_result,
        }

    # Step 3: Quality checks
    df_clean, issues = run_quality_checks(df, file_category)
    valid_rows = len(df_clean)
    quality_score = calculate_quality_score(total_rows, valid_rows, issues)

    # Step 4: Save file to active storage
    active_path = _get_storage_path(os.path.join("uploads", "active"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stored_filename = f"{file_category}_{timestamp}_{filename}"
    storage_path = os.path.join(active_path, stored_filename)

    with open(storage_path, "wb") as f:
        f.write(file_bytes)

    # Step 5: Archive existing file if replacing
    if upload_mode == "replace":
        db_service.archive_active_file(file_category)

    # Step 6: Load clean data to DuckDB
    db_service.load_dataframe(df_clean, file_category, mode=upload_mode)

    # Step 7: Record upload metadata
    upload_id = db_service.record_upload(
        file_category=file_category,
        filename=filename,
        row_count=valid_rows,
        file_size_bytes=len(file_bytes),
        quality_score=quality_score,
        storage_path=storage_path,
        uploaded_by=uploaded_by,
        validation_errors=json.dumps([i for i in issues if not i.get("auto_resolved")]),
    )

    return {
        "status": "success",
        "upload_id": upload_id,
        "file_category": file_category,
        "filename": filename,
        "row_count": valid_rows,
        "total_rows_in_file": total_rows,
        "quality_score": quality_score,
        "issues": issues,
        "message": f"Successfully uploaded {valid_rows:,} rows to {file_category}",
    }
