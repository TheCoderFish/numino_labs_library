from typing import List, Optional, Tuple, Dict, Any

from repositories import BookRepository
from .base_service import BaseService


class BookService(BaseService):
    """Service for book-related business logic"""

    def __init__(self):
        self._book_repository = BookRepository()

    def create_book(self, title: str, author: str) -> Dict[str, Any]:
        """Create a new book with validation"""
        self.validate_book_data(title, author)
        return self._book_repository.create_book(title, author)

    def update_book(self, book_id: int, title: str, author: str) -> Optional[Dict[str, Any]]:
        """Update an existing book with validation"""
        self.validate_book_data(title, author)
        return self._book_repository.update_book(book_id, title, author)

    def get_book_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        """Get a book by ID"""
        return self._book_repository.get_book_by_id(book_id)

    def list_books(self) -> List[Dict[str, Any]]:
        """List all books"""
        return self._book_repository.list_books()

    def list_recent_books(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent books"""
        return self._book_repository.list_recent_books(limit)

    def list_books_paginated(self, limit: int = 20, cursor: Optional[str] = None,
                           filter_type: str = 'all', search: Optional[str] = None,
                           order_by: str = 'id') -> Tuple[List[Dict[str, Any]], Optional[str], bool]:
        """List books with pagination and filters"""
        return self._book_repository.list_books_paginated(limit, cursor, filter_type, search, order_by)

    def search_books(self, query: str) -> List[Dict[str, Any]]:
        """Search books by title or author"""
        return self._book_repository.search_books(query)

    def is_book_available(self, book_id: int) -> bool:
        """Check if a book is available"""
        return self._book_repository.is_book_available(book_id)

    def list_borrowed_books(self, member_id: int) -> List[Dict[str, Any]]:
        """List books borrowed by a member"""
        return self._book_repository.list_borrowed_books(member_id)