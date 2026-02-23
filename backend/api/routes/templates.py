"""
Template Download API Routes
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io
from core.config import settings

router = APIRouter()

SAMPLE_DATA = {
    "sales": [
        {"date": "2025-01-01", "sku": "SKU-001", "quantity": 10, "revenue": 499.90, "customer_name": "Acme Corp", "region": "North", "category": "Electronics"},
        {"date": "2025-01-02", "sku": "SKU-002", "quantity": 5, "revenue": 249.50, "customer_name": "Beta Inc", "region": "South", "category": "Office"},
        {"date": "2025-01-03", "sku": "SKU-003", "quantity": 20, "revenue": 999.80, "customer_name": "Gamma LLC", "region": "East", "category": "Electronics"},
        {"date": "2025-01-04", "sku": "SKU-001", "quantity": 8, "revenue": 399.92, "customer_name": "Delta Corp", "region": "West", "category": "Electronics"},
        {"date": "2025-01-05", "sku": "SKU-004", "quantity": 15, "revenue": 750.00, "customer_name": "Epsilon Ltd", "region": "North", "category": "Furniture"},
    ],
    "inventory": [
        {"sku": "SKU-001", "qty_on_hand": 150, "reorder_point": 50, "location": "WH-A", "unit_cost": 25.00, "supplier_id": "SUP-001"},
        {"sku": "SKU-002", "qty_on_hand": 80, "reorder_point": 30, "location": "WH-A", "unit_cost": 15.50, "supplier_id": "SUP-001"},
        {"sku": "SKU-003", "qty_on_hand": 25, "reorder_point": 40, "location": "WH-B", "unit_cost": 42.00, "supplier_id": "SUP-002"},
        {"sku": "SKU-004", "qty_on_hand": 200, "reorder_point": 100, "location": "WH-B", "unit_cost": 55.00, "supplier_id": "SUP-003"},
        {"sku": "SKU-005", "qty_on_hand": 10, "reorder_point": 25, "location": "WH-A", "unit_cost": 8.75, "supplier_id": "SUP-002"},
    ],
    "supplier": [
        {"supplier_id": "SUP-001", "supplier_name": "Alpha Supplies", "lead_time": 7, "contact_email": "sales@alpha.com", "rating": 4.5, "country": "USA"},
        {"supplier_id": "SUP-002", "supplier_name": "Beta Manufacturing", "lead_time": 14, "contact_email": "info@beta.com", "rating": 4.0, "country": "Germany"},
        {"supplier_id": "SUP-003", "supplier_name": "Gamma Logistics", "lead_time": 21, "contact_email": "order@gamma.com", "rating": 3.8, "country": "China"},
        {"supplier_id": "SUP-004", "supplier_name": "Delta Trading", "lead_time": 10, "contact_email": "trade@delta.com", "rating": 4.2, "country": "India"},
    ],
    "purchase_order": [
        {"po_number": "PO-001", "sku": "SKU-001", "quantity": 100, "order_date": "2025-01-10", "delivery_date": "2025-01-17", "supplier_id": "SUP-001"},
        {"po_number": "PO-002", "sku": "SKU-003", "quantity": 50, "order_date": "2025-01-12", "delivery_date": "2025-01-26", "supplier_id": "SUP-002"},
        {"po_number": "PO-003", "sku": "SKU-004", "quantity": 200, "order_date": "2025-01-15", "delivery_date": "2025-02-05", "supplier_id": "SUP-003"},
        {"po_number": "PO-004", "sku": "SKU-002", "quantity": 75, "order_date": "2025-01-20", "delivery_date": "2025-01-27", "supplier_id": "SUP-001"},
    ],
}


@router.get("/download/{file_category}")
async def download_template(file_category: str, format: str = "csv"):
    """Download a template file for a given category"""
    if file_category not in SAMPLE_DATA:
        raise HTTPException(404, f"Unknown category: {file_category}")

    df = pd.DataFrame(SAMPLE_DATA[file_category])

    if format == "csv":
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        content = buffer.getvalue().encode()
        media_type = "text/csv"
        ext = "csv"
    elif format == "xlsx":
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, sheet_name="Data")
        content = buffer.getvalue()
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "xlsx"
    else:
        raise HTTPException(400, "Format must be 'csv' or 'xlsx'")

    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{file_category}_template.{ext}"'
        },
    )
