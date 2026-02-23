"""
Supply Chain Analytics - Backend Configuration
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DUCKDB_PATH: str = os.getenv("DUCKDB_PATH", "./data/supply_chain.duckdb")
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./storage")

    # FalkorDB
    USE_FALKORDB: bool = os.getenv("USE_FALKORDB", "false").lower() == "true"
    FALKORDB_HOST: str = os.getenv("FALKORDB_HOST", "localhost")
    FALKORDB_PORT: int = int(os.getenv("FALKORDB_PORT", "6379"))

    # Upload limits
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "200"))
    ALLOWED_EXTENSIONS: set = {".xlsx", ".csv"}

    # Schema definitions for each file category
    SCHEMA_RULES: dict = {
        "sales": {
            "required_columns": ["date", "sku", "quantity", "revenue"],
            "optional_columns": ["customer_name", "region", "category"],
            "data_types": {
                "date": "datetime",
                "sku": "string",
                "quantity": "float",
                "revenue": "float",
            },
            "constraints": {
                "quantity": {"min": 0},
                "revenue": {"min": 0},
            },
        },
        "inventory": {
            "required_columns": ["sku", "qty_on_hand", "reorder_point"],
            "optional_columns": ["location", "unit_cost", "supplier_id"],
            "data_types": {
                "sku": "string",
                "qty_on_hand": "integer",
                "reorder_point": "integer",
            },
            "constraints": {
                "qty_on_hand": {"min": 0},
                "reorder_point": {"min": 0},
            },
        },
        "supplier": {
            "required_columns": ["supplier_id", "supplier_name", "lead_time"],
            "optional_columns": ["contact_email", "rating", "country"],
            "data_types": {
                "supplier_id": "string",
                "supplier_name": "string",
                "lead_time": "integer",
            },
            "constraints": {
                "lead_time": {"min": 0},
            },
        },
        "purchase_order": {
            "required_columns": ["po_number", "sku", "quantity"],
            "optional_columns": ["order_date", "delivery_date", "supplier_id"],
            "data_types": {
                "po_number": "string",
                "sku": "string",
                "quantity": "float",
            },
            "constraints": {
                "quantity": {"min": 0},
            },
        },
    }

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
