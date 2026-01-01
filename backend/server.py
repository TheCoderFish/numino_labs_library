import json
from concurrent import futures
from datetime import datetime

import grpc
from dotenv import load_dotenv
from google.protobuf.json_format import ParseDict
from google.protobuf.timestamp_pb2 import Timestamp

import book_pb2
import ledger_pb2
import library_pb2_grpc
import member_pb2
from db_helper import DatabaseHelper, Book, Member
from error_codes import ErrorCodes
from messages import Messages

load_dotenv()


class LibraryService(library_pb2_grpc.LibraryServiceServicer):

    def CreateBook(self, request, context):
        """Create a new book"""
        try:
            Book.validate_data(request.title, request.author)
            result = DatabaseHelper.create_book(request.title, request.author)
            book = book_pb2.Book()
            ParseDict(result, book, ignore_unknown_fields=True)
            return book_pb2.CreateBookResponse(book=book, message=Messages.BOOK_CREATED)
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": str(e)}))
            return book_pb2.CreateBookResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
            return book_pb2.CreateBookResponse()

    def UpdateBook(self, request, context):
        """Update an existing book"""
        try:
            Book.validate_data(request.title, request.author)
            result = DatabaseHelper.update_book(request.id, request.title, request.author)
            if not result:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(json.dumps({"code": ErrorCodes.BOOK_NOT_FOUND, "message": "Book not found"}))
                return book_pb2.UpdateBookResponse()
            book = book_pb2.Book()
            ParseDict(result, book, ignore_unknown_fields=True)
            return book_pb2.UpdateBookResponse(book=book, message=Messages.BOOK_UPDATED)
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": str(e)}))
            return book_pb2.UpdateBookResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
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
            Member.validate_data(request.name, request.email)
            result = DatabaseHelper.create_member(request.name, request.email)
            member = member_pb2.Member()
            ParseDict(result, member, ignore_unknown_fields=True)
            return member_pb2.CreateMemberResponse(member=member, message=Messages.MEMBER_CREATED)
        except ValueError as e:
            if "Email already exists" in str(e):
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(json.dumps({"code": ErrorCodes.EMAIL_ALREADY_EXISTS, "message": str(e)}))
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": str(e)}))
            return member_pb2.CreateMemberResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
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
            Member.validate_data(request.name, request.email)
            result = DatabaseHelper.update_member(request.id, request.name, request.email)
            if not result:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(json.dumps({"code": ErrorCodes.MEMBER_NOT_FOUND, "message": "Member not found"}))
                return member_pb2.UpdateMemberResponse()
            member = member_pb2.Member()
            ParseDict(result, member, ignore_unknown_fields=True)
            return member_pb2.UpdateMemberResponse(member=member, message=Messages.MEMBER_UPDATED)
        except ValueError as e:
            if "Email already exists" in str(e):
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(json.dumps({"code": ErrorCodes.EMAIL_ALREADY_EXISTS, "message": str(e)}))
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": str(e)}))
            return member_pb2.UpdateMemberResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
            return member_pb2.UpdateMemberResponse()

    def BorrowBook(self, request, context):
        """Borrow a book"""
        try:
            # Business logic validations
            if not DatabaseHelper.is_book_available(request.book_id):
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(
                    json.dumps({"code": ErrorCodes.BOOK_ALREADY_BORROWED, "message": "Book is not available"}))
                return ledger_pb2.BorrowBookResponse()
            if not DatabaseHelper.member_exists(request.member_id):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(json.dumps({"code": ErrorCodes.MEMBER_NOT_FOUND, "message": "Member not found"}))
                return ledger_pb2.BorrowBookResponse()

            # Borrow the book using DatabaseHelper
            result = DatabaseHelper.borrow_book(request.book_id, request.member_id)

            # Convert result to protobuf format
            ledger_entry = ledger_pb2.LedgerEntry()
            ledger_entry.id = result['id']
            ledger_entry.book_id = result['book_id']
            ledger_entry.member_id = result['member_id']
            ledger_entry.action_type = ledger_pb2.ActionType.BORROW if result['action_type'] == 'BORROW' else ledger_pb2.ActionType.RETURN

            log_date_ts = Timestamp()
            log_date = datetime.fromisoformat(result['log_date'].replace('Z', '+00:00'))
            log_date_ts.FromDatetime(log_date)
            ledger_entry.log_date.CopyFrom(log_date_ts)

            due_date_ts = Timestamp()
            due_date = datetime.fromisoformat(result['due_date_snapshot'].replace('Z', '+00:00'))
            due_date_ts.FromDatetime(due_date)
            ledger_entry.due_date_snapshot.CopyFrom(due_date_ts)

            return ledger_pb2.BorrowBookResponse(
                success=True,
                ledger_entry=ledger_entry,
                message=Messages.BOOK_BORROWED
            )
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": str(e)}))
            return ledger_pb2.BorrowBookResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
            return ledger_pb2.BorrowBookResponse()

    def ReturnBook(self, request, context):
        """Return a book"""
        try:
            # Business logic validations
            if not DatabaseHelper.is_book_borrowed_by_member(request.book_id, request.member_id):
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(json.dumps(
                    {"code": ErrorCodes.BOOK_NOT_BORROWED_BY_MEMBER, "message": "Book is not borrowed by this member"}))
                return ledger_pb2.ReturnBookResponse()

            # Return the book using DatabaseHelper
            result = DatabaseHelper.return_book(request.book_id, request.member_id)

            # Convert result to protobuf format
            ledger_entry = ledger_pb2.LedgerEntry()
            ledger_entry.id = result['id']
            ledger_entry.book_id = result['book_id']
            ledger_entry.member_id = result['member_id']
            ledger_entry.action_type = ledger_pb2.ActionType.RETURN

            log_date_ts = Timestamp()
            log_date = datetime.fromisoformat(result['log_date'].replace('Z', '+00:00'))
            log_date_ts.FromDatetime(log_date)
            ledger_entry.log_date.CopyFrom(log_date_ts)

            if result['due_date_snapshot'] is not None:
                due_date_ts = Timestamp()
                due_date = datetime.fromisoformat(result['due_date_snapshot'].replace('Z', '+00:00'))
                due_date_ts.FromDatetime(due_date)
                ledger_entry.due_date_snapshot.CopyFrom(due_date_ts)

            return ledger_pb2.ReturnBookResponse(
                success=True,
                ledger_entry=ledger_entry,
                message=Messages.BOOK_RETURNED
            )
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": str(e)}))
            return ledger_pb2.ReturnBookResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
            return ledger_pb2.ReturnBookResponse()

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
