
import streamlit as st
import requests
from utils.config import BACKEND_URL, USERNAME

st.title("Create New Experiment")

title = st.text_input("Experiment Title")
project = st.text_input("Project")
category = st.text_input("Category")
notes = st.text_area("Experiment Notes")

if st.button("Save Experiment"):
    payload = {
        "title": title,
        "author": USERNAME,
        "project_id": 1,
        "category_id": 1,
        "notes": notes
    }
    resp = requests.post(f"{BACKEND_URL}/experiments", json=payload)
    if resp.status_code == 200:
        st.success("Experiment created successfully.")
    else:
        st.error("Error creating experiment.")
