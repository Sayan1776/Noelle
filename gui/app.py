import customtkinter as ctk
import threading
from tkinter import messagebox
import winsound
from gui.controller import ChatController
from gui.widgets import ChatBubble

# =========================
# Global UI config
# =========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class assistantGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # -------------------------
        # Window
        # -------------------------
        self.title("assistant ♡")
        self.geometry("480x720")
        self.minsize(440, 640)

        # -------------------------
        # Controller
        # -------------------------
        self.controller = ChatController(view=self)

        self.last_agent_logs = []
        self.reasoning_visible = False

        # =========================
        # HEADER (clean, minimal)
        # =========================
        header = ctk.CTkFrame(self, fg_color="#1f2937", height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_text = ctk.CTkFrame(header, fg_color="transparent")
        header_text.pack(side="left", padx=18, pady=12)

        name = ctk.CTkLabel(
            header_text,
            text="assistant Silva",
            font=("Segoe UI Semibold", 16),
            text_color="#e5e7eb"
        )
        name.pack(anchor="w")

        status = ctk.CTkLabel(
            header_text,
            text="Typically replies in a few seconds",
            font=("Segoe UI", 11),
            text_color="#9ca3af"
        )
        status.pack(anchor="w")

        # =========================
        # Tabs bar
        # =========================
        self.tabs_frame = ctk.CTkFrame(self, fg_color="#111827")
        self.tabs_frame.pack(fill="x", padx=10, pady=(6, 4))

        self.new_tab_btn = ctk.CTkButton(
            self.tabs_frame,
            text="+",
            width=36,
            height=28,
            command=self.new_tab
        )
        self.new_tab_btn.pack(side="right")

        self.clear_btn = ctk.CTkButton(
            self.tabs_frame,
            text="🗑",
            width=36,
            height=28,
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            command=self.clear_current_chat
        )
        self.clear_btn.pack(side="right", padx=(6, 0))

        self.render_tabs()

        # =========================
        # Chat area
        # =========================
        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#0b0f14"
        )
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=(4, 6))

        # =========================
        # Bottom input bar
        # =========================
        bottom = ctk.CTkFrame(self, fg_color="#0b0f14")
        bottom.pack(fill="x", padx=10, pady=10)

        self.entry = ctk.CTkEntry(
            bottom,
            placeholder_text="Enter your message…",
            height=44,
            corner_radius=18,
            font=("Segoe UI", 13)
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry.bind("<Return>", self.send_text)

        self.send_btn = ctk.CTkButton(
            bottom,
            text="➤",
            width=46,
            height=44,
            corner_radius=18,
            command=self.send_text
        )
        self.send_btn.pack(side="right")

        # =========================
        # Mode toggle
        # =========================
        self.mode_btn = ctk.CTkButton(
            self,
            text="💗 Noelle Mode",
            height=32,
            command=self.toggle_mode
        )
        self.mode_btn.pack(pady=(4, 6))

        # =========================
        # Reasoning toggle
        # =========================
        self.reason_btn = ctk.CTkButton(
            self,
            text="🧠 Show reasoning",
            height=30,
            state="disabled",
            command=self.toggle_reasoning
        )
        self.reason_btn.pack(pady=(0, 6))

        self.reasoning_frame = ctk.CTkScrollableFrame(
            self,
            height=180,
            fg_color="#020617"
        )
        self.reasoning_frame.pack_forget()

        # Initial render
        self.reload_chat()

    # Helper functions

    def scroll_to_bottom(self):
        canvas = self.chat_frame._parent_canvas
        self.after(20, lambda: canvas.yview_moveto(1.0))

    def show_typing_indicator(self):
        if hasattr(self, "_typing_label"):
            return

        self._typing_label = ChatBubble(
            self.chat_frame,
            "assistant is typing…",
            "ai"
        )
        self._typing_label.pack(anchor="w", padx=60, pady=4)
        self.scroll_to_bottom()


    def hide_typing_indicator(self):
        if hasattr(self, "_typing_label"):
            self._typing_label.destroy()
            del self._typing_label
            self.scroll_to_bottom()


    # ==================================================
    # Sound cues
    # ==================================================
    def play_send_sound(self):
        winsound.Beep(900, 35)

    def play_receive_sound(self):
        winsound.Beep(650, 40)

    # ==================================================
    # Tabs
    # ==================================================
    def new_tab(self):
        self.controller.create_new_session()
        self.render_tabs()
        self.reload_chat()

    def render_tabs(self):
        for child in self.tabs_frame.winfo_children():
            if child not in (self.new_tab_btn, self.clear_btn):
                child.destroy()

        for session in self.controller.sessions:
            is_active = session is self.controller.active_session
            btn = ctk.CTkButton(
                self.tabs_frame,
                text=session.title,
                width=120,
                height=28,
                corner_radius=14,
                fg_color="#2563eb" if is_active else "#1f2937",
                hover_color="#3b82f6" if is_active else "#374151",
                command=lambda s=session: self.select_tab(s)
            )
            btn.pack(side="left", padx=4)

    def select_tab(self, session):
        self.controller.active_session = session
        self.render_tabs()
        self.render_session(session)

    # ==================================================
    # Chat rendering (CENTERED COLUMN)
    # ==================================================
    def render_session(self, session):
        for widget in self.chat_frame.winfo_children():
            widget.destroy()

        for msg in session.chat_memory:
            bubble = ChatBubble(
                self.chat_frame,
                msg["content"],
                msg["role"]
            )
            bubble.pack(
                anchor="w" if msg["role"] == "ai" else "e",
                padx=60,
                pady=4
            )

    def reload_chat(self):
        self.chat_frame._parent_canvas.yview_moveto(0)
        self.render_session(self.controller.active_session)

    def add_message(self, text, sender):
        role = "user" if sender == "user" else "assistant"
        self.controller.active_session.chat_memory.append(
            {"role": role, "content": text}
        )

        bubble = ChatBubble(self.chat_frame, text, sender)
        bubble.pack_forget()

        def delayed_show():
            bubble.pack(
                anchor="w" if sender == "ai" else "e",
                padx=60,
                pady=4
            )
            self.scroll_to_bottom()

        self.after(60, delayed_show)

    # ==================================================
    # Input handling
    # ==================================================
    def send_text(self, event=None):
        msg = self.entry.get().strip()
        if not msg:
            return

        self.entry.delete(0, "end")
        self.add_message(msg, "user")

        threading.Thread(
            target=self._handle_ai_reply,
            args=(msg,),
            daemon=True
        ).start()
        self.play_send_sound()

    def _handle_ai_reply(self, msg):
        self.after(0, self.show_typing_indicator)

        result = self.controller.process_text(msg)

        self.after(0, self.hide_typing_indicator)
        self.after(0, lambda: self.add_message(result, "ai"))
        self.play_receive_sound()

    # ==================================================
    # Mode toggle (WITH NOTIFICATION)
    # ==================================================
    def toggle_mode(self):
        mode = self.controller.toggle_mode()

        if mode == "CHAT":
            self.mode_btn.configure(text="💗 Noelle Mode")
            self.add_message("Back to just us 💗", "ai")
        else:
            self.mode_btn.configure(text="🤖 assistant Mode")
            self.add_message("Switching to assistant mode.", "ai")

    # ==================================================
    # Reasoning
    # ==================================================
    def toggle_reasoning(self):
        self.reasoning_visible = not self.reasoning_visible
        if self.reasoning_visible:
            self._show_reasoning()
        else:
            self._hide_reasoning()

    def _show_reasoning(self):
        self.reasoning_frame.pack(fill="x", padx=10, pady=(0, 10))

    def _hide_reasoning(self):
        self.reasoning_frame.pack_forget()

    # ==================================================
    # AgentView REQUIRED METHODS
    # ==================================================
    def clear_output(self) -> None:
        for widget in self.chat_frame.winfo_children():
            widget.destroy()

    def append_output(self, message: str) -> None:
        self.add_message(message, "ai")

    def disable_input(self) -> None:
        self.entry.configure(state="disabled")
        self.send_btn.configure(state="disabled")

    def enable_input(self) -> None:
        self.entry.configure(state="normal")
        self.send_btn.configure(state="normal")

    # ==================================================
    # Clear chat
    # ==================================================
    def clear_current_chat(self):
        session = self.controller.active_session
        if not session:
            return

        confirm = messagebox.askyesno(
            "Clear chat?",
            f"Clear conversation in '{session.title}'?"
        )
        if not confirm:
            return

        session.chat_memory.clear()
        self.clear_output()
        self.controller.persist()


if __name__ == "__main__":
    app = assistantGUI()
    app.mainloop()