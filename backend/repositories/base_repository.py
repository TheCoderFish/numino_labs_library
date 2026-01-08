from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from db_helper import SessionLocal


class BaseRepository(ABC):
    """Base repository class providing common database operations"""

    def __init__(self):
        self._session_factory = SessionLocal

    def _get_session(self) -> Session:
        """Get a database session"""
        return self._session_factory()

    def _commit_and_refresh(self, session: Session, obj):
        """Commit transaction and refresh object"""
        session.commit()
        session.refresh(obj)
        return obj

    def _rollback_on_error(self, session: Session, error):
        """Rollback transaction on error"""
        session.rollback()
        raise error