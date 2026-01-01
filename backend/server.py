import os
import grpc
from concurrent import futures
import psycopg2
from psycopg2 import IntegrityError
from datetime import datetime, date
from dotenv import load_dotenv
import book_pb2
import member_pb2
import ledger_pb2
import library_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.json_format import ParseDict
from db_helper import DatabaseHelper
from messages import Messages
from business_logic import BusinessLogic

load_dotenv()

class LibraryService(library_pb2_grpc.LibraryServiceServicer):
    
    def CreateBook(self, request, context):
        """Create a new book"""
        try:
            BusinessLogic.validate_book_data(request.title, request.author)
            result = DatabaseHelper.create_book(request.title, request.author)
            book = book_pb2.Book()
            ParseDict(result, book, ignore_unknown_fields=True)
            return book_pb2.CreateBookResponse(book=book, message=Messages.BOOK_CREATED)
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return book_pb2.CreateBookResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return book_pb2.CreateBookResponse()
    
    def UpdateBook(self, request, context):
        """Update an existing book"""
        try:
            BusinessLogic.validate_book_data(request.title, request.author)
            result = DatabaseHelper.update_book(request.id, request.title, request.author)
            if not result:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Book not found")
                return book_pb2.UpdateBookResponse()
            book = book_pb2.Book()
            ParseDict(result, book, ignore_unknown_fields=True)
            return book_pb2.UpdateBookResponse(book=book, message=Messages.BOOK_UPDATED)
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return book_pb2.UpdateBookResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return book_pb2.UpdateBookResponse()
    
    def ListBooks(self, request, context):
        """List all books with member name"""
        try:
            results = DatabaseHelper.list_books()
            books = []
            for row in results:
                book = book_pb2.Book()
                ParseDict(row, book, ignore_unknown_fields=True)
                books.append(book)
            return book_pb2.ListBooksResponse(books=books)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return book_pb2.ListBooksResponse()
    
    def SearchBooks(self, request, context):
        """Search books by title or author"""
        try:
            results = DatabaseHelper.search_books(request.query)
            books = []
            for row in results:
                book = book_pb2.Book()
                ParseDict(row, book, ignore_unknown_fields=True)
                books.append(book)
            return book_pb2.SearchBooksResponse(books=books)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return book_pb2.SearchBooksResponse()
    
    def CreateMember(self, request, context):
        """Create a new member"""
        try:
            BusinessLogic.validate_member_data(request.name, request.email)
            result = DatabaseHelper.create_member(request.name, request.email)
            member = member_pb2.Member()
            ParseDict(result, member, ignore_unknown_fields=True)
            return member_pb2.CreateMemberResponse(member=member, message=Messages.MEMBER_CREATED)
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return member_pb2.CreateMemberResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return member_pb2.CreateMemberResponse()
    
    def ListMembers(self, request, context):
        """List all members"""
        try:
            results = DatabaseHelper.list_members()
            members = []
            for row in results:
                member = member_pb2.Member()
                ParseDict(row, member, ignore_unknown_fields=True)
                members.append(member)
            return member_pb2.ListMembersResponse(members=members)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return member_pb2.ListMembersResponse()
    
    def SearchMembers(self, request, context):
        """Search members by name or email"""
        try:
            results = DatabaseHelper.search_members(request.query)
            members = []
            for row in results:
                member = member_pb2.Member()
                ParseDict(row, member, ignore_unknown_fields=True)
                members.append(member)
            return member_pb2.SearchMembersResponse(members=members)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return member_pb2.SearchMembersResponse()
    
    def UpdateMember(self, request, context):
        """Update an existing member"""
        try:
            BusinessLogic.validate_member_data(request.name, request.email)
            result = DatabaseHelper.update_member(request.id, request.name, request.email)
            if not result:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Member not found")
                return member_pb2.UpdateMemberResponse()
            member = member_pb2.Member()
            ParseDict(result, member, ignore_unknown_fields=True)
            return member_pb2.UpdateMemberResponse(member=member, message=Messages.MEMBER_UPDATED)
        except ValueError as e:
            if "Email already exists" in str(e):
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return member_pb2.UpdateMemberResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return member_pb2.UpdateMemberResponse()
    
    def BorrowBook(self, request, context):
        """Borrow a book with transaction and locking"""
        # Business logic validations
        if not BusinessLogic.is_book_available(request.book_id):
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details("Book is not available")
            return ledger_pb2.BorrowBookResponse()
        if not BusinessLogic.member_exists(request.member_id):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Member not found")
            return ledger_pb2.BorrowBookResponse()
        
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Start transaction
                conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
                
                # Lock the book row for update to prevent concurrent modifications
                cur.execute(
                    "SELECT id, title, author, is_borrowed, current_member_id FROM book WHERE id = %s FOR UPDATE",
                    (request.book_id,)
                )
                book = cur.fetchone()
                
                if not book:
                    conn.rollback()
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Book not found")
                    return ledger_pb2.BorrowBookResponse()
                
                if book['is_borrowed']:
                    conn.rollback()
                    context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                    context.set_details("Book is already borrowed")
                    return ledger_pb2.BorrowBookResponse()
                
                # Verify member exists
                cur.execute("SELECT id FROM member WHERE id = %s", (request.member_id,))
                member = cur.fetchone()
                if not member:
                    conn.rollback()
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Member not found")
                    return ledger_pb2.BorrowBookResponse()
                
                # Update book status
                cur.execute(
                    "UPDATE book SET is_borrowed = TRUE, current_member_id = %s WHERE id = %s",
                    (request.member_id, request.book_id)
                )
                
                # Create ledger entry
                due_date = date.today()  # You can add logic for due date calculation
                cur.execute(
                    "INSERT INTO ledger (book_id, member_id, action_type, due_date_snapshot) VALUES (%s, %s, 'BORROW', %s) RETURNING id, book_id, member_id, action_type, log_date, due_date_snapshot",
                    (request.book_id, request.member_id, due_date)
                )
                ledger_entry = cur.fetchone()
                
                conn.commit()
                
                # Convert dates to Timestamp
                log_date_ts = Timestamp()
                if ledger_entry['log_date']:
                    log_date_ts.FromDatetime(ledger_entry['log_date'])
                
                due_date_ts = Timestamp()
                if ledger_entry['due_date_snapshot']:
                    due_date_ts.FromDatetime(datetime.combine(ledger_entry['due_date_snapshot'], datetime.min.time()))
                
                action_type_enum = ledger_pb2.ActionType.BORROW if ledger_entry['action_type'] == 'BORROW' else ledger_pb2.ActionType.RETURN
                
                ledger = ledger_pb2.LedgerEntry(
                    id=ledger_entry['id'],
                    book_id=ledger_entry['book_id'],
                    member_id=ledger_entry['member_id'],
                    action_type=action_type_enum,
                    log_date=log_date_ts,
                    due_date_snapshot=due_date_ts
                )
                
                return ledger_pb2.BorrowBookResponse(
                    success=True,
                    message="Book borrowed successfully",
                    ledger_entry=ledger
                )
        except Exception as e:
            conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ledger_pb2.BorrowBookResponse()
        finally:
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)
            return_db_connection(conn)
    
    def ReturnBook(self, request, context):
        """Return a book with transaction and locking"""
        # Business logic validations
        if not BusinessLogic.is_book_borrowed_by_member(request.book_id, request.member_id):
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details("Book is not borrowed by this member")
            return ledger_pb2.ReturnBookResponse()
        
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Start transaction
                conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
                
                # Lock the book row for update
                cur.execute(
                    "SELECT id, title, author, is_borrowed, current_member_id FROM book WHERE id = %s FOR UPDATE",
                    (request.book_id,)
                )
                book = cur.fetchone()
                
                if not book:
                    conn.rollback()
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Book not found")
                    return ledger_pb2.ReturnBookResponse()
                
                if not book['is_borrowed']:
                    conn.rollback()
                    context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                    context.set_details("Book is not currently borrowed")
                    return ledger_pb2.ReturnBookResponse()
                
                if book['current_member_id'] != request.member_id:
                    conn.rollback()
                    context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                    context.set_details("This member did not borrow this book")
                    return ledger_pb2.ReturnBookResponse()
                
                # Update book status
                cur.execute(
                    "UPDATE book SET is_borrowed = FALSE, current_member_id = NULL WHERE id = %s",
                    (request.book_id,)
                )
                
                # Create ledger entry
                cur.execute(
                    "INSERT INTO ledger (book_id, member_id, action_type, due_date_snapshot) VALUES (%s, %s, 'RETURN', NULL) RETURNING id, book_id, member_id, action_type, log_date, due_date_snapshot",
                    (request.book_id, request.member_id)
                )
                ledger_entry = cur.fetchone()
                
                conn.commit()
                
                # Convert dates to Timestamp
                log_date_ts = Timestamp()
                if ledger_entry['log_date']:
                    log_date_ts.FromDatetime(ledger_entry['log_date'])
                
                due_date_ts = Timestamp()  # Empty for return
                
                action_type_enum = ledger_pb2.ActionType.RETURN
                
                ledger = ledger_pb2.LedgerEntry(
                    id=ledger_entry['id'],
                    book_id=ledger_entry['book_id'],
                    member_id=ledger_entry['member_id'],
                    action_type=action_type_enum,
                    log_date=log_date_ts,
                    due_date_snapshot=due_date_ts
                )
                
                return ledger_pb2.ReturnBookResponse(
                    success=True,
                    message="Book returned successfully",
                    ledger_entry=ledger
                )
        except Exception as e:
            conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ledger_pb2.ReturnBookResponse()
        finally:
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)
            return_db_connection(conn)
    
    def ListBorrowedBooks(self, request, context):
        """List all books borrowed by a member"""
        try:
            results = DatabaseHelper.list_borrowed_books(request.member_id)
            books = []
            for row in results:
                book = book_pb2.Book()
                ParseDict(row, book, ignore_unknown_fields=True)
                books.append(book)
            return ledger_pb2.ListBorrowedBooksResponse(books=books)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ledger_pb2.ListBorrowedBooksResponse()


def serve():
    """Start the gRPC server"""
    # Create tables if not exist
    from db_helper import engine, Base
    Base.metadata.create_all(bind=engine)
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    library_pb2_grpc.add_LibraryServiceServicer_to_server(LibraryService(), server)
    
    port = '50051'
    server.add_insecure_port('[::]:' + port)
    server.start()
    print(f"Server started, listening on port {port}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()

