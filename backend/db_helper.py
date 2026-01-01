import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

# Database connection pool
db_pool = None

def get_db_connection():
    """Get a database connection from the pool"""
    return db_pool.getconn()

def return_db_connection(conn):
    """Return a connection to the pool"""
    db_pool.putconn(conn)

def init_db_pool():
    """Initialize the database connection pool"""
    global db_pool
    db_pool = psycopg2.pool.ThreadedConnectionPool(
        1, 20,
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5435'),
        database=os.getenv('DB_NAME', 'numino_db'),
        user=os.getenv('DB_USER', 'numino_user'),
        password=os.getenv('DB_PASSWORD', 'numino_password')
    )

class DatabaseHelper:
    @staticmethod
    def execute_query(query, params=None, fetch_one=False, fetch_all=False):
        """
        Execute a database query with connection management.
        
        :param query: SQL query string
        :param params: Parameters for the query
        :param fetch_one: If True, return one row
        :param fetch_all: If True, return all rows
        :return: Query result or None
        """
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch_one:
                    result = cur.fetchone()
                elif fetch_all:
                    result = cur.fetchall()
                else:
                    result = None
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            return_db_connection(conn)