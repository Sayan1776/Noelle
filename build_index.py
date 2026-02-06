from pathlib import Path
import pickle
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import cast


DATA_DIR = Path("data")
EMBED_DIR = Path("data/embeddings")
EMBED_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = EMBED_DIR / "index.faiss"
META_PATH = EMBED_DIR / "meta.pkl"

model = SentenceTransformer("all-MiniLM-L6-v2")

texts = []
sources = []

for file in DATA_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8", errors="ignore")
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    for chunk in chunks:
        texts.append(chunk)
        sources.append(str(file))

embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)   #type: ignore

faiss.write_index(index, str(INDEX_PATH))

with open(META_PATH, "wb") as f:
    pickle.dump({"texts": texts, "sources": sources}, f)

print("✅ Index rebuilt successfully.")