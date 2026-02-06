import customtkinter as ctk
import time

class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, text, sender="ai"):
        super().__init__(master, fg_color="transparent")

        is_ai = sender in ("ai", "assistant")

        bubble_color = "#2b2b2b" if is_ai else "#1f6aa5"
        text_color = "#e5e7eb" if is_ai else "#ffffff"
        anchor = "w" if is_ai else "e"

        timestamp = time.strftime("%H:%M")

        self.time_label = ctk.CTkLabel(
            self,
            text=timestamp,
            font=("Segoe UI", 10),
            text_color="#6b7280"
        )
        self.time_label.pack_forget()

        self.bind("<Enter>", lambda e: self.time_label.pack(anchor="e", padx=6))
        self.bind("<Leave>", lambda e: self.time_label.pack_forget())


        container = ctk.CTkFrame(
            self,
            fg_color=bubble_color,
            corner_radius=16
        )
        container.pack(anchor=anchor, padx=10, pady=6)

        label = ctk.CTkLabel(
            container,
            text=text,
            wraplength=280,
            justify="left",
            text_color=text_color,
            font=("Segoe UI", 13),
            padx=14,
            pady=10
        )
        label.pack()
