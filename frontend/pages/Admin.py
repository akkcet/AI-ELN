import streamlit as st
import requests
from utils.config import BACKEND_URL


# -------------------------------------------------------
# ✅ PAGE TITLE
# -------------------------------------------------------
st.title("⚙️ Administration Panel")
st.caption("Manage Projects and Lookups used in the ELN system.")


# -------------------------------------------------------
# ✅ TABS: PROJECTS | LOOKUPS
# -------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Projects", "Lookups", "Requests"])


# =======================================================
# ✅ TAB 1 — PROJECT MANAGEMENT
# =======================================================
with tab1:
    st.header("Projects")

    # Fetch existing projects
    try:
        resp = requests.get(f"{BACKEND_URL}/admin/projects")
        projects = resp.json()
    except Exception:
        projects = []

    # LIST ALL PROJECTS
    for proj in projects:
        col1, col2, col3 = st.columns([6, 1, 1])

        col1.write(f"🔹 {proj['name']}")

        # ✅ EDIT PROJECT
        if col2.button("✏️", key=f"edit_proj_{proj['id']}"):
            st.session_state["edit_proj_id"] = proj["id"]
            st.session_state["edit_proj_name"] = proj["name"]

        # ✅ DELETE PROJECT
        if col3.button("🗑️", key=f"delete_proj_{proj['id']}"):
            requests.delete(f"{BACKEND_URL}/admin/projects/{proj['id']}")
            st.rerun()

    # --------------- EDIT PROJECT MODAL ---------------
    if "edit_proj_id" in st.session_state:
        st.subheader("Edit Project")
        new_name = st.text_input("Project Name", value=st.session_state["edit_proj_name"])

        if st.button("Save Changes"):
            requests.put(
                f"{BACKEND_URL}/admin/projects/{st.session_state['edit_proj_id']}",
                params={"name": new_name},
            )
            st.session_state.pop("edit_proj_id")
            st.session_state.pop("edit_proj_name")
            st.rerun()

        if st.button("Cancel Edit"):
            st.session_state.pop("edit_proj_id")
            st.session_state.pop("edit_proj_name")
            st.rerun()

    st.markdown("---")

    # --------------- ADD NEW PROJECT ---------------
    st.subheader("Add New Project")
    new_proj = st.text_input("Project Name", key="new_project")

    if st.button("Add Project"):
        if new_proj.strip():
            requests.post(
                f"{BACKEND_URL}/admin/projects",
                params={"name": new_proj},
            )
            #st.session_state["new_project"] = ""
            st.rerun()
        else:
            st.warning("Project name cannot be empty.")


