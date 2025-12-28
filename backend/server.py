import os
import grpc
from concurrent import futures
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from datetime import datetime, date
from dotenv import load_dotenv
import library_pb2
import library_pb2_grpc

load_dotenv()

# Database connection pool
db_pool = None

def get_db_connection():
    """Get a database connection from the pool"""
    return db_pool.getconn()

def return_db_connection(conn):
    """Return a connection to the pool"""
    db_pool.putconn(conn)

def init_db_pool():
    """Initialize the database connection pool"""
    global db_pool
    db_pool = psycopg2.pool.ThreadedConnectionPool(
        1, 20,
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5435'),
        database=os.getenv('DB_NAME', 'numino_db'),
        user=os.getenv('DB_USER', 'numino_user'),
        password=os.getenv('DB_PASSWORD', 'numino_password')
    )

class LibraryService(library_pb2_grpc.LibraryServiceServicer):
    
    def CreateBook(self, request, context):
        """Create a new book"""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO book (title, author, is_borrowed) VALUES (%s, %s, FALSE) RETURNING id, title, author, is_borrowed, current_member_id",
                    (request.title, request.author)
                )
                result = cur.fetchone()
                conn.commit()
                
                book = library_pb2.Book(
                    id=result['id'],
                    title=result['title'],
                    author=result['author'],
                    is_borrowed=result['is_borrowed'],
                    current_member_id=result['current_member_id'] or 0
                )
                return library_pb2.CreateBookResponse(book=book, message="Book created successfully")
        except Exception as e:
            conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.CreateBookResponse()
        finally:
            return_db_connection(conn)
    
    def UpdateBook(self, request, context):
        """Update an existing book"""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "UPDATE book SET title = %s, author = %s WHERE id = %s RETURNING id, title, author, is_borrowed, current_member_id",
                    (request.title, request.author, request.id)
                )
                result = cur.fetchone()
                if not result:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Book not found")
                    return library_pb2.UpdateBookResponse()
                
                conn.commit()
                
                book = library_pb2.Book(
                    id=result['id'],
                    title=result['title'],
                    author=result['author'],
                    is_borrowed=result['is_borrowed'],
                    current_member_id=result['current_member_id'] or 0
                )
                return library_pb2.UpdateBookResponse(book=book, message="Book updated successfully")
        except Exception as e:
            conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.UpdateBookResponse()
        finally:
            return_db_connection(conn)
    
    def ListBooks(self, request, context):
        """List all books with member name"""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT b.id, b.title, b.author, b.is_borrowed, b.current_member_id, 
                           COALESCE(m.name, '') as current_member_name
                    FROM book b
                    LEFT JOIN member m ON b.current_member_id = m.id
                    ORDER BY b.id
                """)
                results = cur.fetchall()
                
                books = []
                for row in results:
                    books.append(library_pb2.Book(
                        id=row['id'],
                        title=row['title'],
                        author=row['author'],
                        is_borrowed=row['is_borrowed'],
                        current_member_id=row['current_member_id'] or 0,
                        current_member_name=row['current_member_name'] or ''
                    ))
                
                return library_pb2.ListBooksResponse(books=books)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.ListBooksResponse()
        finally:
            return_db_connection(conn)
    
    def SearchBooks(self, request, context):
        """Search books by title or author"""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = f"%{request.query}%"
                cur.execute("""
                    SELECT b.id, b.title, b.author, b.is_borrowed, b.current_member_id,
                           COALESCE(m.name, '') as current_member_name
                    FROM book b
                    LEFT JOIN member m ON b.current_member_id = m.id
                    WHERE b.title ILIKE %s OR b.author ILIKE %s
                    ORDER BY b.title
                    LIMIT 50
                """, (query, query))
                results = cur.fetchall()
                
                books = []
                for row in results:
                    books.append(library_pb2.Book(
                        id=row['id'],
                        title=row['title'],
                        author=row['author'],
                        is_borrowed=row['is_borrowed'],
                        current_member_id=row['current_member_id'] or 0,
                        current_member_name=row['current_member_name'] or ''
                    ))
                
                return library_pb2.SearchBooksResponse(books=books)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.SearchBooksResponse()
        finally:
            return_db_connection(conn)
    
    def CreateMember(self, request, context):
        """Create a new member"""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO member (name, email) VALUES (%s, %s) RETURNING id, name, email",
                    (request.name, request.email)
                )
                result = cur.fetchone()
                conn.commit()
                
                member = library_pb2.Member(
                    id=result['id'],
                    name=result['name'],
                    email=result['email']
                )
                return library_pb2.CreateMemberResponse(member=member, message="Member created successfully")
        except psycopg2.IntegrityError:
            conn.rollback()
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Email already exists")
            return library_pb2.CreateMemberResponse()
        except Exception as e:
            conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.CreateMemberResponse()
        finally:
            return_db_connection(conn)
    
    def ListMembers(self, request, context):
        """List all members"""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, name, email FROM member ORDER BY name")
                results = cur.fetchall()
                
                members = []
                for row in results:
                    members.append(library_pb2.Member(
                        id=row['id'],
                        name=row['name'],
                        email=row['email']
                    ))
                
                return library_pb2.ListMembersResponse(members=members)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.ListMembersResponse()
        finally:
            return_db_connection(conn)
    
    def SearchMembers(self, request, context):
        """Search members by name or email"""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = f"%{request.query}%"
                cur.execute("""
                    SELECT id, name, email FROM member
                    WHERE name ILIKE %s OR email ILIKE %s
                    ORDER BY name
                    LIMIT 50
                """, (query, query))
                results = cur.fetchall()
                
                members = []
                for row in results:
                    members.append(library_pb2.Member(
                        id=row['id'],
                        name=row['name'],
                        email=row['email']
                    ))
                
                return library_pb2.SearchMembersResponse(members=members)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.SearchMembersResponse()
        finally:
            return_db_connection(conn)
    
    def UpdateMember(self, request, context):
        """Update an existing member"""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "UPDATE member SET name = %s, email = %s WHERE id = %s RETURNING id, name, email",
                    (request.name, request.email, request.id)
                )
                result = cur.fetchone()
                if not result:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Member not found")
                    return library_pb2.UpdateMemberResponse()
                
                conn.commit()
                
                member = library_pb2.Member(
                    id=result['id'],
                    name=result['name'],
                    email=result['email']
                )
                return library_pb2.UpdateMemberResponse(member=member, message="Member updated successfully")
        except psycopg2.IntegrityError:
            conn.rollback()
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Email already exists")
            return library_pb2.UpdateMemberResponse()
        except Exception as e:
            conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.UpdateMemberResponse()
        finally:
            return_db_connection(conn)
    
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
                    return library_pb2.BorrowBookResponse()
                
                if book['is_borrowed']:
                    conn.rollback()
                    context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                    context.set_details("Book is already borrowed")
                    return library_pb2.BorrowBookResponse()
                
                # Verify member exists
                cur.execute("SELECT id FROM member WHERE id = %s", (request.member_id,))
                member = cur.fetchone()
                if not member:
                    conn.rollback()
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Member not found")
                    return library_pb2.BorrowBookResponse()
                
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
                
                ledger = library_pb2.LedgerEntry(
                    id=ledger_entry['id'],
                    book_id=ledger_entry['book_id'],
                    member_id=ledger_entry['member_id'],
                    action_type=ledger_entry['action_type'],
                    log_date=ledger_entry['log_date'].isoformat() if ledger_entry['log_date'] else '',
                    due_date_snapshot=ledger_entry['due_date_snapshot'].isoformat() if ledger_entry['due_date_snapshot'] else ''
                )
                
                return library_pb2.BorrowBookResponse(
                    success=True,
                    message="Book borrowed successfully",
                    ledger_entry=ledger
                )
        except Exception as e:
            conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.BorrowBookResponse()
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
                    return library_pb2.ReturnBookResponse()
                
                if not book['is_borrowed']:
                    conn.rollback()
                    context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                    context.set_details("Book is not currently borrowed")
                    return library_pb2.ReturnBookResponse()
                
                if book['current_member_id'] != request.member_id:
                    conn.rollback()
                    context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                    context.set_details("This member did not borrow this book")
                    return library_pb2.ReturnBookResponse()
                
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
                
                ledger = library_pb2.LedgerEntry(
                    id=ledger_entry['id'],
                    book_id=ledger_entry['book_id'],
                    member_id=ledger_entry['member_id'],
                    action_type=ledger_entry['action_type'],
                    log_date=ledger_entry['log_date'].isoformat() if ledger_entry['log_date'] else '',
                    due_date_snapshot=''
                )
                
                return library_pb2.ReturnBookResponse(
                    success=True,
                    message="Book returned successfully",
                    ledger_entry=ledger
                )
        except Exception as e:
            conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.ReturnBookResponse()
        finally:
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)
            return_db_connection(conn)
    
    def ListBorrowedBooks(self, request, context):
        """List all books borrowed by a member"""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, title, author, is_borrowed, current_member_id FROM book WHERE current_member_id = %s AND is_borrowed = TRUE ORDER BY id",
                    (request.member_id,)
                )
                results = cur.fetchall()
                
                books = []
                for row in results:
                    books.append(library_pb2.Book(
                        id=row['id'],
                        title=row['title'],
                        author=row['author'],
                        is_borrowed=row['is_borrowed'],
                        current_member_id=row['current_member_id'] or 0
                    ))
                
                return library_pb2.ListBorrowedBooksResponse(books=books)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.ListBorrowedBooksResponse()
        finally:
            return_db_connection(conn)


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

