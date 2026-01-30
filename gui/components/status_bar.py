import customtkinter as ctk


class StatusBar(ctk.CTkFrame):
    """Bottom status bar showing server status and connection info."""

    def __init__(self, master, **kwargs):
        super().__init__(master, height=30, **kwargs)

        self._status_label = ctk.CTkLabel(
            self,
            text="Server: Stopped",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._status_label.pack(side="left", padx=10)

        self._db_label = ctk.CTkLabel(
            self,
            text="DB: Not connected",
            font=ctk.CTkFont(size=12),
            anchor="e",
        )
        self._db_label.pack(side="right", padx=10)

    def set_server_status(self, running: bool, port: int = 0) -> None:
        if running:
            self._status_label.configure(
                text=f"Server: Running (port {port})",
                text_color="#2ecc71",
            )
        else:
            self._status_label.configure(
                text="Server: Stopped",
                text_color="#e74c3c",
            )

    def set_db_status(self, connected: bool, db_name: str = "") -> None:
        if connected:
            self._db_label.configure(
                text=f"DB: {db_name}",
                text_color="#2ecc71",
            )
        else:
            self._db_label.configure(
                text="DB: Not connected",
                text_color="#e74c3c",
            )
