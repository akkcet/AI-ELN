
import streamlit as st
import requests
from utils.config import BACKEND_URL

st.title("Search Experiments")

query = st.text_input("Search keyword")
if st.button("Search"):
    try:
        resp = requests.get(f"{BACKEND_URL}/experiments/search?q={query}")
        results = resp.json()
        for r in results:
            st.markdown(f"**{r['experiment_id']}** — {r['title']}")
    except:
        st.error("Backend unreachable.")
