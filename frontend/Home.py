
import streamlit as st
import requests
from utils.config import BACKEND_URL, USERNAME
import pandas as pd
from io import BytesIO

st.set_page_config(layout="wide")
st.title(f"Notebook of {USERNAME}")

# -----------------------------
# 📚 Knowledgebase Chatbot
# -----------------------------
# -----------------------------------------------
st.sidebar.header("💬 Knowledgebase Chatbot")

if "rag_chat" not in st.session_state:
    st.session_state["rag_chat"] = []

# show history
for msg in st.session_state["rag_chat"]:
    st.sidebar.write(f"**{msg['role']}:** {msg['content']}")

q = st.sidebar.text_input("Ask a question:", key="rag_input")

if st.sidebar.button("Ask AI", key="ask_ai_btn"):
    st.session_state["rag_chat"].append({"role": "You", "content": q})

    r = requests.post(f"{BACKEND_URL}/ai/chat", json={"question": q}, timeout=30)
    
    if r.headers.get("content-type", "").startswith("application/json"):
        data = r.json()
        answer = data.get("answer", "⚠️ No answer field returned.")
    else:
        # Backend error (HTML or text)
        answer = f"❌ Backend error:\n{r.text}"

    #answer = r.json().get("answer", "Error.Could not receive answer.")

    st.session_state["rag_chat"].append({"role": "AI", "content": answer})
    st.rerun()



query = st.text_input("Search in All Experiments", "")
search_clicked = st.button("🔍 Search")    

if search_clicked:
    if not query.strip():
        st.warning("Please enter an experiment ID or title.")
    else:
        st.subheader("🔍 Search Results")

        try:
            resp = requests.get(
                f"{BACKEND_URL}/experiments/",
                params={"q": query},
                timeout=5
            )

            if resp.status_code != 200:
                st.error("Backend returned an error.")
            else:
                results = resp.json()
                #print(results)
                #st.write("Raw results from backend:", results)
                if isinstance(results, list):
                    if len(results) == 0:
                        st.info("No experiments found.")
                    else:
                        df = pd.DataFrame(results)
                        # --- Header row (table-like) ---
                        header = st.columns([2, 4, 2])
                        header[0].markdown("**Experiment ID**")
                        header[1].markdown("**Title**")
                        header[2].markdown("**Status**")
                        st.divider()
                        
                        # --- Data rows ---
                        for _, row in df.iterrows():
                            col1, col2, col3 = st.columns([2, 4, 2])

                            # ✅ Clickable experiment_id (looks like a link)
                            
                            col1.markdown(
                                      f"[{row['experiment_id']}](ExperimentDetails?id={row['experiment_id']})"
                                    )


                            col2.write(row["title"])
                            col3.write(row["status"])

                           

                else:
                    st.error("Unexpected backend response format.")

        except requests.exceptions.RequestException as e:
            st.error(f"Backend not reachable: {e}")

st.markdown("---")


# Recently updated
st.subheader("Recently Updated Experiments")

try:
    resp = requests.get(
        f"{BACKEND_URL}/experiments",
        params={"user": USERNAME},
        allow_redirects=True,
        timeout=5
    )

    if resp.status_code != 200:
        st.warning("Could not load recently updated experiments.")
    else:
        results = resp.json()

        if not results:
            st.info("No recent experiments.")
        else:
            for exp in results[:5]:  # show only the latest 5
                st.markdown(
                    f"{exp['experiment_id']} — **{exp['status']}**"
                )

except Exception:
    st.warning("Backend not reachable.")


if st.button("Start New Experiment"):
    st.switch_page("pages/NewExperiment.py")

