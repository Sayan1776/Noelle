from modules.chat_mode import Noelle_chat
from voice.speech_to_text import listen
from agent.loop import run_agent
from gui.session import ChatSession
from gui.session_store import save_sessions, load_sessions

from typing import Optional, Protocol, List
import uuid


# =====================================
# AgentView Protocol (GUI Contract)
# =====================================

class AgentView(Protocol):
    def clear_output(self) -> None: ...
    def append_output(self, message: str) -> None: ...
    def disable_input(self) -> None: ...
    def enable_input(self) -> None: ...
    def render_tabs(self) -> None: ...   # 👈 REQUIRED FOR GUI WIRING
    def render_session(self, session: ChatSession) -> None: ...




# =====================================
# ChatController
# =====================================

class ChatController:
    sessions: List[ChatSession]
    active_session: ChatSession
    view: Optional[AgentView]
    mode: str
    voice_enabled: bool

    def __init__(self, view: Optional[AgentView] = None):
        self.mode = "CHAT"
        self.voice_enabled = True
        self.view = view

        sessions, active_id = load_sessions()

        if not sessions:
            first = ChatSession(str(uuid.uuid4()), "Chat 1")
            self.sessions = [first]
            self.active_session = first
            self.persist()
        else:
            self.sessions = sessions
            self.active_session = next(
                (s for s in sessions if s.id == active_id),
                sessions[0]
            )

    # ----------------------------
    # PERSISTENCE
    # ----------------------------
    def persist(self):
        save_sessions(self.sessions, self.active_session.id)

    # ----------------------------
    # SESSION MANAGEMENT
    # ----------------------------
    def create_new_session(self):
        new = ChatSession(str(uuid.uuid4()), f"Chat {len(self.sessions) + 1}")
        self.sessions.append(new)
        self.active_session = new
        self.persist()
        if self.view:
            self.view.render_tabs()

    def rename_active_session(self, new_title: str) -> None:
        if not self.active_session:
            return

        title = new_title.strip()
        self.active_session.title = title if title else "Untitled Chat"
        self.persist()
        if self.view:
            self.view.render_tabs()

    def close_active_session(self) -> None:
        if len(self.sessions) <= 1:
            return

        index = self.sessions.index(self.active_session)
        self.sessions.remove(self.active_session)

        self.active_session = self.sessions[max(0, index - 1)]
        self.persist()
        if self.view:
            self.view.render_tabs()

    def switch_session(self, session_id: str):
        session = next(
            (s for s in self.sessions if s.id == session_id),
            None
        )
        if not session:
            return
        
        self.active_session = session
        if self.view:
            self.view.render_session(session)

        

    # ----------------------------
    # CHAT CONTEXT
    # ----------------------------
    def get_chat_context(self, max_turns: int = 6) -> str:
        recent = self.active_session.chat_memory[-max_turns:]
        lines = []

        for role, text in recent:
            prefix = "User" if role == "user" else "assistant"
            lines.append(f"{prefix}: {text}")

        return "\n".join(lines)

    # ----------------------------
    # MODE TOGGLE
    # ----------------------------
    def toggle_mode(self):
        self.mode = "assistant" if self.mode == "CHAT" else "CHAT"
        return self.mode

    # ----------------------------
    # TEXT INPUT
    # ----------------------------
    def process_text(self, text: str):
        if self.mode == "CHAT":
            reply, self.active_session.chat_memory = Noelle_chat(
                self.active_session.chat_memory,
                text,
                speak_reply=False
            )
            self.persist()
            return reply

        return self.run_agent_goal(text)

    # ----------------------------
    # VOICE INPUT
    # ----------------------------
    def process_voice(self):
        text = listen()
        reply, self.active_session.chat_memory = Noelle_chat(
            self.active_session.chat_memory,
            text,
            speak_reply=True
        )
        self.persist()
        return text, reply

    # ----------------------------
    # AGENT MODE
    # ----------------------------
    def run_agent_goal(self, goal: str):
        if self.view is None:
            raise RuntimeError("ChatController.view is not set")

        self.view.disable_input()

        try:
            chat_context = self.get_chat_context()

            result = run_agent(
                goal=goal,
                chat_context=chat_context
            )

            self.active_session.last_agent_result = result
            self.persist()
            return result

        finally:
            self.view.enable_input()