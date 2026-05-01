import os

EMBED_MODEL = "BAAI/bge-large-en-v1.5"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 150
TOP_K = 6

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chroma_db")
JSON_DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "data")