# --- AI EXPERIMENT CREATION PANE ---
with st.expander("🤖 Create Experiment using AI"):
    st.markdown("### AI‑Powered Experiment Generator")

    mode = st.radio(
        "Choose input mode:",
        ["Describe Topic", "Upload JSON File"],
        horizontal=True
    )

    ai_payload = {}

    # ✅ MODE 1: TOPIC DESCRIPTION
    if mode == "Describe Topic":
        topic = st.text_area(
            "Describe the experiment you want to create:",
            placeholder="Example: Produce a hair conditioner formula matching Nexxus ROT using Hercules chassis..."
        )

        if st.button("✨ Generate Experiment from Topic"):
            resp = requests.post(
                f"{BACKEND_URL}/ai/generate_experiment",
                json={"topic": topic}
            )
            if resp.status_code == 200:
                new_id = resp.json()["experiment_id"]
                st.success(f"Experiment created: {new_id}")
                
                st.switch_page(
                    "pages/ExperimentDetails.py",
                    query_params={"id": new_id}
                )


            else:
                st.error("AI generation failed.")


    # ✅ MODE 2: JSON UPLOAD
    elif mode == "Upload JSON File":
        uploaded_json = st.file_uploader("Upload JSON experiment file", type=["json"])

        if uploaded_json:
            json_data = uploaded_json.read().decode("utf-8")

            if st.button("📄 Create Experiment from JSON"):
                resp = requests.post(
                    f"{BACKEND_URL}/ai/generate_from_json",
                    json={"json_raw": json_data}
                )
                print(resp)
                if resp.status_code == 200:
                    new_id = resp.json()["experiment_id"]
                    st.success(f"Experiment created: {new_id}")
                    
                    st.query_params["id"] = new_id
                    st.switch_page("pages/ExperimentDetails.py", query_params={"id": new_id})
                    st.rerun()


                else:
                    st.error("JSON import failed.")

##-------------------
# AUDIT TRAIL
##-------------------
st.markdown("## 📝 Audit Trail Viewer")

# --------------------------
# FILTER BAR (User Input)
# --------------------------
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    user = st.text_input("User")

with col2:
    action = st.text_input("Action")

with col3:
    description = st.text_input("Description contains")

with col4:
    entity = st.text_input("Object Type")

with col5:
    entity_id = st.text_input("Object ID")

with col6:
    date_from = st.date_input("From", value=None)

col7, col8 = st.columns([1, 1])
with col7:
    date_to = st.date_input("To", value=None)

with col8:
    apply_filters = st.button("Apply Filters")
    clear_filters = st.button("Clear Filters")

# --------------------------
# CLEAR FILTERS
# --------------------------
if clear_filters:
    st.rerun()

# --------------------------
# BUILD FILTER PARAMS ONLY WHEN BUTTON PRESSED
# --------------------------
if apply_filters:
    date_from_str = date_from.strftime("%Y-%m-%d") if date_from else ""
    date_to_str = date_to.strftime("%Y-%m-%d") if date_to else ""

    params = {
        "user": user or "",
        "action": action or "",
        "entity": entity or "",
        "entity_id": entity_id or "",
        "date_from": date_from_str,
        "date_to": date_to_str,
    }

    resp = requests.get(f"{BACKEND_URL}/audit/filter", params=params)

else:
    # ✅ FIRST LOAD → return ALL audit logs
    resp = requests.get(f"{BACKEND_URL}/audit/filter")


# --------------------------
# PROCESS RESULTS
# --------------------------
if resp.status_code != 200:
    st.error("Failed to load audit logs")
    st.stop()

raw_logs = resp.json()

# local description filter
if description:
    raw_logs = [r for r in raw_logs if description.lower() in r["Description"].lower()]

df = pd.DataFrame(raw_logs)

if df.empty:
    st.info("No audit records found")
    st.stop()

# --------------------------
# PAGINATION
# --------------------------
ROWS_PER_PAGE = 10
total_rows = len(df)
total_pages = max(1, (total_rows - 1) // ROWS_PER_PAGE + 1)

page = st.number_input("Page", 1, total_pages, 1)

start = (page - 1) * ROWS_PER_PAGE
end = start + ROWS_PER_PAGE
df_page = df.iloc[start:end]

# --------------------------
# ✅ DISPLAY TABLE (ONLY ONCE!)
# --------------------------
st.dataframe(
    df_page,
    use_container_width=True,
    hide_index=True
)

# --------------------------
# EXPORT BUTTONS
# --------------------------
colA, colB = st.columns([1, 1])

# ✅ Export to Excel
with colA:
    output = BytesIO()
    df.to_excel(output, index=False)  # requires openpyxl
    st.download_button(
        label="📊 Export to Excel",
        data=output.getvalue(),
        file_name="audit_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ✅ Export to PDF
with colB:
    pdf_resp = requests.get(f"{BACKEND_URL}/audit/export/pdf", params=params if apply_filters else {})
    if pdf_resp.status_code == 200:
        st.download_button(
            label="📄 Export to PDF",
            data=pdf_resp.content,
            file_name="audit_export.pdf",
            mime="application/pdf"
        )
# Reminders
st.subheader("Reminder Lists")
with st.expander("Me to Lock"):
    st.write("Experiments pending lock…")

with st.expander("Me to Submit"):
    st.write("Experiments pending submission…")
