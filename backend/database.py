# This file contains all the database related connection pools and functions

from psycopg2.pool import SimpleConnectionPool

from .config import DATABASE_URL

connection_pool = SimpleConnectionPool(
    minconn= 1,
    maxconn= 10,
    dsn= DATABASE_URL
)

def get_db():
    conn = connection_pool.getconn()
    
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise   
    finally:
        connection_pool.putconn(conn)