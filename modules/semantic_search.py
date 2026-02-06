# modules/semantic_search.py
import faiss
import pickle
from core.llm import chat
from modules.embeddings import INDEX_PATH, META_PATH, get_embedding_model

# NOTE:
# Anytime data/notes.txt changes,
# rebuild the FAISS index using build_index.py
# modules/semantic_search.py


def semantic_file_search(user_input: str) -> str:
    if not INDEX_PATH.exists():
        return "Embeddings not found. Run build_index() first."

    index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, "rb") as f:
        meta = pickle.load(f)

    model = get_embedding_model()
    query_vec = model.encode([user_input])
    _, idxs = index.search(query_vec, k=5)

    context = "\n".join(meta["texts"][i] for i in idxs[0])

    messages = [
        {
            "role": "system",
            "content": (
                "You answer questions using ONLY the provided context. "
                "Be concise and accurate."
            )
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion:\n{user_input}"
        }
    ]

    return chat(messages)