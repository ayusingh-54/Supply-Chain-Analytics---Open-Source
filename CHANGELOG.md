# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Prophet/ARIMA demand forecasting integration
- ABC/XYZ inventory classification
- User authentication and RBAC
- Scheduled data refresh jobs
- Email/Slack alerting

---

## [1.0.0] - 2025-01-01

### Added

#### Core Platform
- **FastAPI Backend** — RESTful API with Swagger/ReDoc documentation
- **Streamlit Frontend** — Multi-page data management UI with file upload wizard
- **DuckDB Integration** — Embedded OLAP database for analytical queries
- **FalkorDB Integration** — Optional graph database for relationship modeling
- **MCP Server** — 12-tool Model Context Protocol server for AI integration

#### Data Management
- File upload with automatic schema validation (CSV/XLSX)
- Data quality engine with duplicate detection, null handling, and constraint checks
- Quality scoring (0-100) based on valid row ratio and unresolved issues
- File versioning with archive/restore capabilities
- Template download for all data categories (Sales, Inventory, Supplier, Purchase Orders)

#### Analytics
- Key Performance Indicator (KPI) dashboard across all data categories
- Sales summary with date, SKU, and region filtering
- Inventory status monitoring with reorder alerts
- Supplier performance analysis with rating and lead time metrics
- Custom SQL query execution (SELECT only, with security filtering)

#### AI Integration (MCP Tools)
- `query_sales_data` — Sales data queries with aggregation modes
- `query_inventory` — Inventory level checks with status filtering
- `query_suppliers` — Supplier information lookup with country/rating filters
- `query_purchase_orders` — Purchase order analysis
- `run_sql_query` — Custom SQL execution (read-only, security-hardened)
- `get_data_quality_report` — File quality metrics
- `get_kpi_dashboard` — Cross-domain KPI summary
- `detect_anomalies` — Statistical outlier detection
- `forecast_demand` — Moving-average demand forecasting
- `analyze_supplier_risk` — Multi-factor risk scoring
- `get_reorder_recommendations` — Priority-ranked reorder suggestions
- `get_supply_chain_graph` — Supply chain relationship network

#### Infrastructure
- Docker Compose deployment with 3 services (backend, streamlit, falkordb)
- Individual Dockerfiles for backend and frontend
- Platform-specific start scripts (Windows `.bat`, Linux/macOS `.sh`)
- Sample data generator (500 sales, 50 inventory, 20 suppliers, 200 POs)
- Database initialization script
- pytest test suite with API and service tests

#### Security
- SQL injection prevention (SELECT-only with keyword blocklist)
- Read-only DuckDB connections in MCP server
- CORS middleware configuration
- File extension validation
- Input sanitization on all API endpoints

---

## [0.1.0] - 2024-12-01

### Added
- Initial project scaffolding
- Basic DuckDB database schema
- Proof-of-concept MCP server with 3 tools
- Minimal Streamlit file upload interface

---

[Unreleased]: https://github.com/your-org/supply-chain-analytics/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-org/supply-chain-analytics/releases/tag/v1.0.0
[0.1.0]: https://github.com/your-org/supply-chain-analytics/releases/tag/v0.1.0
