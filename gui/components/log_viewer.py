import tkinter as tk

import customtkinter as ctk

from utils.log_manager import LogEntry


class LogViewer(ctk.CTkFrame):
    """Real-time log viewer with color-coded entries."""

    # Tag color definitions
    TAG_COLORS = {
        "timestamp": "#888888",
        "method_get": "#3498db",
        "method_post": "#e67e22",
        "method_put": "#9b59b6",
        "method_delete": "#e74c3c",
        "status_2xx": "#2ecc71",
        "status_4xx": "#e67e22",
        "status_5xx": "#e74c3c",
        "body": "#aaaaaa",
        "duration": "#888888",
        "separator": "#555555",
    }

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Header with Clear button
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=(5, 0))

        ctk.CTkLabel(
            header,
            text="Request / Response Log",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        self._auto_scroll_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            header,
            text="Auto-scroll",
            variable=self._auto_scroll_var,
            width=100,
            font=ctk.CTkFont(size=12),
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            header,
            text="Clear",
            width=60,
            height=28,
            command=self._clear_log,
        ).pack(side="right")

        # Text widget for log display
        self._textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=12),
            activate_scrollbars=True,
            wrap="word",
        )
        self._textbox.pack(fill="both", expand=True, padx=5, pady=5)

        # Configure tags on the underlying tk.Text widget
        text_widget = self._textbox._textbox
        for tag_name, color in self.TAG_COLORS.items():
            text_widget.tag_configure(tag_name, foreground=color)

        # Make read-only
        self._textbox.configure(state="disabled")

    def append_entry(self, entry: LogEntry) -> None:
        """Append a formatted log entry with color tags."""
        text_widget = self._textbox._textbox
        self._textbox.configure(state="normal")

        # Separator
        self._insert_tagged("=" * 80 + "\n", "separator")

        # Timestamp
        self._insert_tagged(f"[{entry.timestamp}] ", "timestamp")

        # Method
        method_tag = f"method_{entry.method.lower()}"
        if method_tag not in self.TAG_COLORS:
            method_tag = "method_get"
        self._insert_tagged(f"{entry.method} ", method_tag)

        # Path
        self._insert_tagged(f"{entry.path} ", "body")

        # Status code
        if 200 <= entry.status_code < 300:
            status_tag = "status_2xx"
        elif 400 <= entry.status_code < 500:
            status_tag = "status_4xx"
        else:
            status_tag = "status_5xx"
        self._insert_tagged(f"[{entry.status_code}] ", status_tag)

        # Duration
        self._insert_tagged(f"({entry.duration_ms:.1f}ms)\n", "duration")

        # Request body
        if entry.request_body:
            self._insert_tagged(f"  Request:  {entry.request_body}\n", "body")

        # Response body
        if entry.response_body:
            resp_display = entry.response_body
            if len(resp_display) > 500:
                resp_display = resp_display[:500] + "..."
            self._insert_tagged(f"  Response: {resp_display}\n", "body")

        self._textbox.configure(state="disabled")

        # Auto-scroll
        if self._auto_scroll_var.get():
            self._textbox.see("end")

    def _insert_tagged(self, text: str, tag: str) -> None:
        """Insert text with a specific tag."""
        text_widget = self._textbox._textbox
        text_widget.insert("end", text, tag)

    def _clear_log(self) -> None:
        """Clear the log display."""
        self._textbox.configure(state="normal")
        self._textbox._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")
