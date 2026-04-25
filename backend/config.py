STORAGE_PATH="storage/experiments"
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eln.db")
STORAGE_PATH = os.getenv("STORAGE_PATH", "storage/experiments")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o")
