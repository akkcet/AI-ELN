import streamlit as st
st.set_page_config(page_title="ExperimentDetails", layout="wide")
import requests
from utils.config import BACKEND_URL
import urllib.parse
from rdkit import Chem
from rdkit.Chem import rdChemReactions, AllChem
from rdkit.Chem import Draw
import base64
from io import BytesIO
import pubchempy as pcp
import uuid
import json

def name_to_smiles(name: str):
    name = name.strip()

    # 1. Try OPSIN
    try:
        url = f"https://opsin.ch.cam.ac.uk/opsin/{name}.json"
        print(url)
        r = requests.get(url, timeout=5)
        print("r value:  ",r)
        if r.status_code == 200:
            print("got data from opsin")
            #data = r.json()
            if "smiles" in data:
                print(data["smiles"])
                return data["smiles"]
    except:
        pass

    # 2. Try RDKit directly
    try:
        mol = Chem.MolFromSmiles(name)
        if mol:
            return Chem.MolToSmiles(mol)
    except:
        pass

    # 3. No match
    return None


def render_reaction_image(smiles_rxn: str):
    try:
        #rxn = rdChemReactions.ReactionFromSmarts(smiles_rxn, useSmiles=True)
       # print("smile value:   ",smiles_rxn)
        rxn = AllChem.ReactionFromSmarts(smiles_rxn)
        img = Draw.ReactionToImage(rxn, subImgSize=(100, 100))

        buf = BytesIO()
        img.save(buf, format="PNG")
        encoded = base64.b64encode(buf.getvalue()).decode()
        return f'<img src="data:image/png;base64,{encoded}" />'
    except Exception as e:
        return f"<p style='color:red;'>Unable to render reaction: </p>"

def convert_text_reaction_to_smiles(text_rxn: str):
    """
    Converts arbitrary human-readable reaction:
        benzene + bromine -> bromobenzene + hydrogen bromide
    into SMILES:
        c1ccccc1.BrBr>>c1ccccc1Br.[H]Br
    """

    if "->" not in text_rxn:
        return text_rxn

    left, right = text_rxn.split("->")
    left_parts = [p.strip() for p in left.split("+")]
    right_parts = [p.strip() for p in right.split("+")]
    #print("right parts: ",right_parts)
    def convert_list(parts):
        smiles_list = []
        for item in parts:
            #print("items: ",item)
            compound = pcp.get_compounds(item, 'name')[0]
            #smi = name_to_smiles(item)
            smi = compound.smiles
            smi_mw = compound.molecular_weight
            smi_f = compound.molecular_formula
            #print("smi value:", smi)
            compound_dict = {}
            if smi:
                smiles_list.append(smi)
            else:
                smiles_list.append(item)  # fallback: leave as-is
        return ".".join(smiles_list)

    left_smiles = convert_list(left_parts)
    right_smiles = convert_list(right_parts)
    #print(left_smiles)
    return f"{left_smiles}>>{right_smiles}"

def parse_reaction_str(rxn: str):
    """
    Accepts reaction string in:
    - SMILES form: A.B>>C
    - Text form: A + B -> C
    Returns lists of reactants and products.
    """
    if ">>" in rxn:
        parts = rxn.split(">>")
        left = parts[0].split(".")
        right = parts[1].split(".")
        return [s.strip() for s in left], [s.strip() for s in right]

    if "->" in rxn:
        parts = rxn.split("->")
        left = parts[0].split("+")
        right = parts[1].split("+")
        return [s.strip() for s in left], [s.strip() for s in right]

    return [], []

#st.write("PAGE NAME:", __file__)
#st.set_page_config(page_title="ExperimentDetails")
#FIX: Helper to reset file_uploader widget to prevent re-upload
# ----------------------------------------------------------------
def reset_uploader(key: str):
    if key in st.session_state:
        del st.session_state[key]

#SIGNATURE
def signature_box(label: str):
    st.markdown("**Electronic Signature Required**")
    pwd = st.text_input(
        "Confirm your password",
        type="password",
        key=f"pwd_{label}"
    )
    return pwd

# =========================================================
# ✅ Robust query‑parameter handling (Streamlit safe)
# =========================================================

exp_param = st.query_params.get("id")
st.write(exp_param)
if isinstance(exp_param, list):
    exp_id = exp_param[0]
else:
    exp_id = exp_param

if not exp_id:
    st.error("No experiment selected.")
    st.stop()


