
from rdkit import Chem
from rdkit.Chem import Draw

# Validate SMILES
def validate_smiles(smiles: str) -> bool:
    try:
        return Chem.MolFromSmiles(smiles) is not None
    except:
        return False

# Convert molecule to PNG

def smiles_to_image(smiles: str, out_path: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        img = Draw.MolToImage(mol)
        img.save(out_path)
        return out_path
    return None
