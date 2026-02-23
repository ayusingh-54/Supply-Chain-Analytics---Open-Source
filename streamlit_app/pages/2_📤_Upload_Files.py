"""
📤 Upload Files - File upload and validation interface
"""
import streamlit as st
import pandas as pd
import time
from utils.api_client import get_api_client

st.set_page_config(page_title="Upload Files", page_icon="📤", layout="wide")

api = get_api_client()

st.title("📤 Upload Data Files")
st.markdown("Upload and validate your supply chain data files")

# ─── Initialize State ─────────────────────────────────────────

if "upload_stage" not in st.session_state:
    st.session_state.upload_stage = "select"

if "validation_results" not in st.session_state:
    st.session_state.validation_results = None


# ─── Helper: Reset Upload ─────────────────────────────────────

def reset_upload():
    st.session_state.upload_stage = "select"
    st.session_state.validation_results = None
    if "uploaded_file_data" in st.session_state:
        del st.session_state["uploaded_file_data"]


# ─── STEP 1: Select Category & Upload File ───────────────────

if st.session_state.upload_stage == "select":

    # Category selection
    st.subheader("Step 1: Select File Category")

    if "upload_category" in st.session_state:
        preselected = st.session_state.upload_category
        del st.session_state["upload_category"]
        categories = ["sales", "inventory", "supplier", "purchase_order"]
        default_idx = categories.index(preselected) if preselected in categories else 0
    else:
        categories = ["sales", "inventory", "supplier", "purchase_order"]
        default_idx = 0

    selected_category = st.selectbox(
        "Choose the type of file to upload:",
        categories,
        index=default_idx,
        format_func=lambda x: x.replace("_", " ").title(),
    )
    st.session_state.selected_category = selected_category

    # Show expected schema
    with st.expander("📋 Expected File Schema", expanded=True):
        resp = api.get(f"/api/files/schema/{selected_category}")
        if resp.status_code == 200:
            schema = resp.json()
            st.markdown("**Required Columns:**")
            st.code(", ".join(schema.get("required_columns", [])))
            optional = schema.get("optional_columns", [])
            if optional:
                st.markdown("**Optional Columns:**")
                st.code(", ".join(optional))
        else:
            from backend_schemas import SCHEMAS
            st.info("Connect to backend to see schema details")

    # Download template
    tpl_resp = api.get(f"/api/templates/download/{selected_category}?format=csv")
    if tpl_resp.status_code == 200:
        st.download_button(
            "📥 Download Template CSV",
            tpl_resp.content,
            f"{selected_category}_template.csv",
            "text/csv",
        )

    # File uploader
    st.subheader("Step 2: Upload File")

    uploaded_file = st.file_uploader(
        f"Choose {selected_category.replace('_', ' ')} file",
        type=["xlsx", "csv"],
        help="Upload Excel (.xlsx) or CSV (.csv) file",
    )

    if uploaded_file is not None:
        st.info(f"📎 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

        # Store file data
        st.session_state.uploaded_file_data = {
            "name": uploaded_file.name,
            "bytes": uploaded_file.getvalue(),
            "type": uploaded_file.type,
        }

        if st.button("▶️ Validate File", type="primary"):
            with st.spinner("Validating file..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"file_category": selected_category}

                resp = api.post("/api/files/validate", files=files, data=data)

                if resp.status_code == 200:
                    st.session_state.validation_results = resp.json()
                    st.session_state.upload_stage = "validate"
                    st.rerun()
                else:
                    err = resp.json()
                    st.error(f"Validation failed: {err.get('detail', err.get('error', 'Unknown'))}")


# ─── STEP 2: Review Validation Results ────────────────────────

elif st.session_state.upload_stage == "validate":
    st.subheader("Step 3: Validation Results")

    results = st.session_state.validation_results

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Rows", f"{results.get('total_rows', 0):,}")
    with c2:
        st.metric("Valid Rows", f"{results.get('valid_rows', 0):,}")
    with c3:
        st.metric("Rejected", f"{results.get('rejected_rows', 0):,}")
    with c4:
        score = results.get("quality_score", 0)
        color = "🟢" if score >= 90 else "🟡" if score >= 70 else "🔴"
        st.metric("Quality Score", f"{color} {score:.1f}%")

    # Schema status
    if results.get("schema_valid"):
        st.success("✅ Schema validation passed — all required columns present")
    else:
        st.error("❌ Schema validation failed")
        for col in results.get("missing_columns", []):
            st.error(f"  Missing: `{col}`")

    # Issues
    issues = results.get("issues", [])
    if issues:
        st.subheader("⚠️ Data Quality Issues")
        for issue in issues:
            severity = issue.get("severity", "warning")
            icon = "🔴" if severity == "critical" or severity == "error" else "🟡"
            resolved = "✅ Auto-resolved" if issue.get("auto_resolved") else "⚠️ Needs review"
            with st.expander(f"{icon} {issue.get('type', 'Issue')}: {issue.get('count', 0)} rows — {resolved}"):
                st.write(issue.get("message", ""))
    else:
        st.success("✅ No data quality issues found!")

    # Preview
    preview = results.get("preview_data", [])
    if preview:
        st.subheader("👁️ Data Preview")
        st.dataframe(pd.DataFrame(preview), use_container_width=True)
        st.caption("First 10 rows shown")

    # Action buttons
    st.divider()

    can_proceed = results.get("schema_valid", False)

    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Back to Upload"):
            reset_upload()
            st.rerun()
    with b2:
        if can_proceed:
            if st.button("✅ Proceed to Upload", type="primary"):
                st.session_state.upload_stage = "upload"
                st.rerun()
        else:
            st.error("❌ Fix schema issues before uploading")


# ─── STEP 3: Upload Configuration & Execute ───────────────────

elif st.session_state.upload_stage == "upload":
    st.subheader("Step 4: Upload Configuration")

    upload_mode = st.radio(
        "Upload Mode:",
        ["replace", "append"],
        format_func=lambda x: {
            "replace": "🔄 Replace — Delete existing data and load new",
            "append": "➕ Append — Add new data to existing",
        }[x],
    )

    st.divider()

    b1, b2 = st.columns([1, 3])
    with b1:
        if st.button("← Back"):
            st.session_state.upload_stage = "validate"
            st.rerun()

    with b2:
        if st.button("🚀 Upload & Process", type="primary", use_container_width=True):
            file_data = st.session_state.get("uploaded_file_data")
            if not file_data:
                st.error("File data lost. Please start over.")
            else:
                with st.spinner("Uploading and processing..."):
                    progress = st.progress(0)
                    status_text = st.empty()

                    status_text.text("📤 Uploading file...")
                    progress.progress(20)

                    files = {"file": (file_data["name"], file_data["bytes"], file_data["type"])}
                    data = {
                        "file_category": st.session_state.selected_category,
                        "upload_mode": upload_mode,
                        "uploaded_by": "streamlit_user",
                    }

                    status_text.text("⚙️ Processing...")
                    progress.progress(50)

                    resp = api.post("/api/files/upload", files=files, data=data)

                    progress.progress(80)

                    if resp.status_code == 200:
                        st.session_state.upload_result = resp.json()
                        progress.progress(100)
                        status_text.text("✅ Done!")
                        time.sleep(0.5)
                        st.session_state.upload_stage = "complete"
                        st.rerun()
                    else:
                        progress.progress(100)
                        err = resp.json()
                        st.error(f"Upload failed: {err.get('detail', err.get('message', 'Unknown error'))}")


# ─── STEP 4: Upload Complete ──────────────────────────────────

elif st.session_state.upload_stage == "complete":
    st.subheader("✅ Upload Complete!")
    st.balloons()

    result = st.session_state.get("upload_result", {})

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Rows Loaded", f"{result.get('row_count', 0):,}")
    with c2:
        st.metric("Quality Score", f"{result.get('quality_score', 0):.1f}%")
    with c3:
        st.metric("Category", result.get("file_category", "").replace("_", " ").title())

    st.success(result.get("message", "Upload completed successfully!"))

    # Issues summary
    issues = result.get("issues", [])
    if issues:
        with st.expander(f"ℹ️ {len(issues)} processing notes"):
            for issue in issues:
                st.write(f"• {issue.get('message', '')}")

    st.divider()

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 Go to Dashboard"):
            reset_upload()
            st.switch_page("pages/1_📊_Dashboard.py")
    with c2:
        if st.button("📤 Upload Another"):
            reset_upload()
            st.rerun()
    with c3:
        if st.button("🔗 Get MCP Config"):
            reset_upload()
            st.switch_page("pages/4_🔗_MCP_Config.py")
