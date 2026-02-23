"""
🔗 MCP Config - Generate MCP server configuration for AI tools
"""
import streamlit as st
import json
from utils.api_client import get_api_client

st.set_page_config(page_title="MCP Config", page_icon="🔗", layout="wide")

api = get_api_client()

st.title("🔗 MCP Configuration")
st.markdown("Connect **Claude Desktop**, **Claude Code**, or **Cursor** to your supply chain data")

st.info(
    "💡 **What is MCP?** Model Context Protocol (MCP) lets AI assistants like Claude "
    "directly access your supply chain data through tools. After configuring, just ask "
    "questions in natural language!"
)

# ─── Fetch Config ─────────────────────────────────────────────


@st.cache_data(ttl=300)
def get_mcp_config():
    resp = api.get("/api/mcp/config")
    if resp.status_code == 200:
        return resp.json()
    return None


config = get_mcp_config()

if not config:
    st.error("❌ Cannot connect to backend. Start the API server first.")
    st.code("cd backend && uvicorn main:app --reload --port 8000", language="bash")
    st.stop()

# ─── Tab Layout ───────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "🖥️ Claude Desktop",
    "💻 Claude Code",
    "📝 Cursor",
    "📖 Instructions",
])

# ─── Claude Desktop ───────────────────────────────────────────

with tab1:
    st.subheader("Claude Desktop Configuration")

    st.markdown("""
    **Steps:**
    1. Open Claude Desktop
    2. Go to **Settings** → **Developer** → **Edit Config**
    3. Paste the JSON below into `claude_desktop_config.json`
    4. **Restart Claude Desktop**
    5. Look for 🔧 tools icon in the chat — you'll see supply chain tools!
    """)

    desktop_config = config.get("claude_desktop", {})
    config_json = json.dumps(desktop_config, indent=2)

    st.code(config_json, language="json")

    st.download_button(
        "📥 Download claude_desktop_config.json",
        config_json,
        "claude_desktop_config.json",
        "application/json",
    )

    st.markdown("**Config file location:**")
    st.code(r"Windows: %APPDATA%\Claude\claude_desktop_config.json", language="text")
    st.code("macOS: ~/Library/Application Support/Claude/claude_desktop_config.json", language="text")

# ─── Claude Code ──────────────────────────────────────────────

with tab2:
    st.subheader("Claude Code (CLI) Configuration")

    st.markdown("""
    **Steps:**
    1. Create a `.claude/` folder in your project root
    2. Create `mcp.json` inside it
    3. Paste the JSON below
    4. Run `claude` CLI — it will auto-detect the MCP server
    """)

    code_config = config.get("claude_code", {})
    code_json = json.dumps(code_config, indent=2)

    st.code(code_json, language="json")

    st.download_button(
        "📥 Download mcp.json (Claude Code)",
        code_json,
        "mcp.json",
        "application/json",
        key="dl_claude_code",
    )

    st.markdown("**Quick setup:**")
    st.code("mkdir -p .claude && echo '{}' > .claude/mcp.json".format(
        code_json.replace("'", "\\'")
    ), language="bash")

# ─── Cursor ───────────────────────────────────────────────────

with tab3:
    st.subheader("Cursor IDE Configuration")

    st.markdown("""
    **Steps:**
    1. Open Cursor
    2. Go to **Settings** → **MCP Servers**
    3. Click **Add Server** and paste the config, OR:
    4. Create `.cursor/mcp.json` in your project root
    5. Paste the JSON below
    6. **Restart Cursor**
    """)

    cursor_config = config.get("cursor", {})
    cursor_json = json.dumps(cursor_config, indent=2)

    st.code(cursor_json, language="json")

    st.download_button(
        "📥 Download mcp.json (Cursor)",
        cursor_json,
        "mcp.json",
        "application/json",
        key="dl_cursor",
    )

# ─── Instructions ─────────────────────────────────────────────

with tab4:
    st.subheader("📖 Complete Setup Guide")

    st.markdown(config.get("instructions", ""))

    st.divider()

    st.subheader("🤖 Available MCP Tools")

    st.markdown("""
    Once connected, your AI assistant gets access to these tools:

    | Tool | What it does |
    |------|-------------|
    | `query_sales_data` | Query and analyze sales with date/SKU filters |
    | `query_inventory` | Check stock levels, find items needing reorder |
    | `query_suppliers` | Look up supplier info and performance |
    | `query_purchase_orders` | Analyze purchase order data |
    | `run_sql_query` | Execute custom SQL on supply chain database |
    | `get_supply_chain_graph` | Query supply chain relationships (FalkorDB) |
    | `get_data_quality_report` | Get data quality metrics for uploaded files |
    | `get_kpi_dashboard` | See key performance indicators at a glance |
    | `detect_anomalies` | Find unusual patterns in supply chain data |
    | `forecast_demand` | Simple demand forecasting for a given SKU |
    | `analyze_supplier_risk` | Assess risk scores for suppliers |
    | `get_reorder_recommendations` | Smart suggestions for what to reorder |
    """)

    st.subheader("💬 Example Prompts")

    examples = [
        "What are my top 10 selling products by revenue?",
        "Which inventory items are below their reorder point?",
        "Show me a summary of all supplier performance ratings",
        "Are there any anomalies in recent sales data?",
        "Forecast demand for SKU-001 for the next 30 days",
        "Which suppliers have the longest lead times?",
        "What's the total value of open purchase orders?",
        "Run a query: SELECT sku, SUM(revenue) FROM sales_data GROUP BY sku ORDER BY 2 DESC LIMIT 10",
    ]

    for ex in examples:
        st.code(ex, language="text")

# ─── Server Info ──────────────────────────────────────────────

st.divider()
with st.expander("🔧 Technical Details"):
    st.json({
        "server_path": config.get("server_path", ""),
        "python_path": config.get("python_path", ""),
        "duckdb_path": config.get("claude_desktop", {}).get("mcpServers", {}).get(
            "supply-chain-analytics", {}
        ).get("env", {}).get("DUCKDB_PATH", ""),
    })
