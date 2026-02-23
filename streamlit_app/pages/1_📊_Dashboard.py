"""
📊 Dashboard - File Status Overview
"""
import streamlit as st
import pandas as pd
import time
from utils.api_client import get_api_client

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

api = get_api_client()

st.title("📊 Data Files Dashboard")
st.markdown("Monitor uploaded files and data quality")

# ─── Fetch Status ─────────────────────────────────────────────


@st.cache_data(ttl=30)
def get_file_status():
    response = api.get("/api/files/status")
    if response.status_code == 200:
        return response.json()
    return {}


file_status = get_file_status()

if not file_status:
    st.warning("⚠️ Cannot connect to backend. Make sure the API server is running.")
    st.code("cd backend && uvicorn main:app --reload --port 8000", language="bash")
    st.stop()

# ─── File Cards ───────────────────────────────────────────────

CATEGORY_ICONS = {
    "sales": "💰",
    "inventory": "📦",
    "supplier": "🏢",
    "purchase_order": "📋",
}

CATEGORY_LABELS = {
    "sales": "Sales Data",
    "inventory": "Inventory Data",
    "supplier": "Supplier Data",
    "purchase_order": "Purchase Orders",
}

col1, col2 = st.columns(2)
categories = ["sales", "inventory", "supplier", "purchase_order"]

for idx, category in enumerate(categories):
    col = col1 if idx % 2 == 0 else col2
    info = file_status.get(category, {})
    icon = CATEGORY_ICONS.get(category, "📁")
    label = CATEGORY_LABELS.get(category, category)

    with col:
        with st.container(border=True):
            if info.get("status") == "active":
                st.subheader(f"{icon} {label}")
                st.success("✅ Uploaded")

                m1, m2 = st.columns(2)
                with m1:
                    st.metric("Rows", f"{info.get('row_count', 0):,}")
                with m2:
                    st.metric("Quality", f"{info.get('quality_score', 0):.1f}%")

                st.caption(f"📅 {info.get('upload_timestamp', 'Unknown')} by {info.get('uploaded_by', 'system')}")

                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("📤 Replace", key=f"replace_{category}"):
                        st.session_state["upload_category"] = category
                        st.switch_page("pages/2_📤_Upload_Files.py")
                with b2:
                    if st.button("👁️ Preview", key=f"preview_{category}"):
                        st.session_state["preview_category"] = category
                with b3:
                    if st.button("📜 History", key=f"history_{category}"):
                        st.session_state["history_category"] = category
                        st.switch_page("pages/3_📜_History.py")
            else:
                st.subheader(f"{icon} {label}")
                st.warning("⚠️ Not Uploaded")

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("📤 Upload", key=f"upload_{category}"):
                        st.session_state["upload_category"] = category
                        st.switch_page("pages/2_📤_Upload_Files.py")
                with b2:
                    if st.button("📥 Template", key=f"tpl_{category}"):
                        resp = api.get(f"/api/templates/download/{category}?format=csv")
                        if resp.status_code == 200:
                            st.download_button(
                                "⬇️ Download",
                                resp.content,
                                f"{category}_template.csv",
                                "text/csv",
                                key=f"dl_{category}",
                            )

# ─── Preview Section ──────────────────────────────────────────

if "preview_category" in st.session_state:
    cat = st.session_state["preview_category"]
    st.divider()
    st.subheader(f"👁️ Preview: {CATEGORY_LABELS.get(cat, cat)}")

    resp = api.get(f"/api/files/preview/{cat}?limit=100")
    if resp.status_code == 200:
        data = resp.json()
        df = pd.DataFrame(data.get("data", []))
        if len(df) > 0:
            st.dataframe(df, use_container_width=True)
            st.caption(f"Showing {len(df)} of {data.get('total_rows', 0):,} rows")
        else:
            st.info("No data available")
    else:
        st.error("Failed to load preview")

    if st.button("Close Preview"):
        del st.session_state["preview_category"]
        st.rerun()

# ─── Database Status ──────────────────────────────────────────

st.divider()
st.subheader("🗄️ Database Status")

s1, s2, s3 = st.columns(3)

with s1:
    uploaded_count = sum(1 for f in file_status.values() if isinstance(f, dict) and f.get("status") == "active")
    st.metric("Files Uploaded", f"{uploaded_count}/4")

with s2:
    total_rows = sum(f.get("row_count", 0) for f in file_status.values() if isinstance(f, dict))
    st.metric("Total Rows", f"{total_rows:,}")

with s3:
    avg_quality = 0
    active_files = [f for f in file_status.values() if isinstance(f, dict) and f.get("status") == "active"]
    if active_files:
        avg_quality = sum(f.get("quality_score", 0) for f in active_files) / len(active_files)
    st.metric("Avg Quality", f"{avg_quality:.1f}%")

# Refresh button
col_r1, col_r2 = st.columns([1, 4])
with col_r1:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()
with col_r2:
    if uploaded_count > 0:
        if st.button("🔗 Get MCP Config →"):
            st.switch_page("pages/4_🔗_MCP_Config.py")
