from typing import Dict, Any
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from db_helper import Ledger, DatabaseHelper
from .base_repository import BaseRepository


class LedgerRepository(BaseRepository):
    """Repository for Ledger entity operations"""

    def create_ledger_entry(self, book_id: int, member_id: int, action_type: str,
                          due_date_snapshot: datetime = None) -> Dict[str, Any]:
        """Create a new ledger entry"""
        session = self._get_session()
        try:
            ledger_entry = Ledger(
                book_id=book_id,
                member_id=member_id,
                action_type=action_type,
                due_date_snapshot=due_date_snapshot
            )
            session.add(ledger_entry)
            return DatabaseHelper.sqlalchemy_to_dict(self._commit_and_refresh(session, ledger_entry))
        except SQLAlchemyError as e:
            self._rollback_on_error(session, e)
        finally:
            session.close()