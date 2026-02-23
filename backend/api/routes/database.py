"""
Database Management API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from services.duckdb_service import DuckDBService
from services.falkordb_service import FalkorDBService
from core.config import settings

router = APIRouter()


@router.post("/refresh")
async def refresh_database(
    mode: str = "full",
    file_categories: Optional[List[str]] = None,
):
    """Trigger a database refresh - sync data to FalkorDB graph"""
    db = DuckDBService()

    if not settings.USE_FALKORDB:
        return {
            "status": "success",
            "message": "FalkorDB disabled - data already in DuckDB",
            "files_refreshed": file_categories or ["all"],
        }

    try:
        graph = FalkorDBService(host=settings.FALKORDB_HOST, port=settings.FALKORDB_PORT)

        if not graph.is_connected:
            return {
                "status": "warning",
                "message": "FalkorDB not available. Data is in DuckDB only.",
            }

        # Get data from DuckDB
        sales = db.get_data_preview("sales", limit=50000)
        inventory = db.get_data_preview("inventory", limit=50000)
        suppliers = db.get_data_preview("supplier", limit=50000)
        pos = db.get_data_preview("purchase_order", limit=50000)

        # Sync to graph
        graph.sync_supply_chain_data(sales, inventory, suppliers, pos)

        return {
            "status": "success",
            "message": "Data synced to FalkorDB graph database",
            "files_refreshed": file_categories or ["all"],
        }
    except Exception as e:
        return {
            "status": "warning",
            "message": f"Graph sync failed: {str(e)}. Data remains in DuckDB.",
        }


@router.get("/kpis")
async def get_kpis():
    """Get key performance indicators"""
    db = DuckDBService()
    return db.get_kpis()


@router.get("/sales-summary")
async def get_sales_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sku: Optional[str] = None,
):
    """Get sales data summary"""
    db = DuckDBService()
    filters = {}
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    if sku:
        filters["sku"] = sku
    return db.get_sales_summary(filters if filters else None)


@router.get("/inventory-status")
async def get_inventory_status():
    """Get inventory status with reorder alerts"""
    db = DuckDBService()
    return db.get_inventory_status()


@router.get("/supplier-analysis")
async def get_supplier_analysis():
    """Analyze supplier performance"""
    db = DuckDBService()
    return db.get_supplier_analysis()


@router.post("/query")
async def execute_query(query: str):
    """Execute a custom SQL query on DuckDB (read-only)"""
    # Security: only allow SELECT queries
    clean_query = query.strip().upper()
    if not clean_query.startswith("SELECT"):
        raise HTTPException(400, "Only SELECT queries are allowed")

    # Block dangerous patterns
    dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE"]
    for keyword in dangerous:
        if keyword in clean_query:
            raise HTTPException(400, f"Query contains forbidden keyword: {keyword}")

    db = DuckDBService()
    try:
        result = db.execute_query(query)
        return {
            "columns": list(result.columns),
            "data": result.head(1000).to_dict("records"),
            "row_count": len(result),
            "truncated": len(result) > 1000,
        }
    except Exception as e:
        raise HTTPException(400, f"Query failed: {str(e)}")
