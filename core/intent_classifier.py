from core.llm import chat

INTENTS = ["SYSTEM", "FILE_QA", "MEMORY", "CODING", "BROWSE", "CHAT"]

def classify_intent(user_input: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are an intent classifier for an AI assistant.\n\n"
                "Choose ONE intent from the list below:\n"
                f"{', '.join(INTENTS)}\n\n"
                "Intent definitions:\n"
                "- SYSTEM: user wants the assistant to perform an OS or app action.\n"
                "- FILE_QA: user asks questions that REQUIRE reading the user's local documents or notes.\n"
                "- MEMORY: user wants to save or recall personal information.\n"
                "- CODING: user asks about programming, errors, debugging, explanations, or software behavior.\n"
                "- BROWSE: user wants to open a website, search the web, browse online, look up a product, "
                "google something, visit a URL, or perform any task that requires a web browser.\n"
                "- CHAT: casual conversation or general questions that DON'T require browsing, files, or actions.\n\n"
                "Rules:\n"
                "- If the user mentions a website, URL, 'search online', 'google', 'amazon', 'look up', "
                "'find online', 'browse', or any web-related task, choose BROWSE.\n"
                "- If the question is about programming or errors, choose CODING.\n"
                "- Do NOT choose FILE_QA unless document context is REQUIRED.\n"
                "- Respond with ONLY the intent name.\n"
                "- No explanations. No punctuation."
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    response = chat(messages).strip().upper()

    if response not in INTENTS:
        return "CHAT"

    return response
