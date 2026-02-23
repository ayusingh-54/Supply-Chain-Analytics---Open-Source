<div align="center">

# 🏭 Supply Chain Analytics Platform

**Open-Source, AI-Ready Supply Chain Intelligence System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-FF4B4B.svg)](https://streamlit.io)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.10-FFF000.svg)](https://duckdb.org)
[![MCP](https://img.shields.io/badge/MCP-1.2-purple.svg)](https://modelcontextprotocol.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> **Clone → Upload Data → Connect AI → Get Insights**

A production-ready, open-source supply chain analytics platform featuring a **Streamlit UI** for data management, **DuckDB** for high-performance OLAP analytics, **FalkorDB** for graph-based relationship analysis, and a **Model Context Protocol (MCP) Server** that enables seamless integration with **Claude Desktop**, **Claude Code**, **Cursor**, and any MCP-compatible AI client.

[Quick Start](#-quick-start) · [Architecture](#-architecture) · [Documentation](docs/) · [API Reference](#-api-reference) · [Contributing](CONTRIBUTING.md)

</div>

---

## Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Data Categories & Schemas](#-data-categories--schemas)
- [API Reference](#-api-reference)
- [MCP Server & AI Integration](#-mcp-server--ai-integration)
- [Graph Database (FalkorDB)](#-graph-database-falkordb)
- [Docker Deployment](#-docker-deployment)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## ✨ Features

### Core Platform

- **📤 Drag-and-Drop File Upload** — Upload CSV/XLSX files with automatic schema validation
- **🔍 Data Quality Engine** — Automated duplicate detection, null handling, constraint validation, and quality scoring
- **📊 Real-Time Dashboard** — Monitor file status, data quality, KPIs, and inventory alerts
- **🗂️ File Versioning** — Full version history with archive/restore capabilities
- **📥 Template Downloads** — Pre-built CSV/XLSX templates for every data category

### Analytics & Intelligence

- **📈 KPI Dashboard** — Revenue, inventory turnover, supplier ratings, order volumes
- **🔔 Anomaly Detection** — Statistical outlier detection across sales, inventory, and suppliers
- **📉 Demand Forecasting** — Moving-average based demand prediction per SKU
- **⚠️ Supplier Risk Analysis** — Multi-factor risk scoring (lead time, rating, concentration)
- **🛒 Smart Reorder Recommendations** — Priority-ranked reorder suggestions based on velocity and lead times
- **🕸️ Supply Chain Graph** — Relationship mapping between suppliers, products, and purchase orders

### AI Integration (MCP)

- **12 MCP Tools** — Purpose-built tools that give AI assistants direct access to your supply chain data
- **Multi-Client Support** — Works with Claude Desktop, Claude Code, Cursor, and any MCP-compatible client
- **Dual Transport** — stdio (default) and SSE transport modes
- **Auto-Config Generation** — One-click JSON config generation for every supported AI client
- **Read-Only by Default** — SQL injection protection and query whitelisting for production safety

### Infrastructure

- **⚡ DuckDB** — Embedded OLAP database for sub-second analytical queries on millions of rows
- **🕸️ FalkorDB** — Optional graph database for supply chain relationship modeling (Cypher queries)
- **🐳 Docker Compose** — Full stack orchestration with persistent volumes
- **🧪 Test Suite** — pytest-based unit and integration tests
- **🔧 One-Command Setup** — Platform-specific start scripts for Windows (`start.bat`) and Linux/macOS (`start.sh`)

---

## 🚀 Quick Start

### Prerequisites

| Requirement                 | Version | Notes                        |
| --------------------------- | ------- | ---------------------------- |
| Python                      | 3.11+   | Core runtime                 |
| pip                         | Latest  | Package management           |
| Docker _(optional)_         | 20.10+  | For containerized deployment |
| Docker Compose _(optional)_ | 2.0+    | For full-stack orchestration |

### Option A: Local Development (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/supply-chain-analytics.git
cd supply-chain-analytics

# 2. Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize the database
python scripts/setup_database.py

# 5. (Optional) Generate sample data
python scripts/generate_sample_data.py

# 6. Start the platform
# Terminal 1 — Backend API
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 — Streamlit Frontend
cd streamlit_app && streamlit run app.py

# Terminal 3 — MCP Server (for AI integration)
cd mcp_server && python server.py
```

### Option B: One-Command Start

```bash
# Windows
start.bat

# Linux / macOS
chmod +x start.sh && ./start.sh
```

### Option C: Docker Compose

```bash
docker-compose up --build
```

### Verify Installation

| Service          | URL                          | Description                                |
| ---------------- | ---------------------------- | ------------------------------------------ |
| **Streamlit UI** | http://localhost:8501        | Data upload & dashboard                    |
| **FastAPI Docs** | http://localhost:8000/docs   | Interactive API documentation (Swagger UI) |
| **API ReDoc**    | http://localhost:8000/redoc  | Alternative API docs                       |
| **Health Check** | http://localhost:8000/health | Service health status                      |

---

## 📋 Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                              │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    Streamlit Frontend (:8501)                      │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │  │
│  │  │Dashboard │ │ Upload   │ │ History  │ │MCP Config│ │Settings│  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘  │  │
│  └────────────────────────────┬───────────────────────────────────────┘  │
│                               │ HTTP/REST                                │
├───────────────────────────────┼──────────────────────────────────────────┤
│                          SERVICE LAYER                                   │
│                               │                                          │
│  ┌────────────────────────────▼───────────────────────────────────────┐  │
│  │                    FastAPI Backend (:8000)                          │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │  │
│  │  │ /api/files   │ │/api/database │ │/api/templates│ │ /api/mcp │ │  │
│  │  └──────┬───────┘ └──────┬───────┘ └──────────────┘ └──────────┘ │  │
│  │         │                │                                         │  │
│  │  ┌──────▼────────────────▼─────────────────────────────────────┐  │  │
│  │  │              Services Layer                                  │  │  │
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│  │  │
│  │  │  │ FileService  │ │DuckDBService │ │ FalkorDBService      ││  │  │
│  │  │  │ • Validation │ │ • Analytics  │ │ • Graph Queries      ││  │  │
│  │  │  │ • Quality    │ │ • KPIs       │ │ • Relationship Sync  ││  │  │
│  │  │  │ • Storage    │ │ • SQL Engine │ │ • Cypher Engine      ││  │  │
│  │  │  └──────────────┘ └──────┬───────┘ └──────────┬───────────┘│  │  │
│  │  └──────────────────────────┼────────────────────┼────────────┘  │  │
│  └─────────────────────────────┼────────────────────┼────────────────┘  │
│                                │                    │                    │
├────────────────────────────────┼────────────────────┼────────────────────┤
│                          DATA LAYER                  │                    │
│                                │                    │                    │
│  ┌─────────────────────────────▼──┐  ┌──────────────▼─────────────────┐ │
│  │       DuckDB (Embedded)        │  │     FalkorDB (:6379)           │ │
│  │  • sales_data                  │  │  • :Supplier nodes             │ │
│  │  • inventory_data              │  │  • :Product nodes              │ │
│  │  • supplier_data               │  │  • :PurchaseOrder nodes        │ │
│  │  • purchase_order_data         │  │  • :SUPPLIES relationships     │ │
│  │  • file_uploads (metadata)     │  │  • :ORDERS relationships       │ │
│  │  • file_versions               │  │  • :FROM_SUPPLIER relationships│ │
│  │  • data_quality_issues         │  │                                │ │
│  └────────────────────────────────┘  └────────────────────────────────┘ │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                       AI INTEGRATION LAYER                               │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                MCP Server (stdio / SSE :3001)                      │  │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────────────┐ │  │
│  │  │ Data Queries   │ │ Analytics      │ │ Intelligence           │ │  │
│  │  │ • sales        │ │ • KPI dashboard│ │ • anomaly detection    │ │  │
│  │  │ • inventory    │ │ • data quality │ │ • demand forecasting   │ │  │
│  │  │ • suppliers    │ │ • supply graph │ │ • supplier risk        │ │  │
│  │  │ • POs          │ │ • custom SQL   │ │ • reorder suggestions  │ │  │
│  │  └───────┬────────┘ └───────┬────────┘ └───────────┬────────────┘ │  │
│  └──────────┼──────────────────┼──────────────────────┼──────────────┘  │
│             │                  │                      │                   │
│  ┌──────────▼──────────────────▼──────────────────────▼──────────────┐   │
│  │              MCP-Compatible AI Clients                            │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐              │   │
│  │  │Claude Desktop│ │ Claude Code  │ │   Cursor     │  + Others    │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘              │   │
│  └───────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer            | Technology                | Purpose                                     |
| ---------------- | ------------------------- | ------------------------------------------- |
| Frontend         | Streamlit 1.31            | Interactive data management UI              |
| Backend API      | FastAPI 0.109 + Uvicorn   | High-performance async REST API             |
| Analytics DB     | DuckDB 0.10               | Embedded columnar OLAP engine               |
| Graph DB         | FalkorDB 1.0 _(optional)_ | Supply chain relationship modeling          |
| AI Protocol      | MCP 1.2                   | Model Context Protocol for AI tool exposure |
| Data Processing  | Pandas 2.1 + NumPy 1.26   | DataFrame operations and validation         |
| Visualization    | Plotly 5.18               | Interactive charts and plots                |
| Containerization | Docker + Compose          | Production deployment                       |

---

## 🛠️ Installation

### System Requirements

| Component | Minimum                            | Recommended                |
| --------- | ---------------------------------- | -------------------------- |
| CPU       | 2 cores                            | 4+ cores                   |
| RAM       | 2 GB                               | 8+ GB                      |
| Disk      | 500 MB                             | 5+ GB (for large datasets) |
| OS        | Windows 10, Ubuntu 20.04, macOS 12 | Latest LTS versions        |

### Step-by-Step Installation

#### 1. Clone Repository

```bash
git clone https://github.com/your-org/supply-chain-analytics.git
cd supply-chain-analytics
```

#### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

<details>
<summary><strong>📦 Full Dependency List</strong></summary>

| Package             | Version | Purpose                         |
| ------------------- | ------- | ------------------------------- |
| `fastapi`           | 0.109.0 | REST API framework              |
| `uvicorn`           | 0.27.0  | ASGI server                     |
| `python-multipart`  | 0.0.6   | File upload handling            |
| `streamlit`         | 1.31.0  | Web frontend framework          |
| `plotly`            | 5.18.0  | Interactive visualizations      |
| `pandas`            | 2.1.4   | Data manipulation               |
| `openpyxl`          | 3.1.2   | Excel file support              |
| `duckdb`            | 0.10.0  | Analytical database             |
| `falkordb`          | 1.0.3   | Graph database client           |
| `redis`             | 5.0.1   | FalkorDB connection layer       |
| `requests`          | 2.31.0  | HTTP client                     |
| `httpx`             | 0.26.0  | Async HTTP client               |
| `mcp`               | 1.2.0   | Model Context Protocol SDK      |
| `python-dotenv`     | 1.0.0   | Environment configuration       |
| `pydantic`          | 2.5.3   | Data validation & serialization |
| `pydantic-settings` | 2.1.0   | Settings management             |
| `numpy`             | 1.26.4  | Numerical operations            |

</details>

#### 4. Initialize Database

```bash
python scripts/setup_database.py
```

#### 5. (Optional) Generate Sample Data

```bash
python scripts/generate_sample_data.py
```

This generates 4 CSV files in `sample_data/`:

- `sales_data.csv` — 500 sales transactions
- `inventory_data.csv` — 50 SKU inventory records
- `supplier_data.csv` — 20 supplier profiles
- `purchase_order_data.csv` — 200 purchase orders

#### 6. (Optional) Start FalkorDB for Graph Features

```bash
docker run -d --name falkordb -p 6379:6379 falkordb/falkordb:latest
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root (or copy from `.env.example`):

```env
# Database
DUCKDB_PATH=./data/supply_chain.duckdb

# Storage
STORAGE_PATH=./storage

# FalkorDB (optional)
USE_FALKORDB=false
FALKORDB_HOST=localhost
FALKORDB_PORT=6379

# Upload Limits
MAX_FILE_SIZE_MB=200

# MCP Server
MCP_SERVER_PORT=3001
```

### Configuration Reference

| Variable           | Default                      | Description                     |
| ------------------ | ---------------------------- | ------------------------------- |
| `DUCKDB_PATH`      | `./data/supply_chain.duckdb` | Path to DuckDB database file    |
| `STORAGE_PATH`     | `./storage`                  | Root directory for file storage |
| `USE_FALKORDB`     | `false`                      | Enable FalkorDB graph database  |
| `FALKORDB_HOST`    | `localhost`                  | FalkorDB server hostname        |
| `FALKORDB_PORT`    | `6379`                       | FalkorDB server port            |
| `MAX_FILE_SIZE_MB` | `200`                        | Maximum upload file size in MB  |
| `MCP_SERVER_PORT`  | `3001`                       | Port for SSE transport mode     |

---

## 📖 Usage Guide

### 1. Upload Data

Navigate to **📤 Upload Files** in the Streamlit UI:

1. **Select category** (Sales, Inventory, Supplier, or Purchase Order)
2. **Download template** to see the expected format
3. **Upload your CSV/XLSX** file
4. **Review validation** — schema checks, quality issues, data preview
5. **Confirm upload** — data is loaded into DuckDB

### 2. Monitor Dashboard

The **📊 Dashboard** shows:

- Upload status for all 4 data categories
- Row counts and data quality scores
- Quick actions: preview data, replace files, view history

### 3. Connect AI

Go to **🔗 MCP Config** and copy the generated JSON config into your AI client:

**Claude Desktop:**

```
Windows: %APPDATA%\Claude\claude_desktop_config.json
macOS:   ~/Library/Application Support/Claude/claude_desktop_config.json
```

**Claude Code:**

```
.claude/mcp.json (in your project root)
```

**Cursor:**

```
.cursor/mcp.json (in your project root)
```

### 4. Ask AI Questions

Once connected, ask questions like:

- _"What are my top 10 selling products by revenue?"_
- _"Which inventory items are below their reorder point?"_
- _"Analyze supplier risk for SUP-003"_
- _"Forecast demand for SKU-001 over the next 30 days"_
- _"Show me the supply chain network overview"_
- _"Run a query: SELECT sku, SUM(revenue) FROM sales_data GROUP BY sku ORDER BY 2 DESC LIMIT 10"_

---

## 📁 Data Categories & Schemas

### Sales Data

| Column          | Type    | Required | Constraints                         |
| --------------- | ------- | -------- | ----------------------------------- |
| `date`          | DATE    | ✅       | Valid date, not in future (warning) |
| `sku`           | VARCHAR | ✅       | —                                   |
| `quantity`      | FLOAT   | ✅       | ≥ 0                                 |
| `revenue`       | FLOAT   | ✅       | ≥ 0                                 |
| `customer_name` | VARCHAR | ❌       | —                                   |
| `region`        | VARCHAR | ❌       | —                                   |
| `category`      | VARCHAR | ❌       | —                                   |

### Inventory Data

| Column          | Type    | Required | Constraints            |
| --------------- | ------- | -------- | ---------------------- |
| `sku`           | VARCHAR | ✅       | —                      |
| `qty_on_hand`   | INTEGER | ✅       | ≥ 0                    |
| `reorder_point` | INTEGER | ✅       | ≥ 0                    |
| `location`      | VARCHAR | ❌       | —                      |
| `unit_cost`     | FLOAT   | ❌       | —                      |
| `supplier_id`   | VARCHAR | ❌       | Links to Supplier Data |

### Supplier Data

| Column          | Type    | Required | Constraints       |
| --------------- | ------- | -------- | ----------------- |
| `supplier_id`   | VARCHAR | ✅       | Unique identifier |
| `supplier_name` | VARCHAR | ✅       | —                 |
| `lead_time`     | INTEGER | ✅       | ≥ 0 (days)        |
| `contact_email` | VARCHAR | ❌       | —                 |
| `rating`        | FLOAT   | ❌       | 0.0 – 5.0         |
| `country`       | VARCHAR | ❌       | —                 |

### Purchase Order Data

| Column          | Type    | Required | Constraints            |
| --------------- | ------- | -------- | ---------------------- |
| `po_number`     | VARCHAR | ✅       | Unique identifier      |
| `sku`           | VARCHAR | ✅       | Links to Inventory     |
| `quantity`      | FLOAT   | ✅       | ≥ 0                    |
| `order_date`    | DATE    | ❌       | —                      |
| `delivery_date` | DATE    | ❌       | —                      |
| `supplier_id`   | VARCHAR | ❌       | Links to Supplier Data |

### Data Quality Pipeline

The upload pipeline applies these checks automatically:

1. **Schema Validation** — Required columns present, types correct
2. **Duplicate Detection** — Exact duplicate rows removed (auto-resolved)
3. **Null Handling** — Rows with null required fields removed (auto-resolved)
4. **Constraint Checks** — Negative value validation (auto-resolved)
5. **Date Validation** — Future date detection (flagged as warning)
6. **Quality Scoring** — 0–100 score based on valid row ratio and unresolved issues

---

## 🔌 API Reference

### Base URL

```
http://localhost:8000
```

### Endpoints

#### Health & Info

| Method | Endpoint  | Description                 |
| ------ | --------- | --------------------------- |
| `GET`  | `/`       | API information             |
| `GET`  | `/health` | Health check with DB status |

#### File Management (`/api/files`)

| Method | Endpoint                        | Description                       |
| ------ | ------------------------------- | --------------------------------- |
| `POST` | `/api/files/upload`             | Upload and process a data file    |
| `POST` | `/api/files/validate`           | Validate a file without uploading |
| `GET`  | `/api/files/status`             | Get status of all file categories |
| `GET`  | `/api/files/status/{category}`  | Status for specific category      |
| `GET`  | `/api/files/history/{category}` | Version history for a category    |
| `GET`  | `/api/files/preview/{category}` | Preview uploaded data             |
| `GET`  | `/api/files/schema/{category}`  | Expected schema for category      |

#### Database Analytics (`/api/database`)

| Method | Endpoint                          | Description                      |
| ------ | --------------------------------- | -------------------------------- |
| `GET`  | `/api/database/kpis`              | Key performance indicators       |
| `GET`  | `/api/database/sales-summary`     | Sales summary with filters       |
| `GET`  | `/api/database/inventory-status`  | Inventory reorder alerts         |
| `GET`  | `/api/database/supplier-analysis` | Supplier performance analysis    |
| `POST` | `/api/database/query`             | Execute custom SQL (SELECT only) |
| `POST` | `/api/database/refresh`           | Sync data to FalkorDB graph      |

#### Templates (`/api/templates`)

| Method | Endpoint                             | Description                |
| ------ | ------------------------------------ | -------------------------- |
| `GET`  | `/api/templates/download/{category}` | Download template CSV/XLSX |

#### MCP Configuration (`/api/mcp`)

| Method | Endpoint                         | Description                     |
| ------ | -------------------------------- | ------------------------------- |
| `GET`  | `/api/mcp/config`                | Full MCP config for all clients |
| `GET`  | `/api/mcp/config/claude-desktop` | Claude Desktop config only      |
| `GET`  | `/api/mcp/config/cursor`         | Cursor config only              |

### Upload Example

```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@sales_data.csv" \
  -F "file_category=sales" \
  -F "upload_mode=replace" \
  -F "uploaded_by=cli_user"
```

### Query Example

```bash
curl -X POST http://localhost:8000/api/database/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT sku, SUM(revenue) as total FROM sales_data GROUP BY sku ORDER BY total DESC LIMIT 5"}'
```

---

## 🤖 MCP Server & AI Integration

### Overview

The MCP Server exposes 12 supply chain tools via the [Model Context Protocol](https://modelcontextprotocol.io), allowing AI assistants to query, analyze, and reason about your supply chain data in natural language.

### Transport Modes

```bash
# stdio (default) — for Claude Desktop / Claude Code / Cursor
python mcp_server/server.py

# SSE — for web-based or remote clients
python mcp_server/server.py --sse
```

### Available Tools

| #   | Tool                          | Description                             | Key Parameters                                           |
| --- | ----------------------------- | --------------------------------------- | -------------------------------------------------------- |
| 1   | `query_sales_data`            | Query sales with filters & aggregations | `start_date`, `end_date`, `sku`, `region`, `aggregation` |
| 2   | `query_inventory`             | Check stock levels & reorder status     | `sku`, `location`, `status_filter`                       |
| 3   | `query_suppliers`             | Supplier information & performance      | `supplier_id`, `country`, `min_rating`                   |
| 4   | `query_purchase_orders`       | Purchase order analysis                 | `po_number`, `sku`, `supplier_id`                        |
| 5   | `run_sql_query`               | Execute custom SQL (SELECT only)        | `query` (required)                                       |
| 6   | `get_data_quality_report`     | Data quality metrics for all files      | —                                                        |
| 7   | `get_kpi_dashboard`           | Key performance indicators              | —                                                        |
| 8   | `detect_anomalies`            | Find outliers & unusual patterns        | `category` (sales/inventory/supplier/all)                |
| 9   | `forecast_demand`             | Demand forecasting per SKU              | `sku` (required), `periods`                              |
| 10  | `analyze_supplier_risk`       | Multi-factor supplier risk scoring      | `supplier_id`                                            |
| 11  | `get_reorder_recommendations` | Smart reorder suggestions               | —                                                        |
| 12  | `get_supply_chain_graph`      | Supply chain relationship network       | `focus` (overview/supplier_products/product_orders)      |

### Security

- Only `SELECT` queries are permitted through `run_sql_query`
- Dangerous SQL keywords (`DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `CREATE`, `TRUNCATE`, `EXEC`) are blocked
- DuckDB connection is read-only in the MCP server
- No filesystem access is exposed to AI clients

---

## 🕸️ Graph Database (FalkorDB)

FalkorDB provides a property graph model of your supply chain. When enabled, the platform syncs data from DuckDB into a graph with the following schema:

### Graph Model

```
(:Supplier) -[:SUPPLIES]-> (:Product)
(:PurchaseOrder) -[:ORDERS]-> (:Product)
(:PurchaseOrder) -[:FROM_SUPPLIER]-> (:Supplier)
```

### Node Properties

| Node              | Properties                                              |
| ----------------- | ------------------------------------------------------- |
| **Supplier**      | `supplier_id`, `name`, `lead_time`, `country`, `rating` |
| **Product**       | `sku`, `qty_on_hand`, `reorder_point`, `location`       |
| **PurchaseOrder** | `po_number`, `quantity`, `order_date`                   |

### Enabling FalkorDB

```bash
# Start FalkorDB
docker run -d --name falkordb -p 6379:6379 falkordb/falkordb:latest

# Set environment variable
USE_FALKORDB=true

# Sync data (via Settings page or API)
curl -X POST http://localhost:8000/api/database/refresh
```

---

## 🐳 Docker Deployment

### Full Stack (Recommended)

```bash
docker-compose up --build -d
```

This starts:

- **sc-backend** — FastAPI on port 8000
- **sc-streamlit** — Streamlit on port 8501
- **sc-falkordb** — FalkorDB on port 6379

### Individual Services

```bash
# Backend only
docker build -f backend/Dockerfile -t sc-backend .
docker run -p 8000:8000 -v ./data:/app/data sc-backend

# Streamlit only
docker build -f streamlit_app/Dockerfile -t sc-streamlit .
docker run -p 8501:8501 -e API_BASE_URL=http://host.docker.internal:8000/api sc-streamlit
```

### Docker Compose Configuration

```yaml
services:
  backend:
    ports: ["8000:8000"]
    volumes: [./data:/app/data, ./uploads:/app/uploads]
    environment:
      DUCKDB_PATH: /app/data/supply_chain.duckdb
      USE_FALKORDB: "true"
      FALKORDB_HOST: falkordb

  streamlit:
    ports: ["8501:8501"]
    environment:
      API_BASE_URL: http://backend:8000/api

  falkordb:
    image: falkordb/falkordb:latest
    ports: ["6379:6379"]
    volumes: [falkordb_data:/data]
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test modules
pytest tests/test_api.py -v        # API endpoint tests
pytest tests/test_services.py -v   # Service layer tests

# With coverage
pytest tests/ --cov=backend --cov-report=html
```

### Test Categories

| Test Module        | Coverage                                                                                               |
| ------------------ | ------------------------------------------------------------------------------------------------------ |
| `test_api.py`      | Health endpoint, template routes, database routes, MCP config, file status                             |
| `test_services.py` | File validation, schema checking, quality engine, DuckDB operations, MCP tools, sample data generation |

### Test Environment

Tests use:

- Temporary DuckDB database (auto-cleaned)
- FalkorDB disabled (`USE_FALKORDB=false`)
- Isolated storage directory

---

## 📂 Project Structure

```
supply-chain-analytics/
├── backend/                      # FastAPI Backend Application
│   ├── main.py                   # Application entry point & CORS config
│   ├── Dockerfile                # Backend container image
│   ├── api/
│   │   └── routes/
│   │       ├── files.py          # File upload, validation, preview endpoints
│   │       ├── database.py       # Analytics, KPIs, custom query endpoints
│   │       ├── templates.py      # Template download endpoints
│   │       └── mcp_config.py     # MCP configuration generator
│   ├── core/
│   │   ├── config.py             # Pydantic settings & schema rules
│   │   └── database.py           # DuckDB connection & table initialization
│   ├── models/
│   │   └── schemas.py            # Pydantic request/response models
│   └── services/
│       ├── duckdb_service.py     # DuckDB analytics & metadata operations
│       ├── falkordb_service.py   # Graph database operations
│       └── file_service.py       # File validation, quality, upload pipeline
│
├── streamlit_app/                # Streamlit Frontend Application
│   ├── app.py                    # Main app entry & system status
│   ├── Dockerfile                # Frontend container image
│   ├── pages/
│   │   ├── 1_📊_Dashboard.py     # File status & data quality overview
│   │   ├── 2_📤_Upload_Files.py  # Multi-step upload wizard
│   │   ├── 3_📜_History.py       # File version management
│   │   ├── 4_🔗_MCP_Config.py   # AI client config generator
│   │   └── 5_⚙️_Settings.py     # Application settings & quick actions
│   └── utils/
│       └── api_client.py         # FastAPI HTTP client wrapper
│
├── mcp_server/                   # Model Context Protocol Server
│   ├── server.py                 # MCP server with 12 tools (stdio + SSE)
│   └── tools/                    # Tool extensions (future)
│
├── scripts/
│   ├── setup_database.py         # Database initialization script
│   └── generate_sample_data.py   # Realistic sample data generator
│
├── tests/
│   ├── test_api.py               # API integration tests
│   └── test_services.py          # Service unit tests
│
├── data/                         # DuckDB database files (git-ignored)
├── storage/                      # File storage
│   ├── uploads/
│   │   ├── active/               # Currently active files
│   │   ├── archive/              # Archived file versions
│   │   └── staging/              # Temporary upload staging
│   ├── rejected/                 # Files that failed validation
│   ├── templates/                # Template files
│   └── error_reports/            # Error logs
├── sample_data/                  # Generated sample CSV files
│
├── docker-compose.yml            # Full stack Docker orchestration
├── requirements.txt              # Python dependencies
├── start.bat                     # Windows quick-start script
├── start.sh                      # Linux/macOS quick-start script
├── .env.example                  # Environment variable template
├── LICENSE                       # MIT License
├── README.md                     # This file
├── CONTRIBUTING.md               # Contribution guidelines
├── CHANGELOG.md                  # Version history
├── CODE_OF_CONDUCT.md            # Community standards
├── SECURITY.md                   # Security policy
├── Makefile                      # Common development commands
└── pyproject.toml                # Python project metadata
```

---

## 🗺️ Roadmap

### v1.1 — Enhanced Analytics

- [ ] Time-series demand forecasting with Prophet/ARIMA integration
- [ ] ABC/XYZ inventory classification
- [ ] Supplier scorecards with trend analysis
- [ ] Custom dashboard builder

### v1.2 — Enterprise Features

- [ ] User authentication and role-based access control (RBAC)
- [ ] Audit trail for all data operations
- [ ] Scheduled data refresh (cron-based)
- [ ] Email/Slack alerting for anomalies and reorder triggers

### v1.3 — Advanced AI

- [ ] Multi-agent MCP workflows
- [ ] Natural language to SQL with validation
- [ ] AI-generated supply chain reports
- [ ] What-if scenario simulation

### v2.0 — Scale & Integration

- [ ] PostgreSQL/ClickHouse backend option
- [ ] Real-time data streaming (Kafka/Pulsar)
- [ ] ERP system connectors (SAP, Oracle, NetSuite)
- [ ] REST webhook support for event-driven architecture

---

## 🤝 Contributing

We welcome contributions of all kinds! Please read our [Contributing Guide](CONTRIBUTING.md) for details on:

- How to submit bug reports and feature requests
- Development setup and coding standards
- Pull request process and review guidelines
- Code of Conduct

```bash
# Quick contribution setup
git clone https://github.com/your-org/supply-chain-analytics.git
cd supply-chain-analytics
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v  # Ensure tests pass
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute this software for any purpose, including commercial applications.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com) — High-performance Python web framework
- [Streamlit](https://streamlit.io) — Rapid data app development
- [DuckDB](https://duckdb.org) — In-process analytical SQL engine
- [FalkorDB](https://www.falkordb.com) — Ultra-fast graph database
- [Model Context Protocol](https://modelcontextprotocol.io) — AI tool integration standard
- [Pydantic](https://docs.pydantic.dev) — Data validation using Python type hints
- [Pandas](https://pandas.pydata.org) — Data analysis and manipulation

---

<div align="center">

**Built with ❤️ by the Open Source Community**

[⬆ Back to Top](#-supply-chain-analytics-platform)

</div>
