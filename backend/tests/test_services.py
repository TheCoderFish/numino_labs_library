import pytest
from unittest.mock import Mock, patch
from services import BookService, MemberService, LibraryService


class TestBookService:
    """Unit tests for BookService"""

    def test_create_book_success(self):
        """Test creating a book successfully"""
        with patch('services.book_service.BookRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.create_book.return_value = {
                'id': 1,
                'title': 'Test Book',
                'author': 'Test Author',
                'is_borrowed': False,
                'current_member_id': None,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            }

            service = BookService()
            result = service.create_book('Test Book', 'Test Author')

            mock_repo.create_book.assert_called_once_with('Test Book', 'Test Author')
            assert result['title'] == 'Test Book'
            assert result['author'] == 'Test Author'

    def test_create_book_validation_error(self):
        """Test creating a book with invalid data"""
        service = BookService()

        with pytest.raises(ValueError, match="Title is required"):
            service.create_book('', 'Test Author')

        with pytest.raises(ValueError, match="Author is required"):
            service.create_book('Test Book', '')

    def test_update_book_success(self):
        """Test updating a book successfully"""
        with patch('services.book_service.BookRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.update_book.return_value = {
                'id': 1,
                'title': 'Updated Book',
                'author': 'Updated Author',
                'is_borrowed': False,
                'current_member_id': None,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            }

            service = BookService()
            result = service.update_book(1, 'Updated Book', 'Updated Author')

            mock_repo.update_book.assert_called_once_with(1, 'Updated Book', 'Updated Author')
            assert result['title'] == 'Updated Book'

    def test_update_book_not_found(self):
        """Test updating a non-existent book"""
        with patch('repositories.book_repository.BookRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.update_book.return_value = None

            service = BookService()
            result = service.update_book(999, 'Updated Book', 'Updated Author')

            assert result is None

    def test_list_books_paginated(self):
        """Test listing books with pagination"""
        with patch('services.book_service.BookRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.list_books_paginated.return_value = (
                [{'id': 1, 'title': 'Book 1'}],
                'cursor_2',
                False
            )

            service = BookService()
            books, next_cursor, has_more = service.list_books_paginated(
                limit=10, cursor='cursor_1', filter_type='all', search='test'
            )

            mock_repo.list_books_paginated.assert_called_once_with(
                10, 'cursor_1', 'all', 'test'
            )
            assert len(books) == 1
            assert next_cursor == 'cursor_2'
            assert has_more is False


class TestMemberService:
    """Unit tests for MemberService"""

    def test_create_member_success(self):
        """Test creating a member successfully"""
        with patch('services.member_service.MemberRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.create_member.return_value = {
                'id': 1,
                'name': 'John Doe',
                'email': 'john@example.com',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            }

            service = MemberService()
            result = service.create_member('John Doe', 'john@example.com')

            mock_repo.create_member.assert_called_once_with('John Doe', 'john@example.com')
            assert result['name'] == 'John Doe'
            assert result['email'] == 'john@example.com'

    def test_create_member_validation_error(self):
        """Test creating a member with invalid data"""
        service = MemberService()

        with pytest.raises(ValueError, match="Name is required"):
            service.create_member('', 'john@example.com')

        with pytest.raises(ValueError, match="Email is required"):
            service.create_member('John Doe', '')

        with pytest.raises(ValueError, match="Invalid email format"):
            service.create_member('John Doe', 'invalid-email')


class TestLibraryService:
    """Unit tests for LibraryService"""

    def test_borrow_book_success(self):
        """Test borrowing a book successfully"""
        with patch('services.library_service.BookRepository') as mock_book_repo_class, \
             patch('services.library_service.MemberRepository') as mock_member_repo_class, \
             patch('services.library_service.LedgerRepository') as mock_ledger_repo_class:

            mock_book_repo = Mock()
            mock_member_repo = Mock()
            mock_ledger_repo = Mock()

            mock_book_repo_class.return_value = mock_book_repo
            mock_member_repo_class.return_value = mock_member_repo
            mock_ledger_repo_class.return_value = mock_ledger_repo

            # Mock successful validations
            mock_book_repo.is_book_available.return_value = True
            mock_member_repo.member_exists.return_value = True

            # Mock borrow operation
            mock_book_repo.borrow_book.return_value = {'id': 1, 'title': 'Book'}

            # Mock ledger creation
            mock_ledger_repo.create_ledger_entry.return_value = {
                'id': 1,
                'book_id': 1,
                'member_id': 1,
                'action_type': 'BORROW',
                'log_date': '2024-01-01T00:00:00Z',
                'due_date_snapshot': '2024-01-01T00:00:00Z'
            }

            service = LibraryService()
            result = service.borrow_book(1, 1)

            mock_book_repo.is_book_available.assert_called_once_with(1)
            mock_member_repo.member_exists.assert_called_once_with(1)
            mock_book_repo.borrow_book.assert_called_once_with(1, 1)
            mock_ledger_repo.create_ledger_entry.assert_called_once()
            assert result['action_type'] == 'BORROW'

    def test_borrow_book_not_available(self):
        """Test borrowing a book that is not available"""
        with patch('services.library_service.BookRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.is_book_available.return_value = False

            service = LibraryService()

            with pytest.raises(ValueError, match="Book is not available"):
                service.borrow_book(1, 1)

    def test_borrow_book_member_not_found(self):
        """Test borrowing a book with non-existent member"""
        with patch('services.library_service.BookRepository') as mock_book_repo_class, \
             patch('services.library_service.MemberRepository') as mock_member_repo_class:

            mock_book_repo = Mock()
            mock_member_repo = Mock()

            mock_book_repo_class.return_value = mock_book_repo
            mock_member_repo_class.return_value = mock_member_repo

            mock_book_repo.is_book_available.return_value = True
            mock_member_repo.member_exists.return_value = False

            service = LibraryService()

            with pytest.raises(ValueError, match="Member not found"):
                service.borrow_book(1, 1)

    def test_return_book_success(self):
        """Test returning a book successfully"""
        with patch('services.library_service.BookRepository') as mock_book_repo_class, \
             patch('services.library_service.LedgerRepository') as mock_ledger_repo_class:

            mock_book_repo = Mock()
            mock_ledger_repo = Mock()

            mock_book_repo_class.return_value = mock_book_repo
            mock_ledger_repo_class.return_value = mock_ledger_repo

            # Mock successful validation
            mock_book_repo.is_book_borrowed_by_member.return_value = True

            # Mock return operation
            mock_book_repo.return_book.return_value = {'id': 1, 'title': 'Book'}

            # Mock ledger creation
            mock_ledger_repo.create_ledger_entry.return_value = {
                'id': 2,
                'book_id': 1,
                'member_id': 1,
                'action_type': 'RETURN',
                'log_date': '2024-01-01T00:00:00Z',
                'due_date_snapshot': None
            }

            service = LibraryService()
            result = service.return_book(1, 1)

            mock_book_repo.is_book_borrowed_by_member.assert_called_once_with(1, 1)
            mock_book_repo.return_book.assert_called_once_with(1, 1)
            mock_ledger_repo.create_ledger_entry.assert_called_once()
            assert result['action_type'] == 'RETURN'

    def test_return_book_not_borrowed_by_member(self):
        """Test returning a book not borrowed by the member"""
        with patch('repositories.book_repository.BookRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.is_book_borrowed_by_member.return_value = False

            service = LibraryService()

            with pytest.raises(ValueError, match="Book is not borrowed by this member"):
                service.return_book(1, 1)