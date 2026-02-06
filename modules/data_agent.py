# modules/data_agent.py
from pathlib import Path
import pandas as pd
import json

DATA_DIR = Path("data")

SUPPORTED_EXTENSIONS = {".csv", ".json"}

def load_dataframe(path: Path):
    if path.suffix == ".csv":
        return pd.read_csv(path)
    if path.suffix == ".json":
        return pd.read_json(path)
    raise ValueError("Unsupported data format")

def find_data_files():
    return [
        f for f in DATA_DIR.glob("*")
        if f.suffix in SUPPORTED_EXTENSIONS
    ]

def summarize_dataframe(df: pd.DataFrame) -> str:
    lines = []
    lines.append(f"Rows: {len(df)}")
    lines.append(f"Columns: {len(df.columns)}")
    lines.append("Column summary:")

    for col in df.columns:
        lines.append(f"- {col}: {df[col].dtype}")

    return "\n".join(lines)

def handle_data_analysis(query: str) -> str:
    print("📊 DATA_AGENT CALLED")
    files = find_data_files()
    if not files:
        return "No data files found to analyze."

    # For Phase 1.2: analyze the first dataset found
    file = files[0]

    try:
        df = load_dataframe(file)
    except Exception as e:
        return f"Failed to load data file: {e}"

    query_l = query.lower()

    if "summary" in query_l or "overview" in query_l:
        return f"Data file: {file.name}\n" + summarize_dataframe(df)

    if "columns" in query_l:
        return f"Columns in {file.name}:\n" + ", ".join(df.columns)

    if "rows" in query_l or "count" in query_l:
        return f"{file.name} contains {len(df)} rows."

    if "missing" in query_l or "null" in query_l:
        missing = df.isnull().sum()
        return "Missing values per column:\n" + missing.to_string()

    # fallback
    return f"Loaded {file.name}. Ask for summary, columns, rows, or missing values."