# =========================================================
# ✅ Fetch experiment details from backend
# =========================================================
resp = requests.get(f"{BACKEND_URL}/experiments/{exp_id}")

if resp.status_code != 200:
    st.error("Experiment not found.")
    st.stop()

data = resp.json()

status = data["status"]
editable = status in ["NEW", "REJECTED"]

# =========================================================
# ✅ TOP HEADER + WORKFLOW BANNER
# =========================================================
header_left, header_right = st.columns([4, 2])

with header_left:
    st.title(data["title"])
    st.write(f"**Experiment ID:** {data['experiment_id']}")
    st.write(f"**Author:** {data['author']}")
    st.markdown(f"**Status:** `{status}`")

with header_right:
    st.markdown(
        """
        <div style="
            border:1px solid #e5e7eb;
            border-radius:8px;
            padding:10px;
            background-color:#f9fafb;
        ">
        
        """,
        unsafe_allow_html=True,
    )

    
    if status == "NEW" or status == "REJECTED":
        pwd = signature_box("submit")

        if st.button("📤 Submit for Review", use_container_width=True):
            r = requests.post(
                f"{BACKEND_URL}/experiments/{exp_id}/submit",
                params={"password": pwd}
            )
            if r.status_code == 200:
                st.success("Submitted with electronic signature")
                st.rerun()
            else:
                st.error(r.json().get("detail"))


    elif status == "SUBMITTED":
        pwd = signature_box("approve")
        if st.button("✅ Approve", use_container_width=True):
            r = requests.post(f"{BACKEND_URL}/experiments/{exp_id}/approve",params={"password": pwd})
            if r.status_code == 200:
                st.success("Approved with electronic signature")
                st.rerun()
            else:
                st.error(r.json().get("detail", "Approve failed"))

        reject_reason = st.text_input("Rejection reason", key="reject_reason")

        if st.button("❌ Reject", use_container_width=True):
            r = requests.post(
                f"{BACKEND_URL}/experiments/{exp_id}/reject",
                params={"reason": reject_reason},
            )
            if r.status_code == 200:
                st.warning("Experiment rejected")
                st.rerun()
            else:
                st.error(r.json().get("detail", "Reject failed"))

    elif status == "COMPLETED":
        st.info("✔ Experiment Completed")

    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# =========================================================
# ✅ PAGE LAYOUT: LEFT = SECTION PALETTE, RIGHT = DOCUMENT
# =========================================================
palette_col, content_col = st.columns([1.2, 4])
summary_col = st.sidebar
sections = data.get("sections", [])
with summary_col:
    
    st.markdown("### 📄 AI Summarization")
    if st.button("Summarize Experiment"):
        full_text = ""
        
        for sec in sections:
            if isinstance(sec.get("content"), str):
                full_text +=  sec["content"] + "\n\n"
                #print(full_text)
                #full_text += sec["type"] + ":\n" + sec["content"] + "\n\n"
        if full_text.strip():
            with st.spinner("Generating summary...",):
                print(16*"=")
                print(full_text)
                r = requests.post(
                    f"{BACKEND_URL}/ai/summarize_experiment",
                    json={"text": full_text},
                )

                if r.status_code == 200:
                    st.success("Summary generated")
                    #st.write(r.json().get("summary", ""))
                    # ✅ Create a new section with AI summary
                    new_section = {
                            "id": str(uuid.uuid4()),
                            "type": "AI Experiment Summary",
                            "content": r.json().get("summary", ""),
                            "files": []
                        }
                    sections.append(new_section)
                    
                    save_resp = requests.post(
                            f"{BACKEND_URL}/experiments/{exp_id}/update",
                            json={"sections": sections},
                        )
                    
                    if save_resp.status_code == 200:
                            st.success("AI Summary inserted into experiment!")
                            st.rerun()
                    else:
                        st.error("Summary was generated but failed to insert summary section.")

                else:
                    st.error("Could not summarize experiment")
    st.markdown("---")
    section_titles = [sec["type"] for sec in sections]
    selected_title = st.selectbox("Choose a section", section_titles, key="select_section")
    if st.button("Summarize selected section"):
        full_text = ""
        target = next((s for s in sections if s["type"] == selected_title), None)
        if target and isinstance(target.get("content"), str):
            #print(8*"+")
            #print(target["content"])
            with st.spinner("Generating section summary..."):
                        r = requests.post(
                            f"{BACKEND_URL}/ai/summarize_experiment",
                            json={"text": target["content"]},
                        )
                    
            if r.status_code == 200:
                summary_text = r.json().get("summary", {})
                #print(20*"p")
                discussion_ = json.loads(summary_text)
                
                st.write(discussion_)
            else:
                st.error("Could not summarize section")
        else:
            st.warning("This section has no text to summarize.")

        #####################################
    st.markdown("---")   
    
    if st.button("Generate Review Comment"):
        full_text = ""
        for sec in sections:
            if isinstance(sec.get("content"), str):
                full_text += f"{sec['type']}:\n{sec['content']}\n\n"

        if full_text.strip():
            with st.spinner("Generating review comment..."):
                r = requests.post(
                    f"{BACKEND_URL}/ai/review_comment",
                    json={"text": full_text},
                )
            print(20*"**")
            if r.status_code == 200:
                review_text = r.json().get("review", "")
                print(review_text)
                st.write(review_text)
    st.markdown("---")   
