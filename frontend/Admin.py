
import streamlit as st
import requests
from utils.config import BACKEND_URL

st.title("Admin Panel")
st.subheader("Manage Dropdowns")

project = st.text_input("New Project")
if st.button("Add Project"):
    st.success("Project added (placeholder). Backend integration pending.")

category = st.text_input("New Category")
if st.button("Add Category"):
    st.success("Category added (placeholder). Backend integration pending.")
