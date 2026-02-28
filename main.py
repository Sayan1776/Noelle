from core.llm import chat
from core.intent_classifier import classify_intent
from core.memory import add_memory, recall_memory

from modules.system_control import handle_system_command
from modules.file_qa import handle_file_qa
from modules.coding import handle_coding
from modules.chat_mode import SYSTEM_PROMPT as NOELLE_PERSONA
from modules.web_browse import handle_browse
from modules.chat import generate_reply
from agent.loop import run_agent
from voice.speech_to_text import listen
from voice.text_to_speech import speak


# =====================================================
# NOELLE PERSONA WRAPPER
# =====================================================

def noelle_respond(chat_memory: list, user_text: str, tool_result: str = "",
                   voice_enabled: bool = False) -> tuple[str, list]:
    """
    Generate a response using Noelle's persona.
    If tool_result is provided, she wraps the factual result
    in her personality. Otherwise, she just chats normally.
    """

    if tool_result:
        # Noelle wraps tool output in her personality
        user_content = (
            f"[The user asked: {user_text}]\n\n"
            f"[Here is the factual result from my tools — relay this information "
            f"accurately but in my personality and tone:]\n\n"
            f"{tool_result}"
        )
    else:
        user_content = user_text

    messages = [
        NOELLE_PERSONA,
        *chat_memory,
        {"role": "user", "content": user_content}
    ]

    reply = generate_reply(messages)

    # Persist conversational turn
    chat_memory.extend([
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": reply}
    ])

    if voice_enabled:
        speak(reply)

    return reply, chat_memory


# =====================================================
# MAIN LOOP — UNIFIED MODE
# =====================================================

def main():
    chat_memory = []
    voice_enabled = False
    agent_mode_active = False  # When True, runs full agent loop for complex tasks

    print("=" * 50)
    print("  Noelle online. 💗")
    print("  I can chat, browse the web, analyze data,")
    print("  search your files, and more.")
    print("=" * 50)
    print("\nCommands:")
    print("  'voice on/off'  — toggle voice replies")
    print("  'listen'        — speak instead of type")
    print("  'agent on/off'  — toggle multi-step agent mode")
    print("  'exit'          — shut down\n")

    while True:
        user = input("You: ").strip()

        if not user:
            continue

        if user.lower() in ["exit", "quit"]:
            print("Noelle: ...Fine. Take care of yourself, okay? 💗")
            break

        # ====== VOICE CONTROLS ======
        if user.lower() == "voice on":
            voice_enabled = True
            print("Noelle: Voice enabled 🎙️\n")
            continue

        if user.lower() == "voice off":
            voice_enabled = False
            print("Noelle: Voice disabled 🔇\n")
            continue

        if user.lower() == "listen":
            user = listen()
            print(f"You (voice): {user}")

        # ====== AGENT MODE TOGGLE ======
        if user.lower() == "agent on":
            agent_mode_active = True
            print("Noelle: Agent mode ON — I'll plan multi-step tasks now. 🧠\n")
            continue

        if user.lower() == "agent off":
            agent_mode_active = False
            print("Noelle: Agent mode OFF — back to direct tool routing. ⚡\n")
            continue

        # ====== INTENT CLASSIFICATION ======
        intent = classify_intent(user)

        # --- Safety overrides ---
        lower = user.lower()

        # Memory triggers (LLM often misclassifies these as CHAT)
        memory_triggers = ["remember that", "remember this", "save this",
                           "do you remember", "what do you remember"]
        if any(phrase in lower for phrase in memory_triggers):
            intent = "MEMORY"

        # Coding triggers shouldn't go to FILE_QA
        if intent == "FILE_QA":
            coding_triggers = ["error", "exception", "traceback", "json", "python", "code"]
            if any(word in lower for word in coding_triggers):
                intent = "CODING"

        # Browse triggers (catch what LLM misses)
        browse_triggers = ["amazon", "flipkart", "youtube", "google",
                           "browse", "search online", "open website",
                           "search for", "search on", "look up", "find online"]
        if any(phrase in lower for phrase in browse_triggers):
            intent = "BROWSE"

        print(f"  [intent: {intent}]")

        # ====== BROWSE — always use direct handler (has its own pipeline) ======
        if intent == "BROWSE":
            result = handle_browse(user)
            reply, chat_memory = noelle_respond(
                chat_memory, user,
                tool_result=result,
                voice_enabled=voice_enabled
            )
            print(f"Noelle: {reply}\n")
            continue

        # ====== AGENT MODE (multi-step planning for non-browse tasks) ======
        if agent_mode_active and intent in ["FILE_QA", "CODING"]:
            print("  🧠 Running agent loop...")

            # Build chat context for the agent
            recent = chat_memory[-6:]
            context_lines = []
            for turn in recent:
                prefix = "User" if turn["role"] == "user" else "Noelle"
                context_lines.append(f"{prefix}: {turn['content']}")
            chat_context = "\n".join(context_lines)

            result = run_agent(
                goal=user,
                chat_context=chat_context,
                on_log=lambda msg: print(f"  {msg}")
            )

            final = result["final_answer"]
            reply, chat_memory = noelle_respond(
                chat_memory, user,
                tool_result=final,
                voice_enabled=voice_enabled
            )
            print(f"Noelle: {reply}\n")
            continue

        # ====== DIRECT TOOL ROUTING ======

        # --- SYSTEM ---
        if intent == "SYSTEM":
            result = handle_system_command(user)
            reply, chat_memory = noelle_respond(
                chat_memory, user,
                tool_result=result,
                voice_enabled=voice_enabled
            )
            print(f"Noelle: {reply}\n")
            continue

        # --- FILE_QA ---
        if intent == "FILE_QA":
            result = handle_file_qa(user)
            reply, chat_memory = noelle_respond(
                chat_memory, user,
                tool_result=result,
                voice_enabled=voice_enabled
            )
            print(f"Noelle: {reply}\n")
            continue

        # --- MEMORY ---
        if intent == "MEMORY":
            if user.lower().startswith(("remember", "save")):
                fact = user.split(" ", 1)[1]
                add_memory(fact)
                reply, chat_memory = noelle_respond(
                    chat_memory, user,
                    tool_result="Got it. I'll remember that.",
                    voice_enabled=voice_enabled
                )
            else:
                recalled = recall_memory()
                reply, chat_memory = noelle_respond(
                    chat_memory, user,
                    tool_result=recalled,
                    voice_enabled=voice_enabled
                )
            print(f"Noelle: {reply}\n")
            continue

        # --- CODING ---
        if intent == "CODING":
            result = handle_coding(user)
            reply, chat_memory = noelle_respond(
                chat_memory, user,
                tool_result=result,
                voice_enabled=voice_enabled
            )
            print(f"Noelle: {reply}\n")
            continue

        # ====== CHAT (fallback — pure Noelle conversation) ======
        reply, chat_memory = noelle_respond(
            chat_memory, user,
            voice_enabled=voice_enabled
        )
        print(f"Noelle: {reply}\n")


if __name__ == "__main__":
    main()
