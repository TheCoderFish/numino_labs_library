import re
from db_helper import DatabaseHelper

class BusinessLogic:
    @staticmethod
    def validate_book_data(title, author):
        if not title or not title.strip():
            raise ValueError("Title is required and cannot be empty")
        if not author or not author.strip():
            raise ValueError("Author is required and cannot be empty")

    @staticmethod
    def validate_member_data(name, email):
        if not name or not name.strip():
            raise ValueError("Name is required and cannot be empty")
        if not email or not email.strip():
            raise ValueError("Email is required and cannot be empty")
        # Basic email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format")

    @staticmethod
    def is_book_available(book_id):
        book = DatabaseHelper.get_book_by_id(book_id)
        return book and not book.get('is_borrowed', False)

    @staticmethod
    def member_exists(member_id):
        member = DatabaseHelper.get_member_by_id(member_id)
        return member is not None

    @staticmethod
    def is_book_borrowed_by_member(book_id, member_id):
        book = DatabaseHelper.get_book_by_id(book_id)
        return book and book.get('is_borrowed', False) and book.get('current_member_id') == member_id

    @staticmethod
    def can_member_borrow_more(member_id):
        # For now, no limit, but can add logic later
        return True