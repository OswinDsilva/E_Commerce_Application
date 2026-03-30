# All your enviornment variables get extracted here 

from dotenv import load_dotenv
import os
from urllib.parse import urlparse, unquote

load_dotenv()


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

