from core.llm import chat

def generate_reply(messages):
    """Pure LLM call.
    messages: List[{"role": str, "content": str}]
    returns: assistant reply (str)

    This function must not :
        append to messages
        add system prompts
        store memory
    """
    return chat(messages)