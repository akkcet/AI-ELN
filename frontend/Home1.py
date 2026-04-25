import streamlit as st
from streamlit.components.v1 import html, iframe
from pathlib import Path
st.set_page_config(layout="wide")
import base64
import requests
from datetime import datetime
from streamlit.components.v1 import html as st_html
from utils.config import BACKEND_URL, USERNAME


def load_image_base64(path):
    
    return base64.b64encode(Path(path).read_bytes()).decode("utf-8")


logo_b64 = load_image_base64("unilever.jpg")
#print(logo_b64)


@st.cache_data
def load(path):
    return Path(path).read_text(encoding="utf-8")


# -------------------------------------------------
# CRITICAL CSS FIXES (DO NOT REMOVE)
# -------------------------------------------------
st.markdown("""
<style>
/* Remove Streamlit UI */
#MainMenu, header, footer {
    visibility: hidden;
}

/* Remove top padding */


/* Disable Streamlit overlay blocking clicks */

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# TOP TOOLBAR (JS + HTML)
# -------------------------------------------------

# -------------------------------------------------
# SPACER SO CONTENT IS NOT HIDDEN
# -------------------------------------------------
#st.markdown("<div style='height:70px'></div>", unsafe_allow_html=True)

# -------------------------------------------------
# PAGE ROUTING
# -------------------------------------------------
page = st.query_params.get("page", "home")
#page = st.query_params.get("page", ["home"])[0]
print("Current page:", page)
search_query = st.query_params.get("q")
VIEW_MAP = {
    "home": "ui/home.html",
    "admin": "ui/admin.html",
    "profile": "ui/profile.html",
    "experiments": "ui/experiments.html",
}
# Helper for formatting the recent experiments list

def build_recent_experiment_rows(experiments):
    rows = []

    for exp in experiments:
        rows.append(f"""
        <div class="list-row">
            <div class="row-left">
                <div class="item-title">{exp["title"]}</div>
                <div class="item-meta">{exp["experiment_id"]}</div>
            </div>
            <div class="row-right">{exp["updated"]}</div>
        </div>
        """)

    return "\n".join(rows)

def normalize_recent_experiments():
    resp = requests.get(
        f"{BACKEND_URL}/experiments",
        params={"user": USERNAME},
        timeout=10,
        allow_redirects=True
    )

    if resp.status_code != 200:
        st.warning("Could not load recently updated experiments.")
        results = []
    else:
        results = resp.json() 
    experiments = []

    for exp in results[:3]:  # show only the latest 5
        
        experiments.append({
            "title": exp.get("title", "(Untitled)"),
            "experiment_id": exp.get("experiment_id", ""),
            "updated": exp.get("status", "")
        })

    return experiments
#Helper for search results formatting

def search_experiments(query):
    resp = requests.get(
        f"{BACKEND_URL}/experiments/",
        params={"q": query},
        timeout=5,
        allow_redirects=True
    )
    print(resp.json())
    if resp.status_code != 200:
        return []
    else:
        print(resp.json())
        return resp.json()
    #print(resp.json())


def format_date(ts):
    try:
        return datetime.fromisoformat(ts).strftime("%d %b %Y")
    except Exception:
        return ts    
def build_search_results_table(results):
    if not results:
        return "<div style='padding:12px;color:#777'>No results found</div>"

    
    rows = []

    for i, r in enumerate(results):
        rows.append(f"""
        <tr class="{'selected' if i == 0 else ''}">
          <td>{r.get("experiment_id", "")}</td>
          <td><a>{r.get("title", "")}</a></td>
          <td>{r.get("author", "")}</td>
          <td>{r.get("project", "")}</td>
          <td>{r.get("type", "")}</td>
          <td>{format_date(r.get("updated", ""))}</td>
        </tr>
        """)

    return "\n".join(rows)

# --- load content ---
hard_css = """
    <style>
    /* -------------------------------
       HARD STOP: Streamlit outer scroll
       ------------------------------- */

    html, body {
        height: 100%;
        margin: 0;
        overflow: hidden !important;
    }

    /* Streamlit root containers */
    .stApp,
    .stAppViewContainer,
    [data-testid="stAppViewContainer"] {
        height: 100%;
        overflow: hidden !important;
    }

    /* Main Streamlit content wrapper */
    .block-container {
        padding-top: 0 !important;
        max-width: 100vw !important; 
        
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin: 0 !important;
        height: 100%;
        overflow: hidden !important;
    }

    /* Prevent iframe from introducing scroll */
    iframe {
        display: block;
        border: none;
    }
    </style>
    """
exp_css = """
<style>
.stApp,
.stAppViewContainer,
[data-testid="stAppViewContainer"],
.block-container {
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100% !important;
}
iframe {
        display: block;
        border: none;
    }
.block-container {
        padding-top: 0 !important;
        max-width: 100vw !important; 
        
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin: 0 !important;
        height: 100%;
        overflow: hidden !important;
    }
</style>
"""

# Decide which view to render
if page == "search" and search_query:
    # 🔍 SEARCH VIEW
    st.markdown(hard_css, unsafe_allow_html=True)
    results = search_experiments(search_query)
    table_html = build_search_results_table(results)

    
    search_html = (
        load("ui/search.html")
        .replace("{{SEARCH_RESULTS_ROWS}}", table_html)
        .replace("{{RESULT_COUNT}}", str(len(results)))
    )

    content_html = search_html
    layout_html = load("ui/layout.html").replace("{{CONTENT}}", content_html)
    st_html(
    f"""
    <style>{load("ui/styles.css")}</style>
    {layout_html}
    <script>{load("ui/app.js")}</script>
    """,
    height=1400,
    scrolling=True,
    #key="main_layout"   # ✅ THIS IS THE KEY FIX
)

elif page == "new-experiment-template":
    st.markdown(hard_css, unsafe_allow_html=True)
    content_html = load("ui/template_select.html")
    layout_html = load("ui/layout_template.html").replace("{{CONTENT}}", content_html)
    st_html(
    f"""
    <style>{load("ui/styles.css")}</style>
    {layout_html}
    <script>{load("ui/app.js")}</script>
    """,
    height=1400,
    scrolling=True,
    #key="main_layout"   # ✅ THIS IS THE KEY FIX
)

elif page == "submission":
    st.markdown(exp_css, unsafe_allow_html=True)
    exp_id = st.query_params.get("experiment_id")
    print("Experiment ID for submission view:", exp_id)
    layout_html = load("ui/layout_submission.html") \
        .replace("{{EXPERIMENT_ID}}", exp_id)

    st_html(
        f"""
        <style>{load("ui/submission.css")}</style>
        {layout_html}
        <script>{load("ui/app.js")}</script>
        """,
        height=900,
     
    )

elif page == "experiment-editor":
    st.markdown(exp_css, unsafe_allow_html=True)
    exp_id = st.query_params.get("experiment_id")

    exp = requests.get(
        f"{BACKEND_URL}/experiments/{exp_id}"
    ).json()
    #print(exp["author"],exp["date_started"])
    #layout_html = "ui/layout_experiment.html"
    exp_id = st.query_params.get("experiment_id")
    content_html = load("ui/experiment_editor.html").replace(
        "{{EXPERIMENT_ID}}", exp_id).replace("{{AUTHOR}}", exp["author"]).replace("{{DATE_STARTED}}", exp["date_started"])


    layout_html = load("ui/layout_experiment.html").replace("{{CONTENT}}", content_html)
    st_html(
    f"""
    <style>{load("ui/experiment.css")}</style>
    {layout_html}
    <script>{load("ui/app.js")}</script>
    """,
    height=1200,
    scrolling=False,
    #key="main_layout"   # ✅ THIS IS THE KEY FIX
)
else:
    # 🏠 HOME VIEW
    st.markdown(hard_css, unsafe_allow_html=True)
    results = normalize_recent_experiments()
    recent_rows_html = build_recent_experiment_rows(results)

    home_html = load("ui/home.html")
    content_html = home_html.replace(
        "{{RECENT_EXPERIMENT_ROWS}}",
        recent_rows_html
    )
    layout_html = load("ui/layout.html").replace("{{CONTENT}}", content_html)
    st_html(
    f"""
    <style>{load("ui/styles.css")}</style>
    {layout_html}
    <script>{load("ui/app.js")}</script>
    """,
    height=1400,
    scrolling=True,
    #key="main_layout"   # ✅ THIS IS THE KEY FIX
)
#  Render ONE layout, ONE content
#print("RENDERING MAIN LAYOUT")
#layout_html = load("ui/layout.html").replace("{{CONTENT}}", content_html)









