from modules.file_qa import handle_file_qa
from modules.coding import handle_coding
from modules.file_qa import handle_local_file
from modules.coding import handle_coding
from modules.data_agent import handle_data_analysis



TOOLS = {
    "file_qa": handle_file_qa,
    "coding": handle_coding,
    "data_agent": handle_data_analysis
}

def run_tool(tool_name: str, input_text: str) -> str:
    if tool_name not in TOOLS:
        return "Unknown tool."

    return TOOLS[tool_name](input_text)