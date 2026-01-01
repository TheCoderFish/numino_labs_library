import os
import grpc
from concurrent import futures
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from datetime import datetime, date
from dotenv import load_dotenv
import book_pb2
import member_pb2
import ledger_pb2
import library_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from db_helper import DatabaseHelper, init_db_pool, db_pool

load_dotenv()

class LibraryService(library_pb2_grpc.LibraryServiceServicer):
    
    def CreateBook(self, request, context):
        """Create a new book"""
        try:
            result = DatabaseHelper.execute_query(
                "INSERT INTO book (title, author, is_borrowed) VALUES (%s, %s, FALSE) RETURNING id, title, author, is_borrowed, current_member_id, created_at, updated_at",
                (request.title, request.author),
                fetch_one=True
            )
            
            # Convert timestamps
            created_at_ts = Timestamp()
            created_at_ts.FromDatetime(result['created_at'])
            updated_at_ts = Timestamp()
            updated_at_ts.FromDatetime(result['updated_at'])
            
            book = book_pb2.Book(
                id=result['id'],
                title=result['title'],
                author=result['author'],
                is_borrowed=result['is_borrowed'],
                current_member_id=result['current_member_id'] or 0,
                created_at=created_at_ts,
                updated_at=updated_at_ts
            )
            return book_pb2.CreateBookResponse(book=book, message="Book created successfully")
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return book_pb2.CreateBookResponse()
    
    def UpdateBook(self, request, context):
        """Update an existing book"""
        try:
            result = DatabaseHelper.execute_query(
                "UPDATE book SET title = %s, author = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING id, title, author, is_borrowed, current_member_id, created_at, updated_at",
                (request.title, request.author, request.id),
                fetch_one=True
            )
            if not result:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Book not found")
                return book_pb2.UpdateBookResponse()
            
            # Convert timestamps
            created_at_ts = Timestamp()
            created_at_ts.FromDatetime(result['created_at'])
            updated_at_ts = Timestamp()
            updated_at_ts.FromDatetime(result['updated_at'])
            
            book = book_pb2.Book(
                id=result['id'],
                title=result['title'],
                author=result['author'],
                is_borrowed=result['is_borrowed'],
                current_member_id=result['current_member_id'] or 0,
                created_at=created_at_ts,
                updated_at=updated_at_ts
            )
            return book_pb2.UpdateBookResponse(book=book, message="Book updated successfully")
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return book_pb2.UpdateBookResponse()
    
    def ListBooks(self, request, context):
        """List all books with member name"""
        try:
            results = DatabaseHelper.execute_query("""
                SELECT b.id, b.title, b.author, b.is_borrowed, b.current_member_id, b.created_at, b.updated_at,
                       COALESCE(m.name, '') as current_member_name
                FROM book b
                LEFT JOIN member m ON b.current_member_id = m.id
                ORDER BY b.id
            """, fetch_all=True)
            
            books = []
            for row in results:
                created_at_ts = Timestamp()
                created_at_ts.FromDatetime(row['created_at'])
                updated_at_ts = Timestamp()
                updated_at_ts.FromDatetime(row['updated_at'])
                
                books.append(book_pb2.Book(
                    id=row['id'],
                    title=row['title'],
                    author=row['author'],
                    is_borrowed=row['is_borrowed'],
                    current_member_id=row['current_member_id'] or 0,
                    current_member_name=row['current_member_name'] or '',
                    created_at=created_at_ts,
                    updated_at=updated_at_ts
                ))
            
            return book_pb2.ListBooksResponse(books=books)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return book_pb2.ListBooksResponse()
    
    def SearchBooks(self, request, context):
        """Search books by title or author"""
        try:
            query = f"%{request.query}%"
            results = DatabaseHelper.execute_query("""
                SELECT b.id, b.title, b.author, b.is_borrowed, b.current_member_id, b.created_at, b.updated_at,
                       COALESCE(m.name, '') as current_member_name
                FROM book b
                LEFT JOIN member m ON b.current_member_id = m.id
                WHERE b.title ILIKE %s OR b.author ILIKE %s
                ORDER BY b.title
                LIMIT 50
            """, (query, query), fetch_all=True)
            
            books = []
            for row in results:
                created_at_ts = Timestamp()
                created_at_ts.FromDatetime(row['created_at'])
                updated_at_ts = Timestamp()
                updated_at_ts.FromDatetime(row['updated_at'])
                
                books.append(book_pb2.Book(
                    id=row['id'],
                    title=row['title'],
                    author=row['author'],
                    is_borrowed=row['is_borrowed'],
                    current_member_id=row['current_member_id'] or 0,
                    current_member_name=row['current_member_name'] or '',
                    created_at=created_at_ts,
                    updated_at=updated_at_ts
                ))
            
            return book_pb2.SearchBooksResponse(books=books)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return book_pb2.SearchBooksResponse()
    
    def CreateMember(self, request, context):
        """Create a new member"""
        try:
            result = DatabaseHelper.execute_query(
                "INSERT INTO member (name, email) VALUES (%s, %s) RETURNING id, name, email, created_at, updated_at",
                (request.name, request.email),
                fetch_one=True
            )
            
            created_at_ts = Timestamp()
            created_at_ts.FromDatetime(result['created_at'])
            updated_at_ts = Timestamp()
            updated_at_ts.FromDatetime(result['updated_at'])
            
            member = member_pb2.Member(
                id=result['id'],
                name=result['name'],
                email=result['email'],
                created_at=created_at_ts,
                updated_at=updated_at_ts
            )
            return member_pb2.CreateMemberResponse(member=member, message="Member created successfully")
        except psycopg2.IntegrityError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Email already exists")
            return member_pb2.CreateMemberResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return member_pb2.CreateMemberResponse()
    
    def ListMembers(self, request, context):
        """List all members"""
        try:
            results = DatabaseHelper.execute_query("SELECT id, name, email, created_at, updated_at FROM member ORDER BY name", fetch_all=True)
            
            members = []
            for row in results:
                created_at_ts = Timestamp()
                created_at_ts.FromDatetime(row['created_at'])
                updated_at_ts = Timestamp()
                updated_at_ts.FromDatetime(row['updated_at'])
                
                members.append(member_pb2.Member(
                    id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    created_at=created_at_ts,
                    updated_at=updated_at_ts
                ))
            
            return member_pb2.ListMembersResponse(members=members)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return member_pb2.ListMembersResponse()
    
    def SearchMembers(self, request, context):
        """Search members by name or email"""
        try:
            query = f"%{request.query}%"
            results = DatabaseHelper.execute_query("""
                SELECT id, name, email, created_at, updated_at FROM member
                WHERE name ILIKE %s OR email ILIKE %s
                ORDER BY name
                LIMIT 50
            """, (query, query), fetch_all=True)
            
            members = []
            for row in results:
                created_at_ts = Timestamp()
                created_at_ts.FromDatetime(row['created_at'])
                updated_at_ts = Timestamp()
                updated_at_ts.FromDatetime(row['updated_at'])
                
                members.append(member_pb2.Member(
                    id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    created_at=created_at_ts,
                    updated_at=updated_at_ts
                ))
            
            return member_pb2.SearchMembersResponse(members=members)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return member_pb2.SearchMembersResponse()
    
    def UpdateMember(self, request, context):
        """Update an existing member"""
        try:
            result = DatabaseHelper.execute_query(
                "UPDATE member SET name = %s, email = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING id, name, email, created_at, updated_at",
                (request.name, request.email, request.id),
                fetch_one=True
            )
            if not result:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Member not found")
                return member_pb2.UpdateMemberResponse()
            
            created_at_ts = Timestamp()
            created_at_ts.FromDatetime(result['created_at'])
            updated_at_ts = Timestamp()
            updated_at_ts.FromDatetime(result['updated_at'])
            
            member = member_pb2.Member(
                id=result['id'],
                name=result['name'],
                email=result['email'],
                created_at=created_at_ts,
                updated_at=updated_at_ts
            )
            return member_pb2.UpdateMemberResponse(member=member, message="Member updated successfully")
        except psycopg2.IntegrityError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Email already exists")
            return member_pb2.UpdateMemberResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return member_pb2.UpdateMemberResponse()
    
    def BorrowBook(self, request, context):
        """Borrow a book with transaction and locking"""
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
            results = DatabaseHelper.execute_query(
                "SELECT id, title, author, is_borrowed, current_member_id, created_at, updated_at FROM book WHERE current_member_id = %s AND is_borrowed = TRUE ORDER BY id",
                (request.member_id,),
                fetch_all=True
            )
            
            books = []
            for row in results:
                created_at_ts = Timestamp()
                created_at_ts.FromDatetime(row['created_at'])
                updated_at_ts = Timestamp()
                updated_at_ts.FromDatetime(row['updated_at'])
                
                books.append(book_pb2.Book(
                    id=row['id'],
                    title=row['title'],
                    author=row['author'],
                    is_borrowed=row['is_borrowed'],
                    current_member_id=row['current_member_id'] or 0,
                    created_at=created_at_ts,
                    updated_at=updated_at_ts
                ))
            
            return ledger_pb2.ListBorrowedBooksResponse(books=books)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ledger_pb2.ListBorrowedBooksResponse()


def serve():
    """Start the gRPC server"""
    init_db_pool()
    
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
        db_pool.closeall()


if __name__ == '__main__':
    serve()

