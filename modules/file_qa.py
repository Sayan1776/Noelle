import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
from core.llm import chat
from modules.local_file import handle_local_file

INDEX_PATH = Path("data/embeddings/index.faiss")
META_PATH = Path("data/embeddings/meta.pkl")

_model = None  # lazy-loaded


def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            local_files_only=True  # 🔑 OFFLINE MODE
        )
    return _model

def handle_file_qa(query: str) -> str:
    return handle_local_file(query)

