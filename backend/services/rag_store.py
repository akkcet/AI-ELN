import pickle
import numpy as np
import faiss
import os
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()


# ✅ Folder where this file (rag_store.py) exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Go one level up to backend/
BACKEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))


INDEX_FILE = os.path.join(BACKEND_DIR, "vectorstore.faiss")
STORE_FILE = os.path.join(BACKEND_DIR, "vectorstore.pkl")


print("Current working directory:", os.getcwd())
print("Looking for file:", os.path.abspath(INDEX_FILE))

# ✅ Load FAISS index + text chunks at startup
faiss_index = faiss.read_index(INDEX_FILE)
chunks = pickle.load(open(STORE_FILE, "rb"))

# ✅ Azure embedding client
emb = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBED_MODEL"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

async def rag_search(query: str, top_k: int = 3):
    q_vec = await emb.aembed_query(query)
    q_np = np.array(q_vec).astype("float32").reshape(1, -1)

    distances, indices = faiss_index.search(q_np, top_k)

    return [chunks[i] for i in indices[0] if i != -1]