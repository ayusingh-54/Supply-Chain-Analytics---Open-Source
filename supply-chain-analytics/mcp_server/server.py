"""
Supply Chain Analytics - MCP Server
Model Context Protocol server that exposes supply chain data tools
for Claude Desktop, Claude Code, Cursor, and other MCP-compatible AI clients.

Usage:
    python server.py              # Run with stdio transport (default)
    python server.py --sse        # Run with SSE transport on port 3001
"""
import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-supply-chain")

# ─── MCP Server Setup ────────────────────────────────────────

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("supply-chain-analytics")

# ─── Database Connection ──────────────────────────────────────

import duckdb
import pandas as pd

DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(PROJECT_ROOT / "data" / "supply_chain.duckdb"))


def get_db():
    """Get DuckDB connection"""
    return duckdb.connect(DUCKDB_PATH, read_only=True)


def safe_query(query: str, params=None) -> str:
    """Execute a query safely and return results as formatted string"""
    try:
        conn = get_db()
        if params:
            df = conn.execute(query, params).fetchdf()
        else:
            df = conn.execute(query).fetchdf()
        conn.close()

        if len(df) == 0:
            return "No data found."
        return df.to_string(index=False, max_rows=100)
    except Exception as e:
        return f"Query error: {str(e)}"


def query_to_json(query: str, params=None) -> str:
    """Execute query and return JSON string"""
    try:
        conn = get_db()
        if params:
            df = conn.execute(query, params).fetchdf()
        else:
            df = conn.execute(query).fetchdf()
        conn.close()

        if len(df) == 0:
            return json.dumps({"message": "No data found", "row_count": 0})

        # Convert to serializable types
        result = df.head(200).to_dict("records")
        for row in result:
            for k, v in row.items():
                if pd.isna(v):
                    row[k] = None
                elif hasattr(v, "isoformat"):
                    row[k] = v.isoformat()
                elif hasattr(v, "item"):
                    row[k] = v.item()

        return json.dumps({"data": result, "row_count": len(df), "columns": list(df.columns)}, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ─── Tool Definitions ────────────────────────────────────────

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_sales_data",
            description="Query and analyze sales data. Can filter by date range, SKU, region. Returns sales records with date, sku, quantity, revenue, customer, region.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date filter (YYYY-MM-DD). Optional."},
                    "end_date": {"type": "string", "description": "End date filter (YYYY-MM-DD). Optional."},
                    "sku": {"type": "string", "description": "Filter by specific SKU. Optional."},
                    "region": {"type": "string", "description": "Filter by region. Optional."},
                    "limit": {"type": "integer", "description": "Max rows to return (default 50)", "default": 50},
                    "aggregation": {
                        "type": "string",
                        "description": "Aggregation mode: 'raw' for raw data, 'by_sku' for grouped by SKU, 'by_date' for grouped by date, 'by_region' for grouped by region, 'summary' for totals",
                        "enum": ["raw", "by_sku", "by_date", "by_region", "summary"],
                        "default": "summary",
                    },
                },
            },
        ),
        Tool(
            name="query_inventory",
            description="Check inventory levels. Shows stock on hand, reorder points, and which items need reordering. Can filter by SKU, location, or status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sku": {"type": "string", "description": "Filter by specific SKU. Optional."},
                    "location": {"type": "string", "description": "Filter by warehouse location. Optional."},
                    "status_filter": {
                        "type": "string",
                        "description": "Filter: 'all', 'reorder_needed' (below reorder point), 'low_stock' (below 1.5x reorder point)",
                        "enum": ["all", "reorder_needed", "low_stock"],
                        "default": "all",
                    },
                    "limit": {"type": "integer", "default": 50},
                },
            },
        ),
        Tool(
            name="query_suppliers",
            description="Look up supplier information including name, lead time, rating, country. Can filter by supplier_id, country, or minimum rating.",
            inputSchema={
                "type": "object",
                "properties": {
                    "supplier_id": {"type": "string", "description": "Filter by supplier ID. Optional."},
                    "country": {"type": "string", "description": "Filter by country. Optional."},
                    "min_rating": {"type": "number", "description": "Minimum rating filter. Optional."},
                    "limit": {"type": "integer", "default": 50},
                },
            },
        ),
        Tool(
            name="query_purchase_orders",
            description="Analyze purchase order data. Shows PO numbers, SKUs, quantities, dates, and supplier info.",
            inputSchema={
                "type": "object",
                "properties": {
                    "po_number": {"type": "string", "description": "Filter by PO number. Optional."},
                    "sku": {"type": "string", "description": "Filter by SKU. Optional."},
                    "supplier_id": {"type": "string", "description": "Filter by supplier. Optional."},
                    "limit": {"type": "integer", "default": 50},
                },
            },
        ),
        Tool(
            name="run_sql_query",
            description="Execute a custom SQL SELECT query on the supply chain DuckDB database. Available tables: sales_data, inventory_data, supplier_data, purchase_order_data, file_uploads. Only SELECT queries allowed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute. Only SELECT statements allowed. Available tables: sales_data (date, sku, quantity, revenue, customer_name, region, category), inventory_data (sku, qty_on_hand, reorder_point, location, unit_cost, supplier_id), supplier_data (supplier_id, supplier_name, lead_time, contact_email, rating, country), purchase_order_data (po_number, sku, quantity, order_date, delivery_date, supplier_id).",
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_data_quality_report",
            description="Get data quality metrics for all uploaded files, including row counts, quality scores, upload timestamps, and any validation issues.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_kpi_dashboard",
            description="Get key performance indicators across the supply chain: total revenue, inventory turnover signals, supplier count, order volumes, and reorder alerts.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="detect_anomalies",
            description="Detect anomalies and unusual patterns in supply chain data. Looks for outliers in sales, inventory issues, and supplier concerns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Which data to analyze: 'sales', 'inventory', 'supplier', 'all'",
                        "enum": ["sales", "inventory", "supplier", "all"],
                        "default": "all",
                    }
                },
            },
        ),
        Tool(
            name="forecast_demand",
            description="Simple demand forecasting based on historical sales data. Uses moving averages and trend analysis for a given SKU.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sku": {"type": "string", "description": "SKU to forecast demand for"},
                    "periods": {"type": "integer", "description": "Number of future periods to forecast", "default": 7},
                },
                "required": ["sku"],
            },
        ),
        Tool(
            name="analyze_supplier_risk",
            description="Assess supplier risk based on lead times, ratings, concentration of supply, and order history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "supplier_id": {"type": "string", "description": "Specific supplier to analyze. If omitted, analyzes all suppliers."},
                },
            },
        ),
        Tool(
            name="get_reorder_recommendations",
            description="Generate smart reorder recommendations based on current inventory levels, reorder points, sales velocity, and supplier lead times.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_supply_chain_graph",
            description="Get supply chain relationship data showing connections between suppliers, products, and purchase orders. Uses FalkorDB if available, otherwise derives from DuckDB.",
            inputSchema={
                "type": "object",
                "properties": {
                    "focus": {
                        "type": "string",
                        "description": "Focus area: 'overview', 'supplier_products', 'product_orders'",
                        "enum": ["overview", "supplier_products", "product_orders"],
                        "default": "overview",
                    }
                },
            },
        ),
    ]