# -------------------------
# ✅ LEFT PANE — Section Palette
# -------------------------
with palette_col:
    st.markdown("## Sections")
    
    try:
        lookups_resp = requests.get(f"{BACKEND_URL}/admin/lookups").json()
        LOOKUP_SECTION_TYPES = [f"Lookup: {lu['name']}" for lu in lookups_resp]
    except:
        LOOKUP_SECTION_TYPES = []

    AVAILABLE_SECTIONS = [
        "Objectives",
        "Method",
        "Materials",
        "Chemical Reaction",
        "Body Text",
        "Image",
        "Excel Workbook",
        "PDF Document",
        "File Attachment",
        "Project",
    ] + LOOKUP_SECTION_TYPES

    if not editable:
        st.info("Experiment is locked")
    else:
        for section in AVAILABLE_SECTIONS:
            if st.button(f"+ {section}", key=f"add_{section}", use_container_width=True):
                r = requests.post(
                    f"{BACKEND_URL}/experiments/{exp_id}/sections",
                    params={"section_type": section},
                )
                if r.status_code == 200:
                    st.rerun()
                else:
                    st.error("Failed to add section")

# -------------------------
# ✅ RIGHT PANE — Experiment Document
# -------------------------
with content_col:
    st.markdown("## Experiment Document")

    sections = data.get("sections", [])

    if not sections:
        st.info("No sections added yet. Use the panel on the left to insert sections.")

    for idx, sec in enumerate(sections):
        
        
