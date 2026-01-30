import queue
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class LogEntry:
    timestamp: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    request_body: Optional[str] = None
    response_body: Optional[str] = None


class LogManager:
    """Thread-safe log queue for passing log entries from middleware to GUI."""

    def __init__(self):
        self._queue: queue.Queue[LogEntry] = queue.Queue()
        self._lock = threading.Lock()

    def push(self, entry: LogEntry) -> None:
        """Push a log entry (called from middleware thread)."""
        self._queue.put(entry)

    def poll_all(self) -> list[LogEntry]:
        """Get all pending log entries (called from GUI thread)."""
        entries = []
        while True:
            try:
                entries.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return entries

    def clear(self) -> None:
        """Clear all pending entries."""
        with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break


# Global singleton
log_manager = LogManager()
