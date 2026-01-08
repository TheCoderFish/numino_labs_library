from abc import ABC
from typing import Optional

from db_helper import Book, Member


class BaseService(ABC):
    """Base service class providing common validation methods"""

    @staticmethod
    def validate_book_data(title: str, author: str) -> None:
        """Validate book data"""
        Book.validate_data(title, author)

    @staticmethod
    def validate_member_data(name: str, email: str) -> None:
        """Validate member data"""
        Member.validate_data(name, email)