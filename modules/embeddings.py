import numpy as np
import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer

DATA_DIR = Path("data")
INDEX_PATH = Path("data/embeddings/index.faiss")
META_PATH = Path("data/embeddings/meta.pkl")

# Lazy-loaded embedding model
_model = None


def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            local_files_only=True
        )
    return _model


def build_index():
    texts = []
    sources = []

    for file in DATA_DIR.glob("*.txt"):
        content = file.read_text(encoding="utf-8")
        for chunk in content.split("\n"):
            if chunk.strip():
                texts.append(chunk)
                sources.append(file.name)

    if not texts:
        raise ValueError("No text found to embed.")

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=False
    ).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)   #type: ignore

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))

    with open(META_PATH, "wb") as f:
        pickle.dump({"texts": texts, "sources": sources}, f)

    print("Embeddings index built successfully.")