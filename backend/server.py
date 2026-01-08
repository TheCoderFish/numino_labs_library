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
from services import BookService, MemberService, LibraryService
from error_codes import ErrorCodes
from messages import Messages
from logger import logger
from config import Config

load_dotenv()


class LibraryGrpcService(library_pb2_grpc.LibraryServiceServicer):

    def __init__(self):
        self._book_service = BookService()
        self._member_service = MemberService()
        self._library_service = LibraryService()

    def CreateBook(self, request, context):
        """Create a new book"""
        logger.info(f"CreateBook operation started for title: {request.title}, author: {request.author}")
        try:
            result = self._book_service.create_book(request.title, request.author)
            book = book_pb2.Book()
            ParseDict(result, book, ignore_unknown_fields=True)
            logger.info(f"CreateBook operation successful for book ID: {book.id}")
            return book_pb2.CreateBookResponse(book=book, message=Messages.BOOK_CREATED)
        except ValueError as e:
            logger.warning(f"CreateBook validation error: {str(e)}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": str(e)}))
            return book_pb2.CreateBookResponse()
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} CreateBook operation failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
            return book_pb2.CreateBookResponse()

    def UpdateBook(self, request, context):
        """Update an existing book"""
        try:
            result = self._book_service.update_book(request.id, request.title, request.author)
            if not result:
                logger.warning(f"UpdateBook: Book not found for ID: {request.id}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(json.dumps({"code": ErrorCodes.BOOK_NOT_FOUND, "message": "Book not found"}))
                return book_pb2.UpdateBookResponse()
            book = book_pb2.Book()
            ParseDict(result, book, ignore_unknown_fields=True)
            logger.info(f"UpdateBook operation successful for book ID: {book.id}")
            return book_pb2.UpdateBookResponse(book=book, message=Messages.BOOK_UPDATED)
        except ValueError as e:
            logger.warning(f"UpdateBook validation error: {str(e)}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": str(e)}))
            return book_pb2.UpdateBookResponse()
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} UpdateBook operation failed for ID {request.id}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
            return book_pb2.UpdateBookResponse()

    def ListBooks(self, request, context):
        """List books with pagination and filters"""
        logger.info(f"ListBooks operation started with limit: {request.limit}, cursor: {request.cursor}, filter: {request.filter}, search: {request.search}")
        try:
            limit = request.limit if request.limit > 0 else 20
            books, next_cursor, has_more = self._book_service.list_books_paginated(
                limit=limit,
                cursor=request.cursor,
                filter_type=request.filter,
                search=request.search
            )
            books_proto = []
            for row in books:
                book = book_pb2.Book()
                ParseDict(row, book, ignore_unknown_fields=True)
                books_proto.append(book)
            logger.info(f"ListBooks operation successful, returned {len(books_proto)} books, has_more: {has_more}")
            return book_pb2.ListBooksResponse(books=books_proto, next_cursor=next_cursor or '', has_more=has_more)
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} ListBooks operation failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return book_pb2.ListBooksResponse()

    def ListRecentBooks(self, request, context):
        """List recent books by updated_at"""
        logger.info(f"ListRecentBooks operation started with limit: {request.limit}")
        try:
            limit = request.limit if request.limit > 0 else 20
            results = self._book_service.list_recent_books(limit=limit)
            books = []
            for row in results:
                book = book_pb2.Book()
                ParseDict(row, book, ignore_unknown_fields=True)
                books.append(book)
            logger.info(f"ListRecentBooks operation successful, returned {len(books)} books")
            return book_pb2.ListRecentBooksResponse(books=books)
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} ListRecentBooks operation failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return book_pb2.ListRecentBooksResponse()

    def SearchBooks(self, request, context):
        """Search books by title or author"""
        logger.info(f"SearchBooks operation started with query: {request.query}")
        try:
            results = self._book_service.search_books(request.query)
            books = []
            for row in results:
                book = book_pb2.Book()
                ParseDict(row, book, ignore_unknown_fields=True)
                books.append(book)
            logger.info(f"SearchBooks operation successful, found {len(books)} books")
            return book_pb2.SearchBooksResponse(books=books)
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} SearchBooks operation failed for query '{request.query}': {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return book_pb2.SearchBooksResponse()

    def CreateMember(self, request, context):
        """Create a new member"""
        logger.info(f"CreateMember operation started for name: {request.name}, email: {request.email}")
        try:
            result = self._member_service.create_member(request.name, request.email)
            member = member_pb2.Member()
            ParseDict(result, member, ignore_unknown_fields=True)
            logger.info(f"CreateMember operation successful for member ID: {member.id}")
            return member_pb2.CreateMemberResponse(member=member, message=Messages.MEMBER_CREATED)
        except ValueError as e:
            if "Email already exists" in str(e):
                logger.warning(f"CreateMember: Email already exists for {request.email}")
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(json.dumps({"code": ErrorCodes.EMAIL_ALREADY_EXISTS, "message": str(e)}))
            else:
                logger.warning(f"CreateMember validation error: {str(e)}")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": str(e)}))
            return member_pb2.CreateMemberResponse()
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} CreateMember operation failed for {request.name}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
            return member_pb2.CreateMemberResponse()

    def ListMembers(self, request, context):
        """List members with pagination and search"""
        logger.info(f"ListMembers operation started with limit: {request.limit}, cursor: {request.cursor}, search: {request.search}")
        try:
            limit = request.limit if request.limit > 0 else 20
            members, next_cursor, has_more = self._member_service.list_members_paginated(
                limit=limit,
                cursor=request.cursor,
                search=request.search
            )
            members_proto = []
            for row in members:
                member = member_pb2.Member()
                ParseDict(row, member, ignore_unknown_fields=True)
                members_proto.append(member)
            logger.info(f"ListMembers operation successful, returned {len(members_proto)} members, has_more: {has_more}")
            return member_pb2.ListMembersResponse(members=members_proto, next_cursor=next_cursor or '', has_more=has_more)
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} ListMembers operation failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return member_pb2.ListMembersResponse()

    def SearchMembers(self, request, context):
        """Search members by name or email"""
        logger.info(f"SearchMembers operation started with query: {request.query}")
        try:
            results = self._member_service.search_members(request.query)
            members = []
            for row in results:
                member = member_pb2.Member()
                ParseDict(row, member, ignore_unknown_fields=True)
                members.append(member)
            logger.info(f"SearchMembers operation successful, found {len(members)} members")
            return member_pb2.SearchMembersResponse(members=members)
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} SearchMembers operation failed for query '{request.query}': {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return member_pb2.SearchMembersResponse()

    def UpdateMember(self, request, context):
        """Update an existing member"""
        logger.info(f"UpdateMember operation started for member ID: {request.id}, name: {request.name}, email: {request.email}")
        try:
            result = self._member_service.update_member(request.id, request.name, request.email)
            if not result:
                logger.warning(f"UpdateMember: Member not found for ID: {request.id}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(json.dumps({"code": ErrorCodes.MEMBER_NOT_FOUND, "message": "Member not found"}))
                return member_pb2.UpdateMemberResponse()
            member = member_pb2.Member()
            ParseDict(result, member, ignore_unknown_fields=True)
            logger.info(f"UpdateMember operation successful for member ID: {member.id}")
            return member_pb2.UpdateMemberResponse(member=member, message=Messages.MEMBER_UPDATED)
        except ValueError as e:
            if "Email already exists" in str(e):
                logger.warning(f"UpdateMember: Email already exists for {request.email}")
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(json.dumps({"code": ErrorCodes.EMAIL_ALREADY_EXISTS, "message": str(e)}))
            else:
                logger.warning(f"UpdateMember validation error: {str(e)}")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": str(e)}))
            return member_pb2.UpdateMemberResponse()
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} UpdateMember operation failed for ID {request.id}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
            return member_pb2.UpdateMemberResponse()

    def BorrowBook(self, request, context):
        """Borrow a book"""
        logger.info(f"BorrowBook operation started for book ID: {request.book_id}, member ID: {request.member_id}")
        try:
            # Borrow the book using the library service
            result = self._library_service.borrow_book(request.book_id, request.member_id)

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

            logger.info(f"BorrowBook operation successful, ledger entry ID: {ledger_entry.id}")
            return ledger_pb2.BorrowBookResponse(
                success=True,
                ledger_entry=ledger_entry,
                message=Messages.BOOK_BORROWED
            )
        except ValueError as e:
            error_msg = str(e)
            # Handle specific business logic errors
            if "already borrowed" in error_msg.lower() or "not available" in error_msg.lower():
                logger.warning(f"BorrowBook: Book {request.book_id} is not available")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(json.dumps({"code": ErrorCodes.BOOK_ALREADY_BORROWED, "message": error_msg}))
            elif "not found" in error_msg.lower():
                if "book" in error_msg.lower():
                    logger.warning(f"BorrowBook: Book {request.book_id} not found")
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(json.dumps({"code": ErrorCodes.BOOK_NOT_FOUND, "message": error_msg}))
                elif "member" in error_msg.lower():
                    logger.warning(f"BorrowBook: Member {request.member_id} not found")
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(json.dumps({"code": ErrorCodes.MEMBER_NOT_FOUND, "message": error_msg}))
                else:
                    logger.warning(f"BorrowBook validation error: {error_msg}")
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": error_msg}))
            else:
                logger.warning(f"BorrowBook validation error: {error_msg}")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": error_msg}))
            return ledger_pb2.BorrowBookResponse()
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} BorrowBook operation failed for book {request.book_id}, member {request.member_id}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
            return ledger_pb2.BorrowBookResponse()

    def ReturnBook(self, request, context):
        """Return a book"""
        logger.info(f"ReturnBook operation started for book ID: {request.book_id}, member ID: {request.member_id}")
        try:
            # Return the book using the library service
            result = self._library_service.return_book(request.book_id, request.member_id)

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

            logger.info(f"ReturnBook operation successful, ledger entry ID: {ledger_entry.id}")
            return ledger_pb2.ReturnBookResponse(
                success=True,
                ledger_entry=ledger_entry,
                message=Messages.BOOK_RETURNED
            )
        except ValueError as e:
            error_msg = str(e)
            # Handle specific business logic errors
            if "not currently borrowed" in error_msg.lower() or "not borrowed" in error_msg.lower():
                logger.warning(f"ReturnBook: Book {request.book_id} is not currently borrowed")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(json.dumps({"code": ErrorCodes.BOOK_NOT_BORROWED, "message": error_msg}))
            elif "did not borrow" in error_msg.lower() or "not borrowed by" in error_msg.lower():
                logger.warning(f"ReturnBook: Book {request.book_id} is not borrowed by member {request.member_id}")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(json.dumps({"code": ErrorCodes.BOOK_NOT_BORROWED_BY_MEMBER, "message": error_msg}))
            elif "not found" in error_msg.lower():
                if "book" in error_msg.lower():
                    logger.warning(f"ReturnBook: Book {request.book_id} not found")
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(json.dumps({"code": ErrorCodes.BOOK_NOT_FOUND, "message": error_msg}))
                else:
                    logger.warning(f"ReturnBook validation error: {error_msg}")
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": error_msg}))
            else:
                logger.warning(f"ReturnBook validation error: {error_msg}")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(json.dumps({"code": ErrorCodes.INVALID_INPUT, "message": error_msg}))
            return ledger_pb2.ReturnBookResponse()
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} ReturnBook operation failed for book {request.book_id}, member {request.member_id}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(json.dumps({"code": "INTERNAL_ERROR", "message": "An internal error occurred"}))
            return ledger_pb2.ReturnBookResponse()

    def ListBorrowedBooks(self, request, context):
        """List all books borrowed by a member"""
        logger.info(f"ListBorrowedBooks operation started for member ID: {request.member_id}")
        try:
            results = self._book_service.list_borrowed_books(request.member_id)
            books = []
            for row in results:
                book = book_pb2.Book()
                ParseDict(row, book, ignore_unknown_fields=True)
                books.append(book)
            logger.info(f"ListBorrowedBooks operation successful, returned {len(books)} books for member {request.member_id}")
            return ledger_pb2.ListBorrowedBooksResponse(books=books)
        except Exception as e:
            logger.error(f"{Config.ERROR_KEYWORD} ListBorrowedBooks operation failed for member {request.member_id}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ledger_pb2.ListBorrowedBooksResponse()


def serve():
    """Start the gRPC server"""
    # Create tables if not exist
    from db_helper import engine, Base
    Base.metadata.create_all(bind=engine)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    library_pb2_grpc.add_LibraryServiceServicer_to_server(LibraryGrpcService(), server)

    port = Config.SERVER_PORT
    server.add_insecure_port('[::]:' + port)
    server.start()
    logger.info(f"Library gRPC server started, listening on port {port}")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        server.stop(0)


if __name__ == '__main__':
    serve()
