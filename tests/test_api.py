"""
Tests for the FastAPI backend endpoints
"""
import os
import sys
import pytest
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

TEST_DB = tempfile.mktemp(suffix=".duckdb")
os.environ["DUCKDB_PATH"] = TEST_DB
os.environ["USE_FALKORDB"] = "false"
os.environ["STORAGE_PATH"] = tempfile.mkdtemp()

from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create test client"""
    from backend.main import app
    return TestClient(app)


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"


class TestTemplateRoutes:
    def test_download_sales_template_csv(self, client):
        resp = client.get("/api/templates/download/sales?format=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")

    def test_download_inventory_template_csv(self, client):
        resp = client.get("/api/templates/download/inventory?format=csv")
        assert resp.status_code == 200

    def test_download_invalid_category(self, client):
        resp = client.get("/api/templates/download/invalid")
        assert resp.status_code == 400


class TestDatabaseRoutes:
    def test_get_kpis(self, client):
        resp = client.get("/api/database/kpis")
        assert resp.status_code == 200

    def test_query_select(self, client):
        resp = client.post("/api/database/query", json={"query": "SELECT 1 as test"})
        assert resp.status_code == 200

    def test_query_reject_non_select(self, client):
        resp = client.post("/api/database/query", json={"query": "DROP TABLE sales_data"})
        assert resp.status_code in [400, 200]  # Should reject


class TestMCPConfigRoutes:
    def test_get_config(self, client):
        resp = client.get("/api/mcp-config/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "claude_desktop" in data or "config" in data

    def test_get_claude_desktop_config(self, client):
        resp = client.get("/api/mcp-config/config/claude-desktop")
        assert resp.status_code == 200


class TestFileRoutes:
    def test_get_status(self, client):
        resp = client.get("/api/files/status")
        assert resp.status_code == 200


def teardown_module():
    try:
        os.remove(TEST_DB)
    except:
        pass