# ─── Tool Implementations ────────────────────────────────────

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """Route tool calls to implementations"""

    if name == "query_sales_data":
        result = _query_sales(arguments)
    elif name == "query_inventory":
        result = _query_inventory(arguments)
    elif name == "query_suppliers":
        result = _query_suppliers(arguments)
    elif name == "query_purchase_orders":
        result = _query_purchase_orders(arguments)
    elif name == "run_sql_query":
        result = _run_sql_query(arguments)
    elif name == "get_data_quality_report":
        result = _get_data_quality_report()
    elif name == "get_kpi_dashboard":
        result = _get_kpis()
    elif name == "detect_anomalies":
        result = _detect_anomalies(arguments)
    elif name == "forecast_demand":
        result = _forecast_demand(arguments)
    elif name == "analyze_supplier_risk":
        result = _analyze_supplier_risk(arguments)
    elif name == "get_reorder_recommendations":
        result = _get_reorder_recommendations()
    elif name == "get_supply_chain_graph":
        result = _get_supply_chain_graph(arguments)
    else:
        result = json.dumps({"error": f"Unknown tool: {name}"})

    return [TextContent(type="text", text=result)]


# ─── Tool Implementation Functions ────────────────────────────

def _query_sales(args: dict) -> str:
    agg = args.get("aggregation", "summary")
    limit = args.get("limit", 50)
    conditions = []
    params = []

    if args.get("start_date"):
        conditions.append("date >= ?")
        params.append(args["start_date"])
    if args.get("end_date"):
        conditions.append("date <= ?")
        params.append(args["end_date"])
    if args.get("sku"):
        conditions.append("sku = ?")
        params.append(args["sku"])
    if args.get("region"):
        conditions.append("region = ?")
        params.append(args["region"])

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    if agg == "summary":
        query = f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT sku) as unique_skus,
                COALESCE(SUM(quantity), 0) as total_quantity,
                COALESCE(SUM(revenue), 0) as total_revenue,
                COALESCE(AVG(revenue), 0) as avg_revenue_per_record,
                MIN(date) as earliest_date,
                MAX(date) as latest_date
            FROM sales_data {where}
        """
    elif agg == "by_sku":
        query = f"""
            SELECT sku, 
                   SUM(quantity) as total_qty, 
                   SUM(revenue) as total_revenue,
                   COUNT(*) as num_records
            FROM sales_data {where}
            GROUP BY sku ORDER BY total_revenue DESC LIMIT {limit}
        """
    elif agg == "by_date":
        query = f"""
            SELECT date, 
                   SUM(quantity) as total_qty, 
                   SUM(revenue) as total_revenue,
                   COUNT(*) as num_records
            FROM sales_data {where}
            GROUP BY date ORDER BY date DESC LIMIT {limit}
        """
    elif agg == "by_region":
        query = f"""
            SELECT region, 
                   SUM(quantity) as total_qty, 
                   SUM(revenue) as total_revenue,
                   COUNT(*) as num_records
            FROM sales_data {where}
            GROUP BY region ORDER BY total_revenue DESC LIMIT {limit}
        """
    else:
        query = f"SELECT * FROM sales_data {where} LIMIT {limit}"

    return query_to_json(query, params if params else None)


def _query_inventory(args: dict) -> str:
    limit = args.get("limit", 50)
    status_filter = args.get("status_filter", "all")
    conditions = []

    if args.get("sku"):
        conditions.append(f"sku = '{args['sku']}'")
    if args.get("location"):
        conditions.append(f"location = '{args['location']}'")

    if status_filter == "reorder_needed":
        conditions.append("qty_on_hand <= reorder_point")
    elif status_filter == "low_stock":
        conditions.append("qty_on_hand <= reorder_point * 1.5")

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    query = f"""
        SELECT sku, qty_on_hand, reorder_point, 
               CASE WHEN qty_on_hand <= reorder_point THEN 'REORDER NOW'
                    WHEN qty_on_hand <= reorder_point * 1.5 THEN 'LOW STOCK'
                    ELSE 'OK' END as stock_status,
               location, unit_cost, supplier_id
        FROM inventory_data {where}
        ORDER BY CASE WHEN qty_on_hand <= reorder_point THEN 0 ELSE 1 END, qty_on_hand ASC
        LIMIT {limit}
    """
    return query_to_json(query)


def _query_suppliers(args: dict) -> str:
    limit = args.get("limit", 50)
    conditions = []

    if args.get("supplier_id"):
        conditions.append(f"supplier_id = '{args['supplier_id']}'")
    if args.get("country"):
        conditions.append(f"country = '{args['country']}'")
    if args.get("min_rating"):
        conditions.append(f"rating >= {args['min_rating']}")

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    query = f"SELECT * FROM supplier_data {where} ORDER BY rating DESC NULLS LAST LIMIT {limit}"
    return query_to_json(query)


def _query_purchase_orders(args: dict) -> str:
    limit = args.get("limit", 50)
    conditions = []

    if args.get("po_number"):
        conditions.append(f"po_number = '{args['po_number']}'")
    if args.get("sku"):
        conditions.append(f"sku = '{args['sku']}'")
    if args.get("supplier_id"):
        conditions.append(f"supplier_id = '{args['supplier_id']}'")

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    query = f"SELECT * FROM purchase_order_data {where} ORDER BY order_date DESC NULLS LAST LIMIT {limit}"
    return query_to_json(query)


def _run_sql_query(args: dict) -> str:
    query = args.get("query", "").strip()

    if not query.upper().startswith("SELECT"):
        return json.dumps({"error": "Only SELECT queries are allowed for safety."})

    dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE", "EXEC"]
    for kw in dangerous:
        if kw in query.upper().split():
            return json.dumps({"error": f"Query contains forbidden keyword: {kw}"})

    return query_to_json(query)


def _get_data_quality_report() -> str:
    query = """
        SELECT file_category, filename, upload_timestamp, row_count, 
               quality_score, status, uploaded_by
        FROM file_uploads 
        ORDER BY upload_timestamp DESC
    """
    return query_to_json(query)


def _get_kpis() -> str:
    results = {}

    # Sales KPIs
    sales_kpi = safe_query("""
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(DISTINCT sku) as unique_products,
            COALESCE(SUM(revenue), 0) as total_revenue,
            COALESCE(AVG(revenue), 0) as avg_revenue,
            COALESCE(SUM(quantity), 0) as total_units_sold
        FROM sales_data
    """)

    # Inventory KPIs
    inv_kpi = safe_query("""
        SELECT
            COUNT(*) as total_skus_tracked,
            COALESCE(SUM(qty_on_hand), 0) as total_units_in_stock,
            SUM(CASE WHEN qty_on_hand <= reorder_point THEN 1 ELSE 0 END) as items_needing_reorder,
            COALESCE(AVG(qty_on_hand), 0) as avg_stock_level,
            COALESCE(SUM(qty_on_hand * unit_cost), 0) as estimated_inventory_value
        FROM inventory_data
    """)

    # Supplier KPIs
    sup_kpi = safe_query("""
        SELECT
            COUNT(*) as total_suppliers,
            COALESCE(AVG(lead_time), 0) as avg_lead_time_days,
            COALESCE(AVG(rating), 0) as avg_supplier_rating,
            COUNT(DISTINCT country) as supplier_countries
        FROM supplier_data
    """)

    # PO KPIs
    po_kpi = safe_query("""
        SELECT
            COUNT(DISTINCT po_number) as total_purchase_orders,
            COALESCE(SUM(quantity), 0) as total_units_ordered,
            COUNT(DISTINCT sku) as unique_skus_ordered
        FROM purchase_order_data
    """)

    report = f"""=== SUPPLY CHAIN KPI DASHBOARD ===

