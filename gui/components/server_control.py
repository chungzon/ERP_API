import customtkinter as ctk


class ServerControl(ctk.CTkFrame):
    """Start/Stop button panel with status indicator."""

    def __init__(self, master, on_start=None, on_stop=None, **kwargs):
        super().__init__(master, **kwargs)

        self._on_start = on_start
        self._on_stop = on_stop

        # Status indicator
        self._status_indicator = ctk.CTkLabel(
            self,
            text="\u2b24",  # Filled circle
            font=ctk.CTkFont(size=16),
            text_color="#e74c3c",
            width=20,
        )
        self._status_indicator.pack(side="left", padx=(10, 5))

        self._status_text = ctk.CTkLabel(
            self,
            text="Stopped",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=80,
        )
        self._status_text.pack(side="left", padx=(0, 10))

        # Buttons
        self._start_btn = ctk.CTkButton(
            self,
            text="Start Server",
            width=120,
            height=35,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self._handle_start,
        )
        self._start_btn.pack(side="left", padx=5)

        self._stop_btn = ctk.CTkButton(
            self,
            text="Stop Server",
            width=120,
            height=35,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self._handle_stop,
            state="disabled",
        )
        self._stop_btn.pack(side="left", padx=5)

    def _handle_start(self):
        if self._on_start:
            self._on_start()

    def _handle_stop(self):
        if self._on_stop:
            self._on_stop()

    def set_running(self, running: bool) -> None:
        if running:
            self._status_indicator.configure(text_color="#2ecc71")
            self._status_text.configure(text="Running")
            self._start_btn.configure(state="disabled")
            self._stop_btn.configure(state="normal")
        else:
            self._status_indicator.configure(text_color="#e74c3c")
            self._status_text.configure(text="Stopped")
            self._start_btn.configure(state="normal")
            self._stop_btn.configure(state="disabled")
