from datetime import datetime

import customtkinter as ctk

from app.api_app import create_app
from app.database.connection import db_manager
from app.middleware.logging_middleware import LoggingMiddleware
from gui.components.config_panel import ConfigPanel
from gui.components.log_viewer import LogViewer
from gui.components.server_control import ServerControl
from gui.components.status_bar import StatusBar
from server.uvicorn_server import server_manager
from utils.log_manager import LogEntry, log_manager


class AppGUI(ctk.CTk):
    """Main application window with dark theme."""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("ERP API Server")
        self.geometry("900x650")
        self.minsize(750, 500)

        # Dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._build_ui()
        self._start_log_polling()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Auto-start API server after UI is ready
        self.after(100, self._start_server)

    def _build_ui(self):
        # Top frame: config + server control
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Config panel (left side)
        self._config_panel = ConfigPanel(
            top_frame,
            on_config_changed=self._on_config_changed,
        )
        self._config_panel.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Server control (right side)
        control_frame = ctk.CTkFrame(top_frame)
        control_frame.pack(side="right", fill="y", padx=(5, 0))

        self._server_control = ServerControl(
            control_frame,
            on_start=self._start_server,
            on_stop=self._stop_server,
        )
        self._server_control.pack(padx=10, pady=10)

        # Log viewer (center, expandable)
        self._log_viewer = LogViewer(self)
        self._log_viewer.pack(fill="both", expand=True, padx=10, pady=5)

        # Status bar (bottom)
        self._status_bar = StatusBar(self)
        self._status_bar.pack(fill="x", padx=10, pady=(0, 10))

    def _start_server(self):
        """Start the API server."""
        # Configure database
        server_info = self._config_panel.get_selected_db()
        if server_info is None:
            self._status_bar.set_db_status(False)
            return

        db_manager.configure(server_info)

        # Test connection first
        success, msg = db_manager.test_connection()
        if not success:
            self._status_bar.set_db_status(False)
            self._log_viewer.append_entry(
                LogEntry(
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    method="SYSTEM",
                    path="Database Connection",
                    status_code=500,
                    duration_ms=0,
                    response_body=f"Connection failed: {msg}",
                )
            )
            return

        self._status_bar.set_db_status(True, server_info.display)

        # Create FastAPI app with middleware
        context_path = self._config_panel.get_context_path()
        app = create_app(context_path)
        app.add_middleware(LoggingMiddleware)

        # Start server
        port = self._config_panel.get_port()
        server_manager.start(app, port=port)

        self._server_control.set_running(True)
        self._status_bar.set_server_status(True, port)

    def _stop_server(self):
        """Stop the API server."""
        server_manager.stop()
        self._server_control.set_running(False)
        self._status_bar.set_server_status(False)

    def _on_config_changed(self):
        """Handle configuration changes."""
        pass

    def _start_log_polling(self):
        """Poll the log queue every 100ms and append entries to the viewer."""
        entries = log_manager.poll_all()
        for entry in entries:
            self._log_viewer.append_entry(entry)
        self.after(100, self._start_log_polling)

    def _on_close(self):
        """Handle window close: stop server, then destroy."""
        if server_manager.is_running:
            server_manager.stop()
        db_manager.close()
        self.destroy()
