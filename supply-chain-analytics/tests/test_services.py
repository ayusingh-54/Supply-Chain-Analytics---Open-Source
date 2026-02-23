"""
Tests for backend services
"""
import os
import sys
import pytest
import tempfile
import pandas as pd
from pathlib import Path
from io import BytesIO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Use temp database for tests
TEST_DB = tempfile.mktemp(suffix=".duckdb")
os.environ["DUCKDB_PATH"] = TEST_DB
os.environ["USE_FALKORDB"] = "false"
os.environ["STORAGE_PATH"] = tempfile.mkdtemp()


class TestFileService:
    """Test file validation and processing"""

    def test_validate_file_extension_csv(self):
        from backend.services.file_service import FileService
        svc = FileService()
        assert svc.validate_file_extension("data.csv") == True

    def test_validate_file_extension_xlsx(self):
        from backend.services.file_service import FileService
        svc = FileService()
        assert svc.validate_file_extension("data.xlsx") == True

    def test_validate_file_extension_invalid(self):
        from backend.services.file_service import FileService
        svc = FileService()
        assert svc.validate_file_extension("data.txt") == False

    def test_validate_schema_sales(self):
        from backend.services.file_service import FileService
        svc = FileService()
        df = pd.DataFrame({
            "date": ["2024-01-01"],
            "sku": ["SKU-001"],
            "quantity": [10],
            "revenue": [100.0]
        })
        is_valid, missing, extra = svc.validate_schema(df, "sales")
        assert is_valid == True
        assert len(missing) == 0

    def test_validate_schema_missing_columns(self):
        from backend.services.file_service import FileService
        svc = FileService()
        df = pd.DataFrame({
            "date": ["2024-01-01"],
            "sku": ["SKU-001"]
        })
        is_valid, missing, extra = svc.validate_schema(df, "sales")
        assert is_valid == False
        assert "quantity" in missing
        assert "revenue" in missing

    def test_validate_schema_inventory(self):
        from backend.services.file_service import FileService
        svc = FileService()
        df = pd.DataFrame({
            "sku": ["SKU-001"],
            "qty_on_hand": [50],
            "reorder_point": [20]
        })
        is_valid, missing, extra = svc.validate_schema(df, "inventory")
        assert is_valid == True

    def test_quality_checks(self):
        from backend.services.file_service import FileService
        svc = FileService()
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-01-01"],
            "sku": ["SKU-001", "SKU-001"],
            "quantity": [10, 10],
            "revenue": [100.0, 100.0]
        })
        issues = svc.run_quality_checks(df, "sales")
        # Should detect duplicates
        assert any("duplicate" in str(i).lower() for i in issues)


class TestDuckDBService:
    """Test DuckDB operations"""

    def setup_method(self):
        """Initialize test database"""
        import duckdb
        conn = duckdb.connect(TEST_DB)
        conn.execute("CREATE SEQUENCE IF NOT EXISTS file_upload_id_seq START 1;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_uploads (
                id INTEGER DEFAULT nextval('file_upload_id_seq'),
                filename VARCHAR, file_category VARCHAR,
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER, row_count INTEGER, column_count INTEGER,
                quality_score FLOAT, status VARCHAR DEFAULT 'active',
                uploaded_by VARCHAR DEFAULT 'system', file_hash VARCHAR,
                version INTEGER DEFAULT 1, notes TEXT
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales_data (
                date DATE, sku VARCHAR, quantity INTEGER, revenue DOUBLE,
                customer_name VARCHAR, region VARCHAR, category VARCHAR
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory_data (
                sku VARCHAR, qty_on_hand INTEGER, reorder_point INTEGER,
                location VARCHAR, unit_cost DOUBLE, supplier_id VARCHAR
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS supplier_data (
                supplier_id VARCHAR, supplier_name VARCHAR, lead_time INTEGER,
                contact_email VARCHAR, rating DOUBLE, country VARCHAR
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS purchase_order_data (
                po_number VARCHAR, sku VARCHAR, quantity INTEGER,
                order_date DATE, delivery_date DATE, supplier_id VARCHAR
            );
        """)
        conn.close()

    def test_record_upload(self):
        from backend.services.duckdb_service import DuckDBService
        svc = DuckDBService()
        file_id = svc.record_upload("test.csv", "sales", 1024, 100, 5, 95.0)
        assert file_id is not None

    def test_get_row_count(self):
        import duckdb
        conn = duckdb.connect(TEST_DB)
        conn.execute("INSERT INTO sales_data VALUES ('2024-01-01', 'SKU-001', 10, 100.0, 'Test', 'North', 'Electronics')")
        conn.close()

        from backend.services.duckdb_service import DuckDBService
        svc = DuckDBService()
        count = svc.get_row_count("sales_data")
        assert count >= 1

    def test_execute_query(self):
        from backend.services.duckdb_service import DuckDBService
        svc = DuckDBService()
        result = svc.execute_query("SELECT COUNT(*) as cnt FROM sales_data")
        assert result is not None


class TestMCPToolHelpers:
    """Test MCP server tool functions"""

    def test_safe_query(self):
        sys.path.insert(0, str(PROJECT_ROOT / "mcp_server"))
        # Set DB path for mcp server
        os.environ["DUCKDB_PATH"] = TEST_DB
        
        # Re-import to pick up env var
        import importlib
        if "mcp_server.server" in sys.modules:
            importlib.reload(sys.modules["mcp_server.server"])
        
        from mcp_server.server import safe_query
        result = safe_query("SELECT 1 as test")
        assert "test" in result or "1" in result

    def test_query_to_json(self):
        import json
        from mcp_server.server import query_to_json
        result = query_to_json("SELECT 1 as value")
        parsed = json.loads(result)
        assert "data" in parsed or "error" in parsed


class TestSampleDataGenerator:
    """Test sample data generation"""

    def test_generate_sales_data(self):
        from scripts.generate_sample_data import generate_sales_data
        filepath = generate_sales_data(10)
        assert filepath.exists()
        df = pd.read_csv(filepath)
        assert len(df) == 10
        assert "date" in df.columns
        assert "sku" in df.columns

    def test_generate_inventory_data(self):
        from scripts.generate_sample_data import generate_inventory_data
        filepath = generate_inventory_data()
        assert filepath.exists()
        df = pd.read_csv(filepath)
        assert len(df) > 0
        assert "sku" in df.columns

    def test_generate_supplier_data(self):
        from scripts.generate_sample_data import generate_supplier_data
        filepath = generate_supplier_data()
        assert filepath.exists()
        df = pd.read_csv(filepath)
        assert len(df) > 0

    def test_generate_purchase_order_data(self):
        from scripts.generate_sample_data import generate_purchase_order_data
        filepath = generate_purchase_order_data(10)
        assert filepath.exists()
        df = pd.read_csv(filepath)
        assert len(df) == 10


# Cleanup
def teardown_module():
    """Remove test database"""
    try:
        os.remove(TEST_DB)
    except:
        pass
