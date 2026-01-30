import json
import os
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseServerInfo:
    index: int
    user: str
    display: str
    host: str
    port: int
    database: str
    password: str
    driver: str


@dataclass
class AppConfig:
    port: int = 8080
    context_path: str = ""
    selected_db_index: int = 1


def _get_conf_dir() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "conf")


def parse_jdbc_url(url: str) -> tuple[str, int, str]:
    """Parse JDBC URL to extract host, port, database.

    Supports formats:
        jdbc:sqlserver://host:port;DatabaseName=DB
        jdbc:sqlserver://host;DatabaseName=DB  (default port 1433)
    """
    pattern = r"jdbc:sqlserver://([^:;]+)(?::(\d+))?;DatabaseName=(.+)"
    match = re.match(pattern, url)
    if not match:
        raise ValueError(f"Cannot parse JDBC URL: {url}")
    host = match.group(1)
    port = int(match.group(2)) if match.group(2) else 1433
    database = match.group(3)
    return host, port, database


def load_database_servers(config_path: Optional[str] = None) -> list[DatabaseServerInfo]:
    """Load database server configurations from DataBaseServer.json."""
    if config_path is None:
        config_path = os.path.join(_get_conf_dir(), "DataBaseServer.json")

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    servers = []
    for server in data.get("Servers", []):
        host, port, database = parse_jdbc_url(server["Url"])
        servers.append(DatabaseServerInfo(
            index=server["Index"],
            user=server["User"],
            display=server["Display"],
            host=host,
            port=port,
            database=database,
            password=server["Password"],
            driver=server.get("Driver", ""),
        ))
    return servers


def load_app_config(config_path: Optional[str] = None) -> AppConfig:
    """Load application configuration from app_config.json."""
    if config_path is None:
        config_path = os.path.join(_get_conf_dir(), "app_config.json")

    if not os.path.exists(config_path):
        return AppConfig()

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return AppConfig(
        port=data.get("port", 8080),
        context_path=data.get("context_path", ""),
        selected_db_index=data.get("selected_db_index", 1),
    )


def save_app_config(config: AppConfig, config_path: Optional[str] = None) -> None:
    """Save application configuration to app_config.json."""
    if config_path is None:
        config_path = os.path.join(_get_conf_dir(), "app_config.json")

    data = {
        "port": config.port,
        "context_path": config.context_path,
        "selected_db_index": config.selected_db_index,
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