📊 SALES
{sales_kpi}

📦 INVENTORY
{inv_kpi}

🏢 SUPPLIERS
{sup_kpi}

📋 PURCHASE ORDERS
{po_kpi}
"""
    return report


def _detect_anomalies(args: dict) -> str:
    category = args.get("category", "all")
    anomalies = []

    if category in ("sales", "all"):
        # Detect revenue outliers (simple: > 3x average)
        sales_anomalies = safe_query("""
            SELECT sku, date, quantity, revenue, 
                   revenue / NULLIF(quantity, 0) as unit_price
            FROM sales_data
            WHERE revenue > (SELECT AVG(revenue) * 3 FROM sales_data)
               OR quantity > (SELECT AVG(quantity) * 3 FROM sales_data)
            ORDER BY revenue DESC
            LIMIT 20
        """)
        anomalies.append(f"📊 SALES ANOMALIES (records > 3x average):\n{sales_anomalies}")

    if category in ("inventory", "all"):
        # Items at critical stock levels
        inv_anomalies = safe_query("""
            SELECT sku, qty_on_hand, reorder_point, location,
                   CAST(qty_on_hand AS FLOAT) / NULLIF(reorder_point, 0) as stock_ratio
            FROM inventory_data
            WHERE qty_on_hand <= reorder_point * 0.5
            ORDER BY stock_ratio ASC
        """)
        anomalies.append(f"📦 CRITICAL INVENTORY (below 50% of reorder point):\n{inv_anomalies}")

    if category in ("supplier", "all"):
        # Low-rated or high lead-time suppliers
        sup_anomalies = safe_query("""
            SELECT supplier_id, supplier_name, rating, lead_time, country
            FROM supplier_data
            WHERE rating < 3.0 OR lead_time > (SELECT AVG(lead_time) * 2 FROM supplier_data)
            ORDER BY rating ASC
        """)
        anomalies.append(f"🏢 SUPPLIER CONCERNS (low rating or high lead time):\n{sup_anomalies}")

    return "\n\n".join(anomalies) if anomalies else "No anomalies detected."


def _forecast_demand(args: dict) -> str:
    sku = args.get("sku", "")
    periods = args.get("periods", 7)

    # Get historical sales for the SKU
    history = safe_query(f"""
        SELECT date, SUM(quantity) as daily_qty, SUM(revenue) as daily_revenue
        FROM sales_data
        WHERE sku = '{sku}'
        GROUP BY date
        ORDER BY date
    """)

    # Get basic stats for simple forecast
    stats = safe_query(f"""
        SELECT 
            COUNT(DISTINCT date) as num_days,
            AVG(quantity) as avg_daily_qty,
            STDDEV(quantity) as stddev_qty,
            MIN(quantity) as min_qty,
            MAX(quantity) as max_qty,
            SUM(quantity) as total_qty,
            SUM(revenue) as total_revenue
        FROM sales_data
        WHERE sku = '{sku}'
    """)

    return f"""=== DEMAND FORECAST: {sku} ===

