# 🏭 Supply Chain Analytics - Open Source

> **Clone → Upload Data → Connect AI → Get Insights**

A complete open-source supply chain analytics platform with **Streamlit UI** for data upload, **DuckDB + FalkorDB** for storage/analysis, and an **MCP Server** that lets you connect **Claude Desktop, Claude Code, or Cursor** for AI-powered supply chain intelligence.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Clone & Install

```bash
git clone https://github.com/your-org/supply-chain-analytics.git
cd supply-chain-analytics
pip install -r requirements.txt
python scripts/setup_database.py
```

### Step 2: Run the App

```bash
# Terminal 1: Start Backend API
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2: Start Streamlit Frontend
cd streamlit_app && streamlit run app.py

# Terminal 3: Start MCP Server
cd mcp_server && python server.py
```

### Step 3: Connect AI

After uploading data in Streamlit, go to the **🔗 MCP Config** page and copy the JSON config into:

- **Claude Desktop** → `claude_desktop_config.json`
- **Claude Code** → `.claude/mcp.json`
- **Cursor** → `.cursor/mcp.json`

---

## 📋 Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│   Streamlit  │───▶│  FastAPI      │───▶│  DuckDB          │
│   Frontend   │    │  Backend      │    │  (Analytics DB)   │
│  :8501       │    │  :8000        │    │                  │
└──────────────┘    └──────┬───────┘    └──────────────────┘
                           │
                           ▼
                    ┌──────────────┐    ┌──────────────────┐
                    │  FalkorDB    │    │  MCP Server      │
                    │  (Graph DB)  │    │  (AI Tools)      │
                    │  :6379       │    │  stdio/SSE       │
                    └──────────────┘    └──────────────────┘
                                               │
                           ┌───────────────────┤
                           ▼                   ▼
                    ┌──────────────┐    ┌──────────────┐
                    │ Claude       │    │ Cursor /     │
                    │ Desktop/Code │    │ Other AI     │
                    └──────────────┘    └──────────────┘
```

## 📁 Data Categories

| Category            | Required Columns                            | Formats   |
| ------------------- | ------------------------------------------- | --------- |
| **Sales**           | `date`, `sku`, `quantity`, `revenue`        | CSV, XLSX |
| **Inventory**       | `sku`, `qty_on_hand`, `reorder_point`       | CSV, XLSX |
| **Suppliers**       | `supplier_id`, `supplier_name`, `lead_time` | CSV, XLSX |
| **Purchase Orders** | `po_number`, `sku`, `quantity`              | CSV, XLSX |

## 🤖 MCP Tools (AI gets these)

| Tool                          | Description                               |
| ----------------------------- | ----------------------------------------- |
| `query_sales_data`            | Query and analyze sales data with filters |
| `query_inventory`             | Check inventory levels and reorder status |
| `query_suppliers`             | Look up supplier info and performance     |
| `query_purchase_orders`       | Analyze purchase order data               |
| `run_sql_query`               | Execute custom SQL on DuckDB              |
| `get_supply_chain_graph`      | Query supply chain relationships          |
| `get_data_quality_report`     | Get data quality metrics                  |
| `get_kpi_dashboard`           | Get key performance indicators            |
| `detect_anomalies`            | Find anomalies in supply chain data       |
| `forecast_demand`             | Simple demand forecasting                 |
| `analyze_supplier_risk`       | Assess supplier risk scores               |
| `get_reorder_recommendations` | Smart reorder suggestions                 |

## 🐳 Docker Setup

```bash
docker-compose up --build
```

## 📝 License

MIT License - Use freely for any purpose.
