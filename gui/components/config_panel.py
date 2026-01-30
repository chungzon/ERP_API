import threading
from typing import Callable, Optional

import customtkinter as ctk

from app.database.config import (
    AppConfig,
    DatabaseServerInfo,
    load_app_config,
    load_database_servers,
    save_app_config,
)
from app.database.connection import db_manager


class ConfigPanel(ctk.CTkFrame):
    """Configuration panel for port, context path, and database selection."""

    def __init__(self, master, on_config_changed: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)

        self._on_config_changed = on_config_changed
        self._servers: list[DatabaseServerInfo] = []
        self._config = AppConfig()

        self._build_ui()
        self._load_config()

    def _build_ui(self):
        # Title
        ctk.CTkLabel(
            self,
            text="Configuration",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))

        # Port
        ctk.CTkLabel(self, text="Port:", font=ctk.CTkFont(size=12)).grid(
            row=1, column=0, sticky="w", padx=10, pady=3
        )
        self._port_entry = ctk.CTkEntry(self, width=100, font=ctk.CTkFont(size=12))
        self._port_entry.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        # Context Path
        ctk.CTkLabel(self, text="Context Path:", font=ctk.CTkFont(size=12)).grid(
            row=2, column=0, sticky="w", padx=10, pady=3
        )
        self._context_entry = ctk.CTkEntry(self, width=160, font=ctk.CTkFont(size=12))
        self._context_entry.grid(row=2, column=1, sticky="w", padx=5, pady=3)

        # Database selection
        ctk.CTkLabel(self, text="Database:", font=ctk.CTkFont(size=12)).grid(
            row=3, column=0, sticky="w", padx=10, pady=3
        )
        self._db_combo = ctk.CTkComboBox(
            self,
            width=200,
            font=ctk.CTkFont(size=12),
            values=["Loading..."],
            command=self._on_db_selected,
        )
        self._db_combo.grid(row=3, column=1, sticky="w", padx=5, pady=3)

        # Test Connection button
        self._test_btn = ctk.CTkButton(
            self,
            text="Test Connection",
            width=130,
            height=30,
            command=self._test_connection,
        )
        self._test_btn.grid(row=3, column=2, padx=5, pady=3)

        # Connection status label
        self._conn_status = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            wraplength=300,
        )
        self._conn_status.grid(row=4, column=0, columnspan=3, sticky="w", padx=10, pady=2)

        # Save button
        self._save_btn = ctk.CTkButton(
            self,
            text="Save Config",
            width=110,
            height=30,
            command=self._save_config,
        )
        self._save_btn.grid(row=5, column=0, columnspan=3, sticky="w", padx=10, pady=(5, 10))

    def _load_config(self):
        """Load config files and populate UI."""
        try:
            self._config = load_app_config()
        except Exception:
            self._config = AppConfig()

        try:
            self._servers = load_database_servers()
        except Exception:
            self._servers = []

        # Populate port
        self._port_entry.delete(0, "end")
        self._port_entry.insert(0, str(self._config.port))

        # Populate context path
        self._context_entry.delete(0, "end")
        self._context_entry.insert(0, self._config.context_path)

        # Populate database dropdown
        if self._servers:
            display_names = [s.display for s in self._servers]
            self._db_combo.configure(values=display_names)
            # Select the configured one
            selected = next(
                (s for s in self._servers if s.index == self._config.selected_db_index),
                self._servers[0],
            )
            self._db_combo.set(selected.display)
        else:
            self._db_combo.configure(values=["No databases found"])
            self._db_combo.set("No databases found")

    def _on_db_selected(self, value: str):
        """Handle database selection change."""
        pass

    def _test_connection(self):
        """Test the selected database connection."""
        server = self._get_selected_server()
        if server is None:
            self._conn_status.configure(text="No database selected", text_color="#e74c3c")
            return

        self._conn_status.configure(text="Testing...", text_color="#f39c12")
        self._test_btn.configure(state="disabled")

        def _test():
            success, message = db_manager.test_connection(server)
            self.after(0, lambda: self._on_test_result(success, message))

        threading.Thread(target=_test, daemon=True).start()

    def _on_test_result(self, success: bool, message: str):
        self._test_btn.configure(state="normal")
        if success:
            self._conn_status.configure(text=f"OK: {message}", text_color="#2ecc71")
        else:
            self._conn_status.configure(text=f"Failed: {message}", text_color="#e74c3c")

    def _save_config(self):
        """Save current UI values to config file."""
        try:
            port = int(self._port_entry.get())
        except ValueError:
            port = 8080

        context_path = self._context_entry.get().strip()
        server = self._get_selected_server()
        selected_index = server.index if server else 1

        self._config = AppConfig(
            port=port,
            context_path=context_path,
            selected_db_index=selected_index,
        )
        save_app_config(self._config)
        self._conn_status.configure(text="Config saved", text_color="#2ecc71")

        if self._on_config_changed:
            self._on_config_changed()

    def _get_selected_server(self) -> Optional[DatabaseServerInfo]:
        """Get the currently selected database server."""
        display = self._db_combo.get()
        return next((s for s in self._servers if s.display == display), None)

    def get_port(self) -> int:
        try:
            return int(self._port_entry.get())
        except ValueError:
            return 8080

    def get_context_path(self) -> str:
        return self._context_entry.get().strip()

    def get_selected_db(self) -> Optional[DatabaseServerInfo]:
        return self._get_selected_server()
