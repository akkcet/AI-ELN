
import hashlib

def compute_hash(data: str):
    return hashlib.sha256(data.encode()).hexdigest()
