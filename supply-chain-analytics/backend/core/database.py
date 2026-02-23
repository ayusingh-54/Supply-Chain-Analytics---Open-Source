"""
DuckDB database initialization and connection management
"""
import duckdb
import os
from pathlib import Path
from .config import settings


_connection = None


def get_db_path() -> str:
    """Resolve the DuckDB path relative to the project root"""
    path = settings.DUCKDB_PATH
    if not os.path.isabs(path):
        path = os.path.join(settings.BASE_DIR, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def get_connection() -> duckdb.DuckDBPyConnection:
    """Get or create a DuckDB connection (singleton)"""
    global _connection
    if _connection is None:
        db_path = get_db_path()
        _connection = duckdb.connect(db_path)
        _init_tables(_connection)
    return _connection


def _init_tables(conn: duckdb.DuckDBPyConnection):
    """Create required tables if they don't exist"""
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_file_uploads START 1;
        CREATE TABLE IF NOT EXISTS file_uploads (
            id INTEGER DEFAULT nextval('seq_file_uploads') PRIMARY KEY,
            file_category VARCHAR(50),
            filename VARCHAR(255),
            upload_timestamp TIMESTAMP DEFAULT current_timestamp,
            uploaded_by VARCHAR(100) DEFAULT 'system',
            row_count INTEGER DEFAULT 0,
            file_size_bytes BIGINT DEFAULT 0,
            status VARCHAR(20) DEFAULT 'active',
            quality_score DECIMAL(5,2) DEFAULT 0,
            validation_errors VARCHAR DEFAULT '[]',
            storage_path VARCHAR(500)
        );
    """)

    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_file_versions START 1;
        CREATE TABLE IF NOT EXISTS file_versions (
            id INTEGER DEFAULT nextval('seq_file_versions') PRIMARY KEY,
            file_upload_id INTEGER,
            version_number INTEGER,
            replaced_at TIMESTAMP DEFAULT current_timestamp,
            replaced_by INTEGER
        );
    """)

    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_data_quality START 1;
        CREATE TABLE IF NOT EXISTS data_quality_issues (
            id INTEGER DEFAULT nextval('seq_data_quality') PRIMARY KEY,
            file_upload_id INTEGER,
            issue_type VARCHAR(50),
            severity VARCHAR(20),
            row_numbers VARCHAR DEFAULT '[]',
            issue_count INTEGER DEFAULT 0,
            auto_resolved BOOLEAN DEFAULT false
        );
    """)

    # Create data tables for each category
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sales_data (
            date DATE,
            sku VARCHAR,
            quantity DOUBLE,
            revenue DOUBLE,
            customer_name VARCHAR,
            region VARCHAR,
            category VARCHAR
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS inventory_data (
            sku VARCHAR,
            qty_on_hand INTEGER,
            reorder_point INTEGER,
            location VARCHAR,
            unit_cost DOUBLE,
            supplier_id VARCHAR
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS supplier_data (
            supplier_id VARCHAR,
            supplier_name VARCHAR,
            lead_time INTEGER,
            contact_email VARCHAR,
            rating DOUBLE,
            country VARCHAR
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS purchase_order_data (
            po_number VARCHAR,
            sku VARCHAR,
            quantity DOUBLE,
            order_date DATE,
            delivery_date DATE,
            supplier_id VARCHAR
        );
    """)


def reset_connection():
    """Reset the database connection"""
    global _connection
    if _connection:
        _connection.close()
    _connection = None
