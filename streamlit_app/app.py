"""
Supply Chain Analytics - Main Streamlit Application
"""
import streamlit as st

st.set_page_config(
    page_title="Supply Chain Analytics",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏭 Supply Chain Analytics")
st.markdown("---")

st.markdown("""
### Welcome to the Supply Chain Analytics Platform

This open-source tool helps you **upload, analyze, and get AI-powered insights** 
from your supply chain data.

#### 🚀 Getting Started

1. **📊 Dashboard** — View status of all uploaded data files
2. **📤 Upload Files** — Upload Sales, Inventory, Supplier, and Purchase Order data
3. **📜 History** — View and manage file versions
4. **🔗 MCP Config** — Connect Claude Desktop, Claude Code, or Cursor for AI analysis
5. **⚙️ Settings** — Configure the application

#### 📁 Supported Data Categories

| Category | Required Columns |
|----------|-----------------|
| **Sales** | `date`, `sku`, `quantity`, `revenue` |
| **Inventory** | `sku`, `qty_on_hand`, `reorder_point` |
| **Suppliers** | `supplier_id`, `supplier_name`, `lead_time` |
| **Purchase Orders** | `po_number`, `sku`, `quantity` |

#### 🤖 AI Integration

After uploading data, go to the **🔗 MCP Config** page to get configuration 
that connects your data to:
- **Claude Desktop** — Full conversational analysis
- **Claude Code** — Code-level data interaction
- **Cursor** — AI-powered IDE analysis
""")

# Quick status check
st.markdown("---")
st.subheader("📡 System Status")

from utils.api_client import get_api_client

api = get_api_client()
response = api.get("/health")

if response.status_code == 200:
    health = response.json()
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ API Server: {health.get('status', 'unknown')}")
    with col2:
        st.success(f"✅ Database: {health.get('database', 'unknown')}")
else:
    st.error("❌ Backend API is not running. Start it with: `cd backend && uvicorn main:app --reload --port 8000`")
