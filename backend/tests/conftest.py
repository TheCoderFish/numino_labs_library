import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from server import init_db_pool, get_db_connection, return_db_connection

load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Setup test database"""
    # Initialize the pool
    init_db_pool()
    yield
    # Cleanup after all tests

@pytest.fixture
def db_connection():
    """Provide a database connection for tests"""
    conn = get_db_connection()
    yield conn
    return_db_connection(conn)

@pytest.fixture
def clean_database(db_connection):
    """Clean all tables before each test"""
    with db_connection.cursor() as cur:
        cur.execute("DELETE FROM ledger")
        cur.execute("DELETE FROM book")
        cur.execute("DELETE FROM member")
        db_connection.commit()