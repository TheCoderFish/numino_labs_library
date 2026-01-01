import json
import os
import re
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

Base = declarative_base()


class Member(Base):
    __tablename__ = 'member'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def validate_data(cls, name, email):
        if not name or not name.strip():
            raise ValueError("Name is required and cannot be empty")
        if not email or not email.strip():
            raise ValueError("Email is required and cannot be empty")
        # Basic email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format")

    @classmethod
    def exists(cls, session, member_id):
        member = session.query(cls).filter(cls.id == member_id).first()
        return member is not None


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    is_borrowed = Column(Boolean, default=False)
    current_member_id = Column(Integer, ForeignKey('member.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def validate_data(cls, title, author):
        if not title or not title.strip():
            raise ValueError("Title is required and cannot be empty")
        if not author or not author.strip():
            raise ValueError("Author is required and cannot be empty")

    @classmethod
    def is_available(cls, session, book_id):
        book = session.query(cls).filter(cls.id == book_id).first()
        return book and not book.is_borrowed

    @classmethod
    def is_borrowed_by_member(cls, session, book_id, member_id):
        book = session.query(cls).filter(cls.id == book_id).first()
        return book and book.is_borrowed and book.current_member_id == member_id


class Ledger(Base):
    __tablename__ = 'ledger'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('member.id'), nullable=False)
    action_type = Column(String, nullable=False)  # 'BORROW' or 'RETURN'
    log_date = Column(DateTime, default=datetime.utcnow)
    due_date_snapshot = Column(DateTime)


# Database setup
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseHelper:
    @staticmethod
    def sqlalchemy_to_dict(obj):
        data = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        data.pop('_sa_instance_state', None)
        for key, value in data.items():
            # Convert datetime objects to ISO strings for ParseDict
            if isinstance(value, datetime):
                data[key] = value.strftime('%Y-%m-%dT%H:%M:%SZ')

        return data

    @staticmethod
    def create_book(title, author):
        db = SessionLocal()
        try:
            book = Book(title=title, author=author, is_borrowed=False)
            db.add(book)
            db.commit()
            db.refresh(book)
            return DatabaseHelper.sqlalchemy_to_dict(book)
        except IntegrityError:
            db.rollback()
            raise ValueError("Book creation failed due to integrity constraint")
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def update_book(book_id, title, author):
        db = SessionLocal()
        try:
            book = db.query(Book).filter(Book.id == book_id).first()
            if not book:
                return None
            book.title = title
            book.author = author
            book.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(book)
            return DatabaseHelper.sqlalchemy_to_dict(book)
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def list_books():
        db = SessionLocal()
        try:
            books = db.query(Book, Member.name.label('current_member_name')).outerjoin(Member,
                                                                                       Book.current_member_id == Member.id).all()
            result = []
            for book, member_name in books:
                book_dict = DatabaseHelper.sqlalchemy_to_dict(book)
                book_dict['current_member_name'] = member_name or ''
                result.append(book_dict)
            return result
        except SQLAlchemyError as e:
            raise e
        finally:
            db.close()

    @staticmethod
    def list_recent_books(limit=20):
        db = SessionLocal()
        try:
            books = db.query(Book, Member.name.label('current_member_name')).outerjoin(Member,
                                                                                       Book.current_member_id == Member.id).order_by(Book.updated_at.desc()).limit(limit).all()
            result = []
            for book, member_name in books:
                book_dict = DatabaseHelper.sqlalchemy_to_dict(book)
                book_dict['current_member_name'] = member_name or ''
                result.append(book_dict)
            return result
        except SQLAlchemyError as e:
            raise e
        finally:
            db.close()

    @staticmethod
    def list_books_paginated(limit=20, cursor=None, filter_type='all', search=None):
        db = SessionLocal()
        try:
            query = db.query(Book, Member.name.label('current_member_name')).outerjoin(Member,
                                                                                       Book.current_member_id == Member.id)
            
            # Apply search filter
            if search:
                query = query.filter(
                    (Book.title.ilike(f"%{search}%")) | (Book.author.ilike(f"%{search}%"))
                )
            
            # Apply status filter
            if filter_type == 'available':
                query = query.filter(Book.is_borrowed == False)
            elif filter_type == 'borrowed':
                query = query.filter(Book.is_borrowed == True)
            
            # Apply cursor for pagination
            if cursor:
                try:
                    cursor_id = int(cursor)
                    query = query.filter(Book.id > cursor_id)
                except ValueError:
                    pass  # Invalid cursor, ignore
            
            # Order by ID for consistent pagination
            query = query.order_by(Book.id)
            
            # Limit results
            books = query.limit(limit + 1).all()  # +1 to check if there are more
            
            result = []
            for book, member_name in books[:limit]:
                book_dict = DatabaseHelper.sqlalchemy_to_dict(book)
                book_dict['current_member_name'] = member_name or ''
                result.append(book_dict)
            
            # Determine next cursor and has_more
            has_more = len(books) > limit
            next_cursor = str(books[limit - 1][0].id) if result and has_more else None
            
            return result, next_cursor, has_more
        except SQLAlchemyError as e:
            raise e
        finally:
            db.close()

    @staticmethod
    def search_books(query):
        db = SessionLocal()
        try:
            books = db.query(Book, Member.name.label('current_member_name')).outerjoin(Member,
                                                                                       Book.current_member_id == Member.id).filter(
                (Book.title.ilike(f"%{query}%")) | (Book.author.ilike(f"%{query}%"))
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
            db.close()

    @staticmethod
    def create_member(name, email):
        db = SessionLocal()
        try:
            member = Member(name=name, email=email)
            db.add(member)
            db.commit()
            db.refresh(member)
            return DatabaseHelper.sqlalchemy_to_dict(member)
        except IntegrityError:
            db.rollback()
            raise ValueError("Email already exists")
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def update_member(member_id, name, email):
        db = SessionLocal()
        try:
            member = db.query(Member).filter(Member.id == member_id).first()
            if not member:
                return None
            member.name = name
            member.email = email
            member.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(member)
            return DatabaseHelper.sqlalchemy_to_dict(member)
        except IntegrityError:
            db.rollback()
            raise ValueError("Email already exists")
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def list_members():
        db = SessionLocal()
        try:
            members = db.query(Member).all()
            return [DatabaseHelper.sqlalchemy_to_dict(member) for member in members]
        except SQLAlchemyError as e:
            raise e
        finally:
            db.close()

    @staticmethod
    def list_members_paginated(limit=20, cursor=None, search=None):
        db = SessionLocal()
        try:
            query = db.query(Member)
            
            # Apply search filter
            if search:
                query = query.filter(
                    (Member.name.ilike(f"%{search}%")) | (Member.email.ilike(f"%{search}%"))
                )
            
            # Apply cursor for pagination
            if cursor:
                try:
                    cursor_id = int(cursor)
                    query = query.filter(Member.id > cursor_id)
                except ValueError:
                    pass  # Invalid cursor, ignore
            
            # Order by ID for consistent pagination
            query = query.order_by(Member.id)
            
            # Limit results
            members = query.limit(limit + 1).all()  # +1 to check if there are more
            
            result = [DatabaseHelper.sqlalchemy_to_dict(member) for member in members[:limit]]
            
            # Determine next cursor and has_more
            has_more = len(members) > limit
            next_cursor = str(members[limit - 1].id) if result and has_more else None
            
            return result, next_cursor, has_more
        except SQLAlchemyError as e:
            raise e
        finally:
            db.close()

    @staticmethod
    def search_members(query):
        db = SessionLocal()
        try:
            members = db.query(Member).filter(
                (Member.name.ilike(f"%{query}%")) | (Member.email.ilike(f"%{query}%"))
            ).limit(50).all()
            return [DatabaseHelper.sqlalchemy_to_dict(member) for member in members]
        except SQLAlchemyError as e:
            raise e
        finally:
            db.close()

    @staticmethod
    def list_borrowed_books(member_id):
        db = SessionLocal()
        try:
            books = db.query(Book).filter(Book.current_member_id == member_id, Book.is_borrowed == True).all()
            return [DatabaseHelper.sqlalchemy_to_dict(book) for book in books]
        except SQLAlchemyError as e:
            raise e
        finally:
            db.close()

    @staticmethod
    def get_book_by_id(book_id):
        db = SessionLocal()
        try:
            book = db.query(Book).filter(Book.id == book_id).first()
            return DatabaseHelper.sqlalchemy_to_dict(book) if book else None
        except SQLAlchemyError as e:
            raise e
        finally:
            db.close()

    @staticmethod
    def is_book_available(book_id):
        db = SessionLocal()
        try:
            return Book.is_available(db, book_id)
        finally:
            db.close()

    @staticmethod
    def member_exists(member_id):
        db = SessionLocal()
        try:
            return Member.exists(db, member_id)
        finally:
            db.close()

    @staticmethod
    def is_book_borrowed_by_member(book_id, member_id):
        db = SessionLocal()
        try:
            return Book.is_borrowed_by_member(db, book_id, member_id)
        finally:
            db.close()

    @staticmethod
    def borrow_book(book_id, member_id):
        db = SessionLocal()
        try:
            # Get the book
            book = db.query(Book).filter(Book.id == book_id).first()
            if not book:
                raise ValueError("Book not found")
            if book.is_borrowed:
                raise ValueError("Book is already borrowed")

            # Get the member
            member = db.query(Member).filter(Member.id == member_id).first()
            if not member:
                raise ValueError("Member not found")

            # Update book
            book.is_borrowed = True
            book.current_member_id = member_id
            book.updated_at = datetime.utcnow()

            # Create ledger entry
            ledger_entry = Ledger(
                book_id=book_id,
                member_id=member_id,
                action_type='BORROW',
                due_date_snapshot=datetime.utcnow()  # You can add logic for due date calculation
            )
            db.add(ledger_entry)

            db.commit()
            db.refresh(ledger_entry)

            return DatabaseHelper.sqlalchemy_to_dict(ledger_entry)
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def return_book(book_id, member_id):
        db = SessionLocal()
        try:
            # Get the book
            book = db.query(Book).filter(Book.id == book_id).first()
            if not book:
                raise ValueError("Book not found")
            if not book.is_borrowed:
                raise ValueError("Book is not currently borrowed")
            if book.current_member_id != member_id:
                raise ValueError("This member did not borrow this book")

            # Update book
            book.is_borrowed = False
            book.current_member_id = None
            book.updated_at = datetime.utcnow()

            # Create ledger entry
            ledger_entry = Ledger(
                book_id=book_id,
                member_id=member_id,
                action_type='RETURN',
                due_date_snapshot=None
            )
            db.add(ledger_entry)

            db.commit()
            db.refresh(ledger_entry)

            return DatabaseHelper.sqlalchemy_to_dict(ledger_entry)
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()
