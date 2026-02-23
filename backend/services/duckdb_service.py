"""
DuckDB Service - Handles all analytical database operations
"""
import duckdb
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os

from core.database import get_connection
from core.config import settings


class DuckDBService:
    """Service for DuckDB analytical database operations"""

    def __init__(self):
        self.conn = get_connection()

    # ─── File Metadata ────────────────────────────────────────

    def record_upload(
        self,
        file_category: str,
        filename: str,
        row_count: int,
        file_size_bytes: int,
        quality_score: float,
        storage_path: str,
        uploaded_by: str = "system",
        validation_errors: str = "[]",
    ) -> int:
        """Record a file upload and return the upload ID"""
        result = self.conn.execute(
            """
            INSERT INTO file_uploads 
                (file_category, filename, row_count, file_size_bytes, 
                 quality_score, storage_path, uploaded_by, validation_errors, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
            RETURNING id
            """,
            [file_category, filename, row_count, file_size_bytes,
             quality_score, storage_path, uploaded_by, validation_errors],
        ).fetchone()
        return result[0]

    def get_active_file(self, file_category: str) -> Optional[Dict]:
        """Get the currently active file for a category"""
        result = self.conn.execute(
            """
            SELECT * FROM file_uploads 
            WHERE file_category = ? AND status = 'active'
            ORDER BY upload_timestamp DESC LIMIT 1
            """,
            [file_category],
        ).fetchdf()

        if len(result) == 0:
            return None
        return result.iloc[0].to_dict()

    def get_all_file_status(self) -> Dict[str, Any]:
        """Get status for all file categories"""
        categories = ["sales", "inventory", "supplier", "purchase_order"]
        status = {}

        for cat in categories:
            active = self.get_active_file(cat)
            if active:
                status[cat] = {
                    "status": "active",
                    "filename": active["filename"],
                    "upload_timestamp": str(active["upload_timestamp"]),
                    "uploaded_by": active.get("uploaded_by", "system"),
                    "row_count": int(active["row_count"]),
                    "quality_score": float(active["quality_score"]),
                    "needs_refresh": False,
                }
            else:
                status[cat] = {
                    "status": "missing",
                    "filename": None,
                    "upload_timestamp": None,
                    "uploaded_by": None,
                    "row_count": 0,
                    "quality_score": 0,
                    "needs_refresh": False,
                }
        return status

    def archive_active_file(self, file_category: str) -> Optional[int]:
        """Archive the currently active file and return its ID"""
        active = self.get_active_file(file_category)
        if active is None:
            return None

        file_id = int(active["id"])

        # Get next version number
        version_result = self.conn.execute(
            """
            SELECT COALESCE(MAX(version_number), 0) + 1 as next_ver
            FROM file_versions WHERE file_upload_id IN (
                SELECT id FROM file_uploads WHERE file_category = ?
            )
            """,
            [file_category],
        ).fetchone()
        next_version = version_result[0]

        # Create version record
        self.conn.execute(
            """
            INSERT INTO file_versions (file_upload_id, version_number)
            VALUES (?, ?)
            """,
            [file_id, next_version],
        )

        # Update status to archived
        self.conn.execute(
            "UPDATE file_uploads SET status = 'archived' WHERE id = ?",
            [file_id],
        )
        return file_id

    def get_file_history(self, file_category: str) -> Dict[str, Any]:
        """Get version history for a file category"""
        # Current active
        current = self.get_active_file(file_category)

        # Previous versions
        versions_df = self.conn.execute(
            """
            SELECT fu.*, fv.version_number, fv.replaced_at
            FROM file_uploads fu
            LEFT JOIN file_versions fv ON fu.id = fv.file_upload_id
            WHERE fu.file_category = ? AND fu.status = 'archived'
            ORDER BY fu.upload_timestamp DESC
            LIMIT 10
            """,
            [file_category],
        ).fetchdf()

        versions = []
        for _, row in versions_df.iterrows():
            versions.append({
                "id": int(row["id"]),
                "filename": row["filename"],
                "upload_timestamp": str(row["upload_timestamp"]),
                "uploaded_by": row.get("uploaded_by", "system"),
                "row_count": int(row["row_count"]),
                "quality_score": float(row["quality_score"]),
                "file_size_bytes": int(row.get("file_size_bytes", 0)),
                "status": row["status"],
                "version_number": int(row.get("version_number", 0)) if row.get("version_number") else 0,
            })

        return {
            "category": file_category,
            "current": current,
            "versions": versions,
        }

    # ─── Data Operations ──────────────────────────────────────

    def load_dataframe(self, df: pd.DataFrame, file_category: str, mode: str = "replace"):
        """Load a DataFrame into the appropriate data table"""
        table_name = f"{file_category}_data"

        if mode == "replace":
            self.conn.execute(f"DELETE FROM {table_name}")

        # Use DuckDB's native DataFrame insertion
        self.conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")

    def get_data_preview(self, file_category: str, limit: int = 100) -> List[Dict]:
        """Get a preview of data for a category"""
        table_name = f"{file_category}_data"
        try:
            df = self.conn.execute(
                f"SELECT * FROM {table_name} LIMIT ?", [limit]
            ).fetchdf()
            return df.to_dict("records")
        except Exception:
            return []

    def get_row_count(self, file_category: str) -> int:
        """Get row count for a data table"""
        table_name = f"{file_category}_data"
        try:
            result = self.conn.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()
            return result[0]
        except Exception:
            return 0

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a raw SQL query and return results"""
        return self.conn.execute(query).fetchdf()

    def get_table_schema(self, file_category: str) -> List[Dict]:
        """Get the schema of a data table"""
        table_name = f"{file_category}_data"
        try:
            df = self.conn.execute(
                f"DESCRIBE {table_name}"
            ).fetchdf()
            return df.to_dict("records")
        except Exception:
            return []

    # ─── Analytics Queries ────────────────────────────────────

    def get_sales_summary(self, filters: Optional[Dict] = None) -> Dict:
        """Get sales data summary with optional filters"""
        where_clause = ""
        params = []

        if filters:
            conditions = []
            if filters.get("start_date"):
                conditions.append("date >= ?")
                params.append(filters["start_date"])
            if filters.get("end_date"):
                conditions.append("date <= ?")
                params.append(filters["end_date"])
            if filters.get("sku"):
                conditions.append("sku = ?")
                params.append(filters["sku"])
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

        query = f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT sku) as unique_skus,
                SUM(quantity) as total_quantity,
                SUM(revenue) as total_revenue,
                AVG(revenue) as avg_revenue,
                MIN(date) as date_from,
                MAX(date) as date_to
            FROM sales_data {where_clause}
        """
        result = self.conn.execute(query, params).fetchdf()
        if len(result) == 0:
            return {}
        return result.iloc[0].to_dict()

    def get_inventory_status(self) -> List[Dict]:
        """Get inventory status with reorder alerts"""
        query = """
            SELECT 
                sku,
                qty_on_hand,
                reorder_point,
                CASE 
                    WHEN qty_on_hand <= reorder_point THEN 'REORDER'
                    WHEN qty_on_hand <= reorder_point * 1.5 THEN 'LOW'
                    ELSE 'OK'
                END as status,
                location,
                unit_cost
            FROM inventory_data
            ORDER BY 
                CASE WHEN qty_on_hand <= reorder_point THEN 0 ELSE 1 END,
                qty_on_hand ASC
        """
        return self.conn.execute(query).fetchdf().to_dict("records")

    def get_supplier_analysis(self) -> List[Dict]:
        """Analyze supplier performance"""
        query = """
            SELECT 
                s.supplier_id,
                s.supplier_name,
                s.lead_time,
                s.rating,
                s.country,
                COUNT(po.po_number) as total_orders,
                SUM(po.quantity) as total_quantity_ordered
            FROM supplier_data s
            LEFT JOIN purchase_order_data po ON s.supplier_id = po.supplier_id
            GROUP BY s.supplier_id, s.supplier_name, s.lead_time, s.rating, s.country
            ORDER BY s.rating DESC NULLS LAST
        """
        try:
            return self.conn.execute(query).fetchdf().to_dict("records")
        except Exception:
            # If purchase_order_data doesn't have data, return just suppliers
            return self.conn.execute(
                "SELECT * FROM supplier_data"
            ).fetchdf().to_dict("records")

    def get_kpis(self) -> Dict[str, Any]:
        """Get key performance indicators across all data"""
        kpis = {}

        try:
            # Sales KPIs
            sales = self.conn.execute("""
                SELECT 
                    SUM(revenue) as total_revenue,
                    COUNT(DISTINCT sku) as products_sold,
                    AVG(revenue / NULLIF(quantity, 0)) as avg_unit_price,
                    COUNT(*) as total_transactions
                FROM sales_data
            """).fetchdf()
            if len(sales) > 0:
                kpis["sales"] = sales.iloc[0].to_dict()
        except Exception:
            kpis["sales"] = {}

        try:
            # Inventory KPIs
            inv = self.conn.execute("""
                SELECT 
                    COUNT(*) as total_skus,
                    SUM(qty_on_hand) as total_units,
                    SUM(CASE WHEN qty_on_hand <= reorder_point THEN 1 ELSE 0 END) as items_below_reorder,
                    AVG(qty_on_hand) as avg_stock_level
                FROM inventory_data
            """).fetchdf()
            if len(inv) > 0:
                kpis["inventory"] = inv.iloc[0].to_dict()
        except Exception:
            kpis["inventory"] = {}

        try:
            # Supplier KPIs
            sup = self.conn.execute("""
                SELECT 
                    COUNT(*) as total_suppliers,
                    AVG(lead_time) as avg_lead_time,
                    AVG(rating) as avg_rating,
                    COUNT(DISTINCT country) as countries
                FROM supplier_data
            """).fetchdf()
            if len(sup) > 0:
                kpis["suppliers"] = sup.iloc[0].to_dict()
        except Exception:
            kpis["suppliers"] = {}

        try:
            # PO KPIs
            po = self.conn.execute("""
                SELECT 
                    COUNT(DISTINCT po_number) as total_pos,
                    SUM(quantity) as total_quantity,
                    COUNT(DISTINCT sku) as unique_skus_ordered
                FROM purchase_order_data
            """).fetchdf()
            if len(po) > 0:
                kpis["purchase_orders"] = po.iloc[0].to_dict()
        except Exception:
            kpis["purchase_orders"] = {}

        return kpis
