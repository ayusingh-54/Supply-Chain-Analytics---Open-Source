"""
📜 History - File Version History
"""
import streamlit as st
import pandas as pd
from utils.api_client import get_api_client

st.set_page_config(page_title="Version History", page_icon="📜", layout="wide")

api = get_api_client()

st.title("📜 Version History")
st.markdown("View and manage file versions")

# Category selection
if "history_category" in st.session_state:
    preselected = st.session_state.history_category
    del st.session_state["history_category"]
    categories = ["sales", "inventory", "supplier", "purchase_order"]
    default_idx = categories.index(preselected) if preselected in categories else 0
else:
    categories = ["sales", "inventory", "supplier", "purchase_order"]
    default_idx = 0

selected_category = st.selectbox(
    "Select file category:",
    categories,
    index=default_idx,
    format_func=lambda x: x.replace("_", " ").title(),
)


@st.cache_data(ttl=30)
def get_history(cat):
    resp = api.get(f"/api/files/history/{cat}")
    if resp.status_code == 200:
        return resp.json()
    return {"category": cat, "current": None, "versions": []}


history = get_history(selected_category)

# ─── Current Active Version ───────────────────────────────────

st.subheader("📌 Current Active Version")

current = history.get("current")
if current:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Filename", current.get("filename", "Unknown"))
    with c2:
        st.metric("Rows", f"{current.get('row_count', 0):,}")
    with c3:
        st.metric("Quality", f"{current.get('quality_score', 0):.1f}%")
    with c4:
        st.metric("Uploaded", str(current.get("upload_timestamp", ""))[:19])
else:
    st.info(f"No active {selected_category.replace('_', ' ')} file. Upload one from the Upload page.")

# ─── Previous Versions ────────────────────────────────────────

st.divider()
st.subheader("📚 Previous Versions")

versions = history.get("versions", [])
if versions:
    for idx, version in enumerate(versions):
        with st.expander(
            f"v{version.get('version_number', idx + 1)}: {version.get('filename', 'Unknown')} "
            f"— {str(version.get('upload_timestamp', ''))[:19]}"
        ):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Rows:** {version.get('row_count', 0):,}")
            with c2:
                st.write(f"**Quality:** {version.get('quality_score', 0):.1f}%")
            with c3:
                st.write(f"**Status:** {version.get('status', 'archived')}")
else:
    st.info("No previous versions available")

# Refresh
if st.button("🔄 Refresh History"):
    st.cache_data.clear()
    st.rerun()
