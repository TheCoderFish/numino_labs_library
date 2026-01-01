import pytest
from sqlalchemy.orm import sessionmaker
from db_helper import engine, Base, SessionLocal

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
    db_session.query(Base.metadata.tables['ledger']).delete()
    db_session.query(Base.metadata.tables['book']).delete()
    db_session.query(Base.metadata.tables['member']).delete()
    db_session.commit()