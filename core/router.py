def route(user_input: str) -> str:
    text = user_input.lower()

    system_keywords = [
        "open", "launch", "start", "run",
        "shutdown", "restart"
    ]

    file_keywords = [
        "summarize", "summary", "notes",
        "pdf", "document", "file", "read"
    ]

    memory_keywords = [
        "remember that", "remember this", "save this",
        "do you remember", "what do you remember"
    ]

    coding_keywords = [
        "error", "traceback", "bug", "debug",
        "code", "function", "class", "exception",
        "optimize", "why does", "fix this"
    ]

    for word in system_keywords:
        if word in text:
            return "SYSTEM"

    for word in file_keywords:
        if word in text:
            return "FILE_QA"

    for word in memory_keywords:
        if word in text:
            return "MEMORY"

    for word in coding_keywords:
        if word in text:
            return "CODING"

    return "CHAT"
