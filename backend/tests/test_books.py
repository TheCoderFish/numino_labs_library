import pytest
from server import LibraryService
import book_pb2
import grpc

class MockContext:
    def __init__(self):
        self.code = None
        self.details = None

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details

class TestBooks:
    def test_create_book_success(self, clean_database):
        """Test creating a book successfully"""
        service = LibraryService()
        request = book_pb2.CreateBookRequest(title="Test Book", author="Test Author")
        context = MockContext()

        response = service.CreateBook(request, context)

        assert response.message == "Book created successfully"
        assert response.book.title == "Test Book"
        assert response.book.author == "Test Author"
        assert not response.book.is_borrowed
        assert response.book.current_member_id == 0

    def test_update_book_success(self, clean_database):
        """Test updating a book successfully"""
        service = LibraryService()

        # Create a book first
        create_request = book_pb2.CreateBookRequest(title="Original Title", author="Original Author")
        create_context = MockContext()
        create_response = service.CreateBook(create_request, create_context)
        book_id = create_response.book.id

        # Update the book
        update_request = book_pb2.UpdateBookRequest(id=book_id, title="Updated Title", author="Updated Author")
        update_context = MockContext()
        update_response = service.UpdateBook(update_request, update_context)

        assert update_response.message == "Book updated successfully"
        assert update_response.book.title == "Updated Title"
        assert update_response.book.author == "Updated Author"

    def test_update_book_not_found(self, clean_database):
        """Test updating a non-existent book"""
        service = LibraryService()
        request = book_pb2.UpdateBookRequest(id=999, title="Test", author="Test")
        context = MockContext()

        response = service.UpdateBook(request, context)

        assert context.code == grpc.StatusCode.NOT_FOUND

    def test_list_books(self, clean_database):
        """Test listing books"""
        service = LibraryService()

        # Create some books
        books_data = [
            ("Book 1", "Author 1"),
            ("Book 2", "Author 2"),
        ]

        for title, author in books_data:
            request = book_pb2.CreateBookRequest(title=title, author=author)
            context = MockContext()
            service.CreateBook(request, context)

        # List books
        list_request = book_pb2.ListBooksRequest()
        list_context = MockContext()
        list_response = service.ListBooks(list_request, list_context)

        assert len(list_response.books) == 2
        titles = [book.title for book in list_response.books]
        assert "Book 1" in titles
        assert "Book 2" in titles

    def test_search_books(self, clean_database):
        """Test searching books"""
        service = LibraryService()

        # Create some books
        books_data = [
            ("Python Guide", "John Doe"),
            ("JavaScript Basics", "Jane Smith"),
            ("Advanced Python", "John Doe"),
        ]

        for title, author in books_data:
            request = book_pb2.CreateBookRequest(title=title, author=author)
            context = MockContext()
            service.CreateBook(request, context)

        # Search for Python books
        search_request = book_pb2.SearchBooksRequest(query="Python")
        search_context = MockContext()
        search_response = service.SearchBooks(search_request, search_context)

        assert len(search_response.books) == 2
        titles = [book.title for book in search_response.books]
        assert "Python Guide" in titles
        assert "Advanced Python" in titles