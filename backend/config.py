import os
from urllib.parse import urlparse, unquote

from dotenv import load_dotenv

load_dotenv()


def parse_bool_env(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_database_url(url: str | None):
    if not url:
        return None

    parsed = urlparse(url)

    if parsed.scheme not in {"mysql", "mysql+pymysql"}:
        raise ValueError("DATABASE_URL must use mysql or mysql+pymysql scheme")

    return {
        "host": parsed.hostname or "localhost",
        "user": unquote(parsed.username) if parsed.username else "",
        "password": unquote(parsed.password) if parsed.password else "",
        "database": parsed.path.lstrip("/") if parsed.path else "",
        "port": parsed.port or 3306,
    }


DATABASE_URL = parse_database_url(os.getenv("DATABASE_URL"))
TEST_DATABASE_URL = parse_database_url(os.getenv("TEST_DATABASE_URL"))
SQL_DEBUG = parse_bool_env(os.getenv("SQL_DEBUG"), default=False)

