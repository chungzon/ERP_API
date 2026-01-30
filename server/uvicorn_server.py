import threading
import asyncio

import uvicorn


class EmbeddedServer(uvicorn.Server):
    """Custom uvicorn Server that runs in a daemon thread.

    Overrides install_signal_handlers to no-op since signal handlers
    can only be installed on the main thread (which runs tkinter).
    """

    def install_signal_handlers(self):
        pass  # No-op: signals only work on the main thread


class ServerManager:
    """Manages the embedded uvicorn server lifecycle."""

    def __init__(self):
        self._server: EmbeddedServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._server is not None and self._server.started

    def start(self, app, host: str = "0.0.0.0", port: int = 8080) -> None:
        """Start the uvicorn server in a background daemon thread."""
        if self.is_running:
            return

        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="warning",
            access_log=False,
        )
        self._server = EmbeddedServer(config=config)

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._server.serve())

    def stop(self) -> None:
        """Signal the uvicorn server to shut down."""
        if self._server is not None:
            self._server.should_exit = True
            if self._thread is not None:
                self._thread.join(timeout=5)
            self._server = None
            self._thread = None


# Global singleton
server_manager = ServerManager()
