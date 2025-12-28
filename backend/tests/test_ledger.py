import pytest
from server import LibraryService
from psycopg2.extras import RealDictCursor
import book_pb2
import member_pb2
import ledger_pb2
import grpc

class MockContext:
    def __init__(self):
        self.code = None
        self.details = None

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details

class TestLedger:
    def test_borrow_book_success(self, clean_database, db_connection):
        """Test borrowing a book successfully"""
        service = LibraryService()

        # Create a book
        book_request = book_pb2.CreateBookRequest(title="Test Book", author="Test Author")
        book_context = MockContext()
        book_response = service.CreateBook(book_request, book_context)
        book_id = book_response.book.id

        # Create a member
        member_request = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        member_context = MockContext()
        member_response = service.CreateMember(member_request, member_context)
        member_id = member_response.member.id

        # Borrow the book
        borrow_request = ledger_pb2.BorrowBookRequest(book_id=book_id, member_id=member_id)
        borrow_context = MockContext()
        borrow_response = service.BorrowBook(borrow_request, borrow_context)

        assert borrow_response.success
        assert borrow_response.message == "Book borrowed successfully"
        assert borrow_response.ledger_entry.book_id == book_id
        assert borrow_response.ledger_entry.member_id == member_id

    def test_borrow_book_not_found(self, clean_database):
        """Test borrowing a non-existent book"""
        service = LibraryService()
        request = ledger_pb2.BorrowBookRequest(book_id=999, member_id=1)
        context = MockContext()

        response = service.BorrowBook(request, context)

        assert context.code == grpc.StatusCode.NOT_FOUND

    def test_borrow_member_not_found(self, clean_database, db_connection):
        """Test borrowing with non-existent member"""
        service = LibraryService()

        # Create a book
        book_request = book_pb2.CreateBookRequest(title="Test Book", author="Test Author")
        book_context = MockContext()
        book_response = service.CreateBook(book_request, book_context)
        book_id = book_response.book.id

        # Try to borrow with non-existent member
        borrow_request = ledger_pb2.BorrowBookRequest(book_id=book_id, member_id=999)
        borrow_context = MockContext()
        borrow_response = service.BorrowBook(borrow_request, borrow_context)

        assert borrow_context.code == grpc.StatusCode.NOT_FOUND

    def test_borrow_already_borrowed(self, clean_database, db_connection):
        """Test borrowing an already borrowed book"""
        service = LibraryService()

        # Create a book
        book_request = book_pb2.CreateBookRequest(title="Test Book", author="Test Author")
        book_context = MockContext()
        book_response = service.CreateBook(book_request, book_context)
        book_id = book_response.book.id

        # Create two members
        member1_request = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        member1_context = MockContext()
        member1_response = service.CreateMember(member1_request, member1_context)
        member1_id = member1_response.member.id

        member2_request = member_pb2.CreateMemberRequest(name="Jane Doe", email="jane@example.com")
        member2_context = MockContext()
        member2_response = service.CreateMember(member2_request, member2_context)
        member2_id = member2_response.member.id

        # First borrow
        borrow1_request = ledger_pb2.BorrowBookRequest(book_id=book_id, member_id=member1_id)
        borrow1_context = MockContext()
        service.BorrowBook(borrow1_request, borrow1_context)

        # Try to borrow again
        borrow2_request = ledger_pb2.BorrowBookRequest(book_id=book_id, member_id=member2_id)
        borrow2_context = MockContext()
        borrow2_response = service.BorrowBook(borrow2_request, borrow2_context)

        assert borrow2_context.code == grpc.StatusCode.FAILED_PRECONDITION

    def test_double_borrow_same_member(self, clean_database, db_connection):
        """Test same member trying to borrow same book twice"""
        service = LibraryService()

        # Create a book
        book_request = book_pb2.CreateBookRequest(title="Test Book", author="Test Author")
        book_context = MockContext()
        book_response = service.CreateBook(book_request, book_context)
        book_id = book_response.book.id

        # Create a member
        member_request = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        member_context = MockContext()
        member_response = service.CreateMember(member_request, member_context)
        member_id = member_response.member.id

        # First borrow
        borrow1_request = ledger_pb2.BorrowBookRequest(book_id=book_id, member_id=member_id)
        borrow1_context = MockContext()
        service.BorrowBook(borrow1_request, borrow1_context)

        # Try to borrow again with same member
        borrow2_request = ledger_pb2.BorrowBookRequest(book_id=book_id, member_id=member_id)
        borrow2_context = MockContext()
        borrow2_response = service.BorrowBook(borrow2_request, borrow2_context)

        assert borrow2_context.code == grpc.StatusCode.FAILED_PRECONDITION

    def test_return_book_success(self, clean_database, db_connection):
        """Test returning a book successfully"""
        service = LibraryService()

        # Create a book
        book_request = book_pb2.CreateBookRequest(title="Test Book", author="Test Author")
        book_context = MockContext()
        book_response = service.CreateBook(book_request, book_context)
        book_id = book_response.book.id

        # Create a member
        member_request = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        member_context = MockContext()
        member_response = service.CreateMember(member_request, member_context)
        member_id = member_response.member.id

        # Borrow the book
        borrow_request = ledger_pb2.BorrowBookRequest(book_id=book_id, member_id=member_id)
        borrow_context = MockContext()
        service.BorrowBook(borrow_request, borrow_context)

        # Return the book
        return_request = ledger_pb2.ReturnBookRequest(book_id=book_id, member_id=member_id)
        return_context = MockContext()
        return_response = service.ReturnBook(return_request, return_context)

        assert return_response.success
        assert return_response.message == "Book returned successfully"
        assert return_response.ledger_entry.book_id == book_id
        assert return_response.ledger_entry.member_id == member_id

    def test_return_book_not_borrowed(self, clean_database, db_connection):
        """Test returning a book that is not borrowed"""
        service = LibraryService()

        # Create a book
        book_request = book_pb2.CreateBookRequest(title="Test Book", author="Test Author")
        book_context = MockContext()
        book_response = service.CreateBook(book_request, book_context)
        book_id = book_response.book.id

        # Create a member
        member_request = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        member_context = MockContext()
        member_response = service.CreateMember(member_request, member_context)
        member_id = member_response.member.id

        # Try to return without borrowing
        return_request = ledger_pb2.ReturnBookRequest(book_id=book_id, member_id=member_id)
        return_context = MockContext()
        return_response = service.ReturnBook(return_request, return_context)

        assert return_context.code == grpc.StatusCode.FAILED_PRECONDITION

    def test_return_wrong_member(self, clean_database, db_connection):
        """Test returning a book by wrong member"""
        service = LibraryService()

        # Create a book
        book_request = book_pb2.CreateBookRequest(title="Test Book", author="Test Author")
        book_context = MockContext()
        book_response = service.CreateBook(book_request, book_context)
        book_id = book_response.book.id

        # Create two members
        member1_request = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        member1_context = MockContext()
        member1_response = service.CreateMember(member1_request, member1_context)
        member1_id = member1_response.member.id

        member2_request = member_pb2.CreateMemberRequest(name="Jane Doe", email="jane@example.com")
        member2_context = MockContext()
        member2_response = service.CreateMember(member2_request, member2_context)
        member2_id = member2_response.member.id

        # Borrow with member1
        borrow_request = ledger_pb2.BorrowBookRequest(book_id=book_id, member_id=member1_id)
        borrow_context = MockContext()
        service.BorrowBook(borrow_request, borrow_context)

        # Try to return with member2
        return_request = ledger_pb2.ReturnBookRequest(book_id=book_id, member_id=member2_id)
        return_context = MockContext()
        return_response = service.ReturnBook(return_request, return_context)

        assert return_context.code == grpc.StatusCode.PERMISSION_DENIED

    def test_double_return(self, clean_database, db_connection):
        """Test returning the same book twice"""
        service = LibraryService()

        # Create a book
        book_request = book_pb2.CreateBookRequest(title="Test Book", author="Test Author")
        book_context = MockContext()
        book_response = service.CreateBook(book_request, book_context)
        book_id = book_response.book.id

        # Create a member
        member_request = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        member_context = MockContext()
        member_response = service.CreateMember(member_request, member_context)
        member_id = member_response.member.id

        # Borrow the book
        borrow_request = ledger_pb2.BorrowBookRequest(book_id=book_id, member_id=member_id)
        borrow_context = MockContext()
        service.BorrowBook(borrow_request, borrow_context)

        # Return the book first time
        return1_request = ledger_pb2.ReturnBookRequest(book_id=book_id, member_id=member_id)
        return1_context = MockContext()
        service.ReturnBook(return1_request, return1_context)

        # Try to return again
        return2_request = ledger_pb2.ReturnBookRequest(book_id=book_id, member_id=member_id)
        return2_context = MockContext()
        return2_response = service.ReturnBook(return2_request, return2_context)

        assert return2_context.code == grpc.StatusCode.FAILED_PRECONDITION

    def test_list_borrowed_books(self, clean_database, db_connection):
        """Test listing borrowed books for a member"""
        service = LibraryService()

        # Create two books
        book1_request = book_pb2.CreateBookRequest(title="Book 1", author="Author 1")
        book1_context = MockContext()
        book1_response = service.CreateBook(book1_request, book1_context)
        book1_id = book1_response.book.id

        book2_request = book_pb2.CreateBookRequest(title="Book 2", author="Author 2")
        book2_context = MockContext()
        book2_response = service.CreateBook(book2_request, book2_context)
        book2_id = book2_response.book.id

        # Create a member
        member_request = member_pb2.CreateMemberRequest(name="John Doe", email="john@example.com")
        member_context = MockContext()
        member_response = service.CreateMember(member_request, member_context)
        member_id = member_response.member.id

        # Borrow both books
        borrow1_request = ledger_pb2.BorrowBookRequest(book_id=book1_id, member_id=member_id)
        borrow1_context = MockContext()
        service.BorrowBook(borrow1_request, borrow1_context)

        borrow2_request = ledger_pb2.BorrowBookRequest(book_id=book2_id, member_id=member_id)
        borrow2_context = MockContext()
        service.BorrowBook(borrow2_request, borrow2_context)

        # List borrowed books
        list_request = ledger_pb2.ListBorrowedBooksRequest(member_id=member_id)
        list_context = MockContext()
        list_response = service.ListBorrowedBooks(list_request, list_context)

        assert len(list_response.books) == 2
        titles = [book.title for book in list_response.books]
        assert "Book 1" in titles
        assert "Book 2" in titles