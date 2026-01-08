import pytest
from server import LibraryGrpcService
import book_pb2
import member_pb2
import ledger_pb2
import grpc
import threading

class MockContext:
    def __init__(self):
        self.code = None
        self.details = None

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details

class TestLedger:
    def test_borrow_book_success(self, clean_database):
        """Test borrowing a book successfully"""
        service = LibraryGrpcService()

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
        service = LibraryGrpcService()
        request = ledger_pb2.BorrowBookRequest(book_id=999, member_id=1)
        context = MockContext()

        response = service.BorrowBook(request, context)

        # Note: Server returns FAILED_PRECONDITION because is_book_available 
        # returns False for non-existent books (book is None)
        assert context.code == grpc.StatusCode.FAILED_PRECONDITION

    def test_borrow_member_not_found(self, clean_database):
        """Test borrowing with non-existent member"""
        service = LibraryGrpcService()

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

    def test_borrow_already_borrowed(self, clean_database):
        """Test borrowing an already borrowed book"""
        service = LibraryGrpcService()

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

    def test_double_borrow_same_member(self, clean_database):
        """Test same member trying to borrow same book twice"""
        service = LibraryGrpcService()

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

    def test_return_book_success(self, clean_database):
        """Test returning a book successfully"""
        service = LibraryGrpcService()

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

    def test_return_book_not_borrowed(self, clean_database):
        """Test returning a book that is not borrowed"""
        service = LibraryGrpcService()

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

    def test_return_wrong_member(self, clean_database):
        """Test returning a book by wrong member"""
        service = LibraryGrpcService()

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

        assert return_context.code == grpc.StatusCode.FAILED_PRECONDITION

    def test_double_return(self, clean_database):
        """Test returning the same book twice"""
        service = LibraryGrpcService()

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

    def test_list_borrowed_books(self, clean_database):
        """Test listing borrowed books for a member"""
        service = LibraryGrpcService()

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

    def test_concurrent_borrow_same_book_different_members(self, clean_database):
        """Test concurrent borrows of the same book by different members - only one should succeed"""
        service = LibraryGrpcService()

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

        # Results storage for concurrent operations
        results = []
        errors = []

        def borrow_book_thread(member_id, thread_id):
            """Thread function to borrow book"""
            try:
                borrow_request = ledger_pb2.BorrowBookRequest(book_id=book_id, member_id=member_id)
                borrow_context = MockContext()
                borrow_response = service.BorrowBook(borrow_request, borrow_context)
                results.append({
                    'thread_id': thread_id,
                    'member_id': member_id,
                    'success': borrow_response.success,
                    'error_code': borrow_context.code
                })
            except Exception as e:
                errors.append({'thread_id': thread_id, 'error': str(e)})

        # Start two threads trying to borrow the same book simultaneously
        thread1 = threading.Thread(target=borrow_book_thread, args=(member1_id, 1))
        thread2 = threading.Thread(target=borrow_book_thread, args=(member2_id, 2))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Verify only one borrow succeeded
        successful_borrows = [r for r in results if r['success']]
        failed_borrows = [r for r in results if not r['success'] and r['error_code'] == grpc.StatusCode.FAILED_PRECONDITION]

        assert len(successful_borrows) == 1, "Only one borrow should succeed"
        assert len(failed_borrows) == 1, "One borrow should fail with FAILED_PRECONDITION"
        assert len(results) == 2, "Both threads should complete"

    def test_concurrent_return_same_book(self, clean_database):
        """Test concurrent returns of the same book - only one should succeed"""
        service = LibraryGrpcService()

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

        # Borrow the book first
        borrow_request = ledger_pb2.BorrowBookRequest(book_id=book_id, member_id=member_id)
        borrow_context = MockContext()
        service.BorrowBook(borrow_request, borrow_context)

        # Results storage for concurrent operations
        results = []

        def return_book_thread(thread_id):
            """Thread function to return book"""
            try:
                return_request = ledger_pb2.ReturnBookRequest(book_id=book_id, member_id=member_id)
                return_context = MockContext()
                return_response = service.ReturnBook(return_request, return_context)
                results.append({
                    'thread_id': thread_id,
                    'success': return_response.success,
                    'error_code': return_context.code
                })
            except Exception as e:
                results.append({
                    'thread_id': thread_id,
                    'success': False,
                    'error': str(e)
                })

        # Start two threads trying to return the same book simultaneously
        thread1 = threading.Thread(target=return_book_thread, args=(1,))
        thread2 = threading.Thread(target=return_book_thread, args=(2,))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Verify only one return succeeded
        successful_returns = [r for r in results if r.get('success', False)]
        failed_returns = [r for r in results if not r.get('success', False) and r.get('error_code') == grpc.StatusCode.FAILED_PRECONDITION]

        assert len(successful_returns) == 1, "Only one return should succeed"
        assert len(failed_returns) == 1, "One return should fail with FAILED_PRECONDITION"
        assert len(results) == 2, "Both threads should complete"