📈 Historical Data:
{history}

📊 Statistics:
{stats}

🔮 Simple Forecast ({periods} periods):
Based on the average daily quantity, the forecast for the next {periods} periods 
uses a moving average approach. Review the statistics above to assess confidence.
Note: For production forecasting, integrate with proper time-series models (Prophet, ARIMA).
"""


def _analyze_supplier_risk(args: dict) -> str:
    supplier_id = args.get("supplier_id")

    if supplier_id:
        # Single supplier analysis
        info = safe_query(f"""
            SELECT s.*, 
                   COUNT(DISTINCT po.po_number) as total_orders,
                   SUM(po.quantity) as total_qty_ordered,
                   COUNT(DISTINCT po.sku) as unique_products
            FROM supplier_data s
            LEFT JOIN purchase_order_data po ON s.supplier_id = po.supplier_id
            WHERE s.supplier_id = '{supplier_id}'
            GROUP BY s.supplier_id, s.supplier_name, s.lead_time, 
                     s.contact_email, s.rating, s.country
        """)

        # Products depending on this supplier
        products = safe_query(f"""
            SELECT sku, qty_on_hand, reorder_point
            FROM inventory_data
            WHERE supplier_id = '{supplier_id}'
        """)

        return f"""=== SUPPLIER RISK ANALYSIS: {supplier_id} ===

