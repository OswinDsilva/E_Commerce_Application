import pymysql

from .config import DATABASE_URL, SQL_DEBUG


class DebugDictCursor(pymysql.cursors.DictCursor):
    def _log_query(self, query, args=None) -> None:
        if not SQL_DEBUG:
            return

        try:
            rendered_query = self.mogrify(query, args)
        except Exception:
            rendered_query = None

        if rendered_query is not None:
            print(f"SQL DEBUG: {rendered_query}")
            return

        print(f"SQL DEBUG: {query}")
        if args is not None:
            print(f"SQL DEBUG PARAMS: {args}")

    def execute(self, query, args=None):
        self._log_query(query, args)
        return super().execute(query, args)

    def executemany(self, query, args):
        if SQL_DEBUG:
            print(f"SQL DEBUG (executemany): {query}")
            print(f"SQL DEBUG PARAM SETS: {len(args)}")
        return super().executemany(query, args)


def get_connection():
    if DATABASE_URL is None:
        raise RuntimeError("DATABASE_URL is not configured")

    return pymysql.connect(
        host=DATABASE_URL["host"],
        user=DATABASE_URL["user"],
        password=DATABASE_URL["password"],
        database=DATABASE_URL["database"],
        port=DATABASE_URL.get("port", 3306),
        cursorclass=DebugDictCursor,  # returns dicts instead of tuples
        autocommit=False,
    )

def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
