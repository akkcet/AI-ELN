import streamlit as st
import requests
from utils.config import BACKEND_URL

def render_chemistry(smiles: str):
    if smiles:
        img_resp = requests.get(f"{BACKEND_URL}/chem/render?smiles={smiles}")
        if img_resp.status_code == 200:
            st.image(img_resp.content, caption="Chemical Structure")
        else:
            st.error("Invalid SMILES structure")