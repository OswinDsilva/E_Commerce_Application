import pymysql
from urllib.parse import quote_plus

DB_USER = "root"
DB_PASSWORD = "DBSProject@1"
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "ecommerce"

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
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