# ---------- CUSTOM INLINE HEADER ----------
        
        
        
        # Custom toggle script for collapsible box
    
        #st.markdown(toggle_code, unsafe_allow_html=True)

        head_left, head_right = st.columns([8.5, 1.5])

        with head_left:
            st.markdown(
                f"""
                <div style="
                    font-size: 20px; 
                    font-weight: 600; 
                    padding: 6px 0;">
                    {sec['type']}
                </div>
                """,
                unsafe_allow_html=True
            )

        with head_right:
            if editable:
                b1, b2, b3 = st.columns([1,1,1])

                with b1:
                    if st.button("▲", key=f"up_{sec['id']}"):
                        requests.post(
                            f"{BACKEND_URL}/experiments/{exp_id}/sections/{sec['id']}/move",
                            params={"direction": "up"},
                        )
                        st.rerun()

                with b2:
                    if st.button("▼", key=f"down_{sec['id']}"):
                        requests.post(
                            f"{BACKEND_URL}/experiments/{exp_id}/sections/{sec['id']}/move",
                            params={"direction": "down"},
                        )
                        st.rerun()

                with b3:
                    if st.button("✕", key=f"del_{sec['id']}"):
                        requests.delete(
                            f"{BACKEND_URL}/experiments/{exp_id}/sections/{sec['id']}"
                        )
                        st.rerun()



        with st.expander("", expanded=True):
            # -----------------------------
            # ✅ Section content
            # -----------------------------
            if sec["type"] not in ["File Attachment", "Project","Chemical Reaction"]\
            and not sec["type"].startswith("Lookup:"):
                if editable:
                    sec["content"] = st.text_area(
                        sec["type"],
                        value=sec.get("content", ""),
                        key=sec["id"],
                        height=180,
                    )
                else:
                    st.write(sec.get("content") or "_No content_")

            
            # ✅ FILE ATTACHMENT SECTION
            if sec["type"] == "File Attachment":

                # Upload UI
                uploader_key = f"uploader_{sec['id']}"
                st.markdown("### Upload File")
                uploaded = st.file_uploader(
                    "Choose a file",
                    key=uploader_key,
                    accept_multiple_files=False
                )

                # Upload logic
                if uploaded and editable:
                    files = {"file": uploaded}
                    r = requests.post(
                        f"{BACKEND_URL}/experiments/{exp_id}/upload",
                        params={"section_id": sec["id"]},
                        files=files
                    )
                    if r.status_code == 200:
                        st.success("File uploaded successfully")
                        reset_uploader(uploader_key)
                        st.rerun()
                    else:
                        st.error("Failed to upload file")

                # ✅ SHOW ATTACHED FILES (ONLY HERE)
                if "files" in sec and sec["files"]:
                    st.markdown("### Attached Files")

                    for f in sec["files"]:
                        file_name = f["file_name"]
                        encoded_name = urllib.parse.quote(file_name)
                        file_url = f"{BACKEND_URL}/uploads/{exp_id}/{encoded_name}"

                        st.markdown(
                            f'<a href="{file_url}" download>'
                            f'📎 {file_name}'
                            '</a>',
                            unsafe_allow_html=True
                        )

            
            # ✅ PROJECT SECTION (NEW)
            
            elif sec["type"] == "Project":
                
                try:
                    project_resp = requests.get(f"{BACKEND_URL}/admin/projects")
                    project_data = project_resp.json()
                    PROJECT_OPTIONS = [p["name"] for p in project_data]
                except Exception:
                    PROJECT_OPTIONS = ["Hair Care",
                    "Skin Care",
                    "Deodorants",
                    "Home Care",
                    "Internal R&D",
                    "Other"]

              

                state_key = f"project_value_{sec['id']}"

                # Initialize session state only once
                if state_key not in st.session_state:
                    st.session_state[state_key] = sec.get("content", "")

                # Render dropdown bound to session state (NOT backend section)
                selected_project = st.selectbox(
                    "Choose a Project",
                    PROJECT_OPTIONS,
                    index=PROJECT_OPTIONS.index(st.session_state[state_key])
                        if st.session_state[state_key] in PROJECT_OPTIONS else 0,
                    key=state_key
                )

                # Do NOT update backend data until SAVE is pressed
                if editable:
                    sec["content"] = st.session_state[state_key]
                else:
                    st.write(f"**Selected Project:** {sec['content'] or '_Not specified_'}")

            # LOOKUP SECTION
            elif sec["type"].startswith("Lookup:"):
                lookup_name = sec["type"].replace("Lookup:", "").strip()

                # ----------- Load all lookups from backend -----------
                try:
                    all_lookups = requests.get(f"{BACKEND_URL}/admin/lookups").json()
                except:
                    all_lookups = []

                # Find lookup by name
                #lookup = next((l for l in all_lookups if l["name"] == lookup_name), None)
                
                lookup_name = sec["type"].replace("Lookup:", "").strip()

                lookup = next((l for l in all_lookups if l["name"] == lookup_name), None)

                if not lookup:
                    st.error(f"Lookup '{lookup_name}' not found in Admin panel.")
                    continue

                # ----------- Load values for this lookup -----------
                try:
                    values_resp = requests.get(
                        f"{BACKEND_URL}/admin/lookups/{lookup['id']}/values"
                    ).json()

                    LOOKUP_OPTIONS = [v["value"] for v in values_resp]
                except:
                    LOOKUP_OPTIONS = []

                # ----------- Session state key -----------
                state_key = f"lookup_value_{sec['id']}"

                if state_key not in st.session_state:
                    st.session_state[state_key] = sec.get("content", "")

                # ----------- Dropdown UI -----------
                if editable:
                    selected_value = st.selectbox(
                        f"Choose {lookup_name}",
                        LOOKUP_OPTIONS,
                        index=LOOKUP_OPTIONS.index(st.session_state[state_key])
                            if st.session_state[state_key] in LOOKUP_OPTIONS 
                            else 0,
                        key=state_key,
                    )

                    # Do NOT save to backend now (only on Save Experiment)
                    sec["content"] = st.session_state[state_key]

                else:
                    st.write(f"**Selected {lookup_name}:** {sec['content'] or '_Not specified_'}")
         
            elif sec["type"] == "Chemical Reaction":

                st.markdown("### Reaction Scheme (Auto Parsed & Drawn)")

                
                
                # ✅ Session-state key
                state_key = f"rxn_content_{sec['id']}"

                # ✅ Initialize once from stored experiment data
                if state_key not in st.session_state:
                    st.session_state[state_key] = sec.get("content", "")

                # ✅ Bind the text area ONLY to session_state (do NOT assign sec[...] here)
                reaction_input = st.text_area(
                    "Enter reaction (e.g., 'A + B -> C' or SMILES 'A.B>>C')",
                    value=st.session_state[state_key],
                    key=state_key,
                    height=70,
                )

                # ✅ In read-only mode, just display it
                #if not editable:
                 #   st.write(sec.get("content") or "_No reaction scheme_")


                smiles_rxn = convert_text_reaction_to_smiles(reaction_input)
                print("smiles_rxn value: ",smiles_rxn)
                image_html = render_reaction_image(smiles_rxn)
                st.markdown(image_html, unsafe_allow_html=True)
                
                
                # Draw reaction image
               # if sec.get("content"):
                   
                st.markdown("---")
                st.markdown("### Stoichiometric Table (Auto-Filled)")
                reactants, products = parse_reaction_str(st.session_state[state_key])
                print(reactants, products)
                # Build initial table if empty
                if "stoichiometry" not in sec or not sec["stoichiometry"]:
                    sec["stoichiometry"] = []
                    for name in reactants:
                        compound = pcp.get_compounds(name, 'name')[0]
                        mol_wt = compound.molecular_weight
                        mol_fr = compound.molecular_formula
                        sec["stoichiometry"].append({
                            "name": name,
                            "mw": mol_wt,
                            "formula": mol_fr,
                            "mass": 0.0,
                            "moles": 0.0,
                            "role": "reactant"
                        })
                    for name in products:
                        compound = pcp.get_compounds(name, 'name')[0]
                        mol_wt = compound.molecular_weight
                        mol_fr = compound.molecular_formula
                        sec["stoichiometry"].append({
                            "name": name,
                            "mw": mol_wt,
                            "formula": mol_fr,
                            "mass": 0.0,
                            "moles": 0.0,
                            "role": "product"
                        })

                table = sec["stoichiometry"]

                # Editable table rows
                updated = []
                for i, row in enumerate(table):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])

                    name = c1.text_input("Species", value=row["name"], key=f"x_name_{sec['id']}_{i}")
                    mw = c2.number_input("MW", value=row["mw"], key=f"x_mw_{sec['id']}_{i}")
                    formula = c3.text_input("formula", value=row["formula"], key=f"x_sto_{sec['id']}_{i}")
                    mass = c4.number_input("Mass (g)", value=row["mass"], key=f"x_mass_{sec['id']}_{i}")
                    moles = mass / mw if mw > 0 else 0

                    updated.append({
                        "name": name,
                        "mw": mw,
                        "formula": formula,
                        "mass": mass,
                        "moles": moles,
                        "role": row["role"],
                    })

                sec["stoichiometry"] = updated

                # Limiting reagent calculation
                #reactant_rows = [r for r in updated if r["role"] == "reactant" and r["stoich"] > 0]
                #ratios = [(r["moles"] / r["stoich"]) for r in reactant_rows]
                #limiting_index = ratios.index(min(ratios)) if ratios else None

                #st.markdown("### Results")
                #for idx_r, r in enumerate(reactant_rows):
                 #   is_lim = " ✅ Limiting Reagent" if idx_r == limiting_index else ""
                  #  st.write(f"- {r['name']}: {r['moles']:.4f} mol {is_lim}")
             
            
    ##-------------------------------
    # SAVE BUTTON 
    # session so that it doesnt load the page on every operation
    ##------------------------------
    if editable:
        
        
        for sec in sections:
                rxn_k = f"rxn_value_{sec['id']}"
                proj_k = f"project_value_{sec['id']}"
                lookup_k = f"lookup_value_{sec['id']}"
                if rxn_k in st.session_state:
                    sec["content"] = st.session_state[rxn_k]

                if proj_k in st.session_state:
                    sec["content"] = st.session_state[proj_k]
                
                if lookup_k in st.session_state:
                            sec["content"] = st.session_state[lookup_k]                    



        if st.button("💾 Save Experiment", use_container_width=True):
            r = requests.post(
                f"{BACKEND_URL}/experiments/{exp_id}/update",
                json={"sections": sections},
            )
            if r.status_code == 200:
                st.success("Experiment saved")
                st.rerun()
            else:
                st.error("Failed to save experiment")
