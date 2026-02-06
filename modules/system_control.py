import os

def handle_system_command(user_input: str):
    text = user_input.lower()

    if "open chrome" in text:
        os.system("start chrome")
        return "Opening Chrome."

    if "open vscode" in text or "open vs code" in text:
        os.system("code")
        return "Opening VS Code."

    return "System command not recognized."
