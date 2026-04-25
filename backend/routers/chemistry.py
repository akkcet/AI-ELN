from fastapi import APIRouter, HTTPException
import pubchempy as pcp

router = APIRouter()

@router.post("/chemistry/search")
def search_chemical(payload: dict):
    query = payload.get("query", "").strip()

    if not query:
        return []

    try:
        # ✅ Search PubChem by name
        compounds = pcp.get_compounds(query, "name")

        if not compounds:
            return []

        #results = []
        compound = compounds[0] # take the first result which is the best
        
        cid = compound.cid
        smiles = compound.canonical_smiles
        formula = compound.molecular_formula
        mol_weight = compound.molecular_weight
        
        structure_image_url = (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG")
        

        # Limit results to avoid UI overload
        
        return [{
                    "name": compound.iupac_name or query,
                    "smiles": smiles,
                    "formula": formula,
                    "molecular_weight": mol_weight,
                    "pubchem_cid": cid,
                    "structure_image": structure_image_url
                }]


    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PubChem lookup failed: {str(e)}"
        )