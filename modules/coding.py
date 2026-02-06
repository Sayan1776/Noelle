from core.llm import chat

def handle_coding(user_input: str):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a senior Python software engineer.\n"
                "All explanations and examples MUST be in Python.\n"
                "Explain errors clearly and concisely.\n"
                "If an error is mentioned, explain the cause and the fix.\n"
                "Do not use JavaScript or other languages.\n"
                "use other languages only if explicitly mentioned or told to.\n"
                "Do not ramble."
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    return chat(messages)
