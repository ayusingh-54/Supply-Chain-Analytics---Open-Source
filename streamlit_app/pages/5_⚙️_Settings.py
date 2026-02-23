"""
⚙️ Settings - Application configuration
"""
import streamlit as st
from utils.api_client import get_api_client

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

api = get_api_client()

st.title("⚙️ Settings")

# ─── Connection Status ────────────────────────────────────────

st.subheader("📡 Connection Status")

resp = api.get("/health")
if resp.status_code == 200:
    health = resp.json()
    c1, c2 = st.columns(2)
    with c1:
        st.success(f"✅ API Server: {health.get('status')}")
    with c2:
        st.success(f"✅ Database: {health.get('database')}")
else:
    st.error("❌ API Server not responding")

# ─── Quick Actions ────────────────────────────────────────────

st.divider()
st.subheader("🔧 Quick Actions")

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("🔄 Sync to FalkorDB"):
        with st.spinner("Syncing..."):
            r = api.post("/api/database/refresh")
            if r.status_code == 200:
                st.success(r.json().get("message", "Done"))
            else:
                st.warning("Sync returned a non-200 status")

with c2:
    if st.button("📊 View KPIs"):
        r = api.get("/api/database/kpis")
        if r.status_code == 200:
            st.json(r.json())
        else:
            st.info("No KPI data available yet")

with c3:
    if st.button("🔗 MCP Config"):
        st.switch_page("pages/4_🔗_MCP_Config.py")

# ─── Setup Commands ───────────────────────────────────────────

st.divider()
st.subheader("🖥️ Setup Commands")

st.markdown("**Start Backend:**")
st.code("cd backend && uvicorn main:app --reload --port 8000", language="bash")

st.markdown("**Start Streamlit:**")
st.code("cd streamlit_app && streamlit run app.py", language="bash")

st.markdown("**Start MCP Server (standalone):**")
st.code("cd mcp_server && python server.py", language="bash")

st.markdown("**Start FalkorDB (Docker):**")
st.code("docker run -d -p 6379:6379 falkordb/falkordb:latest", language="bash")

st.markdown("**Run with Docker Compose:**")
st.code("docker-compose up --build", language="bash")
