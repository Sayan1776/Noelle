from core.llm import chat
from core.intent_classifier import classify_intent
from core.memory import add_memory, recall_memory

from modules.system_control import handle_system_command
from modules.file_qa import handle_file_qa
from modules.coding import handle_coding
from modules.chat_mode import Noelle_chat
from voice.speech_to_text import listen



def main():
    # ====== GLOBAL STATE ======
    current_mode = "assistant"   # assistant | CHAT
    chat_memory = []             # memory only for Noelle chat
    voice_enabled = True         # voice only for Noelle chat

    print("assistant online.")
    print("Type 'Noelle mode' to enter chat mode.")
    print("Type 'assistant mode' to return.\n")

    # ====== MAIN LOOP ======
    while True:
        user = input("You: ").strip()

        if user.lower() in ["exit", "quit"]:
            print("assistant shutting down.")
            break

        # ====== MODE SWITCHING ======
        if user.lower() in ["Noelle mode", "enter chat mode"]:
            current_mode = "CHAT"
            chat_memory = []   # fresh emotional context
            print("assistant: I'm here 💗 Tell me what's on your mind.\n")
            continue

        if user.lower() in ["assistant mode", "exit chat mode"]:
            current_mode = "assistant"
            print("assistant: Switching back to assistant mode.\n")
            continue

        # =====================================================
        # 💗 CHAT MODE (AI Noelle / companion)
        # =====================================================
        if current_mode == "CHAT":

            if user.lower() == "voice on":
                voice_enabled = True
                print("assistant: Voice enabled 🎙️\n")
                continue

            if user.lower() == "voice off":
                voice_enabled = False
                print("assistant: Voice disabled 🔇\n")
                continue

            if user.lower() == "listen":
                user = listen()
                print(f"You (voice): {user}")

            reply, chat_memory = Noelle_chat(chat_memory, user, voice_enabled)
            print("assistant:", reply, "\n")
            continue


        # =====================================================
        # 🤖 assistant MODE (agentic AI)
        # =====================================================
        intent = classify_intent(user)

        # --- Safety override (important) ---
        if intent == "FILE_QA":
            coding_triggers = ["error", "exception", "traceback", "json", "python", "code"]
            if any(word in user.lower() for word in coding_triggers):
                intent = "CODING"

        # ====== SYSTEM ======
        if intent == "SYSTEM":
            result = handle_system_command(user)
            print("assistant:", result, "\n")
            continue

        # ====== FILE_QA ======
        if intent == "FILE_QA":
            result = handle_file_qa(user)
            print("assistant:", result, "\n")
            continue

        # ====== MEMORY ======
        if intent == "MEMORY":
            if user.lower().startswith(("remember", "save")):
                fact = user.split(" ", 1)[1]
                add_memory(fact)
                print("assistant: Got it. I’ll remember that.\n")
            else:
                print("assistant:", recall_memory(), "\n")
            continue

        # ====== CODING ======
        if intent == "CODING":
            result = handle_coding(user)
            print("assistant:", result, "\n")
            continue

        # ====== CHAT (fallback) ======
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful, concise AI assistant. "
                    "Answer clearly and stop when done."
                )
            },
            {"role": "user", "content": user}
        ]

        reply = chat(messages)
        print("Nolle:", reply, "\n")


if __name__ == "__main__":
    main()
