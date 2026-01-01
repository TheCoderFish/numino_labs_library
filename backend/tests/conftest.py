import pytest
from sqlalchemy.orm import sessionmaker
from db_helper import engine, Base, SessionLocal, Ledger, Book, Member

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Setup test database"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after all tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Provide a database session for tests"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def clean_database(db_session):
    """Clean all tables before each test"""
    # Delete in order to respect foreign key constraints
    db_session.query(Ledger).delete()
    db_session.query(Book).delete()
    db_session.query(Member).delete()
    db_session.commit()