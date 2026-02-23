"""
Initialize the DuckDB database with all required tables.
Run this once before starting the application, or the backend will auto-create tables on startup.

Usage:
    python scripts/setup_database.py
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import duckdb

DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(PROJECT_ROOT / "data" / "supply_chain.duckdb"))


def setup_database():
    """Create all tables needed by the supply chain analytics system"""
    data_dir = Path(DUCKDB_PATH).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(DUCKDB_PATH)

    print(f"📦 Setting up DuckDB database at: {DUCKDB_PATH}")

    # Sequences
    conn.execute("CREATE SEQUENCE IF NOT EXISTS file_upload_id_seq START 1;")

    # File uploads tracking table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS file_uploads (
            id INTEGER DEFAULT nextval('file_upload_id_seq'),
            filename VARCHAR NOT NULL,
            file_category VARCHAR NOT NULL,
            upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER,
            row_count INTEGER,
            column_count INTEGER,
            quality_score FLOAT,
            status VARCHAR DEFAULT 'active',
            uploaded_by VARCHAR DEFAULT 'system',
            file_hash VARCHAR,
            version INTEGER DEFAULT 1,
            notes TEXT,
            PRIMARY KEY (id)
        );
    """)
    print("  ✅ file_uploads table")

    # File versions
    conn.execute("""
        CREATE TABLE IF NOT EXISTS file_versions (
            id INTEGER DEFAULT nextval('file_upload_id_seq'),
            file_category VARCHAR NOT NULL,
            version INTEGER NOT NULL,
            filename VARCHAR NOT NULL,
            upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            row_count INTEGER,
            status VARCHAR DEFAULT 'archived',
            PRIMARY KEY (id)
        );
    """)
    print("  ✅ file_versions table")

    # Data quality issues
    conn.execute("""
        CREATE TABLE IF NOT EXISTS data_quality_issues (
            id INTEGER DEFAULT nextval('file_upload_id_seq'),
            file_upload_id INTEGER,
            issue_type VARCHAR,
            severity VARCHAR,
            column_name VARCHAR,
            description TEXT,
            affected_rows INTEGER
        );
    """)
    print("  ✅ data_quality_issues table")

    # Sales data
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sales_data (
            date DATE,
            sku VARCHAR,
            quantity INTEGER,
            revenue DOUBLE,
            customer_name VARCHAR,
            region VARCHAR,
            category VARCHAR
        );
    """)
    print("  ✅ sales_data table")

    # Inventory data
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
    print("  ✅ inventory_data table")

    # Supplier data
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
    print("  ✅ supplier_data table")

    # Purchase order data
    conn.execute("""
        CREATE TABLE IF NOT EXISTS purchase_order_data (
            po_number VARCHAR,
            sku VARCHAR,
            quantity INTEGER,
            order_date DATE,
            delivery_date DATE,
            supplier_id VARCHAR
        );
    """)
    print("  ✅ purchase_order_data table")

    conn.close()
    print(f"\n✅ Database setup complete! ({DUCKDB_PATH})")


if __name__ == "__main__":
    setup_database()
