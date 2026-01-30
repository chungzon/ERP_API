import threading
from contextlib import contextmanager
from typing import Optional

import pymssql

from app.database.config import DatabaseServerInfo


class DatabaseManager:
    """Thread-safe database connection manager using pymssql."""

    def __init__(self):
        self._lock = threading.Lock()
        self._server_info: Optional[DatabaseServerInfo] = None
        self._connection: Optional[pymssql.Connection] = None

    def configure(self, server_info: DatabaseServerInfo) -> None:
        """Set the active database server configuration."""
        with self._lock:
            self.close()
            self._server_info = server_info

    @property
    def server_info(self) -> Optional[DatabaseServerInfo]:
        return self._server_info

    def _create_connection(self) -> pymssql.Connection:
        if self._server_info is None:
            raise RuntimeError("Database not configured. Call configure() first.")
        return pymssql.connect(
            server=self._server_info.host,
            port=self._server_info.port,
            user=self._server_info.user,
            password=self._server_info.password,
            database=self._server_info.database,
            charset="utf8",
            as_dict=True,
        )

    def get_connection(self) -> pymssql.Connection:
        """Get or create the singleton connection."""
        with self._lock:
            if self._connection is None or self._connection._conn is None:
                self._connection = self._create_connection()
            return self._connection

    @contextmanager
    def cursor(self):
        """Context manager that provides a cursor with auto-commit."""
        conn = self.get_connection()
        cursor = conn.cursor(as_dict=True)
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def test_connection(self, server_info: Optional[DatabaseServerInfo] = None) -> tuple[bool, str]:
        """Test a database connection. Returns (success, message)."""
        info = server_info or self._server_info
        if info is None:
            return False, "No database configured"
        try:
            conn = pymssql.connect(
                server=info.host,
                port=info.port,
                user=info.user,
                password=info.password,
                database=info.database,
                charset="utf8",
                login_timeout=5,
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True, f"Connected to {info.display} ({info.database})"
        except Exception as e:
            return False, str(e)

    def close(self) -> None:
        """Close the current connection."""
        if self._connection is not None:
            try:
                self._connection.close()
            except Exception:
                pass
            self._connection = None


# Global singleton
db_manager = DatabaseManager()
