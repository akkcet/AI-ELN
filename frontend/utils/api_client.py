
import requests
from .config import BACKEND_URL

def api_get(path):
    return requests.get(f"{BACKEND_URL}{path}")

def api_post(path, payload):
    return requests.post(f"{BACKEND_URL}{path}", json=payload)
