# modules/local_file.py
from pathlib import Path
from modules.semantic_search import semantic_file_search


DATA_DIR = Path("data")
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".csv", ".json"}

def read_file(path: Path) -> str:
    if path.suffix not in ALLOWED_EXTENSIONS:
        return "Unsupported file type."

    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"Failed to read file: {e}"

def search_files(query: str):
    query = query.lower()
    matches = []

    for file in DATA_DIR.glob("*"):
        if not file.is_file():
            continue

        # 1️⃣ Filename match
        if query in file.name.lower():
            matches.append(str(file))
            continue

        # 2️⃣ Content match
        try:
            content = file.read_text(encoding="utf-8", errors="ignore").lower()
            if query in content:
                matches.append(str(file))
        except Exception:
            pass

    return matches

def handle_local_file(user_input: str) -> str:
    query = user_input.lower()

    # 1️⃣ Explicit filesystem search FIRST
    if any(k in query for k in ["find", "search", "locate"]):
        results = search_files(user_input)
        if results:
            return "Matching files:\n" + "\n".join(results[:10])
        # only fallback if nothing found
        return semantic_file_search(user_input)

    # 2️⃣ Explicit read / summarize
    if any(k in query for k in ["read", "summarize", "open"]):
        default = DATA_DIR / "notes.txt"
        if default.exists():
            return read_file(default)
        return "Requested file not found."

    # 3️⃣ Conceptual / explanatory questions
    if any(k in query for k in ["what", "why", "how", "explain", "about"]):
        return semantic_file_search(user_input)

    # 4️⃣ Final fallback
    return semantic_file_search(user_input)