from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import or_, desc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db_helper import Book, Member, DatabaseHelper
from .base_repository import BaseRepository


class BookRepository(BaseRepository):
    """Repository for Book entity operations"""

    def create_book(self, title: str, author: str) -> Dict[str, Any]:
        """Create a new book"""
        session = self._get_session()
        try:
            book = Book(title=title, author=author, is_borrowed=False)
            session.add(book)
            return DatabaseHelper.sqlalchemy_to_dict(self._commit_and_refresh(session, book))
        except IntegrityError as e:
            self._rollback_on_error(session, ValueError("Book creation failed due to integrity constraint"))
        except SQLAlchemyError as e:
            self._rollback_on_error(session, e)
        finally:
            session.close()

    def update_book(self, book_id: int, title: str, author: str) -> Optional[Dict[str, Any]]:
        """Update an existing book"""
        session = self._get_session()
        try:
            book = session.query(Book).filter(Book.id == book_id).first()
            if not book:
                return None
            book.title = title
            book.author = author
            book.updated_at = book.updated_at  # This will trigger the onupdate
            return DatabaseHelper.sqlalchemy_to_dict(self._commit_and_refresh(session, book))
        except SQLAlchemyError as e:
            self._rollback_on_error(session, e)
        finally:
            session.close()

    def get_book_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        """Get a book by ID"""
        session = self._get_session()
        try:
            book = session.query(Book).filter(Book.id == book_id).first()
            return DatabaseHelper.sqlalchemy_to_dict(book) if book else None
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    def list_books(self) -> List[Dict[str, Any]]:
        """List all books with member information"""
        session = self._get_session()
        try:
            books = session.query(Book, Member.name.label('current_member_name')).outerjoin(
                Member, Book.current_member_id == Member.id
            ).all()
            result = []
            for book, member_name in books:
                book_dict = DatabaseHelper.sqlalchemy_to_dict(book)
                book_dict['current_member_name'] = member_name or ''
                result.append(book_dict)
            return result
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    def list_recent_books(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent books by updated_at"""
        session = self._get_session()
        try:
            books = session.query(Book, Member.name.label('current_member_name')).outerjoin(
                Member, Book.current_member_id == Member.id
            ).order_by(Book.updated_at.desc()).limit(limit).all()
            result = []
            for book, member_name in books:
                book_dict = DatabaseHelper.sqlalchemy_to_dict(book)
                book_dict['current_member_name'] = member_name or ''
                result.append(book_dict)
            return result
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    def list_books_paginated(self, limit: int = 20, cursor: Optional[str] = None,
                           filter_type: str = 'all', search: Optional[str] = None,
                           order_by: str = 'id') -> Tuple[List[Dict[str, Any]], Optional[str], bool]:
        """List books with pagination and filters
        
        Args:
            limit: Maximum number of books to return
            cursor: Cursor for pagination (book ID or timestamp depending on order_by)
            filter_type: 'all', 'available', or 'borrowed'
            search: Search query for title/author
            order_by: 'id' for ID-based pagination, 'updated_at' for recent books
        """
        session = self._get_session()
        try:
            query = session.query(Book, Member.name.label('current_member_name')).outerjoin(
                Member, Book.current_member_id == Member.id
            )

            # Apply search filter
            if search:
                query = query.filter(
                    or_(Book.title.ilike(f"%{search}%"), Book.author.ilike(f"%{search}%"))
                )

            # Apply status filter
            if filter_type == 'available':
                query = query.filter(Book.is_borrowed == False)
            elif filter_type == 'borrowed':
                query = query.filter(Book.is_borrowed == True)

            # Apply ordering and cursor for pagination
            if order_by == 'updated_at':
                # For recent books, order by updated_at descending
                query = query.order_by(desc(Book.updated_at))
                # Cursor-based pagination with updated_at is complex, so we'll just use limit
                # For recent books, cursor is typically not used
            else:
                # Default: order by ID for consistent pagination
                query = query.order_by(Book.id)
                # Apply cursor for pagination
                if cursor:
                    try:
                        cursor_id = int(cursor)
                        query = query.filter(Book.id > cursor_id)
                    except ValueError:
                        pass  # Invalid cursor, ignore

            # Limit results
            books = query.limit(limit + 1).all() if order_by == 'id' else query.limit(limit).all()

            result = []
            for book, member_name in books[:limit]:
                book_dict = DatabaseHelper.sqlalchemy_to_dict(book)
                book_dict['current_member_name'] = member_name or ''
                result.append(book_dict)

            # Determine next cursor and has_more
            if order_by == 'updated_at':
                # For recent books, we don't use cursor-based pagination
                has_more = False
                next_cursor = None
            else:
                has_more = len(books) > limit
                next_cursor = str(books[limit - 1][0].id) if result and has_more else None

            return result, next_cursor, has_more
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    def search_books(self, query: str) -> List[Dict[str, Any]]:
        """Search books by title or author"""
        session = self._get_session()
        try:
            books = session.query(Book, Member.name.label('current_member_name')).outerjoin(
                Member, Book.current_member_id == Member.id
            ).filter(
                or_(Book.title.ilike(f"%{query}%"), Book.author.ilike(f"%{query}%"))
            ).limit(50).all()
            result = []
            for book, member_name in books:
                book_dict = DatabaseHelper.sqlalchemy_to_dict(book)
                book_dict['current_member_name'] = member_name or ''
                result.append(book_dict)
            return result
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    def is_book_available(self, book_id: int) -> bool:
        """Check if a book is available for borrowing"""
        session = self._get_session()
        try:
            return Book.is_available(session, book_id)
        finally:
            session.close()

    def is_book_borrowed_by_member(self, book_id: int, member_id: int) -> bool:
        """Check if a book is borrowed by a specific member"""
        session = self._get_session()
        try:
            return Book.is_borrowed_by_member(session, book_id, member_id)
        finally:
            session.close()

    def borrow_book(self, book_id: int, member_id: int) -> Dict[str, Any]:
        """Mark a book as borrowed by a member"""
        session = self._get_session()
        try:
            # Get the book with row-level lock to prevent concurrent modifications
            book = session.query(Book).filter(Book.id == book_id).with_for_update().first()
            if not book:
                raise ValueError("Book not found")
            if book.is_borrowed:
                raise ValueError("Book is already borrowed")

            # Update book
            book.is_borrowed = True
            book.current_member_id = member_id
            book.updated_at = book.updated_at  # Trigger onupdate

            self._commit_and_refresh(session, book)
            return DatabaseHelper.sqlalchemy_to_dict(book)
        except SQLAlchemyError as e:
            self._rollback_on_error(session, e)
        finally:
            session.close()

    def return_book(self, book_id: int, member_id: int) -> Dict[str, Any]:
        """Mark a book as returned by a member"""
        session = self._get_session()
        try:
            # Get the book with row-level lock to prevent concurrent modifications
            book = session.query(Book).filter(Book.id == book_id).with_for_update().first()
            if not book:
                raise ValueError("Book not found")
            if not book.is_borrowed:
                raise ValueError("Book is not currently borrowed")
            if book.current_member_id != member_id:
                raise ValueError("This member did not borrow this book")

            # Update book
            book.is_borrowed = False
            book.current_member_id = None
            book.updated_at = book.updated_at  # Trigger onupdate

            self._commit_and_refresh(session, book)
            return DatabaseHelper.sqlalchemy_to_dict(book)
        except SQLAlchemyError as e:
            self._rollback_on_error(session, e)
        finally:
            session.close()

    def list_borrowed_books(self, member_id: int) -> List[Dict[str, Any]]:
        """List all books borrowed by a member"""
        session = self._get_session()
        try:
            books = session.query(Book).filter(
                Book.current_member_id == member_id,
                Book.is_borrowed == True
            ).all()
            return [DatabaseHelper.sqlalchemy_to_dict(book) for book in books]
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()