import streamlit as st
import pandas as pd

def render_spreadsheet():
    st.subheader("📈 Spreadsheet Section")
    df = st.data_editor(
        pd.DataFrame({"Column 1": [], "Column 2": []}),
        num_rows="dynamic"
    )
    return df