📋 Supplier Info:
{info}

📦 Products Dependent on This Supplier:
{products}

⚠️ Risk Factors to Consider:
- Single-source dependency for listed products
- Lead time relative to reorder point coverage
- Rating trend and historical performance
"""
    else:
        # All suppliers risk overview
        risk_overview = safe_query("""
            SELECT 
                s.supplier_id, s.supplier_name, s.rating, s.lead_time, s.country,
                COUNT(DISTINCT i.sku) as products_supplied,
                COUNT(DISTINCT po.po_number) as active_orders,
                CASE 
                    WHEN s.rating < 3.0 THEN 'HIGH RISK'
                    WHEN s.lead_time > 20 THEN 'MEDIUM RISK (Long Lead Time)'
                    WHEN s.rating < 4.0 THEN 'MEDIUM RISK (Low Rating)'
                    ELSE 'LOW RISK'
                END as risk_level
            FROM supplier_data s
            LEFT JOIN inventory_data i ON s.supplier_id = i.supplier_id
            LEFT JOIN purchase_order_data po ON s.supplier_id = po.supplier_id
            GROUP BY s.supplier_id, s.supplier_name, s.rating, s.lead_time, s.country
            ORDER BY s.rating ASC
        """)

        return f"""=== SUPPLIER RISK OVERVIEW ===

{risk_overview}