# =======================================================
# ✅ TAB 2 — LOOKUPS MANAGEMENT
# =======================================================
with tab2:
    st.header("Lookups")

    # Fetch all lookups
    try:
        resp = requests.get(f"{BACKEND_URL}/admin/lookups")
        lookups = resp.json()
    except Exception:
        lookups = []

    # ------------------- LIST LOOKUPS -------------------
    for lu in lookups:
        st.subheader(f"📌 {lu['name']}")
        st.caption(lu["description"] or "No description.")

        # Fetch lookup values
        val_resp = requests.get(
            f"{BACKEND_URL}/admin/lookups/{lu['id']}/values"
        )
        values = val_resp.json() if val_resp.status_code == 200 else []

        # SHOW VALUES
        for val in values:
            col1, col2, col3 = st.columns([6, 1, 1])
            col1.write(f"- {val['value']}")

            # ✅ EDIT VALUE
            if col2.button("✏️", key=f"edit_val_{val['id']}"):
                st.session_state["edit_val_id"] = val["id"]
                st.session_state["edit_val_value"] = val["value"]
                st.session_state["edit_val_lookup"] = lu["id"]

            # ✅ DELETE VALUE
            if col3.button("🗑️", key=f"delete_val_{val['id']}"):
                requests.delete(
                    f"{BACKEND_URL}/admin/lookups/{lu['id']}/values/{val['id']}"
                )
                st.rerun()

        # ------------- EDIT VALUE MODAL ----------------
        if (
            "edit_val_id" in st.session_state
            and st.session_state.get("edit_val_lookup") == lu["id"]
        ):
            st.subheader("Edit Lookup Value")
            new_val = st.text_input(
                "Value", st.session_state["edit_val_value"], key="value_edit_box"
            )

            if st.button("Save Value"):
                requests.put(
                    f"{BACKEND_URL}/admin/lookups/{lu['id']}/values/{st.session_state['edit_val_id']}",
                    params={"value": new_val},
                )
                st.session_state.pop("edit_val_id")
                st.session_state.pop("edit_val_value")
                st.session_state.pop("edit_val_lookup")
                st.rerun()

            if st.button("Cancel Value Edit"):
                st.session_state.pop("edit_val_id")
                st.session_state.pop("edit_val_value")
                st.session_state.pop("edit_val_lookup")
                st.rerun()

        # ------------ ADD NEW VALUE ----------------
        new_value = st.text_input(
            f"Add value to '{lu['name']}'", key=f"add_val_{lu['id']}"
        )

        if st.button(f"Add to {lu['name']}", key=f"add_btn_val_{lu['id']}"):
            requests.post(
                f"{BACKEND_URL}/admin/lookups/{lu['id']}/values",
                params={"value": new_value},
            )
            st.rerun()

        # ------------ DELETE ENTIRE LOOKUP -------------
        if st.button(f"❌ Delete Lookup: {lu['name']}", key=f"delete_lookup_btn_{lu['id']}"):
            requests.delete(f"{BACKEND_URL}/admin/lookups/{lu['id']}")
            st.rerun()

        st.markdown("---")

    # ------------ CREATE NEW LOOKUP -------------
    st.subheader("Create New Lookup")

    lookup_name = st.text_input("Lookup Name", key="new_lookup_name")
    lookup_desc = st.text_area("Description", key="new_lookup_desc")

    if st.button("Create Lookup"):
        if lookup_name.strip():
            requests.post(
                f"{BACKEND_URL}/admin/lookups",
                params={"name": lookup_name, "description": lookup_desc},
            )
            #st.session_state["new_lookup_name"] = ""
            #st.session_state["new_lookup_desc"] = ""
            st.rerun()
        else:
            st.warning("Lookup name cannot be empty.")



# =====================================================
# ✅ REQUESTS TAB
# =====================================================
with tab3:
    st.header("📥 Admin Requests")

    resp = requests.get(f"{BACKEND_URL}/admin-requests/")

    try:
        data = resp.json()
    except Exception:
        st.error("Failed to parse server response")
        st.stop()

    # ✅ Normalize data shape
    if isinstance(data, dict):
        if "detail" in data:
            st.error(f"Backend error: {data['detail']}")
            st.stop()
        data = [data]  # single object → list

    if not isinstance(data, list):
        st.error("Unexpected response format from backend")
        st.stop()

    if not data:
        st.info("No admin requests available.")
        st.stop()

    for r in data:
        # ✅ Defensive access
        req_id = r.get("id", "N/A")
        req_type = r.get("request_type", "UNKNOWN")
        status = r.get("status", "UNKNOWN")

        with st.expander(f"Request #{req_id} — {req_type}"):
            st.json(r)

            if status == "NewRequest":
                col1, col2 = st.columns(2)

                if col1.button("✅ Approve", key=f"approve_{req_id}"):
                    requests.post(
                        f"{BACKEND_URL}/admin-requests/{req_id}/approve",
                        params={"user": "admin"},
                    )
                    st.rerun()

                if col2.button("❌ Reject", key=f"reject_{req_id}"):
                    requests.post(
                        f"{BACKEND_URL}/admin-requests/{req_id}/reject",
                        params={"user": "admin"},
                    )
                    st.rerun()
            else:
                st.success(f"Status: {status}")