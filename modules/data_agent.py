# modules/data_agent.py
from pathlib import Path
import pandas as pd
import json

DATA_DIR = Path("data")

SUPPORTED_EXTENSIONS = {".csv"}

EXCLUDED_FILES = {
    "memory.json",
    "sessions.json"
}

def load_dataframe(path: Path):
    if path.suffix == ".csv":
        return pd.read_csv(path)
    if path.suffix == ".json":
        return pd.read_json(path)
    raise ValueError("Unsupported data format")

def find_data_files():
    files = []
    for f in DATA_DIR.glob("*"):
        if f.suffix not in SUPPORTED_EXTENSIONS:
            continue
        if f.name in EXCLUDED_FILES:
            continue
        files.append(f)
    return files


def summarize_dataframe(df: pd.DataFrame) -> str:
    lines = []
    lines.append(f"Rows: {len(df)}")
    lines.append(f"Columns: {len(df.columns)}")
    lines.append("Column summary:")

    for col in df.columns:
        lines.append(f"- {col}: {df[col].dtype}")

    return "\n".join(lines)

def handle_data_analysis(query: str) -> str:

    files = find_data_files()
    if not files:
        return "ERROR: No data files found."

    query_l = query.lower()

    # dataset selection
    selected_file = None
    for f in files:
        if f.name.lower() in query_l:
            selected_file = f
            break

    if selected_file is None:
        if len(files) == 1:
            selected_file = files[0]
        else:
            return (
                "ERROR: Multiple tabular datasets found. Specify one:\n"
                + "\n".join(f"- {f.name}" for f in files)
            )

    # load dataset
    try:
        df = load_dataframe(selected_file)
    except Exception as e:
        return f"ERROR: Failed to load dataset {selected_file.name}: {e}"

    # HARD FACTS (always computed)
    rows = len(df)
    columns = list(df.columns)
    missing = df.isnull().sum().to_dict()

    facts = [
        f"DATASET: {selected_file.name}",
        f"ROWS: {rows}",
        f"COLUMNS: {', '.join(columns)}",
    ]

    # Only include columns that ACTUALLY have missing values
    missing_lines = [f"- {col}: {cnt}" for col, cnt in missing.items() if cnt > 0]

    if missing_lines:
        facts.append("MISSING_VALUES_COUNT:")
        for col, cnt in missing.items():
            if cnt > 0:
                facts.append(f"{col}={cnt}")
    else:
        facts.append("MISSING_VALUES_COUNT: None")



    # query-specific info
    if "summary" in query_l or "overview" in query_l:
        return "\n".join(facts)

    if "columns" in query_l:
        return "\n".join(facts[:3])

    if "rows" in query_l or "count" in query_l:
        return f"ROWS: {rows}"

    if "missing" in query_l:
        return "\n".join(facts[3:])

    if "relationship" in query_l or "correlation" in query_l:
        return (
            "NO_ANALYSIS: Correlation analysis not implemented.\n"
            + "\n".join(facts)
        )

    return "\n".join(facts)