⚠️ Key Risk Indicators:
- HIGH RISK: Rating < 3.0
- MEDIUM RISK: Lead time > 20 days OR rating < 4.0
- Products with single-source suppliers are higher risk
"""


def _get_reorder_recommendations() -> str:
    recommendations = safe_query("""
        SELECT 
            i.sku,
            i.qty_on_hand,
            i.reorder_point,
            i.reorder_point - i.qty_on_hand as units_below_reorder,
            i.unit_cost,
            i.supplier_id,
            s.supplier_name,
            s.lead_time as supplier_lead_time_days,
            COALESCE(
                (SELECT AVG(sd.quantity) FROM sales_data sd WHERE sd.sku = i.sku),
                0
            ) as avg_daily_demand,
            CASE 
                WHEN i.qty_on_hand <= 0 THEN 'URGENT - OUT OF STOCK'
                WHEN i.qty_on_hand <= i.reorder_point * 0.5 THEN 'URGENT - CRITICAL LOW'
                WHEN i.qty_on_hand <= i.reorder_point THEN 'ORDER NOW'
                WHEN i.qty_on_hand <= i.reorder_point * 1.5 THEN 'ORDER SOON'
                ELSE 'OK'
            END as priority
        FROM inventory_data i
        LEFT JOIN supplier_data s ON i.supplier_id = s.supplier_id
        WHERE i.qty_on_hand <= i.reorder_point * 1.5
        ORDER BY 
            CASE WHEN i.qty_on_hand <= 0 THEN 0
                 WHEN i.qty_on_hand <= i.reorder_point * 0.5 THEN 1
                 WHEN i.qty_on_hand <= i.reorder_point THEN 2
                 ELSE 3 END,
            i.qty_on_hand ASC
    """)

    return f"""=== REORDER RECOMMENDATIONS ===

{recommendations}

📝 Recommended Actions:
- URGENT items: Place orders immediately
- ORDER NOW: Schedule orders this week  
- ORDER SOON: Plan orders for next week
- Consider supplier lead times when placing orders
"""


def _get_supply_chain_graph(args: dict) -> str:
    focus = args.get("focus", "overview")

    if focus == "overview":
        # Get overview from DuckDB relationships
        supplier_product = safe_query("""
            SELECT DISTINCT 
                i.supplier_id, s.supplier_name, i.sku,
                i.qty_on_hand, s.lead_time
            FROM inventory_data i
            LEFT JOIN supplier_data s ON i.supplier_id = s.supplier_id
            WHERE i.supplier_id IS NOT NULL
            ORDER BY s.supplier_name
        """)

        return f"""=== SUPPLY CHAIN NETWORK OVERVIEW ===

Supplier → Product Relationships:
{supplier_product}

This shows which suppliers provide which products. 
Use 'supplier_products' or 'product_orders' focus for deeper analysis.
"""

    elif focus == "supplier_products":
        result = safe_query("""
            SELECT 
                s.supplier_id, s.supplier_name, s.country,
                COUNT(DISTINCT i.sku) as products_supplied,
                SUM(i.qty_on_hand) as total_stock,
                GROUP_CONCAT(DISTINCT i.sku) as sku_list
            FROM supplier_data s
            LEFT JOIN inventory_data i ON s.supplier_id = i.supplier_id
            GROUP BY s.supplier_id, s.supplier_name, s.country
            ORDER BY products_supplied DESC
        """)
        return f"=== SUPPLIER → PRODUCT MAPPING ===\n\n{result}"

    elif focus == "product_orders":
        result = safe_query("""
            SELECT 
                po.sku,
                COUNT(DISTINCT po.po_number) as num_orders,
                SUM(po.quantity) as total_ordered,
                GROUP_CONCAT(DISTINCT po.supplier_id) as suppliers,
                i.qty_on_hand as current_stock
            FROM purchase_order_data po
            LEFT JOIN inventory_data i ON po.sku = i.sku
            GROUP BY po.sku, i.qty_on_hand
            ORDER BY total_ordered DESC
        """)
        return f"=== PRODUCT → ORDER MAPPING ===\n\n{result}"

    return "Unknown focus area"


# ─── Main Entry Point ────────────────────────────────────────

async def main():
    """Run the MCP server with stdio transport"""
    logger.info(f"Starting Supply Chain Analytics MCP Server")
    logger.info(f"DuckDB path: {DUCKDB_PATH}")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    if "--sse" in sys.argv:
        # SSE transport mode
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route

        sse = SseServerTransport("/messages")

        async def handle_sse(request):
            async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
                await server.run(streams[0], streams[1], server.create_initialization_options())

        app = Starlette(routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=sse.handle_post_message, methods=["POST"]),
        ])

        import uvicorn
        port = int(os.getenv("MCP_SERVER_PORT", "3001"))
        logger.info(f"Starting SSE server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        asyncio.run(main())
