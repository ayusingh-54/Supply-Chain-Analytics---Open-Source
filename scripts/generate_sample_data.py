"""
Generate realistic sample data for all 4 supply chain categories.
Creates CSV files that can be uploaded via the Streamlit interface.

Usage:
    python scripts/generate_sample_data.py
"""
import os
import sys
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "sample_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)

# ─── Common Reference Data ────────────────────────────────────

SKUS = [f"SKU-{str(i).zfill(4)}" for i in range(1, 51)]  # 50 SKUs
REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
CATEGORIES = ["Electronics", "Packaging", "Raw Materials", "Components", "Finished Goods"]
LOCATIONS = ["Warehouse-A", "Warehouse-B", "Warehouse-C", "DC-East", "DC-West"]
COUNTRIES = ["USA", "China", "Germany", "Japan", "India", "Mexico", "UK", "South Korea"]
SUPPLIER_IDS = [f"SUP-{str(i).zfill(3)}" for i in range(1, 21)]  # 20 suppliers
SUPPLIER_NAMES = [
    "Apex Manufacturing", "BlueWave Components", "CrystalTech Industries",
    "Delta Supply Co", "EcoSource Materials", "Frontier Electronics",
    "GlobalParts Inc", "Horizon Raw Ltd", "InnoSupply Corp", "JetStream Logistics",
    "KeyStone Materials", "LightPath Components", "MetalWorks International",
    "NovaTech Supplies", "OmniSource Trading", "PrimeParts Global",
    "QuickShip Solutions", "ReliSource Inc", "SteadyFlow Materials", "TechBridge Supply"
]
FIRST_NAMES = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry",
               "Iris", "Jack", "Karen", "Leo", "Maria", "Nate", "Olivia", "Paul"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
              "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor", "Thomas", "Moore"]


def generate_sales_data(num_records: int = 500):
    """Generate sales data CSV"""
    filepath = OUTPUT_DIR / "sales_data.csv"
    start_date = datetime(2024, 1, 1)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "sku", "quantity", "revenue", "customer_name", "region", "category"])

        for _ in range(num_records):
            days_offset = random.randint(0, 180)
            date = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            sku = random.choice(SKUS)
            quantity = random.randint(1, 200)
            unit_price = round(random.uniform(5.0, 500.0), 2)
            revenue = round(quantity * unit_price, 2)
            customer = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            region = random.choice(REGIONS)
            category = random.choice(CATEGORIES)

            writer.writerow([date, sku, quantity, revenue, customer, region, category])

    print(f"  ✅ Sales data: {num_records} records → {filepath}")
    return filepath


def generate_inventory_data():
    """Generate inventory data CSV"""
    filepath = OUTPUT_DIR / "inventory_data.csv"

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sku", "qty_on_hand", "reorder_point", "location", "unit_cost", "supplier_id"])

        for sku in SKUS:
            reorder_point = random.randint(10, 100)
            # Some items below reorder point for testing
            if random.random() < 0.3:
                qty_on_hand = random.randint(0, reorder_point)
            else:
                qty_on_hand = random.randint(reorder_point, reorder_point * 3)
            location = random.choice(LOCATIONS)
            unit_cost = round(random.uniform(2.0, 250.0), 2)
            supplier_id = random.choice(SUPPLIER_IDS)

            writer.writerow([sku, qty_on_hand, reorder_point, location, unit_cost, supplier_id])

    print(f"  ✅ Inventory data: {len(SKUS)} records → {filepath}")
    return filepath


def generate_supplier_data():
    """Generate supplier data CSV"""
    filepath = OUTPUT_DIR / "supplier_data.csv"

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["supplier_id", "supplier_name", "lead_time", "contact_email", "rating", "country"])

        for i, sup_id in enumerate(SUPPLIER_IDS):
            name = SUPPLIER_NAMES[i]
            lead_time = random.randint(3, 45)
            email = f"contact@{name.lower().replace(' ', '').replace('.', '')}.com"
            # Most decent, some poor for testing risk analysis
            rating = round(random.uniform(2.0, 5.0), 1)
            country = random.choice(COUNTRIES)

            writer.writerow([sup_id, name, lead_time, email, rating, country])

    print(f"  ✅ Supplier data: {len(SUPPLIER_IDS)} records → {filepath}")
    return filepath


def generate_purchase_order_data(num_records: int = 200):
    """Generate purchase order data CSV"""
    filepath = OUTPUT_DIR / "purchase_order_data.csv"
    start_date = datetime(2024, 1, 1)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["po_number", "sku", "quantity", "order_date", "delivery_date", "supplier_id"])

        for i in range(num_records):
            po_number = f"PO-{str(10000 + i).zfill(6)}"
            sku = random.choice(SKUS)
            quantity = random.randint(50, 1000)
            days_offset = random.randint(0, 150)
            order_date = start_date + timedelta(days=days_offset)
            lead_time = random.randint(5, 30)
            delivery_date = order_date + timedelta(days=lead_time)
            supplier_id = random.choice(SUPPLIER_IDS)

            writer.writerow([
                po_number, sku, quantity,
                order_date.strftime("%Y-%m-%d"),
                delivery_date.strftime("%Y-%m-%d"),
                supplier_id
            ])

    print(f"  ✅ Purchase order data: {num_records} records → {filepath}")
    return filepath


if __name__ == "__main__":
    print("🏭 Generating Supply Chain Sample Data...\n")
    generate_sales_data(500)
    generate_inventory_data()
    generate_supplier_data()
    generate_purchase_order_data(200)
    print(f"\n✅ All sample data files saved to: {OUTPUT_DIR}")
    print("   Upload these through the Streamlit interface at http://localhost:8501")
