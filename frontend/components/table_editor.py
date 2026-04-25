import streamlit as st
import pandas as pd

def render_table_editor():
    st.subheader("📊 Table Section")
    csv_input = st.text_area("Paste CSV here:")
    if csv_input:
        try:
            df = pd.read_csv(pd.compat.StringIO(csv_input))
            st.dataframe(df)
            return df
        except:
            st.error("Invalid CSV format")
    return None