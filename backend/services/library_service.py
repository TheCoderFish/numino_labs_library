from typing import Dict, Any
from datetime import datetime

from repositories import BookRepository, MemberRepository, LedgerRepository
from error_codes import ErrorCodes


class LibraryService:
    """Service for library operations (borrowing/returning books)"""

    def __init__(self):
        self._book_repository = BookRepository()
        self._member_repository = MemberRepository()
        self._ledger_repository = LedgerRepository()

    def borrow_book(self, book_id: int, member_id: int) -> Dict[str, Any]:
        """Borrow a book for a member"""
        # Validate that the book exists and is available
        if not self._book_repository.is_book_available(book_id):
            raise ValueError("Book is not available")

        # Validate that the member exists
        if not self._member_repository.member_exists(member_id):
            raise ValueError("Member not found")

        # Perform the borrow operation
        self._book_repository.borrow_book(book_id, member_id)

        # Create ledger entry
        ledger_entry = self._ledger_repository.create_ledger_entry(
            book_id=book_id,
            member_id=member_id,
            action_type='BORROW',
            due_date_snapshot=datetime.utcnow()  # You can add logic for due date calculation
        )

        return ledger_entry

    def return_book(self, book_id: int, member_id: int) -> Dict[str, Any]:
        """Return a book from a member"""
        # Validate that the book is borrowed by this member
        if not self._book_repository.is_book_borrowed_by_member(book_id, member_id):
            raise ValueError("Book is not borrowed by this member")

        # Perform the return operation
        self._book_repository.return_book(book_id, member_id)

        # Create ledger entry
        ledger_entry = self._ledger_repository.create_ledger_entry(
            book_id=book_id,
            member_id=member_id,
            action_type='RETURN',
            due_date_snapshot=None
        )

        return ledger_entry