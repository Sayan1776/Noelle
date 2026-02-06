from core.intent_classifier import classify_intent
from core.llm import chat
from core.memory import add_memory, recall_memory

from modules.system_control import handle_system_command
from modules.file_qa import handle_file_qa
from modules.coding import handle_coding


def process_assistant_input(user):
    intent = classify_intent(user)

    if intent == "SYSTEM":
        return handle_system_command(user)

    if intent == "FILE_QA":
        return handle_file_qa(user)

    if intent == "MEMORY":
        if user.lower().startswith(("remember", "save")):
            fact = user.split(" ", 1)[1]
            add_memory(fact)
            return "Got it. I’ll remember that."
        return recall_memory()

    if intent == "CODING":
        return handle_coding(user)

    # fallback chat
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user}
    ]
    return chat(messages)
