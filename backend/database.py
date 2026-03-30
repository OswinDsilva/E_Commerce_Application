# This file contains all the database related connection functions

import pymysql
from .config import DATABASE_URL


def get_connection():
    return pymysql.connect(
        host=DATABASE_URL["host"],
        user=DATABASE_URL["user"],
        password=DATABASE_URL["password"],
        database=DATABASE_URL["database"],
        port=DATABASE_URL.get("port", 3306),
        cursorclass=pymysql.cursors.DictCursor,  # returns dicts instead of tuples
        autocommit=False
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